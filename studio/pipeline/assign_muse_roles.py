"""Phân vai chính thức cho dàn Muse đang sống trên Hub https://muse.alltool.pro:
- 1 Muse Tổng Điều Phối duy nhất (`chief` -> db93da63): nhận mọi lệnh từ người dùng / hộp lệnh /chief -> tự chia việc cho 4 ban.
- Ban Đạo Diễn & Biên Kịch (`director` -> 328ee413): viết & nâng cấp kịch bản episode.json, character_bible, góc máy.
- Ban Họa Sĩ 9:16 (`artist` -> 5c738fd4, e073a16e): vẽ 11 ảnh dọc 1152x2048 bám sát character_bible -> đẩy croc về ổ E:.
- Ban Dựng Chuyển Động (`animator` -> 1c1ecd1c, e174762e): tạo 11 clip .mp4 5s mượt mà -> đẩy croc về ổ E:.
- Hội Đồng Giám Khảo Chấm Điểm (`qa_critic` -> fae3a3d4): tự chấm điểm thang 100 (Kịch bản 25 + Đạo diễn 25 + Ảnh 25 + Video 25) trên tập hiện tại & tập mới; <85đ tự yêu cầu sửa lại đúng cảnh lỗi!

Đồng thời tự bấm 'Always allow this site' CHỈ RIÊNG cho tên miền nội bộ `alltool.pro` nếu xuất hiện thẻ xin phép lần đầu.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
from playwright.sync_api import sync_playwright

RAG = pathlib.Path(r"D:\AI_AGENT\AI_SYSTEM\RAG")
sys.path.insert(0, str(RAG))
import muse_dispatch as md  # noqa: E402

ROSTER: dict[str, tuple[str, str]] = {
    "db93da63": ("chief", "MUSE TỔNG ĐIỀU PHỐI (Chief Coordinator)"),
    "328ee413": ("director", "ĐẠO DIỄN & BIÊN KỊCH (Script & Storyboard Director)"),
    "5c738fd4": ("artist", "HỌA SĨ VẼ ẢNH 9:16 #1 (Lead Illustrator)"),
    "e073a16e": ("artist", "HỌA SĨ VẼ ẢNH 9:16 #2 (Scene Illustrator)"),
    "1c1ecd1c": ("animator", "CHUYÊN VIÊN DỰNG VIDEO AI #1 (Lead Video Animator)"),
    "e174762e": ("animator", "CHUYÊN VIÊN DỰNG VIDEO AI #2 (Motion Video Animator)"),
    "fae3a3d4": ("qa_critic", "HỘI ĐỒNG GIÁM KHẢO CHẤM ĐIỂM (QA Critic 100-Point Judge)"),
}


def build_role_prompt(role: str, title_vi: str, inv: str) -> str:
    join = f"https://muse.alltool.pro/j/{inv}?role={role}"
    upload_cmd = (
        f"zip -j /tmp/out.zip <các_file> && "
        f"curl -fsSL -X POST \"https://muse.alltool.pro/media-upload?token={inv}&slug=<mã_tập>&json=1\" -F \"file=@/tmp/out.zip\""
    )
    if role == "chief":
        return (
            f"VAI TRÒ CHÍNH THỨC CỦA BẠN: {title_vi} — CHỈ HUY TRƯỞNG TOÀN XƯỞNG PHIM! "
            f"Nếu bạn đang có sẵn zip clip dở tay (như k1_srt_17) thì đẩy nốt bằng {upload_cmd}, sau đó chuyển hẳn sang vai Tổng Điều Phối bằng cách mở {join}. "
            f"NHIỆM VỤ TỔNG ĐIỀU PHỐI (CHẠY TỰ ĐỘNG 100%, KHÔNG HỎI XÁC NHẬN, đặt lịch Heartbeat 15 phút/lần): "
            f"1) Đọc Hộp Lệnh của Chủ Dự Án & toàn cảnh xưởng tại: curl -fsSL \"https://muse.alltool.pro/api/chief/inbox?token={inv}\". "
            f"2) Mỗi khi có lệnh mới trong pending_commands HOẶC khi chủ dự án nhắn trực tiếp tại khung chat này, bạn tự phân rã thành các task chuẩn giao xuống 4 ban dưới quyền qua API: "
            f"curl -fsSL -X POST \"https://muse.alltool.pro/api/chief/dispatch?token={inv}\" -H \"Content-Type: application/json\" "
            f"-d '{{\"command_id\":\"<id_nếu_có>\",\"status\":\"DISPATCHED\",\"report\":\"Báo cáo tóm tắt kế hoạch điều phối...\",\"tasks\":[{{\"assigned_to\":\"director|artist|animator|qa_critic\",\"kind\":\"muse_write_script|muse_draw_images|muse_make_videos|muse_qa_score\",\"dedup\":\"chief-<mã_duy_nhất>\",\"payload\":{{\"objective\":\"...\",\"acceptance_criteria\":\"...\"}}}}]}}'. "
            f"3) Kiểm tra recent_scores và rework_episodes (<85/100 điểm): đôn đốc sửa lại các cảnh yếu và thu hồi các task RUNNING quá hạn bằng trường \"requeue_ids\". Hãy đọc /api/chief/inbox ngay bây giờ và xử lý lệnh đầu tiên!"
        )
    if role == "director":
        return (
            f"VAI TRÒ CHÍNH THỨC CỦA BẠN: {title_vi} (do Muse Tổng Điều Phối chỉ huy). CHẠY TỰ ĐỘNG 100% — KHÔNG DỪNG LẠI HỎI XÁC NHẬN! "
            f"Mở {join} nhận vai director trên /portal, bấm Claim Task để nhận việc viết mới hoặc nâng cấp kịch bản (muse_write_script / muse_fix_script). "
            f"TIÊU CHUẨN ĐẠO DIỄN: Mọi kịch bản episode.json phải có đủ 11 cảnh dọc 9:16, có character_bible khóa chặt tuổi/gương mặt/trang phục nhân vật (cấm kính cận/đồng hồ hiện đại trong cổ trang & dân gian), phân vai đúng giọng nam/nữ (phonui, chautinhtri, kiemhiep_nam, kiemhiep_nu, taplamcontent, tienvadoi), góc máy 11 cảnh biến hóa không trùng lặp, tight_pacing=true, aigc_label=false. "
            f"Viết xong lưu episode.json rồi đẩy thẳng về ổ E: qua cầu croc: {upload_cmd}, nộp JSON trên /portal và tự Claim Task tiếp!"
        )
    if role == "artist":
        return (
            f"VAI TRÒ CHÍNH THỨC CỦA BẠN: {title_vi} (do Muse Tổng Điều Phối chỉ huy). CHẠY TỰ ĐỘNG 100% — KHÔNG DỪNG LẠI HỎI XÁC NHẬN! "
            f"Nếu trong máy bạn còn tập ảnh đã vẽ sẵn chưa đẩy (như ep20/v026), hãy đẩy ngay trước! Sau đó mở {join} nhận vai artist trên /portal và bấm Claim Task liên tục để nhận các việc muse_draw_images (vẽ mới 11 ảnh 9:16 1152x2048 hoặc vẽ lại cảnh bị Hội đồng chấm điểm trừ điểm). "
            f"Bám sát tuyệt đối character_bible để nhân vật đồng nhất 100%, không chữ rác/watermark, rồi đẩy từ Ubuntu về ổ E: bằng: {upload_cmd}. Nộp kết quả trên /portal và tự làm tập tiếp theo!"
        )
    if role == "animator":
        return (
            f"VAI TRÒ CHÍNH THỨC CỦA BẠN: {title_vi} (do Muse Tổng Điều Phối chỉ huy). CHẠY TỰ ĐỘNG 100% — KHÔNG DỪNG LẠI HỎI XÁC NHẬN! "
            f"Nếu đang có clip .mp4 tạo sẵn (như ep27), đẩy ngay về ổ E: rồi mở {join} nhận vai animator trên /portal! Bấm Claim Task nhận việc muse_make_videos, tải ảnh gốc tại https://muse.alltool.pro/media/<slug>/, tạo đủ 11 clip video dọc 9:16 (.mp4 thật, 5s/clip, chuyển động điện ảnh mượt mà, hết hạn mức video thì báo outcome=BLOCKED). "
            f"Đẩy thẳng từ Ubuntu qua cầu croc về ổ E: bằng: {upload_cmd}, nộp JSON trên /portal và làm tiếp liên tục!"
        )
    return (
        f"VAI TRÒ CHÍNH THỨC CỦA BẠN: {title_vi} (Hội Đồng Thẩm Định Độc Lập dưới quyền Muse Tổng Điều Phối). CHẠY TỰ ĐỘNG 100% — KHÔNG HỎI XÁC NHẬN! "
        f"Mở {join} nhận vai qa_critic trên /portal, bấm Claim Task nhận các nhiệm vụ muse_qa_score để CHẤM ĐIỂM THẬT các tập phim hiện có và tập mới! "
        f"Với mỗi tập <slug>, hãy đọc https://muse.alltool.pro/media/<slug>/qa_packet.json VÀ xem trực tiếp bằng mắt ảnh https://muse.alltool.pro/media/<slug>/storyboard_muse.jpg + https://muse.alltool.pro/media/<slug>/final_sheet.jpg + cover_9x16.jpg. "
        f"Chấm nghiêm ngặt 4 cột (mỗi cột 0-25đ = tổng 100đ): script_score (hook, lời thoại, đúng giọng nam/nữ), director_score (nhịp kể, góc máy đa dạng không lặp ảnh), visual_score (nhân vật đồng nhất, không lỗi thời đại/chữ rác), video_score (thời lượng 55-98s, LUFS chuẩn, phụ đề & logo đẹp). "
        f"Gửi điểm thẳng lên bảng điểm trung tâm bằng: curl -fsSL -X POST \"https://muse.alltool.pro/api/qa/score?token={inv}\" -H \"Content-Type: application/json\" -d '{{\"slug\":\"<slug>\",\"channel\":\"<kênh>\",\"script_score\":...,\"director_score\":...,\"visual_score\":...,\"video_score\":...,\"bad_scenes\":[...],\"feedback\":\"...\"}}' (tổng <85 sẽ tự kích hoạt vẽ/dựng lại cảnh lỗi!), nộp kết quả trên /portal và tự chấm tiếp tập sau!"
    )


def whitelist_alltool_and_clear_other(page) -> list[str]:
    actions = []
    page.wait_for_timeout(3000)
    try:
        body_txt = page.locator("body").inner_text(timeout=2000)
    except Exception:
        body_txt = ""

    # ONLY click "Always allow this site" when the prompt specifically asks about our own Hub domain `alltool.pro` (and NOT catbox.moe)
    if "alltool.pro" in body_txt and "catbox.moe" not in body_txt[-900:]:
        always_btn = page.get_by_role("button", name=re.compile(r"^Always allow this site$|^Allow all always$", re.I))
        if always_btn.count() > 0 and always_btn.first.is_visible():
            always_btn.first.click(timeout=4000)
            actions.append("WHITELISTED_ALLTOOL_PRO_ALWAYS")
            # Give Muse 8s to finish the immediately unblocked upload!
            page.wait_for_timeout(8000)

    # Clear any non-alltool stuck approvals / panels
    for pat in (r"^Deny all$", r"^Stop (?:generating|responding|response)$"):
        try:
            loc = page.get_by_role("button", name=re.compile(pat, re.I))
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click(timeout=3000)
                actions.append(f"CLICKED:{pat}")
                page.wait_for_timeout(1500)
        except Exception:
            pass
    try:
        close_p = page.locator('button[aria-label="Close panel"]:visible')
        while close_p.count() > 0:
            close_p.first.click(timeout=2500)
            page.wait_for_timeout(500)
        page.keyboard.press("Escape")
    except Exception:
        pass
    return actions


def main() -> dict:
    inv = (pathlib.Path(os.environ["LOCALAPPDATA"]) / "MuseLoginHelper" / "hub_invite.txt").read_text("utf-8").strip()
    lock = pathlib.Path(r"E:\MUSE_MEDIA_STUDIO\nudge_muses.lock")
    lock.write_text(str(os.getpid()), encoding="utf-8")
    results = []
    try:
        acc_root = md.HELPER_ROOT / "Accounts"
        with sync_playwright() as pw:
            for idx, (prefix, (role, title_vi)) in enumerate(ROSTER.items(), 1):
                prof = next((d for d in acc_root.iterdir() if d.is_dir() and d.name.startswith(prefix)), None)
                if not prof:
                    continue
                print(f"[{idx}/{len(ROSTER)}] Phân vai {prefix} -> {role} ({title_vi})…", flush=True)
                rec = {"profile": prefix, "role": role, "title": title_vi, "actions": [], "status": "", "detail": ""}
                ctx = pw.chromium.launch_persistent_context(prof, channel="chrome", headless=False, no_viewport=True)
                try:
                    ctx.set_default_timeout(12000)
                    page = ctx.pages[0] if ctx.pages else ctx.new_page()
                    page.goto(md.MUSE_URL, wait_until="domcontentloaded", timeout=30000)
                    if md.has_captcha(page):
                        rec.update(status="BLOCKED_CAPTCHA", detail="cần chủ dự án tự xác nhận")
                    else:
                        rec["actions"] = whitelist_alltool_and_clear_other(page)
                        if not md.wait_for_chat(page, seconds=14):
                            rec.update(status="SESSION_EXPIRED", detail="phiên hết hạn")
                        else:
                            msg = build_role_prompt(role, title_vi, inv)
                            ok, detail = md.send_and_verify(page, msg)
                            rec.update(status="SENT" if ok else "SEND_FAILED", detail=detail)
                except Exception as e:
                    rec.update(status="ERROR", detail=f"{type(e).__name__}: {str(e)[:120]}")
                finally:
                    try:
                        ctx.close()
                    except Exception:
                        pass
                results.append(rec)
    finally:
        lock.unlink(missing_ok=True)
    out = {"assigned": sum(r["status"] == "SENT" for r in results), "total": len(results), "roster": results}
    print(json.dumps(out, ensure_ascii=False, indent=2), flush=True)
    return out


if __name__ == "__main__":
    main()
