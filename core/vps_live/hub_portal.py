"""AgentNet Web Hub (muse.alltool.pro) — Public HTTPS Invite Portal & Admin Command Center.

Shares registry.sqlite3 and research.sqlite3 with corner.py while enforcing strict
token authentication, invite expiration/quotas, CSRF tokens, and CSP/XSS protection.
"""
from __future__ import annotations

import hashlib
import hmac
import html
import json
import mimetypes
import os
import re
import zipfile
from email.parser import BytesParser
from email.policy import default as EMAIL_POLICY
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from pathlib import Path
import secrets
import subprocess
import threading
import time
from urllib.parse import parse_qs, urlsplit

from research_queue import PROJECT, QueueError, WORKER_ROLES

HUB_DEVICE_TAG = 'hub-web'
MEDIA_DROP_ROOT = Path(os.environ.get('AGENTNET_MEDIA_ROOT', '/var/lib/agentnet-media'))
MEDIA_ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.webm', '.zip', '.json'}
MEDIA_MAX_BYTES = 120 * 1024 * 1024
SAFE_SLUG_RE = re.compile(r'^[a-zA-Z0-9_-]{2,80}$')


def _safe_media_name(raw_name: str) -> str:
    base = Path(raw_name or '').name
    clean = re.sub(r'[^a-zA-Z0-9._-]+', '_', base).strip('._')
    if not clean or len(clean) > 120:
        return ''
    ext = Path(clean).suffix.lower()
    return clean if ext in MEDIA_ALLOWED_EXT else ''


def _relay_to_e_via_croc(hub, slug_val: str, ram_items: list[tuple[str, bytes]], sdir: Path) -> None:
    """Stream uploaded media from VPS RAM (/dev/shm) straight to Windows E:\\ via croc P2P, leaving 0 MB .mp4 on VPS."""
    if not ram_items:
        return

    def _worker():
        croc_bin = '/usr/local/bin/croc' if Path('/usr/local/bin/croc').is_file() else '/tmp/croc_bin/croc'
        shm_root = Path('/dev/shm') if Path('/dev/shm').is_dir() else Path('/tmp')
        tok_hex = secrets.token_hex(6)
        zpath = shm_root / f'croc_{slug_val}_{tok_hex}.zip'
        code_val = f'agy-{slug_val[:28]}-{tok_hex}'
        delivered = False
        try:
            if Path(croc_bin).is_file():
                with zipfile.ZipFile(zpath, 'w', compression=zipfile.ZIP_STORED) as zf:
                    for fname, data in ram_items:
                        zf.writestr(fname, data)
                env = dict(os.environ, CROC_SECRET=code_val)
                proc = subprocess.Popen(
                    [croc_bin, '--quiet', 'send', str(zpath)],
                    env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                time.sleep(1.8)
                hub.create_croc_offer(slug_val, code_val)
                try:
                    rc = proc.wait(timeout=75)
                    delivered = (rc == 0)
                except subprocess.TimeoutExpired:
                    proc.kill()
        except Exception:
            delivered = False
        finally:
            zpath.unlink(missing_ok=True)
            if not delivered:
                # Fallback only if Windows PC croc receiver was temporarily unreachable
                sdir.mkdir(parents=True, exist_ok=True)
                for fname, data in ram_items:
                    if fname.lower().endswith(('.mp4', '.mov', '.webm')):
                        (sdir / fname).write_bytes(data)

    threading.Thread(target=_worker, daemon=True).start()


def _parse_multipart(content_type: str, body: bytes) -> tuple[dict[str, str], list[tuple[str, bytes]]]:
    fields: dict[str, str] = {}
    files: list[tuple[str, bytes]] = []
    hdr = f'Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n'.encode('utf-8')
    msg = BytesParser(policy=EMAIL_POLICY).parsebytes(hdr + body)
    if not msg.is_multipart():
        return fields, files
    for part in msg.iter_parts():
        cd = part.get('Content-Disposition', '')
        name = part.get_param('name', header='content-disposition') or ''
        fname = part.get_filename()
        payload = part.get_payload(decode=True) or b''
        if fname:
            files.append((fname, payload))
        elif name:
            fields[name] = payload.decode('utf-8', errors='replace').strip()
    return fields, files


def _sha256(val: str) -> str:
    return hashlib.sha256(val.encode('utf-8')).hexdigest()


def _csrf_for(secret_token: str) -> str:
    return hmac.new(secret_token.encode('utf-8'), b'agentnet-hub-csrf-v1', hashlib.sha256).hexdigest()[:28]


def _esc(val: object) -> str:
    return html.escape('' if val is None else str(val), quote=True)


def init_hub_tables(connect_fn, root):
    with connect_fn(root) as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS hub_invites(
                id TEXT PRIMARY KEY,
                code_hint TEXT NOT NULL,
                code_hash TEXT UNIQUE NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                max_uses INTEGER NOT NULL,
                used_count INTEGER NOT NULL DEFAULT 0,
                targets_json TEXT NOT NULL,
                default_role TEXT NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS croc_offers(
                id TEXT PRIMARY KEY,
                slug TEXT NOT NULL,
                croc_code TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chief_commands(
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                command_text TEXT NOT NULL,
                status TEXT NOT NULL,
                plan_json TEXT NOT NULL DEFAULT '{}',
                report_text TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS episode_scores(
                slug TEXT PRIMARY KEY,
                channel TEXT NOT NULL DEFAULT '',
                script_score INTEGER NOT NULL DEFAULT 0,
                director_score INTEGER NOT NULL DEFAULT 0,
                visual_score INTEGER NOT NULL DEFAULT 0,
                video_score INTEGER NOT NULL DEFAULT 0,
                total_score INTEGER NOT NULL DEFAULT 0,
                verdict TEXT NOT NULL DEFAULT 'PENDING',
                bad_scenes_json TEXT NOT NULL DEFAULT '[]',
                feedback TEXT NOT NULL DEFAULT '',
                reviewer_node TEXT NOT NULL DEFAULT '',
                updated_at REAL NOT NULL
            );
        ''')


from urllib.parse import urlencode

from ggmap_scout import (
    GgmapScout,
    parse_multipart,
    render_ggmap_admin_page,
    render_ggmap_join_page,
    render_ggmap_worker_page,
)


class HubManager:
    def __init__(self, registry, queue, connect_fn, capacity_fn, lock):
        self.registry = registry
        self.queue = queue
        self.connect = connect_fn
        self.capacity = capacity_fn
        self.lock = lock
        init_hub_tables(self.connect, self.registry.root)
        self.ggmap = GgmapScout(self.registry.root, capacity_fn=self.capacity, lock=self.lock)

    # --- Admin key management ---
    def set_admin_key(self, raw_key: str) -> None:
        if not isinstance(raw_key, str) or not (20 <= len(raw_key) <= 200):
            raise ValueError('Admin key must be 20..200 chars')
        with self.lock, self.connect(self.registry.root) as db:
            self.capacity(self.registry.root)
            db.execute(
                'INSERT OR REPLACE INTO config VALUES(?,?)',
                ('hub_admin_hash', json.dumps({'sha256': _sha256(raw_key), 'updated_at': time.time()})),
            )

    def verify_admin(self, supplied: str) -> bool:
        if not isinstance(supplied, str) or not (20 <= len(supplied) <= 200):
            return False
        with self.connect(self.registry.root) as db:
            row = db.execute("SELECT value FROM config WHERE key='hub_admin_hash'").fetchone()
        if not row:
            return False
        expected = json.loads(row['value']).get('sha256', '')
        return bool(expected) and hmac.compare_digest(_sha256(supplied), expected)

    def verify_invite_token(self, raw_code: str) -> bool:
        code = (raw_code or '').strip()
        if not (8 <= len(code) <= 80):
            return False
        now = time.time()
        with self.connect(self.registry.root) as db:
            row = db.execute(
                "SELECT expires_at, status FROM hub_invites WHERE code_hash=?",
                (_sha256(code),),
            ).fetchone()
        return bool(row and row['status'] == 'ACTIVE' and float(row['expires_at']) > now)

    def create_croc_offer(self, slug: str, croc_code: str) -> dict:
        if not SAFE_SLUG_RE.match(slug or ''):
            raise ValueError('invalid_slug')
        code = re.sub(r'[^a-zA-Z0-9_-]', '', croc_code or '')
        if not (12 <= len(code) <= 96):
            raise ValueError('invalid_croc_code')
        oid = secrets.token_hex(8)
        now = time.time()
        with self.lock, self.connect(self.registry.root) as db:
            db.execute("DELETE FROM croc_offers WHERE created_at < ?", (now - 1800,))
            db.execute(
                "INSERT INTO croc_offers VALUES(?,?,?,?,?,?)",
                (oid, slug, code, 'PENDING', now, now),
            )
        return {'id': oid, 'slug': slug, 'status': 'PENDING'}

    def claim_pending_croc_offers(self, limit: int = 5) -> list[dict]:
        now = time.time()
        with self.lock, self.connect(self.registry.root) as db:
            # Expire stale offers older than 90s
            db.execute("UPDATE croc_offers SET status='EXPIRED', updated_at=? WHERE status IN ('PENDING','RECEIVING') AND created_at < ?", (now, now - 90))
            rows = db.execute(
                "SELECT id, slug, croc_code, created_at FROM croc_offers WHERE status='PENDING' ORDER BY created_at ASC LIMIT ?",
                (max(1, min(10, int(limit))),),
            ).fetchall()
            out = [dict(r) for r in rows]
            for r in out:
                db.execute("UPDATE croc_offers SET status='RECEIVING', updated_at=? WHERE id=?", (now, r['id']))
        return out

    def ack_croc_offer(self, oid: str, status: str = 'DONE') -> dict:
        st = status if status in ('DONE', 'FAILED') else 'DONE'
        now = time.time()
        with self.lock, self.connect(self.registry.root) as db:
            db.execute("UPDATE croc_offers SET status=?, updated_at=? WHERE id=?", (st, now, oid))
        return {'ok': True, 'id': oid, 'status': st}

    # --- Chief Coordinator Command Inbox & QA Scoreboard ---
    def submit_chief_command(self, source: str, command_text: str) -> dict:
        txt = (command_text or '').strip()
        if not txt or len(txt) > 8000:
            raise ValueError('Lệnh điều phối phải từ 1..8000 ký tự')
        cid = 'cmd_' + secrets.token_hex(6)
        now = time.time()
        with self.lock, self.connect(self.registry.root) as db:
            db.execute(
                'INSERT INTO chief_commands VALUES(?,?,?,?,?,?,?,?)',
                (cid, (source or 'owner')[:40], txt, 'PENDING', '{}', '', now, now),
            )
        return {'ok': True, 'command_id': cid, 'status': 'PENDING'}

    def get_chief_inbox(self) -> dict:
        chief_actor = {'id': 'chief-coordinator', 'role': 'controller'}
        fleet = self.queue.get(chief_actor, '/fleet')
        with self.connect(self.registry.root) as db:
            pending = [dict(r) for r in db.execute(
                "SELECT * FROM chief_commands WHERE status='PENDING' ORDER BY created_at ASC LIMIT 20"
            ).fetchall()]
            recent_cmds = [dict(r) for r in db.execute(
                "SELECT * FROM chief_commands ORDER BY created_at DESC LIMIT 15"
            ).fetchall()]
            scores = [dict(r) for r in db.execute(
                "SELECT * FROM episode_scores ORDER BY updated_at DESC LIMIT 60"
            ).fetchall()]
            role_nodes = [dict(r) for r in db.execute(
                "SELECT role, count(*) AS count FROM nodes WHERE status='APPROVED' GROUP BY role"
            ).fetchall()]
        for s in scores:
            try:
                s['bad_scenes'] = json.loads(s.pop('bad_scenes_json', '[]'))
            except Exception:
                s['bad_scenes'] = []
        rework_needed = [s for s in scores if s['verdict'] == 'REWORK']
        return {
            'ok': True,
            'pending_commands': pending,
            'recent_commands': recent_cmds,
            'fleet': fleet,
            'role_nodes': role_nodes,
            'scores_summary': {
                'total_scored': len(scores),
                'passed': sum(1 for s in scores if s['verdict'] == 'PASS'),
                'rework': len(rework_needed),
            },
            'rework_episodes': rework_needed[:20],
            'recent_scores': scores[:25],
        }

    def chief_dispatch(self, payload: dict) -> dict:
        chief_actor = {'id': 'chief-coordinator', 'role': 'controller'}
        now = time.time()
        created_tasks = []
        raw_tasks = payload.get('tasks') or []
        if raw_tasks:
            res = self.queue.post(chief_actor, '/tasks/batch', {'project': PROJECT, 'tasks': raw_tasks})
            created_tasks = res.get('tasks', [])
        requeued = 0
        for tid in (payload.get('requeue_ids') or [])[:50]:
            with self.queue.db() as qdb:
                qdb.execute(
                    "UPDATE tasks SET status='QUEUED', owner_node=NULL, lease=NULL, lease_until=NULL, started_at=NULL WHERE id=?",
                    (str(tid),),
                )
                requeued += 1
        cmd_id = (payload.get('command_id') or '').strip()
        report_txt = (payload.get('report') or '').strip()[:8000]
        plan_obj = payload.get('plan') or {'dispatched_count': len(created_tasks), 'requeued': requeued}
        if cmd_id:
            new_st = (payload.get('status') or 'DISPATCHED').upper()
            if new_st not in ('PENDING', 'DISPATCHED', 'DONE'):
                new_st = 'DISPATCHED'
            with self.lock, self.connect(self.registry.root) as db:
                db.execute(
                    'UPDATE chief_commands SET status=?, plan_json=?, report_text=?, updated_at=? WHERE id=?',
                    (new_st, json.dumps(plan_obj, ensure_ascii=False), report_txt, now, cmd_id),
                )
        return {'ok': True, 'dispatched': len(created_tasks), 'requeued': requeued, 'tasks': created_tasks}

    def record_episode_score(self, reviewer_node: str, data: dict) -> dict:
        slug = (data.get('slug') or '').strip()
        if not SAFE_SLUG_RE.match(slug):
            raise ValueError('Invalid slug')
        s_sc = max(0, min(25, int(data.get('script_score') or 0)))
        d_sc = max(0, min(25, int(data.get('director_score') or 0)))
        v_sc = max(0, min(25, int(data.get('visual_score') or 0)))
        m_sc = max(0, min(25, int(data.get('video_score') or 0)))
        tot = int(data.get('total_score') or (s_sc + d_sc + v_sc + m_sc))
        tot = max(0, min(100, tot))
        verdict = 'PASS' if tot >= 85 and str(data.get('verdict', '')).upper() != 'REWORK' else 'REWORK'
        bad = data.get('bad_scenes') or []
        if not isinstance(bad, list):
            bad = []
        bad_clean = [int(x) for x in bad if str(x).isdigit()][:15]
        fb = (data.get('feedback') or data.get('summary') or '').strip()[:3000]
        ch = (data.get('channel') or '').strip()[:60]
        now = time.time()
        with self.lock, self.connect(self.registry.root) as db:
            db.execute(
                '''INSERT OR REPLACE INTO episode_scores
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                (slug, ch, s_sc, d_sc, v_sc, m_sc, tot, verdict, json.dumps(bad_clean), fb, (reviewer_node or '')[:24], now),
            )
        return {
            'ok': True, 'slug': slug, 'channel': ch,
            'script_score': s_sc, 'director_score': d_sc, 'visual_score': v_sc, 'video_score': m_sc,
            'total_score': tot, 'verdict': verdict, 'bad_scenes': bad_clean,
        }

    def list_episode_scores(self, limit: int = 100) -> list[dict]:
        with self.connect(self.registry.root) as db:
            rows = db.execute(
                'SELECT * FROM episode_scores ORDER BY updated_at DESC LIMIT ?',
                (max(1, min(300, int(limit))),),
            ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d['bad_scenes'] = json.loads(d.pop('bad_scenes_json', '[]'))
            except Exception:
                d['bad_scenes'] = []
            out.append(d)
        return out

    # --- Invite & auto-role balancing ---
    def create_invite(self, ttl_minutes=60, max_uses=20, targets=None, default_role='research') -> dict:
        ttl_minutes = max(1, min(10080, int(ttl_minutes)))
        max_uses = max(1, min(200, int(max_uses)))
        if default_role not in WORKER_ROLES:
            default_role = 'research'
        clean_targets = {}
        for r in WORKER_ROLES:
            clean_targets[r] = max(0, min(200, int((targets or {}).get(r, 0))))
        if sum(clean_targets.values()) == 0:
            clean_targets = {'research': 6, 'verify': 2, 'engineer': 2}

        raw_code = 'MUSE-' + secrets.token_urlsafe(12).replace('-', '').replace('_', '')[:14].upper()
        inv_id = secrets.token_hex(8)
        now = time.time()
        hint = raw_code[:7] + '...' + raw_code[-4:]
        with self.lock, self.connect(self.registry.root) as db:
            self.capacity(self.registry.root)
            db.execute(
                'INSERT INTO hub_invites VALUES(?,?,?,?,?,?,?,?,?,?)',
                (
                    inv_id, hint, _sha256(raw_code), now, now + ttl_minutes * 60,
                    max_uses, 0, json.dumps(clean_targets), default_role, 'ACTIVE',
                ),
            )
        return {
            'id': inv_id,
            'code': raw_code,
            'expires_in_minutes': ttl_minutes,
            'max_uses': max_uses,
            'targets': clean_targets,
        }

    def revoke_invite(self, inv_id: str) -> None:
        with self.lock, self.connect(self.registry.root) as db:
            db.execute("UPDATE hub_invites SET status='REVOKED' WHERE id=?", (inv_id,))

    def list_invites(self) -> list[dict]:
        now = time.time()
        with self.connect(self.registry.root) as db:
            rows = db.execute('SELECT * FROM hub_invites ORDER BY created_at DESC LIMIT 30').fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d['targets'] = json.loads(d.pop('targets_json'))
            d.pop('code_hash', None)
            d['remaining_seconds'] = max(0, round(d['expires_at'] - now))
            if d['status'] == 'ACTIVE' and (d['expires_at'] < now or d['used_count'] >= d['max_uses']):
                d['effective_status'] = 'EXPIRED_OR_FULL'
            else:
                d['effective_status'] = d['status']
            out.append(d)
        return out

    def _pick_balanced_role(self, db, targets: dict, default_role: str, requested_role: str | None) -> str:
        if requested_role in WORKER_ROLES:
            return requested_role
        counts = {r: 0 for r in WORKER_ROLES}
        for row in db.execute("SELECT role, count(*) AS c FROM nodes WHERE status='APPROVED' GROUP BY role").fetchall():
            if row['role'] in counts:
                counts[row['role']] = row['c']
        # 1. Pick role with biggest deficit below target
        deficits = [(targets.get(r, 0) - counts[r], targets.get(r, 0), r) for r in WORKER_ROLES]
        deficits.sort(reverse=True)
        if deficits[0][0] > 0:
            return deficits[0][2]
        # 2. If all targets met, scale proportionally to positive target weights
        best_role = default_role if default_role in WORKER_ROLES else 'research'
        best_ratio = 1e9
        for r in WORKER_ROLES:
            w = targets.get(r, 0)
            if w > 0:
                ratio = counts[r] / float(w)
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_role = r
        return best_role

    def join_with_invite(self, code: str, client_ip: str, requested_role: str | None = None) -> dict:
        if not isinstance(code, str) or not (8 <= len(code) <= 80):
            raise PermissionError('Invalid invite code')
        now = time.time()
        code_hash = _sha256(code.strip())
        with self.lock, self.connect(self.registry.root) as db:
            self.capacity(self.registry.root)
            inv = db.execute('SELECT * FROM hub_invites WHERE code_hash=?', (code_hash,)).fetchone()
            if not inv or inv['status'] != 'ACTIVE':
                raise PermissionError('Invite code invalid or revoked')
            if inv['expires_at'] < now:
                raise PermissionError('Invite code expired')
            if inv['used_count'] >= inv['max_uses']:
                raise PermissionError('Invite code quota reached')
            if db.execute('SELECT count(*) FROM nodes').fetchone()[0] >= 512:
                raise ValueError('Registry node capacity reached')

            targets = json.loads(inv['targets_json'])
            role = self._pick_balanced_role(db, targets, inv['default_role'], requested_role)
            raw_token = 'hubw_' + secrets.token_urlsafe(36)
            nid = secrets.token_hex(12)
            gen = db.execute('SELECT COALESCE(MAX(generation),0)+1 FROM nodes WHERE role=?', (role,)).fetchone()[0]
            db.execute(
                'INSERT INTO nodes VALUES(?,?,?,?,?,?,?,?,?)',
                (nid, HUB_DEVICE_TAG, client_ip or '0.0.0.0', role, _sha256(raw_token), 'APPROVED', now, now, gen),
            )
            db.execute('UPDATE hub_invites SET used_count = used_count + 1 WHERE id=?', (inv['id'],))
        return {'node_id': nid, 'role': role, 'token': raw_token, 'project': PROJECT}

    def authenticate_worker(self, token: str, client_ip: str = '') -> dict:
        if not isinstance(token, str) or not (30 <= len(token) <= 180):
            raise PermissionError('Missing or invalid worker credential')
        digest = _sha256(token)
        now = time.time()
        with self.lock, self.connect(self.registry.root) as db:
            row = db.execute('SELECT * FROM nodes WHERE token_hash=?', (digest,)).fetchone()
            if not row or row['device_id'] != HUB_DEVICE_TAG:
                raise PermissionError('Invalid hub worker credential')
            if row['status'] != 'APPROVED':
                raise PermissionError(row['status'])
            db.execute('UPDATE nodes SET heartbeat=?, ip=? WHERE id=?', (now, client_ip or row['ip'], row['id']))
            row = db.execute('SELECT * FROM nodes WHERE id=?', (row['id'],)).fetchone()
        return dict(row)

    def change_node_role(self, nid: str, new_role: str) -> None:
        if new_role not in WORKER_ROLES:
            raise ValueError('Role must be research, verify, or engineer')
        with self.lock, self.connect(self.registry.root) as db:
            row = db.execute('SELECT * FROM nodes WHERE id=?', (nid,)).fetchone()
            if not row or row['role'] == 'controller':
                raise ValueError('Cannot reassign controller or unknown node')
            db.execute('UPDATE nodes SET role=? WHERE id=?', (new_role, nid))

    def revoke_node(self, nid: str) -> None:
        with self.lock, self.connect(self.registry.root) as db:
            row = db.execute('SELECT * FROM nodes WHERE id=?', (nid,)).fetchone()
            if not row or row['role'] == 'controller':
                raise ValueError('Cannot revoke controller via worker list')
            db.execute("UPDATE nodes SET status='REVOKED' WHERE id=?", (nid,))


BASE_CSS = """
:root { --bg:#0b1020; --card:#131b33; --border:#263359; --txt:#e9eefb; --muted:#95a3c9; --acc:#4f8cff; --ok:#22c55e; --warn:#f59e0b; --err:#ef4444; }
* { box-sizing:border-box; }
body { margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--txt); line-height:1.5; }
.wrap { max-width:1120px; margin:0 auto; padding:20px; }
.card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:18px; margin-bottom:16px; }
h1,h2,h3 { margin-top:0; }
.row { display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px; margin-bottom:16px; }
.stat { background:#0f162b; border:1px solid var(--border); border-radius:10px; padding:14px; }
.stat .num { font-size:26px; font-weight:700; color:#fff; }
.badge { display:inline-block; padding:2px 9px; border-radius:99px; font-size:12px; font-weight:600; background:#1e293b; color:#cbd5e1; }
.badge.ok { background:#14532d; color:#86efac; }
.badge.warn { background:#78350f; color:#fde68a; }
.badge.err { background:#7f1d1d; color:#fca5a5; }
input,select,textarea { width:100%; background:#0c1224; color:var(--txt); border:1px solid var(--border); border-radius:8px; padding:9px 11px; font-size:14px; }
textarea { min-height:92px; font-family:inherit; }
label { display:block; font-size:13px; color:var(--muted); margin:8px 0 4px; }
button,.btn { cursor:pointer; background:var(--acc); color:#fff; border:none; border-radius:8px; padding:9px 15px; font-size:14px; font-weight:600; text-decoration:none; display:inline-block; }
button.sec,.btn.sec { background:#273456; }
button.ok { background:#16a34a; }
button.err { background:#dc2626; }
table { width:100%; border-collapse:collapse; font-size:13.5px; }
th,td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--border); vertical-align:top; }
th { color:var(--muted); font-weight:600; }
pre,code { background:#090d1a; border:1px solid var(--border); border-radius:6px; padding:2px 6px; font-size:13px; overflow-x:auto; }
pre { padding:12px; white-space:pre-wrap; word-break:break-word; }
.flash { border-left:4px solid var(--ok); background:#0f291e; padding:12px 14px; border-radius:8px; margin-bottom:16px; }
.flash.err { border-left-color:var(--err); background:#2c1215; }
"""


def make_hub_handler(hub: HubManager):
    class HubHTTPHandler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def client_ip(self) -> str:
            xff = self.headers.get('X-Real-IP') or self.headers.get('X-Forwarded-For', '').split(',')[0].strip()
            return xff or self.client_address[0]

        def is_https(self) -> bool:
            return self.headers.get('X-Forwarded-Proto', '').lower() == 'https'

        def cookies(self) -> dict[str, str]:
            raw = self.headers.get('Cookie', '')
            c = SimpleCookie()
            try:
                c.load(raw)
            except Exception:
                return {}
            return {k: v.value for k, v in c.items()}

        def send_html(self, status: int, body: str, extra_headers: list[tuple[str, str]] | None = None):
            data = body.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header(
                'Content-Security-Policy',
                "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'",
            )
            for k, v in (extra_headers or []):
                self.send_header(k, v)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def send_json(self, status: int, obj: object, extra_headers: list[tuple[str, str]] | None = None):
            data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            for k, v in (extra_headers or []):
                self.send_header(k, v)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def send_text(self, status: int, txt: str):
            data = txt.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def send_bytes(self, status: int, data: bytes, content_type: str, extra_headers: list[tuple[str, str]] | None = None, cache_control: str = 'private, max-age=300'):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', cache_control)
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('X-Content-Type-Options', 'nosniff')
            for k, v in (extra_headers or []):
                self.send_header(k, v)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def redirect(self, location: str, extra_headers: list[tuple[str, str]] | None = None):
            self.send_response(303)
            self.send_header('Location', location)
            self.send_header('Cache-Control', 'no-store')
            for k, v in (extra_headers or []):
                self.send_header(k, v)
            self.end_headers()

        def read_body(self, max_bytes: int = 524288) -> bytes:
            n = int(self.headers.get('Content-Length', '0'))
            if not (0 <= n <= max_bytes):
                raise ValueError('Request body too large')
            self.connection.settimeout(15)
            return self.rfile.read(n) if n > 0 else b''

        def read_form(self) -> dict[str, str]:
            raw = self.read_body().decode('utf-8', errors='replace')
            parsed = parse_qs(raw, keep_blank_values=True)
            return {k: v[0] for k, v in parsed.items()}

        def cookie_header(self, name: str, value: str, max_age: int = 604800) -> tuple[str, str]:
            sec = '; Secure' if self.is_https() else ''
            return ('Set-Cookie', f'{name}={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}{sec}')

        def current_worker(self) -> tuple[dict | None, str]:
            auth = self.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                tok = auth.removeprefix('Bearer ').strip()
                return hub.authenticate_worker(tok, self.client_ip()), tok
            tok = self.cookies().get('agentnet_worker', '')
            if not tok:
                return None, ''
            try:
                return hub.authenticate_worker(tok, self.client_ip()), tok
            except PermissionError:
                return None, ''

        def current_admin(self) -> str:
            auth = self.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                tok = auth.removeprefix('Bearer ').strip()
                if hub.verify_admin(tok):
                    return tok
            tok = self.cookies().get('agentnet_admin', '')
            return tok if hub.verify_admin(tok) else ''

        def origin_base(self) -> str:
            host = self.headers.get('Host', 'muse.alltool.pro')
            if host.startswith('100.') or host.startswith('163.'):
                return 'https://muse.alltool.pro'
            proto = 'https' if (self.is_https() or 'alltool.pro' in host) else 'http'
            return f'{proto}://{host}'

        # --- GET routes ---
        def do_GET(self):
            try:
                parsed = urlsplit(self.path)
                route = parsed.path.rstrip('/') or '/'
                qs = parse_qs(parsed.query)

                if route == '/health':
                    return self.send_json(200, {'status': 'ok', 'service': 'agentnet-hub', 'project': PROJECT})

                # 1-Click Browser Muse Join Link: /j/<CODE>
                if route.startswith('/j/'):
                    code = route.split('/j/', 1)[1].strip()
                    req_role = qs.get('role', [None])[0]
                    joined = hub.join_with_invite(code, self.client_ip(), requested_role=req_role)
                    return self.redirect('/portal?joined=1', [self.cookie_header('agentnet_worker', joined['token'])])

                # 1-Line Python Bootstrap Script for Code/CLI Muses: /sh/<CODE>
                if route.startswith('/sh/'):
                    code = route.split('/sh/', 1)[1].strip()
                    req_role = qs.get('role', [''])[0]
                    base = self.origin_base()
                    script = _build_cli_bootstrap_script(base, code, req_role)
                    return self.send_text(200, script)

                if route == '/':
                    w, _ = self.current_worker()
                    if w:
                        return self.redirect('/portal')
                    if self.current_admin():
                        return self.redirect('/admin')
                    return self.render_landing(qs.get('err', [''])[0])

                if route == '/portal':
                    w, tok = self.current_worker()
                    if not w:
                        return self.redirect('/?err=Vui+l%C3%B2ng+nh%E1%BA%ADp+M%C3%A3+Tri%E1%BB%87u+T%E1%BA%ADp+%C4%91%E1%BB%83+v%C3%A0o+S%E1%BA%A3nh+Nhi%E1%BB%87m+V%E1%BB%A5')
                    return self.render_worker_portal(w, tok, flash=qs.get('msg', [''])[0], err=qs.get('err', [''])[0])

                if route == '/media-upload':
                    w, _ = self.current_worker()
                    if not w and not self.current_admin():
                        return self.redirect('/?err=Vui+l%C3%B2ng+v%C3%A0o+S%E1%BA%A3nh+Nhi%E1%BB%87m+V%E1%BB%A5+tr%C6%B0%E1%BB%9Bc+khi+upload')
                    slug_val = (qs.get('slug', [''])[0] or '').strip()
                    existing_html = ''
                    if slug_val and SAFE_SLUG_RE.match(slug_val):
                        sdir = MEDIA_DROP_ROOT / slug_val
                        if sdir.is_dir():
                            base = self.origin_base()
                            urls = [f'{base}/media/{slug_val}/{p.name}' for p in sorted(sdir.iterdir()) if p.is_file()]
                            if urls:
                                existing_html = '<h3>File đã upload cho ' + _esc(slug_val) + '</h3><pre>' + _esc(json.dumps({'slug': slug_val, 'urls': urls}, ensure_ascii=False, indent=2)) + '</pre>'
                    page_html = (
                        f'<!doctype html><html><head><meta charset="utf-8"><title>Muse Media Upload</title><style>{BASE_CSS}</style></head><body>'
                        '<div class="wrap"><div class="card">'
                        '<h2>Muse Media Dropbox (muse.alltool.pro)</h2>'
                        '<p>Chọn toàn bộ ảnh 9:16 hoặc clip video .mp4 (hoặc 1 file .zip) cho tập phim rồi bấm Upload Media. Tối đa 120 MB/lần.</p>'
                        '<form method="post" action="/media-upload" enctype="multipart/form-data">'
                        f'<label>Mã tập (slug, vd: pn02_nguoi_di_cham_lai)</label><input name="slug" value="{_esc(slug_val)}" required pattern="[A-Za-z0-9_-]{{2,80}}">'
                        '<label>Chọn file (chọn nhiều file cùng lúc hoặc 1 file .zip)</label><input type="file" name="files" multiple required>'
                        '<label><input type="checkbox" name="extract" value="1" checked> Tự động giải nén nếu là file .zip</label>'
                        '<div style="margin-top:12px"><button class="btn" type="submit">Upload Media</button> <a class="btn sec" href="/portal">Quay lại Sảnh</a></div>'
                        '</form>'
                        f'{existing_html}'
                        '</div></div></body></html>'
                    )
                    return self.send_html(200, page_html)

                if route.startswith('/media/'):
                    parts = route.removeprefix('/media/').split('/')
                    if len(parts) != 2 or not SAFE_SLUG_RE.match(parts[0]):
                        return self.send_json(404, {'error': 'not_found'})
                    fname = _safe_media_name(parts[1])
                    if not fname:
                        return self.send_json(404, {'error': 'not_found'})
                    target = (MEDIA_DROP_ROOT / parts[0] / fname).resolve()
                    try:
                        target.relative_to(MEDIA_DROP_ROOT.resolve())
                    except ValueError:
                        return self.send_json(403, {'error': 'forbidden'})
                    if not target.is_file():
                        return self.send_json(404, {'error': 'not_found'})
                    mime, _ = mimetypes.guess_type(target.name)
                    return self.send_bytes(200, target.read_bytes(), mime or 'application/octet-stream', cache_control='public, max-age=86400')

                if route == '/admin':
                    adm = self.current_admin()
                    if not adm:
                        return self.render_admin_login(qs.get('err', [''])[0])
                    return self.render_admin_dashboard(adm, flash=qs.get('msg', [''])[0], new_code=qs.get('code', [''])[0])

                # JSON API for Hub CLI workers
                if route.startswith('/api/tasks/'):
                    w, _ = self.current_worker()
                    if not w:
                        return self.send_json(403, {'error': 'worker_auth_required'})
                    tid = route.split('/api/tasks/', 1)[1]
                    return self.send_json(200, hub.queue.get(w, '/tasks/' + tid))

                if route == '/api/me':
                    w, _ = self.current_worker()
                    if not w:
                        return self.send_json(403, {'error': 'worker_auth_required'})
                    return self.send_json(200, {'node_id': w['id'], 'role': w['role'], 'status': w['status'], 'project': PROJECT})

                if route == '/ggmap':
                    w, raw_tok = self.current_worker()
                    snap = hub.ggmap.status_snapshot()
                    if not w:
                        return self.send_html(
                            200,
                            render_ggmap_join_page(
                                BASE_CSS,
                                prefill_code=qs.get('code', [''])[0],
                                err=qs.get('err', [''])[0],
                                snap=snap,
                            ),
                        )
                    cur = hub.ggmap.current_for_worker(w['id'])
                    recent = hub.ggmap.recent_done(10)
                    return self.send_html(
                        200,
                        render_ggmap_worker_page(
                            BASE_CSS,
                            w,
                            _csrf_for(raw_tok),
                            snap,
                            cur,
                            recent,
                            flash=qs.get('msg', [''])[0],
                            err=qs.get('err', [''])[0],
                        ),
                    )

                if route.startswith('/ggmap/j/'):
                    code = route.split('/ggmap/j/', 1)[1].strip()
                    req_role = (qs.get('role', ['research'])[0] or 'research').strip()
                    try:
                        joined = hub.join_with_invite(code, self.client_ip(), requested_role=req_role)
                    except (PermissionError, ValueError) as exc:
                        return self.send_html(
                            403,
                            render_ggmap_join_page(
                                BASE_CSS,
                                prefill_code=code,
                                err=str(exc),
                                snap=hub.ggmap.status_snapshot(),
                            ),
                        )
                    return self.redirect(
                        '/ggmap?' + urlencode({'msg': 'Đã gia nhập nhánh Rà Google Maps'}),
                        [self.cookie_header('agentnet_worker', joined['token'])],
                    )

                if route == '/ggmap/admin':
                    adm = self.current_admin()
                    if not adm:
                        return self.render_admin_login(qs.get('err', [''])[0])
                    filter_mode = (qs.get('filter', ['all'])[0] or 'all').strip()
                    return self.send_html(
                        200,
                        render_ggmap_admin_page(
                            BASE_CSS,
                            _csrf_for(adm),
                            hub.ggmap.status_snapshot(),
                            hub.ggmap.list_items(filter_mode),
                            filter_mode=filter_mode,
                            flash=qs.get('msg', [''])[0],
                        ),
                    )

                if route == '/ggmap/export.csv':
                    if not self.current_admin():
                        return self.send_json(403, {'error': 'admin_auth_required'})
                    csv_data = hub.ggmap.export_csv(self.origin_base()).encode('utf-8')
                    return self.send_bytes(
                        200,
                        csv_data,
                        'text/csv; charset=utf-8',
                        extra_headers=[('Content-Disposition', 'attachment; filename="longbien_ggmap_results.csv"')],
                        cache_control='no-store',
                    )

                if route.startswith('/ggmap/shots/'):
                    adm = self.current_admin()
                    w = None
                    if not adm:
                        w, _ = self.current_worker()
                    if not (w or adm):
                        return self.send_json(403, {'error': 'auth_required'})
                    shot_name = route.split('/ggmap/shots/', 1)[1]
                    found = hub.ggmap.get_shot_path(shot_name)
                    if not found:
                        return self.send_json(404, {'error': 'shot_not_found'})
                    shot_path, ctype = found
                    return self.send_bytes(200, shot_path.read_bytes(), ctype)

                if route == '/api/ggmap/status':
                    adm = self.current_admin()
                    w = None
                    if not adm:
                        w, _ = self.current_worker()
                    if not (adm or w):
                        return self.send_json(403, {'error': 'auth_required'})
                    resp = {'ok': True, 'summary': hub.ggmap.status_snapshot()}
                    if qs.get('include', [''])[0] == 'items':
                        resp['items'] = hub.ggmap.list_items(qs.get('filter', ['all'])[0])
                    return self.send_json(200, resp)

                if route in ('/api/chief/inbox', '/api/qa/scores'):
                    tok = (qs.get('token', [''])[0] or self.headers.get('X-Invite-Token', '')).strip()
                    w, _ = self.current_worker()
                    if not (w or self.current_admin() or hub.verify_invite_token(tok)):
                        return self.send_json(403, {'error': 'auth_required'})
                    if route == '/api/qa/scores':
                        return self.send_json(200, {'ok': True, 'scores': hub.list_episode_scores(120)})
                    return self.send_json(200, hub.get_chief_inbox())

                if route == '/chief':
                    tok = (qs.get('token', [''])[0] or '').strip()
                    w, _ = self.current_worker()
                    adm = self.current_admin()
                    if not (adm or (w and w['role'] in ('chief', 'controller')) or hub.verify_invite_token(tok)):
                        return self.render_admin_login('Cần quyền Quản trị hoặc mã mời hợp lệ để mở Trung Tâm Điều Phối')
                    snap = hub.get_chief_inbox()
                    role_badges = ' &middot; '.join(f"<b>{_esc(r['role'])}</b>: {r['count']}" for r in snap['role_nodes']) or 'Đang khởi tạo'
                    cmd_rows = ''.join(
                        f"<tr><td><code>{_esc(c['id'])}</code></td><td><b>{_esc(c['status'])}</b></td>"
                        f"<td>{_esc(c['command_text'])}</td><td><small>{_esc(c['report_text'])}</small></td></tr>"
                        for c in snap['recent_commands']
                    ) or '<tr><td colspan="4">Chưa có lệnh nào</td></tr>'
                    sc_rows = ''.join(
                        f"<tr><td><code>{_esc(s['slug'])}</code><br><small>{_esc(s['channel'])}</small></td>"
                        f"<td><b>{s['total_score']}/100</b> <span class='badge {'ok' if s['verdict']=='PASS' else 'err'}'>{_esc(s['verdict'])}</span></td>"
                        f"<td>KB:{s['script_score']} &middot; ĐD:{s['director_score']} &middot; Ảnh:{s['visual_score']} &middot; Video:{s['video_score']}</td>"
                        f"<td><small>{_esc(s['feedback'])}</small></td></tr>"
                        for s in snap['recent_scores']
                    ) or '<tr><td colspan="4">Đội Giám Khảo (qa_critic) đang chấm lô đầu tiên...</td></tr>'
                    tok_hidden = f'<input type="hidden" name="token" value="{_esc(tok)}">' if tok else ''
                    html_chief = (
                        f"<!doctype html><html lang='vi'><head><meta charset='utf-8'><title>Muse Tổng Điều Phối</title><style>{BASE_CSS}</style></head><body>"
                        "<div class='wrap'>"
                        "<h1>Trung Tâm Giao Lệnh — 1 Muse Tổng Điều Phối &amp; Hội Đồng Chấm Phim</h1>"
                        f"<div class='card'><p>Cơ cấu đội hình đang trực: {role_badges} | Đã chấm: <b>{snap['scores_summary']['total_scored']}</b> tập "
                        f"(Đạt &ge;85đ: <b>{snap['scores_summary']['passed']}</b>, Cần sửa lại: <b>{snap['scores_summary']['rework']}</b>)</p>"
                        f"<form method='post' action='/api/chief/command?redirect=1{('&token=' + _esc(tok)) if tok else ''}'>"
                        f"{tok_hidden}"
                        "<label>Giao lệnh tập trung duy nhất cho Muse Điều Phối Tổng (tự chia việc cho Đạo diễn, Họa sĩ, Dựng video, Giám khảo):</label>"
                        "<textarea name='command_text' placeholder='Ví dụ: Chấm điểm 10 tập mới nhất + viết kịch bản và vẽ 5 tập Phim Ma dân gian nhịp nhanh, tập nào dưới 85 điểm tự cho vẽ lại cảnh lỗi'></textarea>"
                        "<div style='margin-top:10px'><button type='submit' class='ok'>Phát Lệnh Cho Muse Điều Phối</button></div>"
                        "</form></div>"
                        f"<div class='card'><h2>Lịch Sử Lệnh Điều Phối</h2><table><thead><tr><th>Mã</th><th>Trạng thái</th><th>Nội dung lệnh</th><th>Báo cáo từ Muse Điều Phối</th></tr></thead><tbody>{cmd_rows}</tbody></table></div>"
                        f"<div class='card'><h2>Bảng Điểm Hội Đồng Muse QA (Thang 100 — Chuẩn duyệt &ge; 85)</h2><table><thead><tr><th>Tập phim</th><th>Tổng điểm</th><th>Chi tiết 4 ban (25đ/ban)</th><th>Nhận xét &amp; Cảnh cần sửa</th></tr></thead><tbody>{sc_rows}</tbody></table></div>"
                        "</div></body></html>"
                    )
                    return self.send_html(200, html_chief)

                if route == '/croc-offers':
                    tok = (qs.get('token', [''])[0] or self.headers.get('X-Invite-Token', '')).strip()
                    w, _ = self.current_worker()
                    if not (w or self.current_admin() or hub.verify_invite_token(tok)):
                        return self.send_json(403, {'error': 'auth_required'})
                    return self.send_json(200, {'ok': True, 'offers': hub.claim_pending_croc_offers(5)})

                if route == '/croc-push.sh':
                    tok = (qs.get('token', [''])[0] or '').strip()
                    slug_q = (qs.get('slug', [''])[0] or '').strip()
                    if not hub.verify_invite_token(tok):
                        return self.send_json(403, {'error': 'invalid_invite_token'})
                    base = self.origin_base()
                    script = f'''#!/usr/bin/env bash
set -euo pipefail
SLUG="${{SLUG:-{slug_q}}}"
if [ -z "$SLUG" ] || [ "$#" -lt 1 ]; then
  echo "Usage: bash push with SLUG and scene files" >&2
  exit 1
fi
ZIP_PATH="/tmp/${{SLUG}}_croc_$$.zip"
python3 -c '
import pathlib, sys, zipfile
zpath = pathlib.Path(sys.argv[1])
with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_STORED) as zf:
    for arg in sys.argv[2:]:
        p = pathlib.Path(arg)
        if p.is_file():
            zf.write(p, arcname=p.name)
        elif p.is_dir():
            for f in sorted(p.iterdir()):
                if f.is_file():
                    zf.write(f, arcname=f.name)
' "$ZIP_PATH" "$@"
curl -fsSL -X POST "{base}/media-upload?token={tok}&slug=${{SLUG}}&json=1" -F "file=@${{ZIP_PATH}}" >/dev/null
rm -f "$ZIP_PATH"
echo "CROC_PUSH_TO_E_OK slug=$SLUG"
'''
                    return self.send_bytes(200, script.encode('utf-8'), 'text/x-shellscript; charset=utf-8', cache_control='no-store')

                return self.send_json(404, {'error': 'not_found'})
            except QueueError as e:
                return self.send_json(e.code, {'error': e.message})
            except PermissionError as e:
                return self.send_html(403, f'<html><head><style>{BASE_CSS}</style></head><body><div class="wrap"><div class="card"><h2>Từ chối truy cập</h2><p>{_esc(e)}</p><a class="btn sec" href="/">Quay lại trang chủ</a></div></div></body></html>')
            except Exception:
                return self.send_json(503, {'error': 'hub_unavailable'})

        # --- POST routes ---
        def do_POST(self):
            try:
                route = urlsplit(self.path).path.rstrip('/')

                # Public Invite Join (HTML Form or JSON API)
                if route == '/join':
                    form = self.read_form()
                    joined = hub.join_with_invite(form.get('code', ''), self.client_ip(), form.get('role') or None)
                    return self.redirect('/portal?msg=Gia+nh%E1%BA%ADp+%C4%91%E1%BB%99i+qu%C3%A2n+th%C3%A0nh+c%C3%B4ng', [self.cookie_header('agentnet_worker', joined['token'])])

                if route == '/api/join':
                    data = json.loads(self.read_body().decode('utf-8'))
                    joined = hub.join_with_invite(data.get('code', ''), self.client_ip(), data.get('role') or None)
                    return self.send_json(200, joined)

                if route in ('/api/chief/command', '/api/chief/dispatch', '/api/qa/score'):
                    qs = parse_qs(urlsplit(self.path).query)
                    tok = (qs.get('token', [''])[0] or self.headers.get('X-Invite-Token', '')).strip()
                    w, _ = self.current_worker()
                    adm = self.current_admin()
                    if not (w or adm or hub.verify_invite_token(tok)):
                        return self.send_json(403, {'error': 'auth_required'})
                    ctype = (self.headers.get('Content-Type') or '').lower()
                    if 'application/json' in ctype:
                        data = json.loads(self.read_body().decode('utf-8') or '{}')
                    else:
                        data = self.read_form()
                    if route == '/api/chief/command':
                        out = hub.submit_chief_command(data.get('source', 'owner'), data.get('command_text', ''))
                        if qs.get('redirect', ['0'])[0] == '1':
                            t_qs = ('?token=' + _esc(tok)) if tok else ''
                            return self.redirect('/chief' + t_qs)
                        return self.send_json(200, out)
                    if route == '/api/qa/score':
                        rev = w['id'] if w else 'qa_critic'
                        return self.send_json(200, hub.record_episode_score(rev, data))
                    if not (adm or hub.verify_invite_token(tok) or (w and w['role'] in ('chief', 'controller'))):
                        return self.send_json(403, {'error': 'chief_role_required'})
                    return self.send_json(200, hub.chief_dispatch(data))

                if route in ('/croc-offer', '/croc-ack'):
                    qs = parse_qs(urlsplit(self.path).query)
                    tok = (qs.get('token', [''])[0] or self.headers.get('X-Invite-Token', '')).strip()
                    w, _ = self.current_worker()
                    if not (w or self.current_admin() or hub.verify_invite_token(tok)):
                        return self.send_json(403, {'error': 'auth_required'})
                    data = json.loads(self.read_body().decode('utf-8') or '{}')
                    if route == '/croc-offer':
                        return self.send_json(200, hub.create_croc_offer(data.get('slug', ''), data.get('code', '')))
                    return self.send_json(200, hub.ack_croc_offer(data.get('id', ''), data.get('status', 'DONE')))

                if route == '/media-upload':
                    qs = parse_qs(urlsplit(self.path).query)
                    tok = (qs.get('token', [''])[0] or self.headers.get('X-Invite-Token', '')).strip()
                    w, _ = self.current_worker()
                    if not (w or self.current_admin() or hub.verify_invite_token(tok)):
                        return self.send_json(403, {'error': 'worker_auth_required'})
                    ctype = self.headers.get('Content-Type', '')
                    n = int(self.headers.get('Content-Length', '0'))
                    if not (0 < n <= MEDIA_MAX_BYTES):
                        return self.send_json(413, {'error': 'payload_too_large_max_120MB'})
                    self.connection.settimeout(120)
                    raw_body = self.rfile.read(n)
                    fields: dict[str, str] = {}
                    uploads: list[tuple[str, bytes]] = []
                    if 'multipart/form-data' in ctype.lower():
                        fields, uploads = _parse_multipart(ctype, raw_body)
                    else:
                        fields['slug'] = (qs.get('slug', [''])[0] or '').strip()
                        fields['extract'] = (qs.get('extract', ['1'])[0] or '1').strip()
                        raw_name = (qs.get('name', [''])[0] or '').strip()
                        if raw_name:
                            uploads.append((raw_name, raw_body))
                    slug_val = (fields.get('slug') or qs.get('slug', [''])[0] or '').strip()
                    if not SAFE_SLUG_RE.match(slug_val):
                        return self.send_json(400, {'error': 'invalid_slug'})
                    if not uploads:
                        return self.send_json(400, {'error': 'no_files_uploaded'})
                    sdir = MEDIA_DROP_ROOT / slug_val
                    base = self.origin_base()
                    saved: list[dict] = []
                    ram_items: list[tuple[str, bytes]] = []
                    do_extract = fields.get('extract', '1') != '0'
                    for raw_name, payload in uploads:
                        safe = _safe_media_name(raw_name)
                        if not safe or not payload:
                            continue
                        if safe.lower().endswith('.zip') and do_extract:
                            import io as _io
                            with zipfile.ZipFile(_io.BytesIO(payload), 'r') as zf:
                                for info in zf.infolist():
                                    if info.is_dir() or info.file_size > 60 * 1024 * 1024:
                                        continue
                                    inner = _safe_media_name(info.filename)
                                    if not inner or inner.lower().endswith('.zip'):
                                        continue
                                    data_in = zf.read(info)
                                    ram_items.append((inner, data_in))
                                    if not inner.lower().endswith(('.mp4', '.mov', '.webm')):
                                        sdir.mkdir(parents=True, exist_ok=True)
                                        (sdir / inner).write_bytes(data_in)
                                    saved.append({'name': inner, 'size': len(data_in), 'url': f'{base}/media/{slug_val}/{inner}', 'delivery': 'croc_E'})
                        else:
                            ram_items.append((safe, payload))
                            if not safe.lower().endswith(('.mp4', '.mov', '.webm')):
                                sdir.mkdir(parents=True, exist_ok=True)
                                (sdir / safe).write_bytes(payload)
                            saved.append({'name': safe, 'size': len(payload), 'url': f'{base}/media/{slug_val}/{safe}', 'delivery': 'croc_E'})
                    if ram_items:
                        _relay_to_e_via_croc(hub, slug_val, ram_items, sdir)
                    saved.sort(key=lambda x: x['name'])
                    result_obj = {'ok': True, 'slug': slug_val, 'delivery': 'croc_E', 'count': len(saved), 'files': saved}
                    want_json = 'application/json' in (self.headers.get('Accept', '').lower()) or qs.get('json', ['0'])[0] == '1'
                    if want_json:
                        return self.send_json(200, result_obj)
                    links_li = ''.join(f'<li><a href="{_esc(x["url"])}" target="_blank">{_esc(x["url"])}</a> ({x["size"]} B)</li>' for x in saved)
                    page_html = (
                        f'<!doctype html><html><head><meta charset="utf-8"><title>Upload OK</title><style>{BASE_CSS}</style></head><body>'
                        '<div class="wrap"><div class="card">'
                        f'<h2>Upload thành công {len(saved)} file cho {_esc(slug_val)}</h2>'
                        f'<ul>{links_li}</ul>'
                        f'<h3>JSON copy vào form Nộp Kết Quả</h3><pre>{_esc(json.dumps(result_obj, ensure_ascii=False, indent=2))}</pre>'
                        f'<a class="btn" href="/portal">Quay lại Sảnh Nộp Kết Quả</a> <a class="btn sec" href="/media-upload?slug={_esc(slug_val)}">Upload thêm</a>'
                        '</div></div></body></html>'
                    )
                    return self.send_html(200, page_html)

                # JSON Worker API endpoints (/api/claim, /api/tasks/{id}/heartbeat, /api/tasks/{id}/result)
                if route == '/api/claim' or (route.startswith('/api/tasks/') and route.endswith(('/heartbeat', '/result'))):
                    w, _ = self.current_worker()
                    if not w:
                        return self.send_json(403, {'error': 'worker_auth_required'})
                    data = json.loads(self.read_body().decode('utf-8') or '{}')
                    q_path = route.removeprefix('/api')
                    return self.send_json(200, hub.queue.post(w, q_path, data, delegated=False))

                # Browser Worker HTML Portal Actions (/portal/claim, /portal/submit, /portal/logout)
                if route.startswith('/portal/'):
                    w, tok = self.current_worker()
                    if not w:
                        return self.redirect('/?err=Phi%C3%AAn+h%E1%BA%BFt+h%E1%BA%A1n')
                    form = self.read_form()
                    if not hmac.compare_digest(form.get('csrf', ''), _csrf_for(tok)):
                        raise PermissionError('CSRF check failed')
                    if route == '/portal/logout':
                        return self.redirect('/', [self.cookie_header('agentnet_worker', '', max_age=0)])
                    if route == '/portal/claim':
                        caps = [c.strip() for c in form.get('capabilities', 'web_search,browser,research,summarize,verify').split(',') if c.strip()]
                        claimed = hub.queue.post(w, '/claim', {'capabilities': caps[:16]}, delegated=False)
                        if not claimed.get('id'):
                            return self.redirect('/portal?msg=Hi%E1%BB%87n+ch%C6%B0a+c%C3%B3+task+m%E1%BB%9Bi+cho+vai+' + _esc(w['role']) + '+—+h%C3%A3y+b%E1%BA%A5m+Nh%E1%BA%ADn+Vi%E1%BB%87c+l%E1%BA%A1i+sau+60s')
                        return self.redirect('/portal?msg=%C4%90%C3%A3+nh%E1%BA%ADn+nhi%E1%BB%87m+v%E1%BB%A5+' + _esc(claimed['id'][:8]))
                    if route == '/portal/submit':
                        tid = form.get('task_id', '').strip()
                        lease = form.get('lease', '').strip()
                        outcome = form.get('outcome', 'ok').strip()
                        if outcome not in ('ok', 'PASS', 'BLOCKED', 'NEEDS_ACCESS', 'UNSUPPORTED_CAPABILITY'):
                            outcome = 'ok'
                        sources = [ln.strip() for ln in form.get('sources', '').splitlines() if ln.strip()]
                        lessons = [ln.strip() for ln in form.get('lessons', '').splitlines() if ln.strip()]
                        limitations = [ln.strip() for ln in form.get('limitations', '').splitlines() if ln.strip()]
                        res_obj = {
                            'outcome': outcome,
                            'summary': form.get('summary', '').strip(),
                            'sources': sources,
                            'evidence_links': sources,
                            'lessons': lessons,
                            'limitations': limitations,
                        }
                        hub.queue.post(w, f'/tasks/{tid}/result', {'lease': lease, 'result': res_obj}, delegated=False)
                        # Auto-claim next task right away if requested!
                        if form.get('next', '1') == '1':
                            caps = [w['role'], 'browser', 'web_search', 'research', 'summarize']
                            hub.queue.post(w, '/claim', {'capabilities': caps}, delegated=False)
                        return self.redirect('/portal?msg=%C4%90%C3%A3+n%E1%BB%99p+k%E1%BA%BFt+qu%E1%BA%A3+th%C3%A0nh+c%C3%B4ng')

                # Admin Login & Actions
                if route == '/admin/login':
                    form = self.read_form()
                    key = form.get('admin_key', '').strip()
                    if not hub.verify_admin(key):
                        time.sleep(0.4)
                        return self.redirect('/admin?err=Sai+m%C3%A3+Qu%E1%BA%A3n+tr%E1%BB%8B')
                    return self.redirect('/admin', [self.cookie_header('agentnet_admin', key)])

                if route.startswith('/admin/'):
                    adm = self.current_admin()
                    if not adm:
                        return self.redirect('/admin?err=Ch%C6%B0a+%C4%91%C4%83ng+nh%E1%BA%ADp')
                    form = self.read_form()
                    if not hmac.compare_digest(form.get('csrf', ''), _csrf_for(adm)):
                        raise PermissionError('CSRF check failed')
                    admin_actor = {'id': 'hub-owner', 'role': 'controller'}

                    if route == '/admin/logout':
                        return self.redirect('/admin', [self.cookie_header('agentnet_admin', '', max_age=0)])
                    if route == '/admin/invite/create':
                        targets = {
                            'research': int(form.get('t_research', '6') or 0),
                            'verify': int(form.get('t_verify', '2') or 0),
                            'engineer': int(form.get('t_engineer', '2') or 0),
                        }
                        inv = hub.create_invite(
                            ttl_minutes=int(form.get('ttl', '60') or 60),
                            max_uses=int(form.get('max_uses', '20') or 20),
                            targets=targets,
                        )
                        return self.redirect('/admin?code=' + _esc(inv['code']) + '&msg=%C4%90%C3%A3+t%E1%BA%A1o+Link+Tri%E1%BB%87u+T%E1%BA%ADp+m%E1%BB%9Bi')
                    if route == '/admin/invite/revoke':
                        hub.revoke_invite(form.get('invite_id', ''))
                        return self.redirect('/admin?msg=%C4%90%C3%A3+kh%C3%B3a+m%C3%A3+m%E1%BB%9Di')
                    if route == '/admin/node/role':
                        hub.change_node_role(form.get('node_id', ''), form.get('role', 'research'))
                        return self.redirect('/admin?msg=%C4%90%C3%A3+%C4%91%E1%BB%95i+vai+tr%C3%B2+node')
                    if route == '/admin/node/revoke':
                        hub.revoke_node(form.get('node_id', ''))
                        return self.redirect('/admin?msg=%C4%90%C3%A3+thu+h%E1%BB%93i+node')
                    if route == '/admin/task/approve':
                        tid = form.get('task_id', '').strip()
                        hub.queue.post(admin_actor, f'/tasks/{tid}/approve', {})
                        return self.redirect('/admin?msg=%C4%90%C3%A3+duy%E1%BB%87t+task+' + _esc(tid[:8]))
                    if route == '/admin/task/batch':
                        role = form.get('assigned_to', 'research')
                        kind = form.get('kind', 'research_item').strip() or 'research_item'
                        criteria = form.get('criteria', 'Đối chiếu nguồn thật, ghi rõ bằng chứng và giới hạn.').strip()
                        auto_v = form.get('auto_verify', '') == '1'
                        lines = [ln.strip() for ln in form.get('objectives', '').splitlines() if ln.strip()]
                        if not lines:
                            return self.redirect('/admin?msg=Ch%C6%B0a+nh%E1%BA%ADp+danh+s%C3%A1ch+nhi%E1%BB%87m+v%E1%BB%A5')
                        stamp = int(time.time())
                        tasks = []
                        for idx, line in enumerate(lines[:200], start=1):
                            tasks.append({
                                'project': PROJECT,
                                'assigned_to': role,
                                'kind': kind,
                                'dedup': f'hub-{stamp}-{idx}-{_sha256(line)[:10]}',
                                'auto_verify': auto_v,
                                'payload': {
                                    'objective': line,
                                    'acceptance_criteria': criteria,
                                },
                            })
                        hub.queue.post(admin_actor, '/tasks/batch', {'project': PROJECT, 'tasks': tasks})
                        return self.redirect(f'/admin?msg=%C4%90%C3%A3+giao+{len(tasks)}+nhi%E1%BB%87m+v%E1%BB%A5+v%C3%A0o+h%C3%A0ng+%C4%91%E1%BB%A3i')

                if route == '/ggmap/join':
                    form = self.read_form()
                    try:
                        joined = hub.join_with_invite(form.get('code', ''), self.client_ip(), form.get('role') or 'research')
                    except (PermissionError, ValueError) as exc:
                        return self.redirect('/ggmap?' + urlencode({'err': str(exc), 'code': form.get('code', '')}))
                    return self.redirect(
                        '/ggmap?' + urlencode({'msg': 'Gia nhập nhánh Rà Google Maps thành công'}),
                        [self.cookie_header('agentnet_worker', joined['token'])],
                    )

                if route == '/ggmap/claim':
                    w, raw_tok = self.current_worker()
                    if not w:
                        return self.redirect('/ggmap')
                    form = self.read_form()
                    if form.get('csrf') != _csrf_for(raw_tok):
                        raise PermissionError('CSRF token không hợp lệ')
                    claimed = hub.ggmap.claim(w['id'])
                    msg = f"Đã nhận tuyến {claimed['code']} ({claimed['pdf_name']})" if claimed else 'Hiện không còn tuyến nào chờ rà trong hàng đợi'
                    return self.redirect('/ggmap?' + urlencode({'msg': msg}))

                if route == '/ggmap/release':
                    w, raw_tok = self.current_worker()
                    if not w:
                        return self.redirect('/ggmap')
                    form = self.read_form()
                    if form.get('csrf') != _csrf_for(raw_tok):
                        raise PermissionError('CSRF token không hợp lệ')
                    try:
                        hub.ggmap.release(form.get('code', ''), w['id'], form.get('lease'))
                    except (PermissionError, ValueError) as exc:
                        return self.redirect('/ggmap?' + urlencode({'err': str(exc)}))
                    return self.redirect('/ggmap?' + urlencode({'msg': 'Đã trả tuyến về hàng đợi'}))

                if route == '/ggmap/submit':
                    w, raw_tok = self.current_worker()
                    if not w:
                        return self.redirect('/ggmap')
                    try:
                        ctype = self.headers.get('Content-Type', '')
                        raw_body = self.read_body(max_bytes=4 * 1024 * 1024)
                        shot_bytes = b''
                        if 'multipart/form-data' in ctype.lower():
                            fields, files = parse_multipart(ctype, raw_body)
                            if 'screenshot' in files:
                                shot_bytes = files['screenshot'][1]
                        else:
                            parsed_qs = parse_qs(raw_body.decode('utf-8', errors='replace'), keep_blank_values=True)
                            fields = {k: v[0] for k, v in parsed_qs.items()}
                        if fields.get('csrf') != _csrf_for(raw_tok):
                            raise PermissionError('CSRF token không hợp lệ')
                        item = hub.ggmap.submit(
                            code=fields.get('code', ''),
                            node_id=w['id'],
                            lease=fields.get('lease', ''),
                            maps_found_name=fields.get('maps_found_name', ''),
                            maps_prefix=fields.get('maps_prefix', ''),
                            maps_url=fields.get('maps_url', ''),
                            worker_note=fields.get('worker_note', ''),
                            screenshot_bytes=shot_bytes,
                            screenshot_b64=fields.get('screenshot_base64', ''),
                            screenshot_url=fields.get('screenshot_url', ''),
                        )
                    except (ValueError, PermissionError, OSError) as exc:
                        return self.redirect('/ggmap?' + urlencode({'err': str(exc)}))
                    return self.redirect('/ggmap?' + urlencode({'msg': f"Đã lưu {item['code']} · {item['match_status']}"}))

                if route == '/ggmap/admin/requeue':
                    adm = self.current_admin()
                    if not adm:
                        return self.redirect('/ggmap/admin')
                    form = self.read_form()
                    if form.get('csrf') != _csrf_for(adm):
                        raise PermissionError('CSRF token không hợp lệ')
                    code = form.get('code', '')
                    hub.ggmap.requeue_item(code, clear_result=bool(form.get('clear_result')))
                    return self.redirect('/ggmap/admin?' + urlencode({'msg': f'Đã đẩy {code} về hàng đợi'}))

                if route == '/api/ggmap/seed':
                    if not self.current_admin():
                        return self.send_json(403, {'error': 'admin_auth_required'})
                    try:
                        data = json.loads(self.read_body(max_bytes=2 * 1024 * 1024).decode('utf-8'))
                        res = hub.ggmap.seed_items(data.get('items') or [], reset=bool(data.get('reset')))
                        return self.send_json(200, {'ok': True, **res})
                    except (ValueError, json.JSONDecodeError) as exc:
                        return self.send_json(400, {'error': str(exc)})

                if route == '/api/ggmap/claim':
                    w, _ = self.current_worker()
                    if not w:
                        return self.send_json(403, {'error': 'worker_auth_required'})
                    try:
                        raw = self.read_body().decode('utf-8') or '{}'
                        data = json.loads(raw)
                        item = hub.ggmap.claim(w['id'], lease_seconds=int(data.get('lease_seconds') or 900))
                        return self.send_json(200, {'ok': True, 'item': item})
                    except (ValueError, json.JSONDecodeError) as exc:
                        return self.send_json(400, {'error': str(exc)})

                if route == '/api/ggmap/release':
                    w, _ = self.current_worker()
                    if not w:
                        return self.send_json(403, {'error': 'worker_auth_required'})
                    try:
                        data = json.loads((self.read_body().decode('utf-8') or '{}'))
                        item = hub.ggmap.release(data.get('code', ''), w['id'], data.get('lease'))
                        return self.send_json(200, {'ok': True, 'item': item})
                    except (ValueError, json.JSONDecodeError) as exc:
                        return self.send_json(400, {'error': str(exc)})

                if route == '/api/ggmap/submit':
                    w, _ = self.current_worker()
                    if not w:
                        return self.send_json(403, {'error': 'worker_auth_required'})
                    try:
                        ctype = self.headers.get('Content-Type', '')
                        raw_body = self.read_body(max_bytes=4 * 1024 * 1024)
                        if 'multipart/form-data' in ctype.lower():
                            fields, files = parse_multipart(ctype, raw_body)
                            shot_bytes = files['screenshot'][1] if 'screenshot' in files else b''
                            item = hub.ggmap.submit(
                                code=fields.get('code', ''),
                                node_id=w['id'],
                                lease=fields.get('lease', ''),
                                maps_found_name=fields.get('maps_found_name', ''),
                                maps_prefix=fields.get('maps_prefix', ''),
                                maps_url=fields.get('maps_url', ''),
                                worker_note=fields.get('worker_note', ''),
                                screenshot_bytes=shot_bytes,
                                screenshot_b64=fields.get('screenshot_base64', ''),
                                screenshot_url=fields.get('screenshot_url', ''),
                            )
                        else:
                            data = json.loads(raw_body.decode('utf-8') or '{}')
                            item = hub.ggmap.submit(
                                code=data.get('code', ''),
                                node_id=w['id'],
                                lease=data.get('lease', ''),
                                maps_found_name=data.get('maps_found_name', ''),
                                maps_prefix=data.get('maps_prefix', ''),
                                maps_url=data.get('maps_url', ''),
                                worker_note=data.get('worker_note', ''),
                                screenshot_b64=data.get('screenshot_base64', ''),
                                screenshot_url=data.get('screenshot_url', ''),
                            )
                        return self.send_json(200, {'ok': True, 'item': item})
                    except (ValueError, json.JSONDecodeError) as exc:
                        return self.send_json(400, {'error': str(exc)})
                    except PermissionError as exc:
                        return self.send_json(403, {'error': str(exc)})
                    except OSError as exc:
                        return self.send_json(507, {'error': str(exc)})

                if route == '/api/ggmap/requeue':
                    if not self.current_admin():
                        return self.send_json(403, {'error': 'admin_auth_required'})
                    try:
                        data = json.loads((self.read_body().decode('utf-8') or '{}'))
                        item = hub.ggmap.requeue_item(data.get('code', ''), clear_result=bool(data.get('clear_result')))
                        return self.send_json(200, {'ok': True, 'item': item})
                    except (ValueError, json.JSONDecodeError) as exc:
                        return self.send_json(400, {'error': str(exc)})

                return self.send_json(404, {'error': 'not_found'})
            except QueueError as e:
                if self.path.startswith('/api/'):
                    return self.send_json(e.code, {'error': e.message})
                return self.redirect('/admin?msg=L%E1%BB%97i:+' + _esc(e.message))
            except PermissionError as e:
                if self.path.startswith('/api/'):
                    return self.send_json(403, {'error': str(e)})
                return self.send_html(403, f'<html><head><style>{BASE_CSS}</style></head><body><div class="wrap"><div class="card"><h2>Từ chối truy cập</h2><p>{_esc(e)}</p><a class="btn sec" href="/">Quay lại</a></div></div></body></html>')
            except (ValueError, TypeError) as e:
                if self.path.startswith('/api/'):
                    return self.send_json(400, {'error': str(e)})
                return self.redirect('/?err=Y%C3%AAu+c%E1%BA%A7u+kh%C3%B4ng+h%E1%BB%A3p+l%E1%BB%87')
            except Exception:
                return self.send_json(503, {'error': 'hub_unavailable'})

        # --- HTML Views ---
        def render_landing(self, err: str = ''):
            err_html = f'<div class="flash err">{_esc(err)}</div>' if err else ''
            body = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgentNet Hub — Sảnh Tuyển Quân Muse</title><style>{BASE_CSS}</style></head><body>
<div class="wrap" style="max-width:560px;margin-top:40px">
  <div class="card">
    <h1>AgentNet Hub</h1>
    <p style="color:var(--muted)">Cổng gia nhập nhanh cho Đội quân Muse (Browser &amp; CLI). Nhập <b>Mã Triệu Tập</b> hoặc mở trực tiếp đường dẫn <code>/j/&lt;MA_MOI&gt;</code>.</p>
    {err_html}
    <form method="post" action="/join">
      <label for="code">Mã Triệu Tập (Invite Code)</label>
      <input id="code" name="code" placeholder="VD: MUSE-XXXXXXXXXXXX" required autocomplete="off">
      <label for="role">Vai trò (Để trống = Hub tự động chia quân cân bằng)</label>
      <select id="role" name="role">
        <option value="">Tự động phân vai theo đội hình</option>
        <option value="research">research (Nghiên cứu / Săn nguồn)</option>
        <option value="verify">verify (Kiểm chứng độc lập / QC)</option>
        <option value="engineer">engineer (Kịch bản / Kỹ thuật)</option>
      </select>
      <div style="margin-top:14px" class="row">
        <button type="submit">Gia Nhập Đội Quân</button>
        <a class="btn sec" href="/admin">Bảng Chỉ Huy (Chủ dự án)</a>
      </div>
    </form>
  </div>
</div></body></html>"""
            self.send_html(200, body)

        def render_worker_portal(self, worker: dict, raw_tok: str, flash: str = '', err: str = ''):
            csrf = _csrf_for(raw_tok)
            # Check if this worker currently owns a RUNNING task
            running_task = None
            with hub.queue.db() as c:
                now = time.time()
                c.execute(
                    "UPDATE tasks SET status='QUEUED',lease=NULL,lease_until=NULL,owner_node=NULL WHERE status='RUNNING' AND lease_until<?",
                    (now,),
                )
                row = c.execute(
                    "SELECT * FROM tasks WHERE assigned_to=? AND status='RUNNING' AND owner_node=? LIMIT 1",
                    (worker['role'], worker['id']),
                ).fetchone()
                if row:
                    running_task = hub.queue.decode(row)
                queued_for_role = c.execute(
                    "SELECT count(*) FROM tasks WHERE assigned_to=? AND status='QUEUED'",
                    (worker['role'],),
                ).fetchone()[0]

            parent_html = ''
            if running_task and worker['role'] == 'verify':
                target_id = (running_task.get('payload') or {}).get('target_task_id')
                if target_id:
                    try:
                        target_data = hub.queue.get(worker, '/tasks/' + str(target_id))
                        parent_html = f"""<div class="card" style="background:#0c1428">
                          <h3>Tài liệu gốc cần Kiểm chứng (Task {_esc(target_id)})</h3>
                          <pre>{_esc(json.dumps(target_data, ensure_ascii=False, indent=2))}</pre>
                        </div>"""
                    except Exception:
                        pass

            flash_html = f'<div class="flash">{_esc(flash)}</div>' if flash else ''
            err_html = f'<div class="flash err">{_esc(err)}</div>' if err else ''

            if running_task:
                tid = running_task['id']
                lease = running_task['lease']
                rem_min = max(1, round((running_task['lease_until'] - time.time()) / 60))
                payload_pretty = json.dumps(running_task.get('payload') or {}, ensure_ascii=False, indent=2)
                task_section = f"""
                <div class="card">
                  <div class="row" style="justify-content:space-between">
                    <h2 style="margin:0">Nhiệm vụ đang nhận: <code>{_esc(tid[:8])}</code> ({_esc(running_task['kind'])})</h2>
                    <span class="badge warn">Đang giữ Lease (~{rem_min} phút, tự gia hạn mỗi 60s)</span>
                  </div>
                  <label>Đề bài chi tiết (Payload):</label>
                  <pre>{_esc(payload_pretty)}</pre>
                  {parent_html}
                  <hr style="border:none;border-top:1px solid var(--border);margin:16px 0">
                  <h3>Nộp Báo Cáo Kết Quả</h3>
                  <p style="color:var(--muted);font-size:13px">Quy tắc: Chỉ ghi số liệu/quan sát đã kiểm chứng thật. Không tự git push. Điền đầy đủ rồi bấm nút Nộp bên dưới.</p>
                  <form method="post" action="/portal/submit">
                    <input type="hidden" name="csrf" value="{_esc(csrf)}">
                    <input type="hidden" name="task_id" value="{_esc(tid)}">
                    <input type="hidden" name="lease" value="{_esc(lease)}">
                    <label for="outcome">Trạng thái kết quả (outcome)</label>
                    <select id="outcome" name="outcome">
                      <option value="ok">ok — Hoàn thành đạt tiêu chí</option>
                      <option value="PASS">PASS — Đạt kiểm chứng (dành cho Verify)</option>
                      <option value="BLOCKED">BLOCKED — Bị chặn nguồn / thiếu dữ liệu</option>
                      <option value="NEEDS_ACCESS">NEEDS_ACCESS — Cần cấp thêm quyền truy cập</option>
                      <option value="UNSUPPORTED_CAPABILITY">UNSUPPORTED_CAPABILITY — Thiếu công cụ thực thi</option>
                    </select>
                    <label for="summary">Nội dung phân tích / Kết luận chính (summary)</label>
                    <textarea id="summary" name="summary" required placeholder="Trình bày kết quả chi tiết, mốc thời gian, dẫn chứng cụ thể..."></textarea>
                    <label for="sources">Danh sách URL nguồn / Link minh chứng Google Drive (mỗi dòng 1 link)</label>
                    <textarea id="sources" name="sources" style="min-height:68px" placeholder="https://..."></textarea>
                    <label for="lessons">Bài học rút ra (mỗi dòng 1 ý)</label>
                    <textarea id="lessons" name="lessons" style="min-height:68px" placeholder="Nguyên tắc áp dụng được cho các lô tiếp theo..."></textarea>
                    <label for="limitations">Giới hạn trung thực / Điểm chưa quan sát được (mỗi dòng 1 ý)</label>
                    <textarea id="limitations" name="limitations" style="min-height:60px" placeholder="Ghi rõ nếu có phần nào chưa kiểm tra trực tiếp..."></textarea>
                    <label><input type="checkbox" name="next" value="1" checked style="width:auto"> Tự động nhận luôn nhiệm vụ tiếp theo ngay sau khi nộp</label>
                    <div style="margin-top:12px">
                      <button type="submit" class="ok">Nộp Kết Quả &amp; Nhận Việc Mới</button>
                    </div>
                  </form>
                </div>
                <script>
                setInterval(function(){{
                  fetch('/api/tasks/{_esc(tid)}/heartbeat', {{
                    method:'POST',
                    headers:{{'Content-Type':'application/json'}},
                    body:JSON.stringify({{lease:'{_esc(lease)}'}})
                  }}).catch(function(){{}});
                }}, 60000);
                </script>
                """
            else:
                task_section = f"""
                <div class="card">
                  <h2>Sẵn sàng nhận nhiệm vụ ({queued_for_role} việc đang chờ cho vai <code>{_esc(worker['role'])}</code>)</h2>
                  <p style="color:var(--muted)">Bấm nút <b>Nhận Nhiệm Vụ Mới</b> bên dưới để kéo việc từ hàng đợi trung tâm.</p>
                  <form method="post" action="/portal/claim">
                    <input type="hidden" name="csrf" value="{_esc(csrf)}">
                    <label for="capabilities">Công cụ thật sự bạn đang có (cách nhau dấu phẩy)</label>
                    <input id="capabilities" name="capabilities" value="{_esc(worker['role'])},web_search,browser,research,summarize">
                    <div style="margin-top:14px" class="row">
                      <button type="submit">Nhận Nhiệm Vụ Mới (Claim Task)</button>
                      <a class="btn sec" href="/portal">Làm mới trang</a>
                    </div>
                  </form>
                </div>
                """

            body = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sảnh Nhiệm Vụ Muse — {_esc(worker['role'].upper())}</title><style>{BASE_CSS}</style></head><body>
<div class="wrap">
  <div class="card row" style="justify-content:space-between">
    <div>
      <strong>AgentNet Worker Portal</strong> &middot;
      Node: <code>{_esc(worker['id'][:10])}</code> &middot;
      Vai trò hiện tại: <span class="badge ok">{_esc(worker['role'].upper())}</span>
    </div>
    <form method="post" action="/portal/logout" style="margin:0">
      <input type="hidden" name="csrf" value="{_esc(csrf)}">
      <button type="submit" class="sec">Thoát phiên</button>
    </form>
  </div>
  {flash_html}{err_html}
  {task_section}
</div></body></html>"""
            self.send_html(200, body)

        def render_admin_login(self, err: str = ''):
            err_html = f'<div class="flash err">{_esc(err)}</div>' if err else ''
            body = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bảng Chỉ Huy AgentNet — Đăng nhập</title><style>{BASE_CSS}</style></head><body>
<div class="wrap" style="max-width:460px;margin-top:50px">
  <div class="card">
    <h2>Bảng Chỉ Huy Đội Quân Muse</h2>
    {err_html}
    <form method="post" action="/admin/login">
      <label for="admin_key">Mã Quản Trị Chủ Dự Án (Admin Key)</label>
      <input id="admin_key" name="admin_key" type="password" required autofocus>
      <div style="margin-top:14px" class="row">
        <button type="submit">Đăng nhập</button>
        <a class="btn sec" href="/">Về Sảnh Quân Đoàn</a>
      </div>
    </form>
  </div>
</div></body></html>"""
            self.send_html(200, body)

        def render_admin_dashboard(self, adm_tok: str, flash: str = '', new_code: str = ''):
            csrf = _csrf_for(adm_tok)
            base = self.origin_base()
            nodes = hub.registry.status()
            invites = hub.list_invites()
            admin_actor = {'id': 'hub-owner', 'role': 'controller'}
            fleet = hub.queue.get(admin_actor, '/fleet')
            tasks = hub.queue.get(admin_actor, '/tasks?limit=60')

            approved_nodes = [n for n in nodes if n['status'] == 'APPROVED']
            recent_nodes = [n for n in approved_nodes if n.get('registry_heartbeat_age_seconds') is not None and n['registry_heartbeat_age_seconds'] < 300]
            submitted_tasks = [t for t in tasks if t['status'] == 'SUBMITTED']
            queued_tasks = [t for t in tasks if t['status'] == 'QUEUED']
            running_tasks = [t for t in tasks if t['status'] == 'RUNNING']

            flash_html = f'<div class="flash">{_esc(flash)}</div>' if flash else ''
            code_box = ''
            if new_code:
                join_url = f'{base}/j/{_esc(new_code)}'
                sh_cmd = f'curl -fsSL {base}/sh/{_esc(new_code)} | python3'
                prompt_browser = f'Mở {join_url} để tự động nhận vai trò trong đội quân nghiên cứu và bắt đầu nhận nhiệm vụ trên Sảnh Nhiệm Vụ.'
                code_box = f"""<div class="card" style="border-color:var(--ok)">
                  <h3 style="color:#86efac">Link Triệu Tập Đã Sẵn Sàng! (Dán giống nhau cho cả 10–100 tab Muse)</h3>
                  <label>1. Dành cho Muse dùng Trình duyệt (Browser — chỉ cần dán đúng 1 câu này):</label>
                  <pre>{_esc(prompt_browser)}</pre>
                  <label>2. Dành cho Muse có cửa sổ lệnh Bash/Python (1 dòng tự cài CLI):</label>
                  <pre>{_esc(sh_cmd)}</pre>
                </div>"""

            node_rows = []
            for n in nodes[:120]:
                age = n.get('registry_heartbeat_age_seconds')
                age_txt = f'{age}s trước' if age is not None else 'Chưa ping'
                src_badge = 'Web Hub' if n['device_id'] == HUB_DEVICE_TAG else 'Tailscale'
                st_cls = 'ok' if (n['status'] == 'APPROVED' and age is not None and age < 300) else ('warn' if n['status'] == 'APPROVED' else 'err')
                actions = '<i>Chief cố định</i>'
                if n['role'] != 'controller' and n['status'] == 'APPROVED':
                    opts = ''.join(
                        f'<option value="{r}"{" selected" if r == n["role"] else ""}>{r}</option>'
                        for r in WORKER_ROLES
                    )
                    actions = f"""<div class="row">
                      <form method="post" action="/admin/node/role" class="row" style="margin:0">
                        <input type="hidden" name="csrf" value="{_esc(csrf)}">
                        <input type="hidden" name="node_id" value="{_esc(n['id'])}">
                        <select name="role" style="width:115px;padding:4px 6px">{opts}</select>
                        <button type="submit" class="sec" style="padding:5px 10px">Đổi vai</button>
                      </form>
                      <form method="post" action="/admin/node/revoke" style="margin:0">
                        <input type="hidden" name="csrf" value="{_esc(csrf)}">
                        <input type="hidden" name="node_id" value="{_esc(n['id'])}">
                        <button type="submit" class="err" style="padding:5px 10px">Thu hồi</button>
                      </form>
                    </div>"""
                node_rows.append(
                    f"<tr><td><code>{_esc(n['id'][:10])}</code><br><small style='color:var(--muted)'>{src_badge} &middot; {_esc(n['ip'])}</small></td>"
                    f"<td><b>{_esc(n['role'])}</b></td>"
                    f"<td><span class='badge {st_cls}'>{_esc(n['status'])}</span> ({age_txt})</td>"
                    f"<td>{actions}</td></tr>"
                )

            inv_rows = []
            for inv in invites[:10]:
                tgt = ', '.join(f'{k}:{v}' for k, v in inv['targets'].items())
                rem_m = round(inv['remaining_seconds'] / 60)
                btn = ''
                if inv['effective_status'] == 'ACTIVE':
                    btn = f"""<form method="post" action="/admin/invite/revoke" style="margin:0">
                      <input type="hidden" name="csrf" value="{_esc(csrf)}">
                      <input type="hidden" name="invite_id" value="{_esc(inv['id'])}">
                      <button type="submit" class="err" style="padding:4px 10px">Khóa link</button>
                    </form>"""
                inv_rows.append(
                    f"<tr><td><code>{_esc(inv['code_hint'])}</code></td>"
                    f"<td>{inv['used_count']} / {inv['max_uses']}</td>"
                    f"<td>{rem_m} phút ({_esc(inv['effective_status'])})</td>"
                    f"<td>{_esc(tgt)}</td><td>{btn}</td></tr>"
                )

            task_rows = []
            for t in tasks[:30]:
                res = t.get('result') or {}
                outcome = res.get('outcome', '-')
                summary = (res.get('summary') or (t.get('payload') or {}).get('objective') or '')[:160]
                st_cls = 'ok' if t['status'] == 'APPROVED' else ('warn' if t['status'] in ('SUBMITTED', 'RUNNING') else '')
                app_btn = ''
                if t['status'] == 'SUBMITTED' and outcome in ('ok', 'PASS'):
                    app_btn = f"""<form method="post" action="/admin/task/approve" style="margin:0">
                      <input type="hidden" name="csrf" value="{_esc(csrf)}">
                      <input type="hidden" name="task_id" value="{_esc(t['id'])}">
                      <button type="submit" class="ok" style="padding:5px 10px">Duyệt</button>
                    </form>"""
                task_rows.append(
                    f"<tr><td><code>{_esc(t['id'][:8])}</code><br><small style='color:var(--muted)'>{_esc(t['kind'])}</small></td>"
                    f"<td><b>{_esc(t['assigned_to'])}</b></td>"
                    f"<td><span class='badge {st_cls}'>{_esc(t['status'])}</span> ({_esc(outcome)})</td>"
                    f"<td>{_esc(summary)}</td><td>{app_btn}</td></tr>"
                )

            body = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bảng Chỉ Huy Đội Quân Muse — AgentNet Hub</title><style>{BASE_CSS}</style></head><body>
<div class="wrap">
  <div class="row" style="justify-content:space-between;margin-bottom:14px">
    <h1 style="margin:0">Bảng Chỉ Huy Đội Quân Muse</h1>
    <div class="row">
      <a class="btn sec" href="/admin">Làm mới</a>
      <form method="post" action="/admin/logout" style="margin:0">
        <input type="hidden" name="csrf" value="{_esc(csrf)}">
        <button type="submit" class="sec">Đăng xuất</button>
      </form>
    </div>
  </div>
  {flash_html}{code_box}

  <div class="grid">
    <div class="stat"><div style="color:var(--muted);font-size:13px">Tổng Quân Số Đã Duyệt</div><div class="num">{len(approved_nodes)}</div><small style="color:var(--muted)">Hoạt động &lt;5p: {len(recent_nodes)} | Poll Queue &lt;15p: {fleet['active_workers_15m']}</small></div>
    <div class="stat"><div style="color:var(--muted);font-size:13px">Đang Chờ Làm (QUEUED)</div><div class="num">{len(queued_tasks)}</div><small style="color:var(--muted)">Đang chạy (RUNNING): {len(running_tasks)}</small></div>
    <div class="stat"><div style="color:var(--muted);font-size:13px">Chờ Duyệt (SUBMITTED)</div><div class="num">{len(submitted_tasks)}</div><small style="color:var(--muted)">Bấm nút Duyệt ở bảng dưới</small></div>
  </div>

  <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(340px,1fr))">
    <div class="card">
      <h2>1. Tạo Link Triệu Tập Nhanh (1-Click Join)</h2>
      <form method="post" action="/admin/invite/create">
        <input type="hidden" name="csrf" value="{_esc(csrf)}">
        <div class="row">
          <div style="flex:1"><label>Số Muse tối đa</label><input name="max_uses" type="number" value="15" min="1" max="200"></div>
          <div style="flex:1"><label>Hiệu lực (phút)</label><input name="ttl" type="number" value="60" min="5" max="10080"></div>
        </div>
        <label>Cơ cấu đội hình mục tiêu (Hub tự động điền chỗ trống):</label>
        <div class="row">
          <div style="flex:1"><small>Research</small><input name="t_research" type="number" value="5" min="0" max="200"></div>
          <div style="flex:1"><small>Verify</small><input name="t_verify" type="number" value="2" min="0" max="200"></div>
          <div style="flex:1"><small>Engineer</small><input name="t_engineer" type="number" value="2" min="0" max="200"></div>
        </div>
        <div style="margin-top:12px"><button type="submit">Tạo Link Triệu Tập</button></div>
      </form>
      <table style="margin-top:14px">
        <thead><tr><th>Mã</th><th>Đã vào</th><th>Còn lại</th><th>Cơ cấu</th><th></th></tr></thead>
        <tbody>{''.join(inv_rows) or '<tr><td colspan="5">Chưa có mã mời</td></tr>'}</tbody>
      </table>
    </div>

    <div class="card">
      <h2>2. Giao Việc Theo Lô (Batch Dispatch)</h2>
      <form method="post" action="/admin/task/batch">
        <input type="hidden" name="csrf" value="{_esc(csrf)}">
        <div class="row">
          <div style="flex:1">
            <label>Giao cho đội</label>
            <select name="assigned_to">
              <option value="research">research</option>
              <option value="verify">verify</option>
              <option value="engineer">engineer</option>
            </select>
          </div>
          <div style="flex:1"><label>Phân loại (kind)</label><input name="kind" value="research_topic"></div>
        </div>
        <label>Danh sách nhiệm vụ / URL (mỗi dòng = 1 task độc lập cho 1 Muse nhận)</label>
        <textarea name="objectives" placeholder="Phân tích hook 3s và nhịp dựng video https://...\nKhảo sát 10 chủ đề Visual Essay ngách khoa học thú vị..."></textarea>
        <label><input type="checkbox" name="auto_verify" value="1" checked style="width:auto"> Tự động chuyển sang đội Verify kiểm chứng ngay khi nộp xong</label>
        <div style="margin-top:12px"><button type="submit" class="ok">Phát Lệnh Cho Đội Quân</button></div>
      </form>
    </div>
  </div>

  <div class="card">
    <h2>3. Danh Sách Quân Số ({len(nodes)} node)</h2>
    <table>
      <thead><tr><th>Node / Kênh</th><th>Vai trò</th><th>Trạng thái</th><th>Điều khiển nhanh</th></tr></thead>
      <tbody>{''.join(node_rows) or '<tr><td colspan="4">Chưa có node</td></tr>'}</tbody>
    </table>
  </div>

  <div class="card">
    <div class="row" style="justify-content:space-between;align-items:center">
      <h2 style="margin:0">4. Hàng Đợi Nhiệm Vụ Gần Nhất</h2>
      <a class="btn" style="background:#16a34a" href="/ggmap/admin">Nhánh Rà Google Maps Long Biên (/ggmap/admin)</a>
    </div>
    <table>
      <thead><tr><th>Task</th><th>Đội</th><th>Trạng thái</th><th>Tóm tắt / Mục tiêu</th><th>Duyệt</th></tr></thead>
      <tbody>{''.join(task_rows) or '<tr><td colspan="5">Hàng đợi trống</td></tr>'}</tbody>
    </table>
  </div>
</div></body></html>"""
            self.send_html(200, body)

    return HubHTTPHandler


def _build_cli_bootstrap_script(base_url: str, invite_code: str, role: str) -> str:
    return f'''import json, os, pathlib, urllib.request
base = {json.dumps(base_url)}
body = {{"code": {json.dumps(invite_code)}}}
if {json.dumps(role)}:
    body["role"] = {json.dumps(role)}
req = urllib.request.Request(base + "/api/join", data=json.dumps(body).encode(), headers={{"Content-Type": "application/json"}})
with urllib.request.urlopen(req, timeout=15) as r:
    joined = json.load(r)
state = pathlib.Path.home() / ".agentnet-corner"
state.mkdir(parents=True, exist_ok=True)
try: os.chmod(state, 0o700)
except OSError: pass
cfg_path = state / "hub_worker.json"
fd = os.open(cfg_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    json.dump({{"hub_url": base, **joined}}, f)
cli = state / "hub_cli.py"
cli.write_text("""import json, pathlib, sys, urllib.request
cfg = json.loads((pathlib.Path.home() / '.agentnet-corner' / 'hub_worker.json').read_text())
def call(method, path, payload=None):
    req = urllib.request.Request(
        cfg['hub_url'] + path,
        data=(json.dumps(payload).encode() if payload is not None else None),
        headers={{'Authorization': 'Bearer ' + cfg['token'], 'Content-Type': 'application/json'}},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)
cmd = sys.argv[1] if len(sys.argv) > 1 else 'me'
if cmd == 'me': print(json.dumps(call('GET', '/api/me'), indent=2))
elif cmd == 'claim': print(json.dumps(call('POST', '/api/claim', {{'capabilities': sys.argv[2:] or [cfg['role']]}}), ensure_ascii=False, indent=2))
elif cmd == 'get': print(json.dumps(call('GET', '/api/tasks/' + sys.argv[2]), ensure_ascii=False, indent=2))
elif cmd == 'heartbeat': print(json.dumps(call('POST', f'/api/tasks/{{sys.argv[2]}}/heartbeat', {{'lease': sys.argv[3]}})))
elif cmd == 'submit': print(json.dumps(call('POST', f'/api/tasks/{{sys.argv[2]}}/result', {{'lease': sys.argv[3], 'result': json.loads(sys.argv[4])}})))
""")
print(json.dumps({{"joined": True, "node_id": joined["node_id"], "role": joined["role"], "cli": str(cli)}}))
'''
