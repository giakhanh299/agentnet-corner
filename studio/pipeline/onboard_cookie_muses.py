"""Nạp 10+ tài khoản Muse mới bằng Cookie vào các hồ sơ Chrome cô lập (%LOCALAPPDATA%\\MuseLoginHelper\\Accounts\\*)
và gán thẳng vào đội artist (4 nick đầu) + đội animator (các nick sau) để chạy song song 4 Hồi phim 8 phút.
Bảo mật [L065]: Không in cookie/mật khẩu ra log hay lưu vào git.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
RAG = pathlib.Path(r"D:\AI_AGENT\AI_SYSTEM\RAG")
sys.path.insert(0, str(RAG))
sys.path.insert(0, str(HERE))
import muse_dispatch as md  # noqa: E402
import assign_muse_roles as amr  # noqa: E402


def main() -> dict:
    acc_file = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else (md.HELPER_ROOT / "new_10_accounts.txt")
    inv = (md.HELPER_ROOT / "hub_invite.txt").read_text(encoding="utf-8").strip()
    raw_lines = acc_file.read_text(encoding="utf-8-sig").splitlines()
    accounts = [a for a in (md.parse_account_line(l) for l in raw_lines) if a]

    roster_file = md.HELPER_ROOT / "studio_roster.json"
    extra_roster = json.loads(roster_file.read_text(encoding="utf-8")) if roster_file.is_file() else {}

    # 4 artist mới + 6 animator mới (artist cũng tự tràn sang animator khi hết queue ảnh!)
    results = []
    with sync_playwright() as pw:
        for idx, acc in enumerate(accounts, 1):
            role = "artist" if idx <= 4 else "animator"
            title_vi = f"HỌA SĨ VẼ ẢNH 9:16 MỚI #{idx}" if role == "artist" else f"CHUYÊN VIÊN DỰNG VIDEO AI MỚI #{idx - 4}"
            profile_dir = md.account_profile(acc["email"])
            profile_dir.mkdir(parents=True, exist_ok=True)
            prefix = profile_dir.name[:8]
            extra_roster[prefix] = [role, title_vi]
            roster_file.write_text(json.dumps(extra_roster, ensure_ascii=False, indent=2), encoding="utf-8")

            rec = {"index": idx, "profile": prefix, "role": role, "status": "", "detail": ""}
            print(f"[{idx}/{len(accounts)}] Nạp cookie hồ sơ {prefix} -> {role}...", flush=True)
            try:
                ctx = pw.chromium.launch_persistent_context(profile_dir, channel="chrome", headless=False, no_viewport=True)
            except Exception as e:
                rec.update(status="LAUNCH_ERROR", detail=type(e).__name__)
                results.append(rec)
                continue
            try:
                ctx.set_default_timeout(14000)
                cookies = md.parse_cookie_header(acc["cookies_raw"])
                if cookies:
                    # Also add for muse.ai & www.muse.ai / .muse.ai
                    ctx.add_cookies(cookies)
                page = ctx.pages[0] if ctx.pages else ctx.new_page()
                page.goto(md.MUSE_URL, wait_until="domcontentloaded", timeout=30000)
                if md.has_captcha(page):
                    rec.update(status="BLOCKED_CAPTCHA", detail="Cần chủ dự án tự xác nhận CAPTCHA")
                elif not md.wait_for_chat(page, seconds=18):
                    rec.update(status="COOKIE_NOT_SIGNED_IN", detail=f"url={page.url[:60]}")
                else:
                    msg = amr.build_role_prompt(role, title_vi, inv)
                    ok, detail = md.send_and_verify(page, msg)
                    if ok:
                        # Wait briefly for any initial alltool.pro permission card and whitelist it automatically
                        page.wait_for_timeout(12000)
                        amr.whitelist_alltool_and_clear_other(page)
                    rec.update(status="SENT" if ok else "SEND_FAILED", detail=detail)
            except Exception as e:
                rec.update(status="ERROR", detail=f"{type(e).__name__}: {str(e)[:120]}")
            finally:
                try:
                    ctx.close()
                except Exception:
                    pass
            print(f"  -> {prefix} ({role}): {rec['status']} | {rec['detail']}", flush=True)
            results.append(rec)

    summary = {"total": len(results), "sent": sum(r["status"] == "SENT" for r in results), "results": results}
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return summary


if __name__ == "__main__":
    main()
