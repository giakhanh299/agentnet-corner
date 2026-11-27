"""Self-healing Hub reconciler:
1) Requeue muse_draw_images tasks stuck RUNNING > 30 min with no submission.
2) For any SUBMITTED muse_make_videos task whose local E:\\MUSE_MEDIA_STUDIO folder still has <11 verified .mp4 clips,
   reset it back to QUEUED with the exact list of missing scene_XX.mp4 clips (and explicit warning against submitting .jpg).
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, r"D:\0.1_FACE_BOOK\macro-tool")
from vps_ssh_helper import connect_vps_ssh  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
import process_muse_pipeline as pm  # noqa: E402


def main():
    tasks = pm.fetch_hub_tasks()
    now = time.time()

    requeue_draw_ids = []
    requeue_vid_updates = []
    bad_owners = {}

    for t in tasks:
        kind = t.get("kind")
        st = t.get("status")
        if kind in ("muse_draw_images", "muse_make_videos") and st == "RUNNING":
            started = float(t.get("started_at") or t.get("created_at") or now)
            age_min = (now - started) / 60.0
            limit = 22.0 if kind == "muse_draw_images" else 25.0
            if age_min >= limit:
                requeue_draw_ids.append((t["id"], (t.get("owner_node") or "")[:8], round(age_min, 1), (t.get("payload") or {}).get("objective", "")[:45]))
        elif kind == "muse_make_videos" and st == "SUBMITTED":
            obj = (t.get("payload") or {}).get("objective", "")
            m = re.match(r"\[([a-z0-9_]+)\]", obj)
            if not m:
                continue
            slug = m.group(1)
            found = pm.find_spec(slug)
            if not found:
                continue
            ch_key, spec_path, spec_url = found
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            n_scenes = len(spec.get("scenes", []))
            clip_dir = pm.MEDIA_ROOT / ch_key / slug / "02_muse_clips"
            missing = [i for i in range(1, n_scenes + 1) if not pm.verify_mp4(clip_dir / f"scene_{i:02d}.mp4")]
            if missing:
                own = (t.get("owner_node") or "")[:8]
                bad_owners[own] = bad_owners.get(own, 0) + 1
                old_pay = t.get("payload") or {}
                excl = list(dict.fromkeys((old_pay.get("excluded_nodes") or []) + ([t["owner_node"]] if t.get("owner_node") else [])))
                title = spec.get("title", slug)
                series = spec.get("series", ch_key)
                sc_list = ", ".join(f"scene_{i:02d}" for i in missing)
                new_payload = {
                    "excluded_nodes": excl,
                    "objective": f"[{slug}] MUSE TẠO VIDEO 9:16 ({len(missing)} clip .mp4 CÒN THIẾU): '{title}' ({series}) — tạo {sc_list}.mp4 + up /media-upload.",
                    "acceptance_criteria": (
                        f"BẮT BUỘC TẠO FILE VIDEO .MP4 (TUYỆT ĐỐI KHÔNG NỘP LẠI ẢNH .JPG!). "
                        f"Tập '{title}' ({series}, mã {slug}) còn thiếu {len(missing)} clip video: {sc_list}. "
                        f"BƯỚC 1: Đọc kịch bản tại {spec_url}. "
                        f"BƯỚC 2: Tải ảnh đầu vào tại https://muse.alltool.pro/media/{slug}/ ({sc_list}.jpg). "
                        f"BƯỚC 3: Dùng công cụ tạo video AI (Image-to-Video) của chính Muse biến {len(missing)} ảnh đó thành {len(missing)} clip dọc 9:16 (.mp4, 5s/clip, chuyển động mượt, KHÔNG chữ/watermark). "
                        f"BƯỚC 4: Nén thành .zip (đặt tên {sc_list}.mp4) và upload qua trình duyệt tại https://muse.alltool.pro/media-upload?slug={slug} (tích giải nén zip -> Upload Media). "
                        f"BƯỚC 5: Nộp JSON chứa mảng \"videos\" với link .mp4 thật (KHÔNG nộp ảnh .jpg). Nếu tài khoản hết hạn mức tạo video, chọn outcome=BLOCKED để Muse khác nhận!"
                    ),
                }
                requeue_vid_updates.append({"id": t["id"], "slug": slug, "missing": missing, "prev_owner": own, "payload": new_payload})

    print("STALLED_DRAW_TO_REQUEUE:", len(requeue_draw_ids), requeue_draw_ids)
    print("PARTIAL_OR_FAKE_VID_TO_REQUEUE:", len(requeue_vid_updates), [(x["slug"], len(x["missing"]), x["prev_owner"]) for x in requeue_vid_updates])
    print("OWNERS_WITH_INCOMPLETE_VID:", bad_owners)

    if not requeue_draw_ids and not requeue_vid_updates:
        return

    import base64
    data_b64 = base64.b64encode(json.dumps({
        "draw_ids": [x[0] for x in requeue_draw_ids],
        "vid_updates": requeue_vid_updates,
    }, ensure_ascii=False).encode("utf-8")).decode("ascii")

    remote = f"""
import base64, json, sqlite3
from pathlib import Path
cfg = json.loads(base64.b64decode({data_b64!r}).decode('utf-8'))
db = Path('/opt/agentnet-corner/state/research.sqlite3')
con = sqlite3.connect(str(db))
for tid in cfg['draw_ids']:
    con.execute("UPDATE tasks SET status='QUEUED', owner_node=NULL, lease=NULL, lease_until=NULL, started_at=NULL WHERE id=?", (tid,))
for item in cfg['vid_updates']:
    con.execute(
        "UPDATE tasks SET status='QUEUED', owner_node=NULL, lease=NULL, lease_until=NULL, started_at=NULL, completed_at=NULL, result=NULL, payload=? WHERE id=?",
        (json.dumps(item['payload'], ensure_ascii=False), item['id']),
    )
con.commit()
print('REQUEUED_OK: draw=', len(cfg['draw_ids']), 'vid=', len(cfg['vid_updates']))
"""
    ssh = connect_vps_ssh(timeout=20)
    try:
        inp, o, e = ssh.exec_command("python3 -")
        inp.write(remote)
        inp.flush()
        inp.channel.shutdown_write()
        print(o.read().decode("utf-8", "replace").strip(), e.read().decode("utf-8", "replace").strip())
    finally:
        ssh.close()


if __name__ == "__main__":
    main()
