"""Always prioritize muse_make_videos (finishing episodes that already have 11 images drawn!)
ahead of muse_draw_images, ordered by user channel priority:
1) muse_make_videos: Phim Ma (KENH_005) -> Tập Làm Content (KENH_008) -> Tiền Và Đời SRT (KENH_001) -> Kiếm Hiệp (KENH_002)
2) muse_draw_images: Phim Ma -> Tập Làm Content -> Tiền Và Đời SRT -> Kiếm Hiệp
"""
import sys
sys.path.insert(0, r"D:\0.1_FACE_BOOK\macro-tool")
from vps_ssh_helper import connect_vps_ssh

remote = """
import sqlite3
con = sqlite3.connect('/opt/agentnet-corner/state/research.sqlite3')
rows = con.execute("SELECT id, kind, status, payload FROM tasks WHERE status='QUEUED'").fetchall()
for i, (tid, kind, st, pay) in enumerate(rows):
    if kind == 'muse_make_videos':
        if '[ep' in pay:
            base = 1000
        elif '[v0' in pay:
            base = 1500
        elif '[k1_srt_' in pay:
            base = 2000
        else:
            base = 2500
    else:
        if '[ep' in pay:
            base = 5000
        elif '[v0' in pay:
            base = 5500
        elif '[k1_srt_' in pay:
            base = 6000
        else:
            base = 6500
    con.execute('UPDATE tasks SET created_at = ? WHERE id = ?', (base + i, tid))
con.commit()
q = con.execute("SELECT kind, status, COUNT(*) FROM tasks WHERE kind IN ('muse_draw_images','muse_make_videos') GROUP BY kind, status").fetchall()
print('HUB_QUEUE_NOW:', q)
"""
ssh = connect_vps_ssh(timeout=20)
try:
    inp, o, _ = ssh.exec_command("python3 -")
    inp.write(remote)
    inp.flush()
    inp.channel.shutdown_write()
    print(o.read().decode("utf-8", "replace").strip())
finally:
    ssh.close()
