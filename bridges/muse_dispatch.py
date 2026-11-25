"""Muse Fleet Dispatcher — đăng nhập các phiên Muse cô lập và giao việc qua AgentNet Hub (:8110).

Bảo mật (L065):
- KHÔNG lưu mật khẩu, cookie hay mã mời trong kho mã nguồn hay log.
- Dữ liệu tài khoản & mã mời chỉ đọc từ %LOCALAPPDATA%/MuseLoginHelper/.
- Nếu gặp CAPTCHA / xác minh con người: DỪNG NGAY trên tài khoản đó và báo để chủ dự án tự xử lý.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import sys
from hashlib import sha256
from time import monotonic
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import Error as BrowserError
from playwright.sync_api import TimeoutError as BrowserTimeout
from playwright.sync_api import sync_playwright

MUSE_URL = "https://muse.ai/"
MAIL_URL = "https://tempmail.plus/en/"
MAIL_DOMAINS = {
    "mailto.plus", "fexpost.com", "fexbox.org", "mailbox.in.ua",
    "rover.info", "fextemp.com", "any.pink", "merepost.com",
}
EMAIL_FIELD = 'input[aria-label="Mobile number or email"]:visible'
PASSWORD_FIELD = 'input[autocomplete="current-password"]:visible'
CODE_FIELD = 'input[autocomplete="one-time-code"]:visible'
SIGN_IN_FIELD = f"{EMAIL_FIELD}, {PASSWORD_FIELD}, {CODE_FIELD}"
CHAT_EDITOR = 'textarea:visible, [contenteditable="true"]:visible'
CHAT_EDITOR_HINT = re.compile(r"\b(message|chat|ask|prompt|tell muse)\b|tin nhắn|hỏi muse", re.I)
CHAT_SEND = re.compile(r"^(?:send(?: (?:a |the |your )?(?:message|prompt))?|submit message|gửi(?: tin nhắn)?)$", re.I)
CHAT_STOP = re.compile(r"^(?:stop (?:generating|responding|response)|dừng phản hồi)$", re.I)
MAIL_ROWS = ".inbox .mail"
CODE_PATTERN = re.compile(r"(?<![0-9])[0-9]{6}(?![0-9])")
SENDER_PATTERN = re.compile(r"\b(?:muse|meta|facebook)(?:mail)?\b", re.I)
LOGIN_MAIL_PATTERN = re.compile(r"\b(?:code|verify|verification|confirm|log\s*in|sign\s*in)\b|mã|xác minh", re.I)
CAPTCHA_PATTERN = re.compile(
    r"captcha|verify you are human|confirm you'?re human|turnstile|arkose|funcaptcha|security check|i'?m not a robot",
    re.I,
)

HELPER_ROOT = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "MuseLoginHelper"
REPORT_PATH = pathlib.Path(__file__).resolve().parent / "data" / "muse_dispatch_last.json"


def parse_account_line(line: str) -> dict | None:
    raw = line.strip().lstrip("\ufeff")
    if not raw or raw.startswith("#"):
        return None
    parts = raw.split("|", 3)
    if len(parts) < 1 or not re.fullmatch(r"[^\s@|]+@[^\s@|.]+(?:\.[^\s@|.]+)+", parts[0].strip()):
        return None
    email_raw = parts[0].strip()
    name, domain = email_raw.rsplit("@", 1)
    email = f"{name}@{domain.lower()}"
    p1 = parts[1].strip() if len(parts) > 1 else ""
    p2 = parts[2].strip() if len(parts) > 2 else ""
    cookies_raw = parts[3].strip() if len(parts) > 3 else ""

    # Tự nhận diện thứ tự cột:
    # - Dạng mới: email|password(>=10 ký tự)|6-char-code|cookie
    # - Dạng cũ dang_nhap_muse.py: email|invite_code|password|cookie
    is_p2_short_code = bool(re.fullmatch(r"[A-Z0-9]{6,8}", p2))
    is_p1_short_code = bool(re.fullmatch(r"[A-Z0-9]{6,8}", p1))
    if is_p2_short_code and len(p1) >= 8:
        password, invite_code = p1, p2
    elif is_p1_short_code and len(p2) >= 8:
        password, invite_code = p2, p1
    else:
        password, invite_code = (p1 or p2), (p2 if p1 else "")
    return {
        "email": email,
        "password": password,
        "invite_code": invite_code,
        "cookies_raw": cookies_raw,
    }


def parse_cookie_header(cookie_header: str) -> list[dict]:
    cookies = []
    for item in cookie_header.split(";"):
        item = item.strip()
        if "=" not in item:
            continue
        name, val = item.split("=", 1)
        name = name.strip()
        val = val.strip()
        if not name:
            continue
        cookies.append({
            "name": name,
            "value": val,
            "domain": ".muse.ai",
            "path": "/",
            "secure": True,
            "sameSite": "None",
        })
    return cookies


def is_site(url: str, host: str) -> bool:
    addr = urlsplit(url)
    return addr.scheme == "https" and (addr.hostname == host or (addr.hostname or "").endswith("." + host))


def has_captcha(page) -> bool:
    try:
        frames = [f.url for f in page.frames]
        if any(k in u.lower() for u in frames for k in ("captcha", "turnstile", "arkose", "hcaptcha", "recaptcha")):
            return True
        txt = page.locator("body").inner_text(timeout=1500)[:2000]
        return bool(CAPTCHA_PATTERN.search(txt))
    except Exception:
        return False


def chat_controls(muse):
    if not is_site(muse.url, "muse.ai") or muse.locator(SIGN_IN_FIELD).count() or muse.get_by_role("dialog").count():
        return None
    editor = muse.locator(CHAT_EDITOR)
    send = muse.get_by_role("button", name=CHAT_SEND)
    stop = muse.get_by_role("button", name=CHAT_STOP)
    if editor.count() != 1 or stop.count() or send.count() > 1:
        return None
    hint = editor.evaluate(
        'el => ["placeholder", "data-placeholder", "aria-label"].map(a => el.getAttribute(a) ?? "").join(" ")'
    )
    if send.count() == 1 or CHAT_EDITOR_HINT.search(hint):
        return editor, send
    return None


def wait_for_chat(muse, seconds: int = 12) -> bool:
    deadline = monotonic() + seconds
    while not muse.is_closed() and monotonic() < deadline:
        if has_captcha(muse):
            return False
        if is_site(muse.url, "muse.ai") and not muse.locator(SIGN_IN_FIELD).count():
            try:
                if muse.title() == "Chat — Muse" or chat_controls(muse):
                    return True
            except BrowserError:
                pass
        muse.wait_for_timeout(450)
    return False


def inbox_response(response, email: str) -> bool:
    addr = urlsplit(response.url)
    return (
        is_site(response.url, "tempmail.plus")
        and addr.path == "/api/mails"
        and parse_qs(addr.query).get("email") == [email]
    )


def open_inbox(context, email: str):
    name, domain = email.rsplit("@", 1)
    if domain not in MAIL_DOMAINS or not re.fullmatch(r"[\w.\-]+", name, re.ASCII):
        return None, None
    inbox = context.new_page()
    try:
        with inbox.expect_response(lambda r: inbox_response(r, email), timeout=20000) as first:
            inbox.goto(f"{MAIL_URL}?{email}", wait_until="domcontentloaded")
        mailbox = first.value.json()
        if not mailbox.get("result"):
            return inbox, None
        return inbox, {str(m["mail_id"]) for m in mailbox.get("mail_list", [])}
    except Exception:
        return inbox, None


def find_code(subject: str, body: str) -> str | None:
    if LOGIN_MAIL_PATTERN.search(subject):
        codes = set(CODE_PATTERN.findall(subject))
        if len(codes) == 1:
            return codes.pop()
    codes = set(CODE_PATTERN.findall(body))
    if LOGIN_MAIL_PATTERN.search(f"{subject}\n{body}") and len(codes) == 1:
        return codes.pop()
    return None


def wait_for_mail(inbox, muse, old_ids: set[str], seconds: int = 90) -> str | None:
    deadline = monotonic() + seconds
    seen = set(old_ids)
    newest_old = max((int(x) for x in old_ids if x.isdecimal()), default=0)
    while monotonic() < deadline and not inbox.is_closed() and not muse.is_closed():
        if not is_site(muse.url, "muse.ai") or not muse.locator(CODE_FIELD).count():
            return None
        if not is_site(inbox.url, "tempmail.plus"):
            return None
        for row in inbox.locator(MAIL_ROWS).all():
            action = row.get_attribute("onclick") or ""
            m = re.search(r"'mail/([0-9]+)'", action)
            if not m or m[1] in seen or int(m[1]) <= newest_old:
                continue
            seen.add(m[1])
            sender = row.locator(".from").inner_text()
            subject = row.locator(".subj").inner_text()
            if not SENDER_PATTERN.search(sender):
                continue
            code = find_code(subject, "")
            if code:
                return code
            row.click()
            try:
                body = inbox.locator(".letter .overflow-auto").inner_text(timeout=5000)
                code = find_code(subject, body)
            except BrowserTimeout:
                code = None
            if code:
                return code
            inbox.locator(".letter #back").click()
            break
        inbox.wait_for_timeout(900)
    return None


def submit_field(field, value: str) -> None:
    auto_submits = field.get_attribute("aria-label") == "6-digit security code"
    field.fill(value)
    if not auto_submits:
        field.locator("xpath=ancestor::form[1]").locator("button[type=submit]:visible").click()


def do_password_login(context, muse, email: str, password: str) -> tuple[bool, str]:
    if has_captcha(muse):
        return False, "BLOCKED_CAPTCHA"
    field = muse.locator(EMAIL_FIELD).first
    if not field.count():
        start = muse.get_by_role("button", name="Log in", exact=True).first
        if start.count() and start.is_visible():
            start.click()
        else:
            return False, "NO_LOGIN_FIELD"
    field.wait_for(state="visible", timeout=15000)
    inbox, old_ids = open_inbox(context, email)
    muse.bring_to_front()
    submit_field(field, email)
    field.wait_for(state="hidden", timeout=18000)

    if has_captcha(muse):
        return False, "BLOCKED_CAPTCHA"

    next_field = muse.locator(f"{PASSWORD_FIELD}, {CODE_FIELD}").first
    next_field.wait_for(state="visible", timeout=15000)
    pw_field = muse.locator(PASSWORD_FIELD).first
    use_pw = muse.get_by_role("button", name="Use password instead", exact=True).first
    if password and not pw_field.count() and use_pw.count() and use_pw.is_visible():
        use_pw.click()
        pw_field.wait_for(state="visible", timeout=10000)

    if pw_field.count():
        if not password:
            return False, "PASSWORD_MISSING"
        submit_field(pw_field, password)
        try:
            pw_field.wait_for(state="hidden", timeout=15000)
        except BrowserTimeout:
            return False, "PASSWORD_REJECTED_OR_SLOW"

    if has_captcha(muse):
        return False, "BLOCKED_CAPTCHA"

    if is_site(muse.url, "muse.ai") and muse.locator(CODE_FIELD).count():
        code_field = muse.locator(CODE_FIELD).first
        if code_field.get_attribute("aria-label") != "6-digit security code":
            return False, "EXTRA_VERIFICATION_REQUIRED"
        if inbox is None or old_ids is None:
            return False, "TEMPMAIL_UNAVAILABLE"
        code = wait_for_mail(inbox, muse, old_ids, seconds=90)
        if not code:
            return False, "OTP_TIMEOUT"
        if not code_field.input_value():
            submit_field(code_field, code)

    if wait_for_chat(muse, seconds=20):
        return True, "LOGIN_PASSWORD_OK"
    if has_captcha(muse):
        return False, "BLOCKED_CAPTCHA"
    return False, f"POST_LOGIN_NOT_CHAT ({muse.url[:40]})"


def wait_for_new_message(muse, transcript, copies_before: int, seconds: int = 20) -> bool:
    deadline = monotonic() + seconds
    while monotonic() < deadline and not muse.is_closed() and is_site(muse.url, "muse.ai"):
        if transcript.count() > copies_before:
            return True
        muse.wait_for_timeout(300)
    return False


def send_and_verify(muse, content: str) -> tuple[bool, str]:
    deadline = monotonic() + 75
    controls = None
    while monotonic() < deadline and not muse.is_closed():
        if has_captcha(muse):
            return False, "BLOCKED_CAPTCHA"
        controls = chat_controls(muse)
        if controls:
            # Chờ Secure VM của Muse kết nối xong ("Connected") để tin không bị rơi khi reload
            try:
                body_txt = muse.locator("body").inner_text(timeout=1500)
                if "Connected" in body_txt or monotonic() > deadline - 35:
                    break
            except Exception:
                break
        muse.wait_for_timeout(600)
    if not controls:
        return False, "CHAT_EDITOR_NOT_FOUND"
    muse.wait_for_timeout(2000)

    editor, send = controls
    muse.bring_to_front()
    existing = editor.evaluate("el => el.value ?? el.innerText").strip()
    if existing:
        editor.fill("")
    transcript = muse.get_by_text(content, exact=True).and_(
        muse.locator(':visible:not(textarea):not([contenteditable="true"]):not([contenteditable="true"] *)')
    )
    copies_before = transcript.count()
    editor.fill(content)
    try:
        send.wait_for(state="visible", timeout=8000)
    except BrowserTimeout:
        return False, "SEND_BUTTON_HIDDEN"
    send.click(timeout=8000)
    if not wait_for_new_message(muse, transcript, copies_before, seconds=20):
        return False, "MESSAGE_NOT_APPEARED"
    # Chờ Muse lưu tin phía cloud rồi reload kiểm chứng thật (L016)
    muse.wait_for_timeout(22000)
    if not is_site(muse.url, "muse.ai"):
        return False, f"REDIRECTED_AFTER_SEND ({muse.url[:40]})"
    muse.reload(wait_until="domcontentloaded", timeout=25000)
    marker = muse.get_by_text("Sảnh Nhiệm Vụ", exact=False).and_(
        muse.locator(':visible:not(textarea):not([contenteditable="true"]):not([contenteditable="true"] *)')
    )
    if wait_for_new_message(muse, transcript, copies_before, seconds=15) or marker.count() > 0:
        return True, f"SENT_AND_PERSISTED ({muse.url.split('?')[0]})"
    return False, f"NOT_PERSISTED_AFTER_RELOAD (url={muse.url.split('?')[0]}, title={muse.title()[:30]})"


def account_profile(email: str) -> pathlib.Path:
    folder = sha256(email.casefold().encode("utf-8")).hexdigest()[:24]
    return HELPER_ROOT / "Accounts" / folder


def dispatch_accounts(accounts_file: pathlib.Path, role: str = "research", limit: int = 0, skip: int = 0) -> dict:
    invite_file = HELPER_ROOT / "active_invite.json"
    if not invite_file.exists():
        raise RuntimeError("Thiếu active_invite.json trong MuseLoginHelper.")
    invite = json.loads(invite_file.read_text(encoding="utf-8"))
    code = invite["code"]
    join_url = f"https://muse.alltool.pro/j/{code}?role={role}"
    prompt_msg = (
        f"Mở {join_url} để tự động nhận vai trò {role} trong đội quân AgentNet và vào Sảnh Nhiệm Vụ (/portal). "
        "Bấm 'Nhận Nhiệm Vụ Mới (Claim Task)', đọc kỹ đề bài JSON, hoàn thành đầy đủ theo nguyên tắc trung thực bằng chứng "
        "(không bịa số liệu/link, ghi rõ limitations), rồi nộp kết quả qua form Nộp Kết Quả trên /portal "
        "(giữ tích chọn tự động nhận nhiệm vụ tiếp theo). Không tự git push, không đụng hệ thống đăng bài công khai."
    )

    if accounts_file.is_file():
        raw_lines = accounts_file.read_text(encoding="utf-8-sig").splitlines()
        accounts = [a for a in (parse_account_line(l) for l in raw_lines) if a]
    else:
        acc_root = HELPER_ROOT / "Accounts"
        profile_dirs = sorted([d for d in acc_root.iterdir() if d.is_dir()]) if acc_root.is_dir() else []
        accounts = [{"email": f"profile:{d.name}", "password": "", "invite_code": "", "cookies_raw": "", "profile_dir": d} for d in profile_dirs]
    if skip > 0:
        accounts = accounts[skip:]
    if limit > 0:
        accounts = accounts[:limit]

    results = []
    with sync_playwright() as pw:
        for idx, acc in enumerate(accounts, 1):
            email = acc["email"]
            rec = {"index": idx, "email": email, "login_method": "", "status": "PENDING", "detail": ""}
            print(f"[{idx}/{len(accounts)}] Đang khởi động phiên cho {email}...", flush=True)
            profile_dir = acc.get("profile_dir") or account_profile(email)
            profile_dir.mkdir(parents=True, exist_ok=True)
            try:
                ctx = pw.chromium.launch_persistent_context(
                    profile_dir, channel="chrome", headless=False, no_viewport=True
                )
            except BrowserError as e:
                rec["status"] = "ERROR"
                rec["detail"] = f"CHROME_LAUNCH_ERR: {type(e).__name__}"
                results.append(rec)
                print(f"  -> {rec['status']} ({rec['detail']})", flush=True)
                continue

            try:
                ctx.set_default_timeout(10000)
                muse = ctx.pages[0] if ctx.pages else ctx.new_page()
                muse.goto(MUSE_URL, wait_until="domcontentloaded", timeout=30000)
                signed_in = wait_for_chat(muse, seconds=8)
                if signed_in:
                    rec["login_method"] = "profile_session"
                else:
                    if has_captcha(muse):
                        rec["status"] = "BLOCKED_CAPTCHA"
                        rec["detail"] = "Gặp xác minh con người — cần chủ dự án tự xác nhận."
                    else:
                        ok_login, detail = do_password_login(ctx, muse, email, acc["password"])
                        signed_in = ok_login
                        rec["login_method"] = "password_otp"
                        if not ok_login:
                            rec["status"] = "BLOCKED_CAPTCHA" if detail == "BLOCKED_CAPTCHA" else "LOGIN_FAILED"
                            rec["detail"] = detail

                if signed_in:
                    ok_send, send_detail = send_and_verify(muse, prompt_msg)
                    rec["status"] = "DISPATCHED" if ok_send else "SEND_FAILED"
                    rec["detail"] = send_detail
            except BrowserTimeout:
                rec["status"] = "TIMEOUT"
                rec["detail"] = "BrowserTimeout"
            except BrowserError as e:
                rec["status"] = "BROWSER_ERROR"
                rec["detail"] = type(e).__name__
            finally:
                try:
                    ctx.close()
                except Exception:
                    pass
            results.append(rec)
            print(f"  -> {rec['status']} | method={rec['login_method']} | {rec['detail']}", flush=True)

    summary = {
        "updated_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(timespec="seconds"),
        "role": role,
        "invite_hint": code[:7] + "..." + code[-4:],
        "total": len(results),
        "dispatched": sum(1 for r in results if r["status"] == "DISPATCHED"),
        "results": results,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    acc_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else (HELPER_ROOT / "pending_accounts.txt")
    role_arg = sys.argv[2] if len(sys.argv) > 2 else "research"
    lim_arg = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    skip_arg = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    out = dispatch_accounts(acc_path, role=role_arg, limit=lim_arg, skip=skip_arg)
    print(json.dumps(out, ensure_ascii=False, indent=2))
