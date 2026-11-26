import sys
sys.path.insert(0, r"D:\0.1_FACE_BOOK\macro-tool")
from vps_ssh_helper import connect_vps_ssh

remote = """
import sqlite3
con = sqlite3.connect('/opt/agentnet-corner/state/research.sqlite3')
rows = con.execute("SELECT id, kind, status, payload FROM tasks WHERE status='QUEUED'").fetchall()
for i, (tid, kind, st, pay) in enumerate(rows):
    if '[ep11_' in pay:
        con.execute('UPDATE tasks SET created_at = 1000 + ? WHERE id = ?', (i, tid))
    elif any(f'[v0{n}_' in pay for n in range(25, 35)) and kind == 'muse_make_videos':
        con.execute('UPDATE tasks SET created_at = 2000 + ? WHERE id = ?', (i, tid))
    elif '[k1_srt_' in pay:
        con.execute('UPDATE tasks SET created_at = 3000 + ? WHERE id = ?', (i, tid))
    elif '[v0' in pay:
        con.execute('UPDATE tasks SET created_at = 4000 + ? WHERE id = ?', (i, tid))
con.commit()
q = con.execute("SELECT kind, status, COUNT(*) FROM tasks GROUP BY kind, status").fetchall()
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
