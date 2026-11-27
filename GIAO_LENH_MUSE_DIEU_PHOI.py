"""Công cụ 1 dòng giao lệnh thẳng cho MUSE ĐIỀU PHỐI TỔNG (Chief Coordinator).

Cách dùng:
  python GIAO_LENH_MUSE_DIEU_PHOI.py "Làm thêm 5 tập Phim Ma dân gian nhịp nhanh và chấm điểm lại 10 tập mới nhất"
  python GIAO_LENH_MUSE_DIEU_PHOI.py --status
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

HUB_BASE = "https://muse.alltool.pro"


def get_token() -> str:
    return (Path(os.environ["LOCALAPPDATA"]) / "MuseLoginHelper" / "hub_invite.txt").read_text("utf-8").strip()


def main() -> int:
    tok = get_token()
    if len(sys.argv) < 2 or sys.argv[1] == "--status":
        req = urllib.request.Request(f"{HUB_BASE}/api/chief/inbox?token={tok}", headers={"User-Agent": "ChiefCLI/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            snap = json.loads(r.read().decode("utf-8"))
        print(json.dumps({
            "chief_portal_url": f"{HUB_BASE}/chief?token=<HUB_INVITE_TOKEN>",
            "role_nodes": snap.get("role_nodes"),
            "scores_summary": snap.get("scores_summary"),
            "pending_commands": len(snap.get("pending_commands", [])),
            "recent_commands": snap.get("recent_commands", [])[:5],
            "recent_scores": snap.get("recent_scores", [])[:5],
        }, ensure_ascii=False, indent=2))
        return 0

    cmd_text = " ".join(sys.argv[1:]).strip()
    payload = json.dumps({"source": "owner_cli", "command_text": cmd_text}).encode("utf-8")
    req = urllib.request.Request(
        f"{HUB_BASE}/api/chief/command?token={tok}",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "ChiefCLI/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode("utf-8"))
    print("ĐÃ GỬI LỆNH CHO MUSE ĐIỀU PHỐI TỔNG:", json.dumps(resp, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
