"""Isolated Google Maps street verification & screenshot branch for AgentNet Corner."""
from __future__ import annotations

import base64
import csv
import email.parser
import email.policy
import html
import io
import os
import re
import secrets
import sqlite3
import threading
import time
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

MAX_SHOT_BYTES = 2 * 1024 * 1024  # 2 MiB
SHOT_EXT_CONTENT_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.webp': 'image/webp',
}
CODE_RE = re.compile(r'^[A-Za-z0-9_-]{2,32}$')
SHOT_FILE_RE = re.compile(r'^[A-Za-z0-9_-]{2,32}\.(png|jpg|webp)$')

CANONICAL_PREFIXES = (
    'ĐƯỜNG',
    'PHỐ',
    'ĐÊ',
    'CẦU',
    'NGÕ',
    'HẺM',
    'KHÁC',
    'KHÔNG TÌM THẤY',
)

_PREFIX_ALIASES = {
    'DUONG': 'ĐƯỜNG',
    'D': 'ĐƯỜNG',
    'PHO': 'PHỐ',
    'P': 'PHỐ',
    'DE': 'ĐÊ',
    'CAU': 'CẦU',
    'NGO': 'NGÕ',
    'NG': 'NGÕ',
    'HEM': 'HẺM',
    'KHAC': 'KHÁC',
    'KHONG TIM THAY': 'KHÔNG TÌM THẤY',
}

_TRAILING_EN_ROAD = ('STREET', 'ST', 'ROAD', 'RD', 'AVENUE', 'AVE', 'LANE', 'LN', 'ALLEY', 'ALY')


def _esc(val: object) -> str:
    return html.escape('' if val is None else str(val), quote=True)


def strip_vn_accents(text: str) -> str:
    """Fold Vietnamese text into uppercase ASCII without diacritics."""
    s = (text or '').replace('Đ', 'D').replace('đ', 'd')
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return ' '.join(s.upper().split())


def normalize_prefix(raw: str) -> str:
    """Normalize a Vietnamese road prefix label to canonical uppercase Vietnamese."""
    folded = strip_vn_accents(raw).replace('.', '').strip()
    return _PREFIX_ALIASES.get(folded, (raw or '').strip().upper())


def split_prefix_and_core(name: str, explicit_prefix: str = '') -> tuple[str, str]:
    """Extract normalized prefix and core street name without diacritics or trailing city."""
    first_seg = (name or '').split(',', 1)[0].strip()
    folded = strip_vn_accents(first_seg)
    clean_words = re.sub(r'[^A-Z0-9]+', ' ', folded).strip().split()

    detected_prefix = ''
    if clean_words and clean_words[0] in _PREFIX_ALIASES:
        detected_prefix = _PREFIX_ALIASES[clean_words[0]]
        clean_words = clean_words[1:]
    elif len(clean_words) > 1 and clean_words[-1] in _TRAILING_EN_ROAD:
        clean_words = clean_words[:-1]

    eff_prefix = normalize_prefix(explicit_prefix) if (explicit_prefix or '').strip() else detected_prefix
    core = ' '.join(clean_words)
    return eff_prefix, core


def classify_maps_match(pdf_name: str, pdf_prefix: str, maps_found_name: str, maps_prefix: str) -> str:
    """Classify comparison between final PDF street entry and Google Maps observation."""
    norm_explicit = normalize_prefix(maps_prefix) if (maps_prefix or '').strip() else ''
    if norm_explicit == 'KHÔNG TÌM THẤY' or not (maps_found_name or '').strip():
        return 'KHÔNG TÌM THẤY'

    norm_pdf_prefix, pdf_core = split_prefix_and_core(pdf_name, pdf_prefix)
    eff_maps_prefix, maps_core = split_prefix_and_core(maps_found_name, norm_explicit)

    compact_pdf = re.sub(r'[^A-Z0-9]+', '', pdf_core)
    compact_maps = re.sub(r'[^A-Z0-9]+', '', maps_core)
    if not compact_maps:
        return 'KHÔNG TÌM THẤY'

    if compact_pdf == compact_maps:
        if not eff_maps_prefix or eff_maps_prefix == norm_pdf_prefix:
            return 'KHỚP'
        return 'KHÁC TIỀN TỐ (ĐƯỜNG/PHỐ)'
    return 'KHÁC TÊN'


def detect_image_ext(data: bytes) -> str | None:
    """Verify image magic bytes and return canonical extension (.png, .jpg, .webp)."""
    if not data:
        return None
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    if data.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return '.webp'
    return None


def decode_base64_image(raw_b64: str) -> bytes:
    """Decode raw base64 or data:image/*;base64 string into validated image bytes."""
    s = (raw_b64 or '').strip()
    if not s:
        return b''
    if s.startswith('data:'):
        m = re.match(r'^data:image/(?:png|jpeg|jpg|webp);base64,(.+)$', s, flags=re.IGNORECASE | re.DOTALL)
        if not m:
            raise ValueError('Dữ liệu ảnh base64 phải là PNG, JPG hoặc WEBP')
        s = m.group(1).strip()
    if len(s) > 3_100_000:
        raise ValueError('Ảnh chụp vượt quá giới hạn 2 MB')
    try:
        data = base64.b64decode(s, validate=True)
    except Exception as exc:
        raise ValueError('Dữ liệu ảnh base64 không hợp lệ') from exc
    if len(data) > MAX_SHOT_BYTES:
        raise ValueError('Ảnh chụp vượt quá giới hạn 2 MB')
    if not detect_image_ext(data):
        raise ValueError('Định dạng ảnh không hợp lệ (chỉ nhận PNG, JPG, WEBP)')
    return data


def parse_multipart(content_type: str, body: bytes) -> tuple[dict[str, str], dict[str, tuple[str, bytes]]]:
    """Parse HTTP multipart/form-data using Python stdlib email.parser (Python 3.12+ safe)."""
    ctype = (content_type or '').strip()
    if 'multipart/form-data' not in ctype.lower():
        raise ValueError('Content-Type phải là multipart/form-data')
    raw_msg = (
        f'Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n'.encode('latin-1', errors='replace') + body
    )
    msg = email.parser.BytesParser(policy=email.policy.default).parsebytes(raw_msg)
    if not msg.is_multipart():
        raise ValueError('Dữ liệu multipart không hợp lệ')

    fields: dict[str, str] = {}
    files: dict[str, tuple[str, bytes]] = {}
    for part in msg.iter_parts():
        name = part.get_param('name', header='content-disposition')
        if not name:
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True)
        if payload is None:
            raw_p = part.get_payload()
            payload = raw_p.encode('utf-8', errors='replace') if isinstance(raw_p, str) else b''
        if filename is not None:
            safe_name = os.path.basename(filename)
            files[name] = (safe_name, payload)
        else:
            fields[name] = payload.decode('utf-8', errors='replace')
    return fields, files


def _validate_http_url(url: str) -> str:
    clean = (url or '').strip()
    if not clean:
        return ''
    if not (clean.startswith('https://') or clean.startswith('http://')):
        raise ValueError('Link phải bắt đầu bằng https:// hoặc http://')
    if len(clean) > 2048:
        raise ValueError('Link quá dài (tối đa 2048 ký tự)')
    return clean


def init_ggmap_tables(root: Path) -> None:
    """Create SQLite schema and screenshot directory under <root>/state/."""
    state_dir = Path(root) / 'state'
    shots_dir = state_dir / 'ggmap_shots'
    state_dir.mkdir(parents=True, exist_ok=True)
    shots_dir.mkdir(parents=True, exist_ok=True)
    db_path = state_dir / 'ggmap_scout.sqlite3'
    conn = sqlite3.connect(db_path, timeout=30.0, isolation_level=None)
    try:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=5000')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ggmap_items (
                code TEXT PRIMARY KEY,
                pdf_name TEXT NOT NULL,
                pdf_prefix TEXT NOT NULL DEFAULT '',
                old_count INTEGER NOT NULL DEFAULT 0,
                total_count INTEGER NOT NULL DEFAULT 0,
                bo_sung INTEGER NOT NULL DEFAULT 0,
                giam INTEGER NOT NULL DEFAULT 0,
                dot1_count INTEGER NOT NULL DEFAULT 0,
                stats_text TEXT NOT NULL DEFAULT '',
                ggmap_search_url TEXT NOT NULL DEFAULT '',
                gcm_codes TEXT NOT NULL DEFAULT '',
                sheet_name TEXT NOT NULL DEFAULT '',
                sheet_tam INTEGER NOT NULL DEFAULT 0,
                sheet_status TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'QUEUED',
                owner_node TEXT,
                lease TEXT,
                lease_until REAL,
                maps_found_name TEXT NOT NULL DEFAULT '',
                maps_prefix TEXT NOT NULL DEFAULT '',
                maps_url TEXT NOT NULL DEFAULT '',
                screenshot_file TEXT NOT NULL DEFAULT '',
                screenshot_url TEXT NOT NULL DEFAULT '',
                match_status TEXT NOT NULL DEFAULT '',
                worker_note TEXT NOT NULL DEFAULT '',
                checked_by TEXT NOT NULL DEFAULT '',
                checked_at REAL,
                updated_at REAL NOT NULL
            )
            """
        )
        conn.execute('CREATE INDEX IF NOT EXISTS idx_ggmap_status_prio ON ggmap_items(status, dot1_count DESC, code ASC)')
    finally:
        conn.close()


class GgmapScout:
    """Manages isolated Long Biên Google Maps street checks and screenshot uploads."""

    def __init__(self, root: Path, capacity_fn=None, lock: threading.RLock | None = None):
        self.root = Path(root)
        self.state_dir = self.root / 'state'
        self.db_path = self.state_dir / 'ggmap_scout.sqlite3'
        self.shots_dir = self.state_dir / 'ggmap_shots'
        self.capacity_fn = capacity_fn
        self.lock = lock or threading.RLock()
        init_ggmap_tables(self.root)

    @contextmanager
    def _db(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA busy_timeout=5000')
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _expire_stale(conn: sqlite3.Connection, now: float) -> None:
        conn.execute(
            """
            UPDATE ggmap_items
            SET status='QUEUED', owner_node=NULL, lease=NULL, lease_until=NULL, updated_at=?
            WHERE status='RUNNING' AND lease_until IS NOT NULL AND lease_until < ?
            """,
            (now, now),
        )

    @staticmethod
    def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
        if row is None:
            return None
        d = dict(row)
        shot_file = d.get('screenshot_file') or ''
        d['screenshot_endpoint'] = f'/ggmap/shots/{shot_file}' if shot_file else (d.get('screenshot_url') or '')
        return d

    def seed_items(self, items: list[dict], reset: bool = False) -> dict:
        if not isinstance(items, list) or not items:
            raise ValueError('Danh sách items không được rỗng')
        cleaned = []
        now = time.time()
        for raw in items:
            if not isinstance(raw, dict):
                raise ValueError('Mỗi item phải là JSON object')
            code = str(raw.get('code') or '').strip()
            pdf_name = str(raw.get('pdf_name') or '').strip()
            if not CODE_RE.match(code):
                raise ValueError(f'Mã tuyến không hợp lệ: {code!r}')
            if not pdf_name:
                raise ValueError(f'Thiếu pdf_name cho mã {code}')
            cleaned.append(
                (
                    code,
                    pdf_name,
                    str(raw.get('pdf_prefix') or '').strip(),
                    int(raw.get('old_count') or 0),
                    int(raw.get('total_count') or 0),
                    int(raw.get('bo_sung') or 0),
                    int(raw.get('giam') or 0),
                    int(raw.get('dot1_count') or 0),
                    str(raw.get('stats_text') or '').strip(),
                    str(raw.get('ggmap_search_url') or '').strip(),
                    str(raw.get('gcm_codes') or '').strip(),
                    str(raw.get('sheet_name') or '').strip(),
                    int(raw.get('sheet_tam') or 0),
                    str(raw.get('sheet_status') or '').strip(),
                    now,
                )
            )

        with self.lock, self._db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            if reset:
                conn.execute('DELETE FROM ggmap_items')
            for rec in cleaned:
                conn.execute(
                    """
                    INSERT INTO ggmap_items (
                        code, pdf_name, pdf_prefix, old_count, total_count, bo_sung, giam,
                        dot1_count, stats_text, ggmap_search_url, gcm_codes, sheet_name,
                        sheet_tam, sheet_status, status, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'QUEUED', ?)
                    ON CONFLICT(code) DO UPDATE SET
                        pdf_name=excluded.pdf_name,
                        pdf_prefix=excluded.pdf_prefix,
                        old_count=excluded.old_count,
                        total_count=excluded.total_count,
                        bo_sung=excluded.bo_sung,
                        giam=excluded.giam,
                        dot1_count=excluded.dot1_count,
                        stats_text=excluded.stats_text,
                        ggmap_search_url=excluded.ggmap_search_url,
                        gcm_codes=excluded.gcm_codes,
                        sheet_name=excluded.sheet_name,
                        sheet_tam=excluded.sheet_tam,
                        sheet_status=excluded.sheet_status,
                        updated_at=excluded.updated_at
                    """,
                    rec,
                )
            total = conn.execute('SELECT count(*) FROM ggmap_items').fetchone()[0]
            conn.execute('COMMIT')
        return {'seeded': len(cleaned), 'reset': bool(reset), 'total': total}

    def current_for_worker(self, node_id: str) -> dict | None:
        now = time.time()
        with self.lock, self._db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            self._expire_stale(conn, now)
            row = conn.execute(
                "SELECT * FROM ggmap_items WHERE status='RUNNING' AND owner_node=? LIMIT 1",
                (node_id,),
            ).fetchone()
            conn.execute('COMMIT')
        return self._row_to_dict(row)

    def claim(self, node_id: str, lease_seconds: int = 900) -> dict | None:
        ttl = max(60, min(3600, int(lease_seconds)))
        now = time.time()
        with self.lock, self._db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            self._expire_stale(conn, now)
            existing = conn.execute(
                "SELECT * FROM ggmap_items WHERE status='RUNNING' AND owner_node=? LIMIT 1",
                (node_id,),
            ).fetchone()
            if existing:
                new_until = now + ttl
                conn.execute(
                    'UPDATE ggmap_items SET lease_until=?, updated_at=? WHERE code=?',
                    (new_until, now, existing['code']),
                )
                row = conn.execute('SELECT * FROM ggmap_items WHERE code=?', (existing['code'],)).fetchone()
                conn.execute('COMMIT')
                return self._row_to_dict(row)

            candidate = conn.execute(
                """
                SELECT code FROM ggmap_items
                WHERE status='QUEUED'
                ORDER BY CASE WHEN dot1_count > 0 THEN 0 ELSE 1 END, dot1_count DESC, code ASC
                LIMIT 1
                """
            ).fetchone()
            if not candidate:
                conn.execute('COMMIT')
                return None

            lease = secrets.token_hex(12)
            conn.execute(
                """
                UPDATE ggmap_items
                SET status='RUNNING', owner_node=?, lease=?, lease_until=?, updated_at=?
                WHERE code=? AND status='QUEUED'
                """,
                (node_id, lease, now + ttl, now, candidate['code']),
            )
            row = conn.execute('SELECT * FROM ggmap_items WHERE code=?', (candidate['code'],)).fetchone()
            conn.execute('COMMIT')
        return self._row_to_dict(row)

    def release(self, code: str, node_id: str, lease: str | None = None) -> dict:
        clean_code = (code or '').strip()
        if not CODE_RE.match(clean_code):
            raise ValueError('Mã tuyến không hợp lệ')
        now = time.time()
        with self.lock, self._db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            row = conn.execute('SELECT * FROM ggmap_items WHERE code=?', (clean_code,)).fetchone()
            if not row:
                conn.execute('ROLLBACK')
                raise ValueError('Không tìm thấy mã tuyến')
            if row['status'] != 'RUNNING' or row['owner_node'] != node_id:
                conn.execute('ROLLBACK')
                raise PermissionError('Bạn không phải người đang giữ nhiệm vụ này')
            if lease is not None and row['lease'] != lease:
                conn.execute('ROLLBACK')
                raise PermissionError('Lease không khớp')
            conn.execute(
                """
                UPDATE ggmap_items
                SET status='QUEUED', owner_node=NULL, lease=NULL, lease_until=NULL, updated_at=?
                WHERE code=?
                """,
                (now, clean_code),
            )
            updated = conn.execute('SELECT * FROM ggmap_items WHERE code=?', (clean_code,)).fetchone()
            conn.execute('COMMIT')
        return self._row_to_dict(updated)

    def requeue_item(self, code: str, clear_result: bool = False) -> dict:
        clean_code = (code or '').strip()
        if not CODE_RE.match(clean_code):
            raise ValueError('Mã tuyến không hợp lệ')
        now = time.time()
        with self.lock, self._db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            row = conn.execute('SELECT * FROM ggmap_items WHERE code=?', (clean_code,)).fetchone()
            if not row:
                conn.execute('ROLLBACK')
                raise ValueError('Không tìm thấy mã tuyến')
            if clear_result:
                conn.execute(
                    """
                    UPDATE ggmap_items
                    SET status='QUEUED', owner_node=NULL, lease=NULL, lease_until=NULL,
                        maps_found_name='', maps_prefix='', maps_url='',
                        screenshot_file='', screenshot_url='', match_status='',
                        worker_note='', checked_by='', checked_at=NULL, updated_at=?
                    WHERE code=?
                    """,
                    (now, clean_code),
                )
            else:
                conn.execute(
                    """
                    UPDATE ggmap_items
                    SET status='QUEUED', owner_node=NULL, lease=NULL, lease_until=NULL, updated_at=?
                    WHERE code=?
                    """,
                    (now, clean_code),
                )
            updated = conn.execute('SELECT * FROM ggmap_items WHERE code=?', (clean_code,)).fetchone()
            conn.execute('COMMIT')
        return self._row_to_dict(updated)

    def _save_screenshot(self, code: str, raw_bytes: bytes) -> str:
        if len(raw_bytes) > MAX_SHOT_BYTES:
            raise ValueError('Ảnh chụp vượt quá giới hạn 2 MB')
        ext = detect_image_ext(raw_bytes)
        if not ext:
            raise ValueError('Định dạng ảnh không hợp lệ (chỉ nhận PNG, JPG, WEBP)')
        if self.capacity_fn:
            used = self.capacity_fn(self.root)
            if isinstance(used, int) and used + len(raw_bytes) > 900_000_000:
                raise OSError('Bộ nhớ lưu trữ trên VPS đã đầy giới hạn')

        self.shots_dir.mkdir(parents=True, exist_ok=True)
        filename = f'{code}{ext}'
        target = (self.shots_dir / filename).resolve()
        if target.parent != self.shots_dir.resolve() or not SHOT_FILE_RE.match(filename):
            raise ValueError('Tên file ảnh không an toàn')

        tmp_path = self.shots_dir / f'.{filename}.{secrets.token_hex(4)}.tmp'
        with open(tmp_path, 'wb') as f:
            f.write(raw_bytes)
        os.replace(tmp_path, target)

        for other_ext in SHOT_EXT_CONTENT_TYPES:
            if other_ext != ext:
                old = self.shots_dir / f'{code}{other_ext}'
                if old.exists():
                    try:
                        old.unlink()
                    except OSError:
                        pass
        return filename

    def submit(
        self,
        code: str,
        node_id: str,
        lease: str,
        maps_found_name: str,
        maps_prefix: str,
        maps_url: str = '',
        worker_note: str = '',
        screenshot_bytes: bytes = b'',
        screenshot_b64: str = '',
        screenshot_url: str = '',
    ) -> dict:
        clean_code = (code or '').strip()
        if not CODE_RE.match(clean_code):
            raise ValueError('Mã tuyến không hợp lệ')
        found_name = (maps_found_name or '').strip()
        prefix = normalize_prefix(maps_prefix) if (maps_prefix or '').strip() else ''
        if not prefix:
            raise ValueError('Vui lòng chọn loại đường/phố trên Google Maps')
        if prefix != 'KHÔNG TÌM THẤY' and not found_name:
            raise ValueError('Vui lòng điền tên đường/phố tìm thấy trên Google Maps')
        clean_maps_url = _validate_http_url(maps_url)
        clean_shot_url = _validate_http_url(screenshot_url)
        note = (worker_note or '').strip()[:1000]

        img_data = screenshot_bytes or (decode_base64_image(screenshot_b64) if (screenshot_b64 or '').strip() else b'')

        now = time.time()
        with self.lock, self._db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            self._expire_stale(conn, now)
            row = conn.execute('SELECT * FROM ggmap_items WHERE code=?', (clean_code,)).fetchone()
            if not row:
                conn.execute('ROLLBACK')
                raise ValueError('Không tìm thấy mã tuyến')
            if row['status'] != 'RUNNING' or row['owner_node'] != node_id or row['lease'] != (lease or '').strip():
                conn.execute('ROLLBACK')
                raise PermissionError('Nhiệm vụ không còn thuộc quyền giữ của bạn hoặc lease đã hết hạn')

            saved_file = row['screenshot_file'] or ''
            if img_data:
                try:
                    saved_file = self._save_screenshot(clean_code, img_data)
                except Exception:
                    conn.execute('ROLLBACK')
                    raise

            match_status = classify_maps_match(row['pdf_name'], row['pdf_prefix'], found_name, prefix)
            conn.execute(
                """
                UPDATE ggmap_items
                SET status='DONE', owner_node=NULL, lease=NULL, lease_until=NULL,
                    maps_found_name=?, maps_prefix=?, maps_url=?,
                    screenshot_file=?, screenshot_url=?, match_status=?,
                    worker_note=?, checked_by=?, checked_at=?, updated_at=?
                WHERE code=?
                """,
                (
                    found_name or ('KHÔNG TÌM THẤY' if prefix == 'KHÔNG TÌM THẤY' else ''),
                    prefix,
                    clean_maps_url,
                    saved_file,
                    clean_shot_url,
                    match_status,
                    note,
                    node_id,
                    now,
                    now,
                    clean_code,
                ),
            )
            updated = conn.execute('SELECT * FROM ggmap_items WHERE code=?', (clean_code,)).fetchone()
            conn.execute('COMMIT')
        return self._row_to_dict(updated)

    def list_items(self, filter_mode: str = 'all') -> list[dict]:
        now = time.time()
        with self.lock, self._db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            self._expire_stale(conn, now)
            conn.execute('COMMIT')
            where = ''
            if filter_mode == 'queued':
                where = "WHERE status='QUEUED'"
            elif filter_mode == 'running':
                where = "WHERE status='RUNNING'"
            elif filter_mode == 'done':
                where = "WHERE status='DONE'"
            elif filter_mode == 'diff':
                where = "WHERE status='DONE' AND match_status != 'KHỚP'"
            elif filter_mode == 'dot1':
                where = 'WHERE dot1_count > 0'
            rows = conn.execute(f'SELECT * FROM ggmap_items {where} ORDER BY code ASC').fetchall()
        return [self._row_to_dict(r) for r in rows]

    def recent_done(self, limit: int = 10) -> list[dict]:
        with self.lock, self._db() as conn:
            rows = conn.execute(
                "SELECT * FROM ggmap_items WHERE status='DONE' ORDER BY checked_at DESC LIMIT ?",
                (max(1, min(50, int(limit))),),
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def status_snapshot(self) -> dict:
        now = time.time()
        with self.lock, self._db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            self._expire_stale(conn, now)
            conn.execute('COMMIT')
            row = conn.execute(
                """
                SELECT
                    count(*) AS total,
                    COALESCE(sum(CASE WHEN status='QUEUED' THEN 1 ELSE 0 END), 0) AS queued,
                    COALESCE(sum(CASE WHEN status='RUNNING' THEN 1 ELSE 0 END), 0) AS running,
                    COALESCE(sum(CASE WHEN status='DONE' THEN 1 ELSE 0 END), 0) AS done,
                    COALESCE(sum(CASE WHEN dot1_count > 0 THEN 1 ELSE 0 END), 0) AS dot1_total,
                    COALESCE(sum(CASE WHEN dot1_count > 0 AND status='DONE' THEN 1 ELSE 0 END), 0) AS dot1_done,
                    COALESCE(sum(CASE WHEN status='DONE' AND match_status='KHỚP' THEN 1 ELSE 0 END), 0) AS khop,
                    COALESCE(sum(CASE WHEN status='DONE' AND match_status='KHÁC TIỀN TỐ (ĐƯỜNG/PHỐ)' THEN 1 ELSE 0 END), 0) AS khac_tien_to,
                    COALESCE(sum(CASE WHEN status='DONE' AND match_status='KHÁC TÊN' THEN 1 ELSE 0 END), 0) AS khac_ten,
                    COALESCE(sum(CASE WHEN status='DONE' AND match_status='KHÔNG TÌM THẤY' THEN 1 ELSE 0 END), 0) AS khong_tim_thay
                FROM ggmap_items
                """
            ).fetchone()
        return dict(row) if row else {}

    def get_shot_path(self, filename: str) -> tuple[Path, str] | None:
        clean = os.path.basename((filename or '').strip())
        if clean != filename or not SHOT_FILE_RE.match(clean):
            return None
        resolved = (self.shots_dir / clean).resolve()
        base = self.shots_dir.resolve()
        if resolved.parent != base or not resolved.is_file():
            return None
        ext = resolved.suffix.lower()
        ctype = SHOT_EXT_CONTENT_TYPES.get(ext)
        if not ctype:
            return None
        return resolved, ctype

    def export_csv(self, base_url: str = '') -> str:
        items = self.list_items('all')
        buf = io.StringIO()
        buf.write('\ufeff')
        writer = csv.writer(buf)
        writer.writerow(
            [
                'Mã PDF',
                'Tên trong PDF',
                'Tiền tố PDF',
                'Tổng biển PDF',
                'Đợt 1 (PDF)',
                'Mã Sheet cũ',
                'Tên Sheet cũ',
                'Trạng thái rà',
                'Đối chiếu PDF vs Maps',
                'Tên Google Maps (Muse điền)',
                'Loại trên Maps',
                'Link Google Maps thực tế',
                'Link Ảnh Chụp',
                'Ghi chú Muse',
                'Node thực hiện',
                'Thời gian kiểm tra (UTC)',
            ]
        )
        prefix_url = (base_url or '').rstrip('/')
        for it in items:
            shot = ''
            if it.get('screenshot_file'):
                shot = f"{prefix_url}/ggmap/shots/{it['screenshot_file']}"
            elif it.get('screenshot_url'):
                shot = it['screenshot_url']
            checked_iso = ''
            if it.get('checked_at'):
                checked_iso = datetime.fromtimestamp(float(it['checked_at']), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(
                [
                    it['code'],
                    it['pdf_name'],
                    it['pdf_prefix'],
                    it['total_count'],
                    it['dot1_count'],
                    it['gcm_codes'],
                    it['sheet_name'],
                    it['status'],
                    it['match_status'],
                    it['maps_found_name'],
                    it['maps_prefix'],
                    it['maps_url'],
                    shot,
                    it['worker_note'],
                    it['checked_by'],
                    checked_iso,
                ]
            )
        return buf.getvalue()


def _status_badge(match_status: str, status: str) -> str:
    if status == 'QUEUED':
        return '<span class="badge">Chờ rà</span>'
    if status == 'RUNNING':
        return '<span class="badge warn">Đang rà</span>'
    if match_status == 'KHỚP':
        return '<span class="badge ok">KHỚP</span>'
    if match_status.startswith('KHÁC TIỀN TỐ'):
        return '<span class="badge warn">KHÁC ĐƯỜNG/PHỐ</span>'
    if match_status in ('KHÁC TÊN', 'KHÔNG TÌM THẤY'):
        return f'<span class="badge err">{_esc(match_status)}</span>'
    return f'<span class="badge">{_esc(match_status or status)}</span>'


def render_ggmap_join_page(base_css: str, prefill_code: str = '', err: str = '', snap: dict | None = None) -> str:
    snap = snap or {}
    err_html = f'<div class="flash err">{_esc(err)}</div>' if err else ''
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rà Tên Đường Google Maps · Gia Nhập Đội Quân</title><style>{base_css}</style></head><body>
<div class="wrap" style="max-width:580px;margin-top:36px">
  <div class="card">
    <div class="row" style="justify-content:space-between;align-items:center">
      <h1 style="margin:0">Rà Tên Đường Google Maps</h1>
      <span class="badge ok">Long Biên · {int(snap.get('done', 0))}/{int(snap.get('total', 0))} tuyến</span>
    </div>
    <p style="color:var(--muted);margin-top:8px">Nhánh việc riêng tách khỏi hàng đợi Video Studio. Dùng để rà chính xác <b>ĐƯỜNG / PHỐ</b> trên Google Maps và lưu ảnh chụp màn hình.</p>
    {err_html}
    <form method="post" action="/ggmap/join">
      <label for="code">Mã mời đội quân (Invite Code)</label>
      <input id="code" name="code" required value="{_esc(prefill_code)}" placeholder="MUSE-..." autofocus>
      <input type="hidden" name="role" value="research">
      <div style="margin-top:14px" class="row">
        <button type="submit">Vào Làm Việc Rà Google Maps</button>
        <a class="btn sec" href="/">Sảnh Video Studio</a>
        <a class="btn sec" href="/ggmap/admin">Bảng Tiến Độ Admin</a>
      </div>
    </form>
  </div>
</div></body></html>"""


def render_ggmap_worker_page(
    base_css: str,
    worker: dict,
    csrf: str,
    snap: dict,
    current_item: dict | None,
    recent_items: list[dict],
    flash: str = '',
    err: str = '',
) -> str:
    flash_html = f'<div class="flash">{_esc(flash)}</div>' if flash else ''
    err_html = f'<div class="flash err">{_esc(err)}</div>' if err else ''
    done_pct = round(100 * snap.get('done', 0) / snap['total']) if snap.get('total') else 0

    if current_item:
        rem_min = max(1, round((float(current_item.get('lease_until') or time.time()) - time.time()) / 60))
        dot1_badge = (
            f'<span class="badge warn">ƯU TIÊN ĐỢT 1: {int(current_item["dot1_count"])} biển</span>'
            if int(current_item.get('dot1_count') or 0) > 0
            else '<span class="badge">Đợt sau (Đợt 1: 0)</span>'
        )
        default_prefix = current_item.get('pdf_prefix') or 'ĐƯỜNG'
        prefix_opts = []
        for p in CANONICAL_PREFIXES:
            sel = ' selected' if p == default_prefix else ''
            prefix_opts.append(f'<option value="{_esc(p)}"{sel}>{_esc(p)}</option>')

        main_card = f"""
        <div class="card" style="border-color:var(--warn)">
          <div class="row" style="justify-content:space-between;align-items:center">
            <div>
              <span class="badge ok" style="font-size:14px">{_esc(current_item['code'])}</span>
              {dot1_badge}
              <span class="badge">Giữ tuyến ~{rem_min} phút</span>
            </div>
            <form method="post" action="/ggmap/release" style="margin:0">
              <input type="hidden" name="csrf" value="{_esc(csrf)}">
              <input type="hidden" name="code" value="{_esc(current_item['code'])}">
              <input type="hidden" name="lease" value="{_esc(current_item.get('lease') or '')}">
              <button type="submit" class="btn sec">Trả lại hàng đợi</button>
            </form>
          </div>
          <h2 style="margin:14px 0 6px;font-size:24px;color:#fff">{_esc(current_item['pdf_name'])}</h2>
          <p style="color:var(--muted);margin:0 0 12px">
            Số liệu PDF: <b>{_esc(current_item.get('stats_text') or '')}</b>
            {f' · Mã Sheet cũ: <code>{_esc(current_item["gcm_codes"])}</code>' if current_item.get('gcm_codes') else ''}
          </p>
          <div class="row" style="margin-bottom:14px">
            <a class="btn" style="background:#16a34a" target="_blank" rel="noopener noreferrer" href="{_esc(current_item['ggmap_search_url'])}">
              1. Mở Google Maps Tìm Tuyến Này ↗
            </a>
          </div>

          <form method="post" action="/ggmap/submit" enctype="multipart/form-data" id="ggmapForm">
            <input type="hidden" name="csrf" value="{_esc(csrf)}">
            <input type="hidden" name="code" value="{_esc(current_item['code'])}">
            <input type="hidden" name="lease" value="{_esc(current_item.get('lease') or '')}">
            <input type="hidden" name="screenshot_base64" id="screenshot_base64" value="">

            <div class="grid">
              <div>
                <label for="maps_found_name">2. Tên ĐÚNG hiện trên Google Maps</label>
                <input id="maps_found_name" name="maps_found_name" required
                  value="{_esc(current_item.get('maps_found_name') or '')}"
                  placeholder="Copy/gõ nguyên tên trên Google Maps (VD: Đường Nguyễn Văn Cừ hoặc Phố Bồ Đề)">
              </div>
              <div>
                <label for="maps_prefix">3. Phân loại trên Maps (ĐƯỜNG hay PHỐ?)</label>
                <select id="maps_prefix" name="maps_prefix">
                  {''.join(prefix_opts)}
                </select>
              </div>
            </div>

            <label for="maps_url">4. Dán Link Google Maps thực tế vừa mở (Copy thanh địa chỉ)</label>
            <input id="maps_url" name="maps_url" value="{_esc(current_item.get('maps_url') or '')}"
              placeholder="https://www.google.com/maps/place/...">

            <label for="screenshot_file">5. Ảnh Chụp Màn Hình Google Maps (Chọn file PNG/JPG/WEBP hoặc bấm Ctrl+V dán thẳng ảnh vào trang này)</label>
            <div id="pasteZone" style="border:2px dashed var(--border);border-radius:10px;padding:12px;background:#0a1020">
              <input id="screenshot_file" name="screenshot" type="file" accept="image/png,image/jpeg,image/webp">
              <div id="pasteHint" style="color:var(--muted);font-size:12px;margin-top:6px">
                Mẹo nhanh: Chụp màn hình (Win+Shift+S) rồi bấm <b>Ctrl+V</b> ngay tại đây, hệ thống tự thu ảnh dưới 2MB.
              </div>
              <img id="shotPreview" style="display:none;max-width:100%;max-height:240px;margin-top:10px;border-radius:8px;border:1px solid var(--border)" alt="Xem trước ảnh chụp">
            </div>

            <label for="worker_note">6. Ghi chú thêm (nếu Maps lệch tên, đường chia đoạn, hoặc cần sửa Sheet)</label>
            <input id="worker_note" name="worker_note" value="{_esc(current_item.get('worker_note') or '')}"
              placeholder="Không bắt buộc">

            <div style="margin-top:16px" class="row">
              <button type="submit">Lưu Kết Quả &amp; Chụp Hình</button>
            </div>
          </form>
        </div>
        <script>
        (function() {{
          var b64Input = document.getElementById('screenshot_base64');
          var fileInput = document.getElementById('screenshot_file');
          var preview = document.getElementById('shotPreview');
          var hint = document.getElementById('pasteHint');
          function showPreview(src, label) {{
            preview.src = src;
            preview.style.display = 'block';
            hint.textContent = label;
          }}
          if (fileInput) {{
            fileInput.addEventListener('change', function() {{
              if (fileInput.files && fileInput.files[0]) {{
                b64Input.value = '';
                var r = new FileReader();
                r.onload = function(ev) {{ showPreview(ev.target.result, 'Đã chọn file: ' + fileInput.files[0].name); }};
                r.readAsDataURL(fileInput.files[0]);
              }}
            }});
          }}
          document.addEventListener('paste', function(e) {{
            var items = (e.clipboardData && e.clipboardData.items) || [];
            for (var i = 0; i < items.length; i++) {{
              if (items[i].type && items[i].type.indexOf('image/') === 0) {{
                var blob = items[i].getAsFile();
                if (!blob) continue;
                var reader = new FileReader();
                reader.onload = function(ev) {{
                  var dataUrl = ev.target.result;
                  if (dataUrl.length <= 2400000) {{
                    b64Input.value = dataUrl;
                    showPreview(dataUrl, 'Đã dán ảnh từ Clipboard (' + Math.round(dataUrl.length * 0.75 / 1024) + ' KB)');
                    return;
                  }}
                  var img = new Image();
                  img.onload = function() {{
                    var scale = Math.min(1, 1440 / Math.max(img.width, img.height));
                    var c = document.createElement('canvas');
                    c.width = Math.round(img.width * scale);
                    c.height = Math.round(img.height * scale);
                    c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
                    var jpegUrl = c.toDataURL('image/jpeg', 0.85);
                    b64Input.value = jpegUrl;
                    showPreview(jpegUrl, 'Đã nén & dán ảnh từ Clipboard (' + Math.round(jpegUrl.length * 0.75 / 1024) + ' KB)');
                  }};
                  img.src = dataUrl;
                }};
                reader.readAsDataURL(blob);
                break;
              }}
            }}
          }});
        }})();
        </script>
        """
    else:
        has_queued = int(snap.get('queued') or 0) > 0
        claim_btn = (
            f"""<form method="post" action="/ggmap/claim">
              <input type="hidden" name="csrf" value="{_esc(csrf)}">
              <button type="submit">Nhận 1 Tuyến Đường Tiếp Theo (Ưu tiên Đợt 1)</button>
            </form>"""
            if has_queued
            else '<span class="badge ok">Tất cả tuyến chờ trong hàng đợi đã được xử lý hoặc đang có Muse khác rà!</span>'
        )
        main_card = f"""
        <div class="card">
          <h2>Sẵn Sàng Nhận Tuyến Mới</h2>
          <p style="color:var(--muted)">Còn <b>{int(snap.get('queued', 0))}</b> tuyến đang chờ rà, <b>{int(snap.get('running', 0))}</b> tuyến đang có Muse khác mở.</p>
          {claim_btn}
        </div>"""

    recent_rows = []
    for it in recent_items:
        shot_html = (
            f'<a target="_blank" href="/ggmap/shots/{_esc(it["screenshot_file"])}">Xem ảnh</a>'
            if it.get('screenshot_file')
            else ('<a target="_blank" href="' + _esc(it['screenshot_url']) + '">Link</a>' if it.get('screenshot_url') else '—')
        )
        recent_rows.append(
            f"<tr><td><code>{_esc(it['code'])}</code></td><td>{_esc(it['pdf_name'])}</td>"
            f"<td>{_esc(it['maps_found_name'])}</td><td>{_status_badge(it.get('match_status', ''), it['status'])}</td>"
            f"<td>{shot_html}</td><td><code>{_esc((it.get('checked_by') or '')[:8])}</code></td></tr>"
        )

    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rà Tên Đường Google Maps · Muse {_esc(worker['id'][:8])}</title><style>{base_css}</style></head><body>
<div class="wrap">
  <div class="row" style="justify-content:space-between;align-items:center;margin-bottom:14px">
    <div>
      <h1 style="margin:0">Rà Tên Đường Google Maps · Long Biên</h1>
      <div style="color:var(--muted);font-size:13px">Node: <code>{_esc(worker['id'])}</code> · Vai trò: <b>{_esc(worker['role'])}</b> · Tiến độ: <b>{int(snap.get('done', 0))}/{int(snap.get('total', 0))} ({done_pct}%)</b></div>
    </div>
    <div class="row">
      <a class="btn sec" href="/portal">Sảnh Video Studio</a>
      <a class="btn sec" href="/ggmap/admin">Tiến độ Admin</a>
    </div>
  </div>
  <div class="grid" style="margin-bottom:14px">
    <div class="card"><div style="color:var(--muted);font-size:12px">Đã xong</div><div style="font-size:22px;font-weight:700">{int(snap.get('done', 0))}/{int(snap.get('total', 0))}</div></div>
    <div class="card"><div style="color:var(--muted);font-size:12px">Xong Đợt 1</div><div style="font-size:22px;font-weight:700">{int(snap.get('dot1_done', 0))}/{int(snap.get('dot1_total', 0))}</div></div>
    <div class="card"><div style="color:var(--muted);font-size:12px">Khác ĐƯỜNG/PHỐ</div><div style="font-size:22px;font-weight:700;color:var(--warn)">{int(snap.get('khac_tien_to', 0))}</div></div>
    <div class="card"><div style="color:var(--muted);font-size:12px">Khác tên / Không thấy</div><div style="font-size:22px;font-weight:700;color:var(--err)">{int(snap.get('khac_ten', 0)) + int(snap.get('khong_tim_thay', 0))}</div></div>
  </div>
  {flash_html}{err_html}{main_card}
  <div class="card">
    <h3>10 Tuyến Vừa Rà Gần Nhất</h3>
    <table>
      <thead><tr><th>Mã</th><th>Tên PDF</th><th>Tên Google Maps</th><th>Kết luận</th><th>Ảnh</th><th>Muse</th></tr></thead>
      <tbody>{''.join(recent_rows) or '<tr><td colspan="6">Chưa có tuyến nào hoàn thành</td></tr>'}</tbody>
    </table>
  </div>
</div></body></html>"""


def render_ggmap_admin_page(
    base_css: str,
    csrf: str,
    snap: dict,
    items: list[dict],
    filter_mode: str = 'all',
    flash: str = '',
) -> str:
    flash_html = f'<div class="flash">{_esc(flash)}</div>' if flash else ''
    rows = []
    for it in items:
        shot_cell = '—'
        if it.get('screenshot_file'):
            src = f"/ggmap/shots/{_esc(it['screenshot_file'])}"
            shot_cell = f'<a target="_blank" href="{src}"><img src="{src}" style="height:42px;border-radius:4px;border:1px solid var(--border)" alt="{_esc(it["code"])}"></a>'
        elif it.get('screenshot_url'):
            shot_cell = f'<a target="_blank" href="{_esc(it["screenshot_url"])}">Link ảnh</a>'

        maps_link = (
            f'<a target="_blank" rel="noopener noreferrer" href="{_esc(it["maps_url"])}">Maps thực tế ↗</a>'
            if it.get('maps_url')
            else f'<a target="_blank" rel="noopener noreferrer" href="{_esc(it["ggmap_search_url"])}">Tìm kiếm</a>'
        )
        rows.append(
            f"<tr>"
            f"<td><code>{_esc(it['code'])}</code><br><span style='color:var(--muted);font-size:11px'>Đ1: {int(it['dot1_count'])} / T: {int(it['total_count'])}</span></td>"
            f"<td><b>{_esc(it['pdf_name'])}</b><br><span style='color:var(--muted);font-size:11px'>Sheet: {_esc(it.get('sheet_name') or '—')}</span></td>"
            f"<td>{_esc(it.get('maps_found_name') or '—')}<br><span style='color:var(--muted);font-size:11px'>Loại: {_esc(it.get('maps_prefix') or '—')}</span></td>"
            f"<td>{_status_badge(it.get('match_status', ''), it['status'])}<br><span style='color:var(--muted);font-size:11px'>{_esc(it.get('worker_note') or '')}</span></td>"
            f"<td>{maps_link}</td>"
            f"<td>{shot_cell}</td>"
            f"<td>"
            f"<form method='post' action='/ggmap/admin/requeue' style='margin:0'>"
            f"<input type='hidden' name='csrf' value='{_esc(csrf)}'>"
            f"<input type='hidden' name='code' value='{_esc(it['code'])}'>"
            f"<button type='submit' class='btn sec' style='padding:4px 8px;font-size:12px'>Rà lại</button>"
            f"</form></td>"
            f"</tr>"
        )

    filters = [
        ('all', f"Tất cả ({int(snap.get('total', 0))})"),
        ('dot1', f"Đợt 1 ({int(snap.get('dot1_total', 0))})"),
        ('done', f"Đã xong ({int(snap.get('done', 0))})"),
        ('diff', f"Lệch tên / ĐƯỜNG-PHỐ ({int(snap.get('khac_tien_to', 0)) + int(snap.get('khac_ten', 0)) + int(snap.get('khong_tim_thay', 0))})"),
        ('queued', f"Chờ rà ({int(snap.get('queued', 0))})"),
        ('running', f"Đang rà ({int(snap.get('running', 0))})"),
    ]
    filter_links = [
        f"<a class='btn {'sec' if fmode != filter_mode else ''}' href='/ggmap/admin?filter={fmode}'>{_esc(label)}</a>"
        for fmode, label in filters
    ]

    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin Rà Google Maps · Long Biên (104 tuyến)</title><style>{base_css}</style></head><body>
<div class="wrap">
  <div class="row" style="justify-content:space-between;align-items:center;margin-bottom:14px">
    <div>
      <h1 style="margin:0">Quản Trị Rà Tên Đường Google Maps · Long Biên</h1>
      <div style="color:var(--muted);font-size:13px">Nguồn chuẩn: <code>LONG_BIEN_BAN_DAN_473_BIEN_CO_DOT_1_A4.pdf</code> (104 tuyến · 473 biển · 200 Đợt 1)</div>
    </div>
    <div class="row">
      <a class="btn" style="background:#16a34a" href="/ggmap/export.csv">Tải CSV Đối Chiếu (UTF-8)</a>
      <a class="btn sec" href="/ggmap">Giao Diện Thợ</a>
      <a class="btn sec" href="/admin">Admin Video Studio</a>
    </div>
  </div>
  {flash_html}
  <div class="grid" style="margin-bottom:14px">
    <div class="card"><div style="color:var(--muted);font-size:12px">Hoàn thành</div><div style="font-size:22px;font-weight:700">{int(snap.get('done', 0))}/{int(snap.get('total', 0))}</div></div>
    <div class="card"><div style="color:var(--muted);font-size:12px">Khớp hoàn toàn</div><div style="font-size:22px;font-weight:700;color:var(--ok)">{int(snap.get('khop', 0))}</div></div>
    <div class="card"><div style="color:var(--muted);font-size:12px">Khác ĐƯỜNG / PHỐ</div><div style="font-size:22px;font-weight:700;color:var(--warn)">{int(snap.get('khac_tien_to', 0))}</div></div>
    <div class="card"><div style="color:var(--muted);font-size:12px">Khác tên / Không thấy</div><div style="font-size:22px;font-weight:700;color:var(--err)">{int(snap.get('khac_ten', 0)) + int(snap.get('khong_tim_thay', 0))}</div></div>
  </div>
  <div class="row" style="margin-bottom:12px">{''.join(filter_links)}</div>
  <div class="card">
    <table>
      <thead><tr><th>Mã</th><th>Tên PDF / Sheet cũ</th><th>Tên Google Maps</th><th>Đối chiếu</th><th>Link</th><th>Ảnh chụp</th><th>Thao tác</th></tr></thead>
      <tbody>{''.join(rows) or '<tr><td colspan="7">Chưa có dữ liệu tuyến đường (hãy seed JSON 104 tuyến)</td></tr>'}</tbody>
    </table>
  </div>
</div></body></html>"""
