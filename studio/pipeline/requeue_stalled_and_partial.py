"""Self-healing Hub reconciler (truy vấn trực tiếp toàn bộ SQLite trên VPS, không bị giới hạn 200 task):
- Tự động giải phóng mọi task RUNNING quá hạn (> 25 phút với vẽ/viết, > 30 phút với dựng video) về lại QUEUED
  để không bao giờ xảy ra cảnh 1 lô bị treo 2-9 tiếng chặn cả bộ phim về đích!
- Tuyệt đối KHÔNG ghi lệnh shell hay token vào payload trên /portal (tránh bộ lọc an toàn Muse).
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"D:\0.1_FACE_BOOK\macro-tool")
from vps_ssh_helper import connect_vps_ssh  # noqa: E402


def main() -> int:
    remote = r"""
import sys, time
from pathlib import Path
sys.path.insert(0, '/opt/agentnet-corner')
from research_queue import ResearchQueue

rq = ResearchQueue(Path('/opt/agentnet-corner'))
now = time.time()
released = []
with rq.db() as db:
    rows = db.execute(
        "SELECT id, kind, dedup, owner_node, started_at, created_at FROM tasks "
        "WHERE status='RUNNING' AND kind IN ('muse_draw_images', 'muse_make_videos', 'muse_write_script', 'muse_fix_script')"
    ).fetchall()
    for r in rows:
        started = float(r['started_at'] or r['created_at'] or now)
        age_min = (now - started) / 60.0
        limit_min = 30.0 if r['kind'] == 'muse_make_videos' else 25.0
        if age_min >= limit_min:
            db.execute(
                "UPDATE tasks SET status='QUEUED', owner_node=NULL, lease=NULL, lease_until=0, started_at=NULL WHERE id=?",
                (r['id'],),
            )
            released.append((r['kind'], r['dedup'], round(age_min, 1)))
    db.commit()
print(f"STALLED_RELEASED={len(released)}", released[:12])
"""
    ssh = connect_vps_ssh(timeout=20)
    try:
        inp, o, e = ssh.exec_command("python3 -")
        inp.write(remote)
        inp.flush()
        inp.channel.shutdown_write()
        out = o.read().decode("utf-8", "replace").strip()
        err = e.read().decode("utf-8", "replace").strip()
        if out:
            print(out, flush=True)
        if err:
            print("ERR:", err, flush=True)
    finally:
        ssh.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
