"""Đọc kết quả task Muse trên Hub (SSH, chỉ đọc SQLite). Dùng chung cho sfx/clip/ảnh.

python studio/hub_results.py --kind sfx_candidates            # bảng trạng thái
python studio/hub_results.py --kind sfx_candidates --json out.json   # xuất kết quả đã nộp
"""
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, r"D:\0.1_FACE_BOOK\macro-tool")

REMOTE = r'''python3 - "$KIND" <<'PY'
import json, sqlite3, sys
kind = sys.argv[1]
c = sqlite3.connect('file:/opt/agentnet-corner/state/research.sqlite3?mode=ro', uri=True)
c.row_factory = sqlite3.Row
rows = [dict(r) for r in c.execute(
    "SELECT id, status, owner_node, payload, result, created_at, completed_at FROM tasks WHERE kind=? ORDER BY created_at", (kind,))]
print(json.dumps(rows, ensure_ascii=False))
PY'''


def fetch(kind: str) -> list[dict]:
    from vps_ssh_helper import connect_vps_ssh

    ssh = connect_vps_ssh(timeout=20)
    try:
        _, out, err = ssh.exec_command(REMOTE.replace('"$KIND"', json.dumps(kind)))
        raw = out.read().decode("utf-8", errors="replace").strip()
        if not raw:
            raise RuntimeError(err.read().decode("utf-8", errors="replace"))
        rows = json.loads(raw)
    finally:
        ssh.close()
    for r in rows:
        r["payload"] = json.loads(r["payload"] or "{}")
        r["result"] = json.loads(r["result"]) if r.get("result") else None
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True)
    ap.add_argument("--json", help="ghi toàn bộ hàng (kể cả result) ra file")
    a = ap.parse_args()
    rows = fetch(a.kind)
    for r in rows:
        obj = (r["payload"].get("objective") or "")[:70]
        print(f"{r['status']:<10} {(r['owner_node'] or '-')[:8]:<9} {obj}")
    print(f"Tổng {len(rows)} task · nộp xong {sum(1 for r in rows if r['status'] in ('SUBMITTED', 'APPROVED'))}")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
