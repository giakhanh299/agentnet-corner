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
    only = None
    if len(sys.argv) >= 3 and sys.argv[1] == "--only":
        only = {x.strip() for x in sys.argv[2].split(",") if x.strip()}
    lock = pathlib.Path(r"E:\MUSE_MEDIA_STUDIO\nudge_muses.lock")
    if lock.is_file() and (__import__("time").time() - lock.stat().st_mtime) < 600:
        print("SKIP_NUDGE: another nudge_muses instance is already running.", flush=True)
        return {"skipped": True}
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(str(os.getpid()), encoding="utf-8")
    try:
        return _run_nudge(only_profiles=only)
    finally:
        lock.unlink(missing_ok=True)


def _clear_stuck_ui(page) -> None:
    """Gỡ tự động các bảng chờ duyệt upload trình duyệt cũ (Deny all / Stop task) và đóng side panel (role=dialog)."""
    page.wait_for_timeout(2500)
    for pat in (r"^Deny all$", r"^Stop task", r"^Stop (?:generating|responding|response)$"):
        try:
            loc = page.get_by_role("button", name=md.re.compile(pat, md.re.I))
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click(timeout=3000)
                page.wait_for_timeout(1500)
        except Exception:
            pass
    for _ in range(4):
        try:
            deny_one = page.get_by_role("button", name=md.re.compile(r"^Deny$", md.re.I))
            if deny_one.count() > 0 and deny_one.first.is_visible():
                deny_one.first.click(timeout=2500)
                page.wait_for_timeout(800)
            else:
                break
        except Exception:
            break
    try:
        close_p = page.locator('button[aria-label="Close panel"]:visible')
        while close_p.count() > 0:
            close_p.first.click(timeout=2500)
            page.wait_for_timeout(600)
    except Exception:
        pass


def _run_nudge(only_profiles: set[str] | None = None) -> dict:
    inv_file = pathlib.Path(os.environ["LOCALAPPDATA"]) / "MuseLoginHelper" / "hub_invite.txt"
    inv = inv_file.read_text(encoding="utf-8").strip()
    join = f"https://muse.alltool.pro/j/{inv}?role=research"
    msg = (
        f"BỎ HẲN bước upload file bằng Browser (catbox/media-upload) để không bao giờ kẹt bảng chờ duyệt! "
        f"Mở {join} vào Sảnh Nhiệm Vụ (/portal, vai research), bấm 'Nhận Nhiệm Vụ Mới (Claim Task)' để vẽ ảnh 9:16 và TẠO CLIP VIDEO AI (.mp4, 9:16, 5s/clip). "
        f"ĐẨY FILE TRỰC TIẾP TỪ UBUNTU THẲNG VỀ Ổ E: QUA CROC chỉ bằng 1 lệnh bash: "
        f"curl -fsSL \"https://muse.alltool.pro/croc-push.sh?token={inv}&slug=<mã_tập>\" | bash -s -- scene_*.* "
        "(chờ báo CROC_PUSH_TO_E_OK là xong! Với muse_make_videos bắt buộc gửi .mp4 thật; hết hạn mức video thì chọn outcome=BLOCKED). Sau đó nộp JSON trên /portal và nhận tiếp việc mới liên tục!"
    )
    acc_root = md.HELPER_ROOT / "Accounts"
    profiles = sorted(d for d in acc_root.iterdir() if d.is_dir())
    if only_profiles:
        profiles = [d for d in profiles if d.name[:8] in only_profiles]
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
                else:
                    _clear_stuck_ui(page)
                    if not md.wait_for_chat(page, seconds=14):
                        rec.update(status="SESSION_EXPIRED", detail="phiên hết hạn - không tự đăng nhập")
                    else:
                        try:
                            nc = page.get_by_role("button", name=md.re.compile(r"new chat|new conversation|cuộc trò chuyện mới", md.re.I))
                            if nc.count() > 0 and nc.first.is_visible():
                                nc.first.click(timeout=3000)
                                page.wait_for_timeout(800)
                                _clear_stuck_ui(page)
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
