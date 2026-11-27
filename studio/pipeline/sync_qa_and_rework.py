"""Đồng bộ hai chiều giữa ổ E:\\MUSE_MEDIA_STUDIO và Hội Đồng Chấm Điểm Muse (qa_critic) + Muse Điều Phối (chief).

1. Đóng gói bằng chứng thật (qa_packet.json + storyboard_muse.jpg + final_sheet.jpg + cover_9x16.jpg) cho các tập đã dựng xong trên ổ E: để giao task muse_qa_score cho vai `qa_critic` tự chấm điểm (thang 100: Kịch bản 25 + Đạo diễn 25 + Hình ảnh 25 + Video/Âm thanh 25).
2. Kéo bảng điểm từ /api/qa/scores lưu về E:\\MUSE_MEDIA_STUDIO\\<channel>\\<slug>\\03_final_v2\\qa_scorecard.json và dọn gói tạm trên VPS.
3. Nếu tập nào bị chấm < 85/100 (REWORK): tự động tách đúng cảnh lỗi (`bad_scenes`) và đẩy task sửa lại về đúng vai (`director` / `artist` / `animator`).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import process_muse_pipeline as pm  # noqa: E402

MEDIA_ROOT = Path(r"E:\MUSE_MEDIA_STUDIO")
HUB_BASE = "https://muse.alltool.pro"


def get_invite_token() -> str:
    p = Path(os.environ["LOCALAPPDATA"]) / "MuseLoginHelper" / "hub_invite.txt"
    return p.read_text(encoding="utf-8").strip()


def fetch_scores(token: str) -> dict[str, dict]:
    req = urllib.request.Request(
        f"{HUB_BASE}/api/qa/scores?token={token}",
        headers={"User-Agent": "StudioQASync/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))
    return {row["slug"]: row for row in (data.get("scores") or [])}


def build_final_sheet(mp4_path: Path, out_jpg: Path) -> bool:
    """Trích 8 khung hình thực tế (kèm phụ đề + logo đã đốt trên hình) ghép thành 1 bảng nhẹ ~180KB cho Giám khảo Muse."""
    if out_jpg.is_file() and out_jpg.stat().st_size > 8000:
        return True
    try:
        pr = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(mp4_path)],
            capture_output=True, text=True,
        )
        dur = max(10.0, float((pr.stdout or "60").strip()))
        step = max(1.5, dur / 9.0)
        tmp_frames = []
        for idx in range(1, 9):
            ts = round(idx * step, 2)
            fp = out_jpg.parent / f"_qa_f{idx}.jpg"
            subprocess.run(
                ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(ts), "-i", str(mp4_path),
                 "-frames:v", "1", "-vf", "scale=270:480", str(fp)],
                check=False,
            )
            if fp.is_file():
                tmp_frames.append(fp)
        if not tmp_frames:
            return False
        cols, rows = 4, 2
        canvas = Image.new("RGB", (cols * 270, rows * 480), (12, 12, 16))
        for i, fp in enumerate(tmp_frames[:8]):
            with Image.open(fp) as im:
                canvas.paste(im.convert("RGB"), ((i % cols) * 270, (i // cols) * 480))
            fp.unlink(missing_ok=True)
        canvas.save(out_jpg, "JPEG", quality=84)
        return True
    except Exception:
        return False


def main(max_enqueue_per_tick: int = 8) -> dict:
    token = get_invite_token()
    scores_map = fetch_scores(token)
    hub_tasks = pm.fetch_hub_tasks()
    # Also fetch qa tasks via SSH so we don't duplicate queued muse_qa_score tasks
    ssh = pm.connect_vps_ssh(timeout=25)
    existing_qa_dedups: set[str] = set()
    try:
        _, o, _ = ssh.exec_command(
            "python3 -c \"import json,sqlite3; c=sqlite3.connect('/opt/agentnet-corner/state/research.sqlite3'); "
            "print(json.dumps([r[0] for r in c.execute(\\\"SELECT dedup FROM tasks WHERE kind LIKE 'muse_qa_%' OR kind LIKE 'muse_fix_%'\\\").fetchall()]))\""
        )
        existing_qa_dedups = set(json.loads(o.read().decode("utf-8", "replace").strip() or "[]"))
    finally:
        ssh.close()

    saved_scorecards = 0
    reworks_triggered = []
    qa_candidates: list[tuple[str, str, Path, Path]] = []

    for ch_key in ("phim-ma-dan-gian", "tap-lam-content", "tien-va-doi-srt", "kiem-hiep-co-trang"):
        ch_dir = MEDIA_ROOT / ch_key
        if not ch_dir.is_dir():
            continue
        for ep_dir in sorted(ch_dir.iterdir()):
            if not ep_dir.is_dir():
                continue
            slug = ep_dir.name
            final_dir = ep_dir / "03_final_v2"
            qc_file = final_dir / "qc_report_v2.json"
            mp4_file = final_dir / f"{slug}.mp4"
            sc_file = final_dir / "qa_scorecard.json"
            if not (qc_file.is_file() and mp4_file.is_file()):
                continue

            if slug in scores_map:
                sc = scores_map[slug]
                if not sc_file.is_file():
                    sc_file.write_text(json.dumps(sc, ensure_ascii=False, indent=2), encoding="utf-8")
                    saved_scorecards += 1
                if sc.get("verdict") == "REWORK":
                    fix_dedup = f"musefix-{slug}-{int(sc.get('updated_at', 0))}"
                    if fix_dedup not in existing_qa_dedups:
                        bad_scenes = sc.get("bad_scenes") or [1]
                        fb = sc.get("feedback", "Cần nâng cấp chất lượng theo nhận xét Giám khảo QA")
                        # Xóa các cảnh bị chê để tự render lại sau khi đội chuyên môn nộp bản sửa
                        for b_idx in bad_scenes:
                            if int(sc.get("visual_score", 25)) < 18:
                                (ep_dir / "01_muse_images" / f"scene_{int(b_idx):02d}.jpg").unlink(missing_ok=True)
                            (ep_dir / "02_muse_clips" / f"scene_{int(b_idx):02d}.mp4").unlink(missing_ok=True)
                        qc_file.unlink(missing_ok=True)
                        target_role = "artist" if int(sc.get("visual_score", 25)) <= int(sc.get("video_score", 25)) else "animator"
                        kind = "muse_draw_images" if target_role == "artist" else "muse_make_videos"
                        found = pm.find_spec(slug)
                        spec_url = found[2] if found else ""
                        sc_str = ", ".join(f"scene_{int(i):02d}" for i in bad_scenes)
                        rework_task = {
                            "dedup": fix_dedup,
                            "assigned_to": target_role,
                            "kind": kind,
                            "payload": {
                                "objective": f"[{slug}] SỬA LẠI THEO HỘI ĐỒNG CHẤM ĐIỂM ({sc.get('total_score')}/100đ): làm lại {sc_str} -> đẩy croc về ổ E:.",
                                "acceptance_criteria": (
                                    f"Hội đồng QA chấm tập {slug} đạt {sc.get('total_score')}/100 (<85đ). Nhận xét: {fb}. "
                                    f"Đọc kịch bản tại {spec_url}, tạo lại đúng các cảnh {sc_str} chất lượng cao nhất, rồi đẩy thẳng từ Ubuntu về ổ E: bằng lệnh: "
                                    f"zip -j /tmp/{slug}_fix.zip scene_*.* && curl -fsSL -X POST \"{HUB_BASE}/media-upload?token={token}&slug={slug}&json=1\" -F \"file=@/tmp/{slug}_fix.zip\"."
                                ),
                            },
                        }
                        pm.enqueue_hub_tasks([rework_task])
                        reworks_triggered.append({"slug": slug, "role": target_role, "bad_scenes": bad_scenes})
                continue

            dedup = f"museqa-score-{slug}"
            if dedup not in existing_qa_dedups:
                found = pm.find_spec(slug)
                if found:
                    qa_candidates.append((ch_key, slug, ep_dir, found[1]))

    # Upload QA packets for up to max_enqueue_per_tick episodes per tick so VPS stays light
    to_enqueue = []
    if qa_candidates:
        ssh = pm.connect_vps_ssh(timeout=30)
        try:
            sftp = ssh.open_sftp()
            for ch_key, slug, ep_dir, spec_path in qa_candidates[:max_enqueue_per_tick]:
                final_dir = ep_dir / "03_final_v2"
                mp4_file = final_dir / f"{slug}.mp4"
                sheet_jpg = final_dir / "final_sheet.jpg"
                build_final_sheet(mp4_file, sheet_jpg)
                sb_jpg = ep_dir / "storyboard_muse.jpg"
                cov_jpg = final_dir / f"{slug}_cover_9x16.jpg"
                qc_obj = json.loads((final_dir / "qc_report_v2.json").read_text(encoding="utf-8"))
                spec_obj = json.loads(spec_path.read_text(encoding="utf-8"))
                packet = {
                    "slug": slug,
                    "channel": ch_key,
                    "title": spec_obj.get("title", slug),
                    "character_bible": spec_obj.get("character_bible", ""),
                    "qc_metrics": qc_obj.get("qc", {}),
                    "voice": qc_obj.get("voice", ""),
                    "scenes": [
                        {
                            "id": s.get("id"),
                            "voice": s.get("voice", spec_obj.get("voice")),
                            "voiceover": s.get("voiceover", ""),
                            "image_prompt": s.get("image_prompt", ""),
                            "motion": s.get("motion", ""),
                        }
                        for s in spec_obj.get("scenes", [])
                    ],
                }
                pkt_local = final_dir / "qa_packet.json"
                pkt_local.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

                rdir = f"/var/lib/agentnet-media/{slug}"
                ssh.exec_command(f"mkdir -p {rdir}")[1].read()
                sftp.put(str(pkt_local), f"{rdir}/qa_packet.json")
                if sb_jpg.is_file():
                    sftp.put(str(sb_jpg), f"{rdir}/storyboard_muse.jpg")
                if sheet_jpg.is_file():
                    sftp.put(str(sheet_jpg), f"{rdir}/final_sheet.jpg")
                if cov_jpg.is_file():
                    sftp.put(str(cov_jpg), f"{rdir}/cover_9x16.jpg")
                ssh.exec_command(f"chown -R agentnet-corner:agentnet-corner {rdir}")[1].read()

                title = spec_obj.get("title", slug)
                to_enqueue.append({
                    "dedup": f"museqa-score-{slug}",
                    "assigned_to": "qa_critic",
                    "kind": "muse_qa_score",
                    "payload": {
                        "objective": f"[{slug}] HỘI ĐỒNG MUSE CHẤM ĐIỂM TẬP PHIM (thang 100): '{title}' ({ch_key})",
                        "acceptance_criteria": (
                            f"VAI TRÒ: GIÁM KHẢO CHẤM ĐIỂM ĐỘC LẬP (qa_critic) cho tập '{title}' (kênh {ch_key}, mã {slug}). "
                            f"BƯỚC 1: Đọc dữ liệu kịch bản + thông số kỹ thuật tại {HUB_BASE}/media/{slug}/qa_packet.json. "
                            f"BƯỚC 2: Xem thật bằng mắt bảng 11 ảnh gốc {HUB_BASE}/media/{slug}/storyboard_muse.jpg, bảng 8 khung hình trích từ video thành phẩm (có phụ đề & logo) {HUB_BASE}/media/{slug}/final_sheet.jpg và ảnh bìa {HUB_BASE}/media/{slug}/cover_9x16.jpg. "
                            f"BƯỚC 3: Chấm điểm khắt khe trung thực trên thang 100: "
                            f"1) script_score (0-25): Hook 3s đầu cuốn hút, thoại tự nhiên giàu chi tiết, đúng giọng nam/nữ nhân vật; "
                            f"2) director_score (0-25): Góc máy 11 cảnh đa dạng, không lặp cảnh nhàm chán, cao trào hợp lý; "
                            f"3) visual_score (0-25): Nhân vật đồng nhất khuôn mặt/trang phục theo character_bible, không kính cận/đồng hồ hiện đại, không chữ rác/AIGC; "
                            f"4) video_score (0-25): Thời lượng chuẩn (55-98s), âm lượng chuẩn (-14..-16 LUFS), phụ đề ngắt câu đẹp không rớt chữ lẻ, có Logo kênh. "
                            f"BƯỚC 4 (NỘP BẢNG ĐIỂM THẲNG TRÊN /PORTAL — KHÔNG CẦN CURL RIÊNG, KHÔNG CẦN CHỜ DUYỆT): Dán thẳng khối JSON điểm số vào ô Tóm tắt (Summary) của form Nộp Kết Quả trên /portal rồi bấm Nộp: "
                            f"{{\"slug\":\"{slug}\",\"channel\":\"{ch_key}\",\"script_score\":23,\"director_score\":22,\"visual_score\":23,\"video_score\":24,\"bad_scenes\":[],\"feedback\":\"Nhận xét chi tiết từng mặt...\"}} "
                            f"(thay bằng số điểm thật của bạn; tổng >=85 là PASS, <85 là REWORK kèm số thứ tự cảnh lỗi trong bad_scenes; hệ thống tự động ghi lên Bảng Điểm 100!)."
                        ),
                    },
                })
            sftp.close()
        finally:
            ssh.close()

    n_qa = pm.enqueue_hub_tasks(to_enqueue)
    out = {
        "total_hub_scores": len(scores_map),
        "saved_scorecards_to_E": saved_scorecards,
        "enqueued_qa_tasks": n_qa,
        "reworks_triggered": reworks_triggered,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2), flush=True)
    return out


if __name__ == "__main__":
    main()
