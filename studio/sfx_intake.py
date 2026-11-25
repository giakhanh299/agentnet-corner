"""Nhận SFX do Muse tìm về -> kiểm -> chuẩn hóa -> đưa vào thư viện assets/sfx/.

Luồng:
  Hub (kind=sfx_candidates) -> lấy JSON {"sounds":[...]} trong result
  -> chặn giấy phép không rõ -> tải file (link share/direct) -> ffprobe kiểm có audio, độ dài
  -> cắt ≤ 30s, chuẩn -20 LUFS / -1 dBTP, xuất .ogg 48 kHz -> assets/sfx/<category>/<slug>.ogg
  -> ghi assets/sfx/manifest.json (nguồn, giấy phép, tác giả, sha256, độ dài, task id, điểm).
Tiếng mới trùng slug sẽ thay bản cũ nếu điểm (score) không thấp hơn (giữ lịch sử trong git).

python studio/sfx_intake.py --from-hub            # lấy kết quả mới trên Hub
python studio/sfx_intake.py --from-json rows.json # từ file xuất bởi hub_results.py
python studio/sfx_intake.py --from-hub --dry-run  # chỉ báo, không tải
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

REPO = Path(__file__).resolve().parent.parent
LIB = REPO / "assets" / "sfx"
MANIFEST = LIB / "manifest.json"
TZ = timezone(timedelta(hours=7))

ALLOWED_LICENSES = {
    "cc0": "CC0-1.0",
    "public domain": "CC0-1.0",
    "cc-by": "CC-BY-4.0",
    "cc by": "CC-BY-4.0",
    "pixabay": "Pixabay-Content-License",
    "mixkit": "Mixkit-Free-License",
}
BLOCKED_HINTS = ("bbc", "youtube", "non-commercial", "noncommercial", "-nc", " nc ", "unknown", "không rõ")
MAX_DOWNLOAD = 25 * 1024 * 1024
MAX_SECONDS = 30.0
MIN_SECONDS = 0.3
MAX_OUT_BYTES = 1_000_000
CATEGORIES = {
    "footsteps", "rain", "leaves_wind", "wood_creak", "water", "night_creatures",
    "fire_lamp", "human_eerie", "horror_stinger", "folk_oneshot", "misc",
}


def slugify(text: str) -> str:
    s = unicodedata.normalize("NFKD", (text or "").replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:48] or "sfx"


def normalize_license(raw: str) -> str | None:
    low = f" {(raw or '').lower()} "
    if any(h in low for h in BLOCKED_HINTS):
        return None
    for key, canon in ALLOWED_LICENSES.items():
        if key in low:
            return canon
    return None


def _find_sounds(obj) -> list[dict]:
    if isinstance(obj, dict):
        if isinstance(obj.get("sounds"), list):
            return obj["sounds"]
        for v in obj.values():
            found = _find_sounds(v)
            if found:
                return found
    return []


def extract_sounds(result: dict | None) -> list[dict]:
    """Lấy danh sách sounds từ result của Muse (field 'sounds' hoặc khối JSON trong summary, kể cả lồng trong result)."""
    if not result:
        return []
    found = _find_sounds(result)
    if found:
        return found
    texts = [str(result.get(k) or "") for k in ("summary", "report", "content")]
    for txt in texts:
        stripped = txt.strip()
        if stripped.startswith("{"):
            try:
                found = _find_sounds(json.loads(stripped))
                if found:
                    return found
            except json.JSONDecodeError:
                pass
        for m in re.finditer(r"\{[\s\S]*?\"sounds\"\s*:\s*\[", txt):
            start = m.start()
            depth = 0
            for i in range(start, len(txt)):
                if txt[i] == "{":
                    depth += 1
                elif txt[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            found = _find_sounds(json.loads(txt[start:i + 1]))
                            if found:
                                return found
                        except json.JSONDecodeError:
                            pass
                        break
    return []


def download(url: str, dest: Path) -> Path:
    parts = urlsplit(url)
    if parts.scheme == "file":
        src = Path(unquote(parts.path.lstrip("/")) if ":" in parts.path else unquote(parts.path))
        shutil.copyfile(src, dest)
        return dest
    if parts.scheme not in ("http", "https"):
        raise ValueError(f"scheme không hỗ trợ: {parts.scheme}")
    req = Request(url, headers={"User-Agent": "AgentNet-SFX-Intake/1.0"})
    with urlopen(req, timeout=60) as r, dest.open("wb") as f:
        total = 0
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_DOWNLOAD:
                raise ValueError("file tải về quá lớn (> 25 MB)")
            f.write(chunk)
    return dest


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,channels,sample_rate",
         "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    data = json.loads(out.stdout or "{}")
    audio = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    return {"has_audio": bool(audio), "duration": float((data.get("format") or {}).get("duration") or 0)}


def normalize_to_ogg(src: Path, dst: Path) -> dict:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-t", str(MAX_SECONDS), "-vn",
        "-af", "silenceremove=start_periods=1:start_threshold=-55dB,loudnorm=I=-20:TP=-1:LRA=11,afade=t=in:d=0.02",
        "-ar", "48000", "-c:a", "libvorbis", "-q:a", "4", str(dst),
    ]
    subprocess.run(cmd, check=True)
    info = probe(dst)
    return {"duration_s": round(info["duration"], 2), "bytes": dst.stat().st_size}


def load_manifest() -> dict:
    if MANIFEST.is_file():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"version": 1, "sounds": {}}


def save_manifest(m: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    m["updated_at"] = datetime.now(TZ).isoformat(timespec="seconds")
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


FREESOUND_PAGE = re.compile(r"^https://freesound\.org/people/[^/]+/sounds/\d+/?$")
FREESOUND_PREVIEW = re.compile(r"https://cdn\.freesound\.org/previews/\d+/\d+_\d+-(?:lq|hq)\.mp3")
MIXKIT_PAIR = re.compile(
    r'data-audio-player-preview-url-value="(https://assets\.mixkit\.co/[^"]+\.mp3)"'
    r'[\s\S]{0,1600}?<h2 class="item-grid-card__title">\s*([^<]+?)\s*</h2>'
)
_MIXKIT_CACHE: dict[str, dict[str, str]] = {}


def _resolve_mixkit(page: str, name: str) -> str:
    if not page.startswith("https://mixkit.co/free-sound-effects/"):
        return ""
    if page not in _MIXKIT_CACHE:
        try:
            html = urlopen(Request(page, headers={"User-Agent": "Mozilla/5.0"}), timeout=25).read().decode("utf-8", "replace")
            _MIXKIT_CACHE[page] = {
                re.sub(r"\s+", " ", title).strip().lower(): u
                for u, title in MIXKIT_PAIR.findall(html)
            }
        except Exception:
            _MIXKIT_CACHE[page] = {}
    key = re.sub(r"\s+", " ", name).strip().lower()
    return _MIXKIT_CACHE[page].get(key, "")


def resolve_download(snd: dict) -> str:
    """Link tải: ưu tiên download_url Muse gửi; nếu trống thì lấy bản preview công khai cùng giấy phép
    từ trang Freesound (-hq/-lq) hoặc Mixkit (assets.mixkit.co). Nguồn chặn bot (Pixabay 403) để trống."""
    url = str(snd.get("download_url") or "").strip()
    if url:
        return url
    page = str(snd.get("source_page_url") or "").strip()
    name = str(snd.get("name") or snd.get("title") or "").strip()
    if page.startswith("https://mixkit.co/free-sound-effects/"):
        return _resolve_mixkit(page, name)
    if not FREESOUND_PAGE.match(page):
        return ""
    try:
        req = Request(page, headers={"User-Agent": "AgentNet-SFX-Intake/1.0"})
        html = urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception:
        return ""
    m = FREESOUND_PREVIEW.search(html)
    if not m:
        return ""
    lq = m.group(0).replace("-hq.mp3", "-lq.mp3")
    hq = lq.replace("-lq.mp3", "-hq.mp3")
    for cand in (hq, lq):
        try:
            with urlopen(Request(cand, method="HEAD", headers={"User-Agent": "AgentNet-SFX-Intake/1.0"}), timeout=20) as r:
                if r.status == 200:
                    return cand
        except Exception:
            continue
    return ""


def ingest_sound(snd: dict, task_id: str, manifest: dict, dry_run: bool = False, default_cat: str = "misc") -> tuple[str, str]:
    name = str(snd.get("name") or snd.get("title") or "").strip()
    cat = re.sub(r"[^a-z_]", "_", str(snd.get("category") or "").strip().lower())
    cat = cat if cat in CATEGORIES else (default_cat if default_cat in CATEGORIES else "misc")
    lic = normalize_license(str(snd.get("license") or ""))
    if not name:
        return "SKIP", "thiếu tên"
    if not lic:
        return "REJECT", f"giấy phép không hợp lệ: {snd.get('license')!r}"
    if lic == "CC-BY-4.0" and not str(snd.get("author") or "").strip():
        return "REJECT", "CC-BY nhưng thiếu tác giả"
    url = resolve_download(snd)
    if not url:
        return "PENDING", "chưa có link tải (chỉ có trang nguồn)"
    slug = slugify(name)
    key = f"{cat}/{slug}"
    score = float(snd.get("score") or 0)
    old = manifest["sounds"].get(key)
    if old and old.get("task_id") == task_id and old.get("download_url") == url and (LIB / old["file"]).is_file():
        return "SAME", f"{key} đã nhận từ task này"
    if old and float(old.get("score") or 0) > score:
        return "KEEP_OLD", f"{key} đã có bản điểm cao hơn"
    if dry_run:
        return "WOULD_ADD", key
    with tempfile.TemporaryDirectory() as td:
        raw = download(url, Path(td) / "raw.bin")
        info = probe(raw)
        if not info["has_audio"]:
            return "REJECT", "file không có audio"
        if info["duration"] < MIN_SECONDS:
            return "REJECT", f"quá ngắn ({info['duration']:.2f}s)"
        dst = LIB / cat / f"{slug}.ogg"
        out = normalize_to_ogg(raw, dst)
        if out["bytes"] > MAX_OUT_BYTES:
            dst.unlink(missing_ok=True)
            return "REJECT", f"sau chuẩn hóa vẫn > 1 MB ({out['bytes']} B)"
        sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    manifest["sounds"][key] = {
        "file": f"{cat}/{slug}.ogg",
        "name": name,
        "category": cat,
        "tags": [str(t) for t in (snd.get("tags") or [])][:12],
        "license": lic,
        "author": str(snd.get("author") or ""),
        "source_page_url": str(snd.get("source_page_url") or ""),
        "download_url": url,
        "fit_note": str(snd.get("fit_note") or "")[:300],
        "duration_s": out["duration_s"],
        "sha256": sha,
        "score": score,
        "uses": int(old.get("uses", 0)) if old else 0,
        "task_id": task_id,
        "added_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "replaced": bool(old),
    }
    return ("REPLACED" if old else "ADDED"), key


def run(rows: list[dict], dry_run: bool = False) -> dict:
    manifest = load_manifest()
    stats: dict[str, int] = {}
    for row in rows:
        if row.get("status") not in ("SUBMITTED", "APPROVED"):
            continue
        sounds = extract_sounds(row.get("result"))
        if not sounds:
            print(f"[{row['id'][:8]}] không thấy JSON sounds trong kết quả")
            stats["NO_JSON"] = stats.get("NO_JSON", 0) + 1
            continue
        tag = re.match(r"\s*\[([a-z_]+)\]", str((row.get("payload") or {}).get("objective") or ""))
        default_cat = tag.group(1) if tag else "misc"
        for snd in sounds:
            try:
                status, detail = ingest_sound(snd, row["id"], manifest, dry_run=dry_run, default_cat=default_cat)
            except Exception as exc:  # tải lỗi, ffmpeg lỗi...
                status, detail = "ERROR", f"{type(exc).__name__}: {str(exc)[:120]}"
            stats[status] = stats.get(status, 0) + 1
            label = str(snd.get("name") or snd.get("title") or "")
            print(f"[{row['id'][:8]}] {status:<9} {label[:40]:<40} {detail}")
    if not dry_run:
        save_manifest(manifest)
    print("Tổng:", stats)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-hub", action="store_true")
    src.add_argument("--from-json", type=Path)
    ap.add_argument("--kind", default="sfx_candidates")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.from_hub:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from hub_results import fetch
        rows = fetch(a.kind)
    else:
        rows = json.loads(a.from_json.read_text(encoding="utf-8"))
    run(rows, dry_run=a.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
