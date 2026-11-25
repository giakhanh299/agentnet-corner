"""Đồng bộ 1 chiều AI_SYSTEM/RAG (bản chạy thật) -> bridges/ (bản lưu trong git).

- Chỉ chép danh sách file cố định, không bao giờ chép ngược.
- Tự bỏ mã Telegram ghi cứng trong muse_mtproto_listener.py (L065).
- Quét chuỗi nghi secret; phát hiện thì DỪNG, không ghi file đó.

Chạy:  python bridges/sync_from_rag.py          (ghi thật)
       python bridges/sync_from_rag.py --check  (chỉ báo khác biệt)
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

RAG = Path(r"D:\AI_AGENT\AI_SYSTEM\RAG")
HERE = Path(__file__).resolve().parent
FILES = [
    "muse_dispatch.py",
    "muse_telegram_council.py",
    "muse_mtproto_listener.py",
    "file_exchange.py",
    "qc_engine.py",
    "MO_PHONG_HOP_MUSE_TELEGRAM.cmd",
    "tests/test_muse_telegram_council.py",
]
SECRET_RE = re.compile(
    r"adm_[A-Za-z0-9_-]{20,}|fleet_[A-Za-z0-9_-]{20,}|hubw_[A-Za-z0-9_-]{16,}"
    r"|MUSE-[A-Z0-9]{12,}|(?<![0-9])[0-9]{8,12}:AA[A-Za-z0-9_-]{30,}"
)
# Fixture giả trong test được phép
ALLOWED_FAKE = ("1234567890:AAH_testTokenSecret", "MUSE-ABCDEFGH123456")
HARDCODED_TG = re.compile(r'(?:client\s*=\s*)?TelegramClient\(SESSION_PATH,\s*\d+,\s*"[0-9a-f]{32}"\)')
TG_REPLACEMENT = (
    "# L065: api_id/api_hash đọc từ telegram_council.json (ngoài git) hoặc biến môi trường,\n"
    "    # không ghi cứng trong mã nguồn. Đăng ký cặp riêng tại my.telegram.org.\n"
    '    api_id = int(cfg.get("api_id") or os.environ.get("TG_API_ID") or 0)\n'
    '    api_hash = str(cfg.get("api_hash") or os.environ.get("TG_API_HASH") or "").strip()\n'
    "    if not api_id or not api_hash:\n"
    '        raise RuntimeError("Thiếu api_id/api_hash trong telegram_council.json hoặc TG_API_ID/TG_API_HASH")\n'
    "    client = TelegramClient(SESSION_PATH, api_id, api_hash)"
)


def sanitize(name: str, text: str) -> str:
    if name == "muse_mtproto_listener.py":
        text = HARDCODED_TG.sub(TG_REPLACEMENT, text)
    return text


def find_secrets(text: str) -> list[str]:
    hits = []
    for m in SECRET_RE.finditer(text):
        s = m.group(0)
        if not any(s.startswith(f) or f.startswith(s) for f in ALLOWED_FAKE):
            hits.append(s[:10] + "…")
    if HARDCODED_TG.search(text):
        hits.append("TelegramClient(api_hash ghi cứng)")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="chỉ báo khác biệt, không ghi")
    args = ap.parse_args()

    changed, blocked = [], []
    for rel in FILES:
        src = RAG / rel
        dst = HERE / rel
        if not src.is_file():
            print(f"THIẾU   {rel} (không có trong RAG)")
            continue
        text = sanitize(Path(rel).name, src.read_text(encoding="utf-8"))
        hits = find_secrets(text)
        if hits:
            blocked.append(rel)
            print(f"CHẶN    {rel}: nghi secret {hits}")
            continue
        new = text.encode("utf-8")
        old = dst.read_bytes() if dst.is_file() else b""
        if hashlib.sha256(new).digest() == hashlib.sha256(old.replace(b"\r\n", b"\n")).digest() or new == old:
            print(f"GIỐNG   {rel}")
            continue
        changed.append(rel)
        print(f"KHÁC    {rel}")
        if not args.check:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(new)

    print(f"\nTổng: {len(changed)} file {'cần cập nhật' if args.check else 'đã cập nhật'}, {len(blocked)} file bị chặn.")
    if changed and not args.check:
        print("Tiếp theo: chạy test bridges rồi git commit.")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
