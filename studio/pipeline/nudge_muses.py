"""Đánh thức toàn bộ phiên Chrome Muse đã đăng nhập trong %LOCALAPPDATA%\\MuseLoginHelper\\Accounts.
Đọc mã mời Hub từ %LOCALAPPDATA%\\MuseLoginHelper\\hub_invite.txt (không lưu token vào git).
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

RAG = pathlib.Path(r"D:\AI_AGENT\AI_SYSTEM\RAG")
sys.path.insert(0, str(RAG))
import muse_dispatch as md  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def get_join_url() -> str:
    inv_file = pathlib.Path(os.environ["LOCALAPPDATA"]) / "MuseLoginHelper" / "hub_invite.txt"
    inv = inv_file.read_text(encoding="utf-8").strip()
    return f"https://muse.alltool.pro/j/{inv}?role=research"


def main() -> dict:
    join = get_join_url()
    msg = (
        f"Chào Muse! Mở {join} vào Sảnh Nhiệm Vụ (vai research), bấm 'Nhận Nhiệm Vụ Mới (Claim Task)' để vẽ ảnh 9:16 và TẠO CLIP VIDEO AI (.mp4, 9:16, 5s/clip) cho Vũ Trụ Cày Phim, Tập Làm Content & Tiền Và Đời! "
        "LƯU Ý BẮT BUỘC: (1) Upload thẳng qua trình duyệt lên kho riêng https://muse.alltool.pro/media-upload?slug=<mã_tập> (nén .zip, tích giải nén -> Upload Media). "
        "(2) Với nhiệm vụ muse_make_videos, BẮT BUỘC tạo và nộp file video .mp4 thật (TUYỆT ĐỐI KHÔNG nộp lại ảnh .jpg; nếu hết hạn mức tạo video thì chọn outcome=BLOCKED để Muse khác làm). "
        "Nộp JSON hợp lệ trên /portal và giữ tích tự động nhận tập tiếp theo!"
    )
    acc_root = md.HELPER_ROOT / "Accounts"
    profiles = sorted(d for d in acc_root.iterdir() if d.is_dir())
    results = []
    with sync_playwright() as pw:
        for i, prof in enumerate(profiles, 1):
            rec = {"profile": prof.name[:8], "status": "", "detail": ""}
            print(f"[{i}/{len(profiles)}] hồ sơ {prof.name[:8]}…", flush=True)
            try:
                ctx = pw.chromium.launch_persistent_context(prof, channel="chrome", headless=False, no_viewport=True)
            except Exception as e:
                rec.update(status="LAUNCH_ERROR", detail=type(e).__name__)
                results.append(rec)
                continue
            try:
                ctx.set_default_timeout(12000)
                page = ctx.pages[0] if ctx.pages else ctx.new_page()
                page.goto(md.MUSE_URL, wait_until="domcontentloaded", timeout=30000)
                if md.has_captcha(page):
                    rec.update(status="BLOCKED_CAPTCHA", detail="cần chủ dự án tự xác nhận")
                elif not md.wait_for_chat(page, seconds=14):
                    rec.update(status="SESSION_EXPIRED", detail="phiên hết hạn - không tự đăng nhập")
                else:
                    # Open a fresh chat thread if New chat button is visible so old 'research-only' threads don't block video generation
                    try:
                        nc = page.get_by_role("button", name=md.re.compile(r"new chat|new conversation|cuộc trò chuyện mới", md.re.I))
                        if nc.count() > 0 and nc.first.is_visible():
                            nc.first.click(timeout=3000)
                            page.wait_for_timeout(800)
                    except Exception:
                        pass
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
    summary = {"total": len(results), "sent": sum(r["status"] == "SENT" for r in results), "results": results}
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return summary


if __name__ == "__main__":
    main()
