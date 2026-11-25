"""Muse Roundtable Council ⇄ Telegram 2-Way Group Bridge (Tier-3 R&D Isolated).

Tuân thủ nghiêm ngặt luật hệ thống (AGENTS.md & PINNED_RULES.json):
- [L060/L008] Cách ly 100% khỏi Tầng 1 (`Lay video tiktok/telegram_bot.py` & `facebook`).
  Dùng Bot Token riêng và tệp trạng thái riêng trong `RAG/data/`.
- [L065] KHÔNG lưu hay in token/secret/invite code ra code, git, stdout hoặc log.
  Đọc `bot_token` duy nhất từ `%LOCALAPPDATA%/MuseLoginHelper/telegram_council.json`.
- [L016] Chỉ phát ngôn trên nhóm Telegram từ kết quả thật do các phiên Muse nộp về
  AgentNet Hub `:8110` (trừ lời khai mạc điều phối của bàn tròn được ghi nhãn rõ).
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import html
import json
import os
import pathlib
import re
import socket
import sys
import time
from typing import Any, Callable

import requests
import urllib3.util.connection

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAG_ROOT = pathlib.Path(__file__).resolve().parent
DATA_DIR = RAG_ROOT / "data"
MACRO_TOOL = pathlib.Path(r"D:\0.1_FACE_BOOK\macro-tool")
HELPER_ROOT = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "MuseLoginHelper"
DEFAULT_CONFIG_PATH = HELPER_ROOT / "telegram_council.json"
DEFAULT_STATE_PATH = DATA_DIR / "muse_council_ghost_vn_state.json"
LOCK_PATH = DATA_DIR / "muse_telegram_council.pid"

PERSONAS: dict[str, dict[str, str]] = {
    "chief": {
        "badge": "👑 MUSE CHÍNH (Tổng Đạo Diễn)",
        "queue_role": "research",
        "focus": "Điều phối bàn tròn, chất vấn chéo các Muse Phụ, tổng hợp quyết định chiến lược và chốt kịch bản Pilot.",
    },
    "folklore": {
        "badge": "📜 MUSE PHỤ 1 · Dân Gian & Kịch Bản",
        "queue_role": "research",
        "focus": "Kho tích truyện ma dân gian Việt Nam 3 miền, tâm lý rợn gáy đời thường & nhân quả, Hook 3s đầu và cấu trúc giữ chân.",
    },
    "visual": {
        "badge": "🎨 MUSE PHỤ 2 · Hình Ảnh & Pipeline Dựng",
        "queue_role": "research",
        "focus": "Visual DNA thuần Việt (tránh lẫn cổ trang Trung Quốc), định dạng 9:16 vs 16:9, pipeline dựng tự động RTX 5060 Ti + FFmpeg/HyperFrames.",
    },
    "audio": {
        "badge": "🔊 MUSE PHỤ 3 · Giọng Kể & Âm Thanh 3D",
        "queue_role": "research",
        "focus": "Thiết kế giọng kể chuyện đêm khuya OmniVoice, nhịp ngắt nghỉ rùng rợn, nhạc cụ ngũ cung Việt Nam & ducking chống lấn lời.",
    },
    "qc": {
        "badge": "🛡️ MUSE PHỤ 4 · Phản Biện & QC An Toàn Kênh",
        "queue_role": "verify",
        "focus": "Vạch rủi ro gậy máu me/mê tín/Reused Content trên FB/TikTok/YT, chống lọt chữ Hán/nhảy mặt, thiết kế QC 2 tầng.",
    },
}


def redact_secret(text: str, secret: str = "") -> str:
    """Xóa sạch mọi dấu vết bot token / mã mời khỏi chuỗi log hoặc lỗi (L065)."""
    if not text:
        return ""
    out = str(text)
    if secret:
        out = out.replace(secret, "[REDACTED_TOKEN]")
    out = re.sub(r"(?:bot)?\d{8,12}:[A-Za-z0-9_-]{25,60}", "bot[REDACTED_BOT_TOKEN]", out)
    out = re.sub(r"\bMUSE-[A-Z0-9]{10,24}\b", "[REDACTED_INVITE]", out)
    return out


def load_council_config(path: pathlib.Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {"bot_token": "", "group_chat_id": "", "topic_title": "Làm Video Truyện Ma Dân Gian Việt Nam"}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def save_council_config(cfg: dict[str, Any], path: pathlib.Path = DEFAULT_CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_state(path: pathlib.Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    default: dict[str, Any] = {
        "session_id": f"ghost-vn-{dt.datetime.now().strftime('%Y%m%d')}",
        "topic": "Làm Video Truyện Ma Dân Gian Việt Nam",
        "tg_offset": 0,
        "opening_queued": False,
        "round1_enqueued": False,
        "round2_enqueued": False,
        "chief_synthesis_enqueued": False,
        "tasks": {},  # task_id -> {persona, round, title, dedup, announced, summary_text, reply_to_msg_id}
        "outbox": [],  # [{id, persona, html_text, reply_to_message_id, sent, sent_at, message_id}]
        "transcript": [],  # [{ts, speaker, text}]
        "user_messages": [],  # [{message_id, user, text, ts, handled}]
    }
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                default.update(loaded)
        except Exception:
            pass
    return default


def save_state(state: dict[str, Any], path: pathlib.Path = DEFAULT_STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


class TelegramBridge:
    """Cầu nối Telegram an toàn: kết nối trực tiếp qua IP sạch 149.154.166.110 (<0.3s, vượt chặn DNS VN) kèm dự phòng VPS."""

    TG_VERIFIED_IP = "149.154.166.110"

    def __init__(self, config_path: pathlib.Path = DEFAULT_CONFIG_PATH, prefer_vps: bool = False):
        self.config_path = config_path
        self._prefer_vps = prefer_vps
        self._ssh = None

    def _creds(self) -> tuple[str, str]:
        cfg = load_council_config(self.config_path)
        return str(cfg.get("bot_token") or "").strip(), str(cfg.get("group_chat_id") or "").strip()

    def _get_ssh(self):
        if self._ssh is not None:
            t = self._ssh.get_transport()
            if t is not None and t.is_active():
                return self._ssh
            try:
                self._ssh.close()
            except Exception:
                pass
            self._ssh = None
        if str(MACRO_TOOL) not in sys.path:
            sys.path.insert(0, str(MACRO_TOOL))
        from vps_ssh_helper import connect_vps_ssh

        self._ssh = connect_vps_ssh()
        return self._ssh

    def _call_direct(self, token: str, method: str, payload: dict[str, Any] | None, timeout: int = 8) -> dict[str, Any]:
        import subprocess

        # Chỉ giấu URL chứa token trong stdin (-K -); body JSON không chứa secret truyền qua --data-raw (tránh lỗi cú pháp quote của curl config)
        curl_cfg = (
            f'url = "https://api.telegram.org/bot{token}/{method}"\n'
            f"silent\n"
            f"max-time = {max(6, int(timeout))}\n"
        )
        cmd = [
            "curl.exe" if os.name == "nt" else "curl",
            "-4",
            "--resolve",
            f"api.telegram.org:443:{self.TG_VERIFIED_IP}",
        ]
        if payload:
            body_str = json.dumps(payload, ensure_ascii=False)
            cmd.extend(["-H", "Content-Type: application/json", "--data-raw", body_str])
        cmd.extend(["-K", "-"])
        proc = subprocess.run(
            cmd,
            input=curl_cfg,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=max(10, int(timeout) + 4),
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            raise RuntimeError(f"curl_rc_{proc.returncode}")
        return json.loads(proc.stdout)

    def _call_via_vps(self, token: str, method: str, payload: dict[str, Any] | None, timeout: int = 12) -> dict[str, Any]:
        remote_py = r"""
import json, subprocess, sys
req_in = json.loads(sys.stdin.read())
tok = req_in["tok"]
method = req_in["method"]
body_str = json.dumps(req_in.get("params") or {}, ensure_ascii=False)
timeout = max(5, int(req_in.get("timeout") or 10))
nl = chr(10)
url_cfg = f'url = "https://api.telegram.org/bot{tok}/{method}"' + nl + 'silent' + nl + f'max-time = {timeout}' + nl
proc = subprocess.run(
    ["curl", "-4", "-X", "POST", "-H", "Content-Type: application/json", "--data-binary", body_str, "-K", "-"],
    input=url_cfg,
    text=True,
    encoding="utf-8",
    capture_output=True,
)
out = (proc.stdout or "").strip()
print(out if out else json.dumps({"ok": False, "description": f"vps_curl_rc_{proc.returncode}"}))
"""
        code_b64 = base64.b64encode(remote_py.encode("utf-8")).decode("ascii")
        for attempt in range(2):
            try:
                ssh = self._get_ssh()
                stdin, stdout, _ = ssh.exec_command(
                    f"python3 -c \"import base64; exec(base64.b64decode('{code_b64}').decode('utf-8'))\""
                )
                stdin.write(json.dumps({"tok": token, "method": method, "params": payload or {}, "timeout": timeout}))
                stdin.channel.shutdown_write()
                raw = stdout.read().decode("utf-8", errors="replace").strip()
                return json.loads(raw) if raw else {"ok": False, "description": "empty_vps_response"}
            except Exception:
                self._ssh = None
                if attempt == 1:
                    raise
        return {"ok": False, "description": "vps_unreachable"}

    def api(self, method: str, payload: dict[str, Any] | None = None, timeout: int = 12) -> dict[str, Any]:
        token, _ = self._creds()
        if not token:
            return {"ok": False, "description": "missing_bot_token"}

        res: dict[str, Any] = {"ok": False, "description": "uninitialized"}
        if not self._prefer_vps:
            try:
                res = self._call_direct(token, method, payload, timeout=max(12, timeout))
            except Exception:
                self._prefer_vps = True

        if self._prefer_vps or "ok" not in res:
            try:
                res = self._call_via_vps(token, method, payload, timeout=timeout)
            except Exception as exc:
                return {"ok": False, "description": redact_secret(f"transport_error:{type(exc).__name__}", token)}

        if res.get("error_code") == 429:
            wait_s = min(int((res.get("parameters") or {}).get("retry_after") or 4), 35)
            time.sleep(wait_s + 1.0)
            try:
                if not self._prefer_vps:
                    res = self._call_direct(token, method, payload, timeout=timeout)
                else:
                    res = self._call_via_vps(token, method, payload, timeout=timeout)
            except Exception as exc:
                return {"ok": False, "description": redact_secret(f"transport_error:{type(exc).__name__}", token)}
        return res

    def discover_and_bind_group(self, state: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
        """Đọc getUpdates: tự phát hiện nhóm Telegram mới nếu chưa cấu hình, đồng thời trả danh sách tin nhắn người dùng."""
        _, current_gid = self._creds()
        offset = int(state.get("tg_offset") or 0)
        res = self.api("getUpdates", {"offset": offset, "timeout": 1, "allowed_updates": ["message", "my_chat_member"]}, timeout=10)
        if not res.get("ok"):
            return current_gid, []

        discovered_gid = current_gid
        discovered_title = ""
        new_user_msgs: list[dict[str, Any]] = []

        for upd in res.get("result") or []:
            uid = int(upd.get("update_id") or 0)
            if uid >= offset:
                state["tg_offset"] = uid + 1

            for key in ("my_chat_member", "message"):
                obj = upd.get(key)
                if not isinstance(obj, dict):
                    continue
                chat = obj.get("chat") or {}
                ctype = str(chat.get("type") or "")
                cid = str(chat.get("id") or "")
                if ctype in ("group", "supergroup") and cid:
                    # Nếu nhóm nâng cấp lên supergroup
                    mig = obj.get("migrate_to_chat_id")
                    if mig:
                        cid = str(mig)
                    if not discovered_gid or ctype == "supergroup" and discovered_gid.startswith("-") and not discovered_gid.startswith("-100"):
                        discovered_gid = cid
                        discovered_title = str(chat.get("title") or "")

            msg = upd.get("message")
            if isinstance(msg, dict):
                chat = msg.get("chat") or {}
                cid = str(chat.get("id") or "")
                sender = msg.get("from") or {}
                if sender.get("is_bot"):
                    continue
                if discovered_gid and cid != discovered_gid:
                    continue
                text = str(msg.get("text") or msg.get("caption") or "").strip()
                media_info = _extract_telegram_media_info(msg)
                if not text and not media_info:
                    continue
                uname = (
                    " ".join(filter(None, [sender.get("first_name"), sender.get("last_name")])).strip()
                    or sender.get("username")
                    or "Chủ dự án"
                )
                new_user_msgs.append(
                    {
                        "message_id": msg.get("message_id"),
                        "chat_id": cid,
                        "user": uname,
                        "text": text,
                        "media": media_info,
                        "ts": int(msg.get("date") or time.time()),
                        "handled": False,
                    }
                )

        if discovered_gid and discovered_gid != current_gid:
            cfg = load_council_config(self.config_path)
            cfg["group_chat_id"] = discovered_gid
            if discovered_title:
                cfg["group_title"] = discovered_title
            save_council_config(cfg, self.config_path)

        return discovered_gid, new_user_msgs

    def send_photo_url(self, chat_id: str, photo_url: str, caption_html: str = "", reply_to_message_id: int | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": str(chat_id),
            "photo": photo_url,
            "caption": (caption_html or "")[:1000],
            "parse_mode": "HTML",
        }
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        res = self.api("sendPhoto", payload, timeout=20)
        if not res.get("ok") and "parse entities" in str(res.get("description") or "").lower():
            payload.pop("parse_mode", None)
            payload["caption"] = re.sub(r"<[^>]+>", "", caption_html or "")[:1000]
            res = self.api("sendPhoto", payload, timeout=20)
        return res

    def download_telegram_file(self, file_id: str, dest_dir: pathlib.Path) -> pathlib.Path | None:
        """Tải video/ảnh/file do Chủ dự án thả vào nhóm Telegram về RAG/data/council_inbox qua VPS tiếp sức."""
        token, _ = self._creds()
        if not token or not file_id:
            return None
        info = self.api("getFile", {"file_id": file_id}, timeout=15)
        if not info.get("ok"):
            return None
        file_path = str((info.get("result") or {}).get("file_path") or "").strip()
        if not file_path:
            return None
        dest_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", pathlib.Path(file_path).name)
        local_target = dest_dir / f"{int(time.time())}_{safe_name}"

        remote_py = """
import base64, json, subprocess, sys
req_in = json.loads(sys.stdin.read())
tok = req_in["tok"]
fpath = req_in["file_path"]
url_cfg = f'url = "https://api.telegram.org/file/bot{tok}/{fpath}"\\nsilent\\nmax-time = 45\\n'
proc = subprocess.run(["curl", "-4", "-K", "-"], input=url_cfg.encode("utf-8"), capture_output=True)
if proc.returncode == 0 and proc.stdout:
    sys.stdout.write(base64.b64encode(proc.stdout).decode("ascii"))
"""
        code_b64 = base64.b64encode(remote_py.encode("utf-8")).decode("ascii")
        ssh = self._get_ssh()
        stdin, stdout, _ = ssh.exec_command(
            f"python3 -c \"import base64; exec(base64.b64decode('{code_b64}').decode('utf-8'))\""
        )
        stdin.write(json.dumps({"tok": token, "file_path": file_path}))
        stdin.channel.shutdown_write()
        b64_data = stdout.read().decode("ascii", errors="ignore").strip()
        if not b64_data:
            return None
        local_target.write_bytes(base64.b64decode(b64_data))
        return local_target

    def send_html(self, chat_id: str, html_text: str, reply_to_message_id: int | None = None) -> dict[str, Any]:
        chunks = split_telegram_html(html_text, max_len=3800)
        last_res: dict[str, Any] = {"ok": False, "description": "empty"}
        target_chat = str(chat_id)
        for idx, chunk in enumerate(chunks):
            payload: dict[str, Any] = {
                "chat_id": target_chat,
                "text": chunk,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
            if idx == 0 and reply_to_message_id:
                payload["reply_to_message_id"] = reply_to_message_id
            res = self.api("sendMessage", payload, timeout=15)
            if not res.get("ok"):
                # Supergroup migration retry
                mig = (res.get("parameters") or {}).get("migrate_to_chat_id")
                if mig:
                    target_chat = str(mig)
                    cfg = load_council_config(self.config_path)
                    cfg["group_chat_id"] = target_chat
                    save_council_config(cfg, self.config_path)
                    payload["chat_id"] = target_chat
                    res = self.api("sendMessage", payload, timeout=15)
                elif res.get("error_code") == 429:
                    wait_s = min(int((res.get("parameters") or {}).get("retry_after") or 3), 8)
                    time.sleep(wait_s)
                    res = self.api("sendMessage", payload, timeout=15)
                elif "parse entities" in str(res.get("description") or "").lower():
                    plain_payload = dict(payload)
                    plain_payload.pop("parse_mode", None)
                    plain_payload["text"] = re.sub(r"<[^>]+>", "", chunk)
                    res = self.api("sendMessage", plain_payload, timeout=15)
            last_res = res
            if not res.get("ok"):
                break
            if idx < len(chunks) - 1:
                time.sleep(0.8)
        return last_res


def _extract_telegram_media_info(msg: dict[str, Any]) -> dict[str, Any] | None:
    """Trích xuất metadata tệp video/ảnh/document nếu người dùng thả trực tiếp vào nhóm Telegram."""
    if isinstance(msg.get("video"), dict):
        v = msg["video"]
        return {"kind": "video", "file_id": v.get("file_id"), "file_name": v.get("file_name") or "video.mp4"}
    if isinstance(msg.get("document"), dict):
        d = msg["document"]
        mime = str(d.get("mime_type") or "").lower()
        kind = "video" if "video" in mime else ("photo" if "image" in mime else "document")
        return {"kind": kind, "file_id": d.get("file_id"), "file_name": d.get("file_name") or "file.bin"}
    if isinstance(msg.get("photo"), list) and msg["photo"]:
        p = msg["photo"][-1]
        return {"kind": "photo", "file_id": p.get("file_id"), "file_name": "photo.jpg"}
    return None


def run_qa_qc_exchange_for_video(video_path: pathlib.Path) -> dict[str, Any]:
    """Chạy QC Tầng 1 (qc_engine.py 0-token) + tải Contact Sheet 3x2 lên file_exchange (L065) để đội Muse chấm Tầng 2."""
    import file_exchange
    import qc_engine

    rep = qc_engine.qc_video(str(video_path), channel="COUNCIL_GHOST_VN", make_sheet=True)
    sheet_url = ""
    sheet_str = str(rep.get("contact_sheet") or "")
    if sheet_str and pathlib.Path(sheet_str).is_file():
        up = file_exchange.upload_temp_share(pathlib.Path(sheet_str))
        sheet_url = str(up.get("url") or "")
    rep["contact_sheet_url"] = sheet_url
    return rep


def split_telegram_html(text: str, max_len: int = 3800) -> list[str]:
    """Chia văn bản dài theo dòng/đoạn sao cho không cắt ngang thẻ HTML cơ bản."""
    clean = (text or "").strip()
    if not clean:
        return []
    if len(clean) <= max_len:
        return [clean]
    paragraphs = clean.split("\n\n")
    chunks: list[str] = []
    buf = ""
    for para in paragraphs:
        candidate = f"{buf}\n\n{para}".strip() if buf else para
        if len(candidate) <= max_len:
            buf = candidate
        else:
            if buf:
                chunks.append(buf)
                buf = ""
            if len(para) <= max_len:
                buf = para
            else:
                lines = para.split("\n")
                for line in lines:
                    c2 = f"{buf}\n{line}".strip() if buf else line
                    if len(c2) <= max_len:
                        buf = c2
                    else:
                        if buf:
                            chunks.append(buf)
                        while len(line) > max_len:
                            chunks.append(line[:max_len])
                            line = line[max_len:]
                        buf = line
    if buf:
        chunks.append(buf)
    return chunks


def _md_to_tg_html(raw_text: str) -> str:
    """Chuyển Markdown nhẹ từ kết quả Muse sang HTML an toàn của Telegram."""
    escaped = html.escape(raw_text or "")
    # **bold** -> <b>bold</b>
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    # ### Heading -> 📌 <b>Heading</b>
    escaped = re.sub(r"(?m)^#{1,4}\s+(.+)$", r"🔸 <b>\1</b>", escaped)
    # `code` -> <code>code</code>
    escaped = re.sub(r"`([^`\n]{1,120})`", r"<code>\1</code>", escaped)
    return escaped


def format_muse_turn_html(persona_key: str, round_label: str, result_obj: Any) -> str:
    """Biến JSON/Markdown result từ Muse trên :8110 thành bài phát biểu hội thoại đẹp trên Telegram."""
    persona = PERSONAS.get(persona_key, {"badge": f"🤖 MUSE ({persona_key.upper()})"})
    header = f"<b>{html.escape(persona['badge'])}</b>\n<i>📍 {html.escape(round_label)}</i>\n{'─' * 22}"

    if isinstance(result_obj, str):
        body_raw = result_obj
    elif isinstance(result_obj, dict):
        parts: list[str] = []
        # Ưu tiên trường speech / dialogue / discussion_post nếu Muse viết đúng dạng đối thoại bàn tròn
        for k in ("dialogue_speech", "speech", "council_message", "summary", "executive_summary", "analysis", "content", "report"):
            val = result_obj.get(k)
            if isinstance(val, str) and val.strip():
                parts.append(val.strip())
                break
        # Các mục chi tiết có cấu trúc
        skip_keys = {
            "outcome", "status", "dialogue_speech", "speech", "council_message",
            "summary", "executive_summary", "analysis", "content", "report",
            "evidence_links", "limitations",
        }
        for k, val in result_obj.items():
            if k in skip_keys or val in (None, "", [], {}):
                continue
            pretty_k = k.replace("_", " ").strip().title()
            if isinstance(val, str):
                parts.append(f"**{pretty_k}:**\n{val.strip()}")
            elif isinstance(val, list):
                lines = []
                for idx, item in enumerate(val[:12], 1):
                    if isinstance(item, str):
                        lines.append(f"• {item}")
                    elif isinstance(item, dict):
                        title = item.get("title") or item.get("name") or item.get("story") or item.get("step") or f"Mục {idx}"
                        desc_bits = [
                            f"{ik}: {iv}"
                            for ik, iv in item.items()
                            if ik not in ("title", "name", "story", "step") and iv not in (None, "", [], {})
                        ]
                        lines.append(f"• **{title}** — " + "; ".join(desc_bits[:5]))
                if lines:
                    parts.append(f"**{pretty_k}:**\n" + "\n".join(lines))
            elif isinstance(val, dict):
                sub_lines = [f"• **{sk}**: {sv}" for sk, sv in list(val.items())[:10] if sv not in (None, "", [], {})]
                if sub_lines:
                    parts.append(f"**{pretty_k}:**\n" + "\n".join(sub_lines))

        lims = result_obj.get("limitations")
        if isinstance(lims, list) and lims:
            parts.append("**Giới hạn / Cần kiểm chứng thêm:**\n" + "\n".join(f"⚠️ {x}" for x in lims[:4]))
        elif isinstance(lims, str) and lims.strip():
            parts.append(f"**Giới hạn / Cần kiểm chứng thêm:** ⚠️ {lims.strip()}")

        body_raw = "\n\n".join(parts).strip()
        if not body_raw:
            body_raw = json.dumps(result_obj, ensure_ascii=False, indent=2)
    else:
        body_raw = str(result_obj)

    return f"{header}\n\n{_md_to_tg_html(body_raw)}"


def queue_outbox_message(
    state: dict[str, Any],
    persona_key: str,
    html_text: str,
    dedup_key: str,
    reply_to_message_id: int | None = None,
) -> bool:
    for item in state.setdefault("outbox", []):
        if item.get("id") == dedup_key:
            return False
    state["outbox"].append(
        {
            "id": dedup_key,
            "persona": persona_key,
            "html_text": html_text,
            "reply_to_message_id": reply_to_message_id,
            "created_at": time.time(),
            "sent": False,
            "sent_at": None,
        }
    )
    return True


def flush_outbox(state: dict[str, Any], bridge: TelegramBridge, chat_id: str) -> int:
    if not chat_id:
        return 0
    sent_count = 0
    for item in state.get("outbox", []):
        if item.get("sent"):
            continue
        res = bridge.send_html(chat_id, item["html_text"], reply_to_message_id=item.get("reply_to_message_id"))
        if res.get("ok"):
            item["sent"] = True
            item["sent_at"] = time.time()
            item["message_id"] = (res.get("result") or {}).get("message_id")
            sent_count += 1
            time.sleep(1.0)
        else:
            item["last_error"] = redact_secret(str(res.get("description") or "send_failed"))
            break
    return sent_count


def build_opening_chief_html(topic: str) -> str:
    badge = PERSONAS["chief"]["badge"]
    return (
        f"<b>{html.escape(badge)}</b>\n"
        f"<i>📍 Khai mạc Phiên Họp Bàn Tròn Đa Muse (AgentNet :8110)</i>\n"
        f"{'─' * 22}\n\n"
        f"Chào Chủ dự án và toàn thể anh em đội Muse! Tôi là <b>Muse Chính</b>, hôm nay triệu tập cuộc họp bàn tròn "
        f"chuyên đề:\n"
        f"👻 <b>{html.escape(topic.upper())}</b>\n\n"
        f"Tôi chia bàn tròn thành <b>4 mũi chuyên môn</b> cho 4 Muse Phụ trên <code>muse.ai</code> vào mổ xẻ song song ngay bây giờ:\n"
        f"1️⃣ <b>📜 Muse Phụ 1 (Dân Gian &amp; Kịch Bản):</b> Chọn lọc kho tích truyện ma dân gian Bắc – Trung – Nam dễ viral nhất, công thức Hook 0–3s và cốt truyện nhân quả giữ chân người xem.\n"
        f"2️⃣ <b>🎨 Muse Phụ 2 (Hình Ảnh &amp; Pipeline Dựng):</b> Khóa Visual DNA làng quê Việt cổ (không lẫn cổ trang Trung Quốc/chữ Hán), so sánh Shorts 9:16 vs Kể chuyện đêm khuya 16:9, thiết kế pipeline dựng tự động trên RTX 5060 Ti + FFmpeg/HyperFrames.\n"
        f"3️⃣ <b>🔊 Muse Phụ 3 (Giọng Kể &amp; Âm Thanh 3D):</b> Thiết kế giọng đọc đêm khuya OmniVoice, nhịp ngắt nghỉ rợn gáy, lớp tiếng mưa đêm/võng tre/đàn bầu ngũ cung và công thức ducking không lấn lời.\n"
        f"4️⃣ <b>🛡️ Muse Phụ 4 (Phản Biện &amp; QC An Toàn):</b> Đóng vai giám khảo bắt lỗi — chỉ rõ bẫy gậy máu me/mê tín/Reused Content trên FB/TikTok/YouTube và bộ tiêu chuẩn QC 2 tầng trước khi đăng.\n\n"
        f"⏳ <i>4 Muse Phụ đang nhận đề bài trên Sảnh :8110. Ngay khi từng Muse phát biểu xong Vòng 1, chúng ta sẽ bước sang Vòng 2 phản biện chéo và tôi sẽ chốt Kịch Bản Tập Pilot #1!</i>\n"
        f"💬 <b>Chủ dự án có thể nhắn trực tiếp ý kiến, câu hỏi hoặc đổi hướng ngay trong nhóm này bất cứ lúc nào!</b>"
    )


def build_round1_task_specs(session_id: str, topic: str) -> list[tuple[str, dict[str, Any]]]:
    """Tạo 4 task Vòng 1 cho 4 Muse Phụ thật trên AgentNet Hub :8110."""
    common_rules = (
        "Bạn đang tham gia CUỘC TRÒ CHUYỆN BÀN TRÒN TRỰC TIẾP trên nhóm Telegram cùng Chủ dự án, Muse Chính và 3 Muse Phụ khác. "
        "Hãy viết trường `dialogue_speech` bằng tiếng Việt tự nhiên, sắc sảo như đang phát biểu trực tiếp trong phòng họp "
        "(xưng 'Tôi - [Tên vai trò]', gọi 'Muse Chính', 'Chủ dự án' và nêu rõ điểm muốn phối hợp hoặc tranh luận với các Muse Phụ khác). "
        "Không bịa số liệu chưa kiểm chứng; nêu rõ `limitations`."
    )
    specs: list[tuple[str, dict[str, Any]]] = [
        (
            "folklore",
            {
                "dedup": f"{session_id}:r1:folklore",
                "project": "research",
                "assigned_to": "research",
                "kind": "council_round1_folklore",
                "auto_verify": False,
                "payload": {
                    "round": "Vòng 1 · Khảo sát Chất liệu Dân Gian & Kịch Bản",
                    "persona": PERSONAS["folklore"]["badge"],
                    "topic": topic,
                    "meeting_instruction": common_rules,
                    "objectives": [
                        "1. Tuyển chọn Top 10 tích truyện/hình tượng ma dân gian Việt Nam giàu sức hút nhất chia theo Bắc - Trung - Nam (ví dụ: Ma Da kéo giò sông nước miền Tây, Chó Đội Nón Mê, Linh Miêu hoàn hồn, Thần Trùng, Ma Gà/Ma Xó vùng cao, Oan hồn Lệ Chi Viên, Tiếng rao đêm xóm vắng...) kèm lý do vì sao hợp tâm lý người Việt.",
                        "2. Đề xuất cấu trúc kịch bản 2 tuyến: (A) Video dọc 9:16 60–90 giây làm phễu kéo view/follow, và (B) Tập kể chuyện đêm khuya 12–20 phút giữ chân sâu — đặc biệt nhấn mạnh yếu tố 'đời thường quen thuộc + luật nhân quả dân gian' thay vì máu me rẻ tiền.",
                        "3. Viết sẵn 6 câu Hook mở đầu 3 giây đầu tiên (0–3s) đậm chất truyền khẩu Việt Nam khiến người lướt đêm khuya không thể vuốt qua.",
                        "4. Đặt 2 câu hỏi trực tiếp gửi sang Muse Hình Ảnh và Muse Âm Thanh để phối hợp ở Vòng 2.",
                    ],
                },
            },
        ),
        (
            "visual",
            {
                "dedup": f"{session_id}:r1:visual",
                "project": "research",
                "assigned_to": "engineer",
                "kind": "council_round1_visual_pipeline",
                "auto_verify": False,
                "payload": {
                    "round": "Vòng 1 · Visual DNA Thuần Việt & Pipeline Dựng Tự Động",
                    "persona": PERSONAS["visual"]["badge"],
                    "topic": topic,
                    "meeting_instruction": common_rules,
                    "hardware_context": "Máy trạm Windows RTX 5060 Ti 16GB + FFmpeg + Python + HyperFrames/GSAP + Muse vẽ ảnh (lưu ý hệ thống đã tắt LoRA/SDXL local nặng để ưu tiên pipeline ổn định).",
                    "objectives": [
                        "1. Xây dựng bộ quy tắc 'Visual DNA Làng Quê Việt Cổ' (nhà ba gian mái ngói ta rêu phong, đèn dầu hột vịt, lũy tre làng, áo bà ba/áo tơi/khăn mỏ quạ, cầu khỉ bến sông, bàn thờ gỗ mộc) và danh sách Negative Prompt chặn triệt để lỗi AI vẽ ra đèn lồng đỏ Trung Quốc, mái cong cung đình Hán phục hoặc lọt chữ Hán trên bùa/biển hiệu.",
                        "2. Thiết kế Pipeline dựng video tự động không bị nhàm chán như ảnh tĩnh: kết hợp chuyển động camera Ken Burns mượt, lớp overlay sương mù là là mặt nước, hạt bụi trôi dưới ánh đèn dầu lập lòe, chớp giật chuyển cảnh bằng FFmpeg hoặc HTML/GSAP (HyperFrames) chuẩn 1080x1920 (9:16) và 1920x1080 (16:9).",
                        "3. Giải pháp giữ đồng nhất gương mặt nhân vật chính xuyên suốt 10–18 cảnh trong 1 tập truyện (Character Reference Sheet 6 ô).",
                        "4. Đặt câu hỏi ngược lại cho Muse Kịch Bản và Muse QC về mật độ đổi cảnh (bao nhiêu giây/cảnh là tối ưu).",
                    ],
                },
            },
        ),
        (
            "audio",
            {
                "dedup": f"{session_id}:r1:audio",
                "project": "research",
                "assigned_to": "research",
                "kind": "council_round1_audio_sfx",
                "auto_verify": False,
                "payload": {
                    "round": "Vòng 1 · Giọng Kể Đêm Khuya & Không Gian Âm Thanh 3D",
                    "persona": PERSONAS["audio"]["badge"],
                    "topic": topic,
                    "meeting_instruction": common_rules,
                    "audio_context": "Hệ thống có sẵn OmniVoice TTS tiếng Việt + FFmpeg filter (`ebur128`, `sidechaincompress`, tách/trộn stem). Bài học thực tế từ K04/K05: nếu nhạc nền dày dải trầm sẽ lấn giọng đọc.",
                    "objectives": [
                        "1. Thiết kế chất giọng kể chuyện ma dân gian Việt Nam (so sánh giọng Nam trầm khàn kiểu bác Nguyễn Ngọc Ngạn / giọng bà lão miền Bắc thầm thì / giọng miền Tây kể chuyện sông nước): tốc độ đọc, quãng nghỉ lặng 0.5–0.8s trước cú twist, và cách tách giọng dẫn chuyện với câu thoại ma mị.",
                        "2. Thiết kế Bảng phân lớp âm thanh 3 tầng: (Tầng 1) Giọng đọc sạch dải 300–3400Hz; (Tầng 2) Ambience làng quê Việt về đêm (tiếng mưa rơi mái lá, tiếng ếch nhái/dế kêu, tiếng chó tru xa xăm, tiếng kẽo kẹt võng tre/cọt kẹt tre già); (Tầng 3) Điểm xuyết âm sắc đàn bầu, đàn nhị hoặc sáo tiêu ngũ cung đúng chỗ cao trào.",
                        "3. Đề xuất chuỗi filter FFmpeg chuẩn (LUFS mục tiêu -14 đến -16 LUFS, True Peak <= -1.5 dBTP, highpass/lowpass cho BGM, sidechain ducking) để người nghe đeo tai nghe ban đêm vừa rợn tóc gáy vừa nghe rõ từng chữ.",
                    ],
                },
            },
        ),
        (
            "qc",
            {
                "dedup": f"{session_id}:r1:qc",
                "project": "research",
                "assigned_to": "verify",
                "kind": "council_round1_qc_safety",
                "auto_verify": False,
                "payload": {
                    "round": "Vòng 1 · Phản Biện Chính Sách Nền Tảng & Chuẩn QC 2 Tầng",
                    "persona": PERSONAS["qc"]["badge"],
                    "topic": topic,
                    "meeting_instruction": common_rules,
                    "qc_context": "Hệ thống đang vận hành QC 2 tầng (`qc_engine.py` 0-token quét khung đen/đứng hình/OCR chữ Trung/LUFS/clipping + Muse chấm điểm người xem) và có kênh sandbox K08 để thử nghiệm cách ly Tầng 1.",
                    "objectives": [
                        "1. Đóng vai người phản biện khó tính: chỉ ra 5 rủi ro bóp tương tác, vàng tiền hoặc gậy cộng đồng trên Facebook Reels, YouTube và TikTok khi làm chủ đề truyện ma (máu me Gore, hình ảnh xác chết biến dạng, hù dọa Jump-scare quá đà, tuyên truyền bùa ngải/mê tín dị đoan, lỗi Reused Content do ảnh tĩnh lặp).",
                        "2. Lập 'Từ Điển Lách Từ Nhạy Cảm' cho phụ đề & giọng đọc (ví dụ thay từ nhạy cảm trực diện bằng cách gợi hình dân gian u ám mà vẫn giữ nguyên độ rợn).",
                        "3. Thiết kế Checklist Chấm Điểm QC 100 điểm chuyên biệt cho Video Truyện Ma Dân Gian Việt Nam (Tầng 1 tự động bằng code + Tầng 2 Muse soi Contact Sheet) và đề xuất quy trình thử nghiệm 5 tập đầu trên kênh thử nghiệm cách ly.",
                    ],
                },
            },
        ),
    ]
    return specs


def build_round2_and_chief_specs(
    session_id: str,
    topic: str,
    round1_summaries: dict[str, str],
    user_feedback: list[str],
) -> list[tuple[str, str, dict[str, Any]]]:
    """Tạo lượt Phản Biện Chéo (Muse QC) & Tổng Hợp Chốt Phương Án (Muse Chính) ở Vòng 2."""
    user_block = (
        "\n".join(f"- Chủ dự án nhắn trong nhóm: {m}" for m in user_feedback)
        if user_feedback
        else "- (Chủ dự án đang theo dõi, chưa bổ sung ràng buộc mới — hãy chủ động chốt phương án tối ưu nhất)."
    )
    return [
        (
            "qc",
            "Vòng 2 · Đối Chất & Phản Biện Chéo Các Đề Xuất Vòng 1",
            {
                "dedup": f"{session_id}:r2:qc-rebuttal",
                "project": "research",
                "assigned_to": "verify",
                "kind": "council_round2_rebuttal",
                "auto_verify": False,
                "payload": {
                    "round": "Vòng 2 · Phản Biện Chéo Trên Bàn Tròn",
                    "persona": PERSONAS["qc"]["badge"],
                    "topic": topic,
                    "round1_transcript": round1_summaries,
                    "owner_messages_from_telegram": user_block,
                    "objectives": [
                        "1. Đọc kỹ phát biểu Vòng 1 của Muse Dân Gian, Muse Hình Ảnh và Muse Âm Thanh ở trên. Chỉ thẳng 3 điểm mâu thuẫn hoặc dễ vấp lỗi thực tế nhất giữa kịch bản - hình ảnh - âm thanh (ví dụ cảnh quá tối bị nén bệt màu trên Facebook Reels, nhịp đổi cảnh quá chậm gây rớt người xem ở giây thứ 8, hoặc tích truyện có chi tiết dễ dính gậy).",
                        "2. Đề xuất chỉnh sửa cụ thể cho từng Muse Phụ để Muse Chính ra quyết định cuối cùng.",
                    ],
                },
            },
        ),
        (
            "chief",
            "Vòng 2 (Chốt Hạ) · Quyết Định Chiến Lược & Kịch Bản Tập Pilot #1",
            {
                "dedup": f"{session_id}:r2:chief-synthesis",
                "project": "research",
                "assigned_to": "research",
                "kind": "council_chief_synthesis",
                "auto_verify": False,
                "payload": {
                    "round": "Vòng 2 · Muse Chính Tổng Hợp & Chốt Tập Pilot #1",
                    "persona": PERSONAS["chief"]["badge"],
                    "topic": topic,
                    "round1_transcript": round1_summaries,
                    "owner_messages_from_telegram": user_block,
                    "objectives": [
                        "1. Với tư cách 👑 MUSE CHÍNH, tổng kết ngắn gọn các ý kiến đắt giá nhất của 4 Muse Phụ (và ý kiến Chủ dự án nếu có), đưa ra QUYẾT ĐỊNH CHỐT cho giai đoạn 1: Chọn tỷ lệ khung hình ưu tiên (9:16 75–90s hay kết hợp), tần suất cảnh, chất giọng và kênh chạy thử nghiệm cách ly.",
                        "2. Chốt danh sách Series 5 tập mở màn đầu tiên mang bản sắc Truyện Ma Dân Gian Việt Nam.",
                        "3. Viết trọn vẹn KỊCH BẢN PHÂN CẢNH CHI TIẾT TẬP PILOT #1 (60–85 giây, chia theo từng mốc giây 0–3s, 3–15s, 15–35s, 35–60s, 60–80s: gồm Lời kể chuyện + Prompt vẽ ảnh thuần Việt + Hiệu ứng âm thanh SFX) để đội kỹ thuật có thể bấm render thử ngay!",
                        "4. Hỏi ý kiến phê duyệt của Chủ dự án ngay cuối tin nhắn trên nhóm Telegram.",
                    ],
                },
            },
        ),
    ]


def build_followup_specs(
    session_id: str,
    topic: str,
    user_name: str,
    user_text: str,
    msg_id: int,
    recent_transcript: list[dict[str, Any]],
) -> list[tuple[str, str, dict[str, Any], int]]:
    """Khi Chủ dự án nhắn câu hỏi/chỉ đạo mới trong nhóm Telegram -> phân công Muse Phụ liên quan + Muse Chính trả lời."""
    low = user_text.lower()
    chosen_sub = "folklore"
    if any(k in low for k in ("ảnh", "hình", "vẽ", "render", "ffmpeg", "9:16", "16:9", "cảnh", "visual", "dựng")):
        chosen_sub = "visual"
    elif any(k in low for k in ("giọng", "âm thanh", "nhạc", "sfx", "tts", "omnivoice", "đọc", "audio")):
        chosen_sub = "audio"
    elif any(k in low for k in ("qc", "gậy", "bản quyền", "chính sách", "lỗi", "kiểm duyệt", "an toàn")):
        chosen_sub = "qc"

    context_tail = recent_transcript[-6:]
    sub_persona = PERSONAS[chosen_sub]
    chief_persona = PERSONAS["chief"]

    return [
        (
            chosen_sub,
            f"Phản hồi chuyên môn cho {user_name}",
            {
                "dedup": f"{session_id}:usr:{msg_id}:{chosen_sub}",
                "project": "research",
                "assigned_to": sub_persona["queue_role"],
                "kind": "council_live_reply",
                "auto_verify": False,
                "payload": {
                    "round": f"Thảo luận trực tiếp · Trả lời {user_name}",
                    "persona": sub_persona["badge"],
                    "topic": topic,
                    "recent_context": context_tail,
                    "user_message": f"{user_name}: {user_text}",
                    "objectives": [
                        f"Trả lời trực tiếp, ngắn gọn, đi thẳng vào câu hỏi/chỉ đạo của {user_name} dưới góc nhìn chuyên môn của {sub_persona['badge']}. Đưa phương án hành động cụ thể."
                    ],
                },
            },
            msg_id,
        ),
        (
            "chief",
            f"Tổng hợp & điều phối theo chỉ đạo của {user_name}",
            {
                "dedup": f"{session_id}:usr:{msg_id}:chief",
                "project": "research",
                "assigned_to": "research",
                "kind": "council_live_chief_reply",
                "auto_verify": False,
                "payload": {
                    "round": f"Thảo luận trực tiếp · Muse Chính phản hồi {user_name}",
                    "persona": chief_persona["badge"],
                    "topic": topic,
                    "recent_context": context_tail,
                    "user_message": f"{user_name}: {user_text}",
                    "objectives": [
                        f"Với tư cách 👑 MUSE CHÍNH, phản hồi trực tiếp chỉ đạo/câu hỏi của {user_name}, chốt hướng điều chỉnh cho cả đội Muse Phụ và nêu bước tiếp theo rõ ràng."
                    ],
                },
            },
            msg_id,
        ),
    ]


class Hub8110Client:
    """Giao tiếp trực tiếp với ResearchQueue & HubManager trên VPS :8110 qua SSH an toàn."""

    def _exec_vps_json(self, remote_py: str, stdin_obj: Any = None) -> dict[str, Any]:
        if str(MACRO_TOOL) not in sys.path:
            sys.path.insert(0, str(MACRO_TOOL))
        from vps_ssh_helper import connect_vps_ssh

        code_b64 = base64.b64encode(remote_py.encode("utf-8")).decode("ascii")
        ssh = connect_vps_ssh()
        try:
            stdin, stdout, stderr = ssh.exec_command(
                f"python3 -c \"import base64; exec(base64.b64decode('{code_b64}').decode('utf-8'))\""
            )
            if stdin_obj is not None:
                stdin.write(json.dumps(stdin_obj, ensure_ascii=False))
                stdin.channel.shutdown_write()
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            if not out:
                return {"ok": False, "error": redact_secret(err[:300] or "empty_vps_output")}
            return json.loads(out)
        finally:
            ssh.close()

    def ensure_fresh_invite_and_role_balance(self) -> dict[str, Any]:
        """Đảm bảo có mã mời còn hạn vào Sảnh :8110 và có đủ worker cho cả 3 role (research, engineer, verify)."""
        remote_py = """
import json, pathlib, sqlite3, sys, threading, time
sys.path.insert(0, '/opt/agentnet-corner')
import corner
from hub_portal import HubManager
from research_queue import ResearchQueue

root = pathlib.Path('/opt/agentnet-corner')
reg = corner.Registry(root)
q = ResearchQueue(root)
cap_fn = getattr(corner, 'check_capacity', getattr(corner, 'enforce_capacity', lambda _r: None))
hm = HubManager(reg, q, corner.connect, cap_fn, threading.Lock())

inv = hm.create_invite(ttl_minutes=1440, max_uses=30, targets={'research': 3, 'engineer': 1, 'verify': 1}, default_role='research')

# Cân bằng các node hub-web gần nhất để có đủ research, engineer, verify nhận việc ngay
with corner.connect(root) as db:
    rows = db.execute("SELECT id, role FROM nodes WHERE status='APPROVED' ORDER BY created_at DESC LIMIT 8").fetchall()
    desired = ['research', 'engineer', 'verify', 'research', 'research']
    rebalanced = []
    for idx, r in enumerate(rows[:len(desired)]):
        target_role = desired[idx]
        if r['role'] != target_role:
            db.execute("UPDATE nodes SET role=? WHERE id=?", (target_role, r['id']))
        rebalanced.append({'node': r['id'][:8], 'role': target_role})

print(json.dumps({
    'ok': True,
    'invite_code': inv['code'],
    'invite_hint': inv['code'][:7] + '...' + inv['code'][-4:],
    'rebalanced': rebalanced,
}))
"""
        res = self._exec_vps_json(remote_py)
        if res.get("ok") and res.get("invite_code"):
            HELPER_ROOT.mkdir(parents=True, exist_ok=True)
            inv_file = HELPER_ROOT / "active_invite.json"
            inv_file.write_text(
                json.dumps(
                    {
                        "code": res["invite_code"],
                        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            res.pop("invite_code", None)  # Không giữ secret trong bộ nhớ trả ra log (L065)
        return res

    def enqueue_specs(self, specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        remote_py = """
import json, pathlib, sys, time
sys.path.insert(0, '/opt/agentnet-corner')
from research_queue import ResearchQueue

q = ResearchQueue(pathlib.Path('/opt/agentnet-corner'))
specs = json.loads(sys.stdin.read())
out = []
with q.db() as c:
    c.execute('BEGIN IMMEDIATE')
    for sp in specs:
        role, kind, dedup, payload = q._validate_task_spec(sp, 'controller')
        tid, created = q._insert_task_tx(c, role, kind, dedup, payload, time.time())
        out.append({'id': tid, 'dedup': dedup, 'assigned_to': role, 'kind': kind, 'created': created})
print(json.dumps({'ok': True, 'tasks': out}))
"""
        res = self._exec_vps_json(remote_py, stdin_obj=specs)
        return res.get("tasks") or []

    def fetch_tasks_status(self, task_ids: list[str]) -> dict[str, dict[str, Any]]:
        if not task_ids:
            return {}
        remote_py = """
import json, pathlib, sqlite3, sys, time
sys.stdout.reconfigure(encoding='utf-8')
tids = json.loads(sys.stdin.read())
c = sqlite3.connect('/opt/agentnet-corner/state/research.sqlite3')
c.row_factory = sqlite3.Row
placeholders = ','.join('?' for _ in tids)
rows = c.execute(f'SELECT id, dedup, assigned_to, kind, status, owner_node, completed_at, result FROM tasks WHERE id IN ({placeholders})', tids).fetchall()
active_15m = [list(x) for x in c.execute('SELECT role, COUNT(*) FROM activity WHERE last_seen > ? GROUP BY role', (time.time() - 900,)).fetchall()]
out = {}
for r in rows:
    d = dict(r)
    if d.get('result'):
        try:
            d['result'] = json.loads(d['result'])
        except Exception:
            pass
    out[d['id']] = d
print(json.dumps({'ok': True, 'tasks': out, 'active_15m': active_15m}, ensure_ascii=False))
"""
        res = self._exec_vps_json(remote_py, stdin_obj=task_ids)
        return res


def step_council_once(
    state: dict[str, Any],
    bridge: TelegramBridge,
    hub: Hub8110Client | None,
) -> dict[str, Any]:
    """Thực thi 1 nhịp điều phối bàn tròn:
    1) Quét nhóm Telegram (tự nhận group_chat_id + đọc câu hỏi mới của Chủ dự án)
    2) Khởi tạo lời mở màn của Muse Chính + 4 task Vòng 1 trên :8110 nếu chưa có
    3) Thu hoạch bài phát biểu đã SUBMITTED trên :8110 -> đẩy vào outbox Telegram
    4) Khi đủ kết quả Vòng 1 -> kích hoạt Vòng 2 phản biện & Muse Chính chốt kịch bản Pilot
    5) Xử lý tin nhắn trực tiếp của Chủ dự án trong nhóm Telegram
    6) Đẩy toàn bộ outbox ra nhóm Telegram
    """
    topic = state.get("topic") or "Làm Video Truyện Ma Dân Gian Việt Nam"
    session_id = state.get("session_id") or "ghost-vn"

    chat_id, new_msgs = bridge.discover_and_bind_group(state)
    for m in new_msgs:
        state.setdefault("user_messages", []).append(m)

    # 1. Lời khai mạc của Muse Chính
    if not state.get("opening_queued"):
        queue_outbox_message(
            state,
            "chief",
            build_opening_chief_html(topic),
            dedup_key=f"{session_id}:opening",
        )
        state["opening_queued"] = True

    # 2. Đẩy 4 task Vòng 1 lên :8110
    if hub is not None and not state.get("round1_enqueued"):
        r1_pairs = build_round1_task_specs(session_id, topic)
        enq = hub.enqueue_specs([sp for _, sp in r1_pairs])
        by_dedup = {sp["dedup"]: persona_key for persona_key, sp in r1_pairs}
        by_round = {sp["dedup"]: sp["payload"]["round"] for _, sp in r1_pairs}
        for item in enq:
            tid = item["id"]
            dedup = item["dedup"]
            state.setdefault("tasks", {})[tid] = {
                "persona": by_dedup[dedup],
                "round": 1,
                "round_label": by_round[dedup],
                "dedup": dedup,
                "announced": False,
                "summary_text": "",
                "reply_to_msg_id": None,
            }
        state["round1_enqueued"] = True

    # 3. Kiểm tra trạng thái các task trên :8110
    active_15m = []
    if hub is not None and state.get("tasks"):
        pending_or_unannounced = [
            tid for tid, meta in state["tasks"].items() if not meta.get("announced")
        ]
        if pending_or_unannounced:
            polled = hub.fetch_tasks_status(pending_or_unannounced)
            active_15m = polled.get("active_15m") or []
            remote_tasks = polled.get("tasks") or {}
            # Đảm bảo thứ tự Vòng 2: QC phản biện hiện trước Muse Chính chốt hạ
            ordered_tids = sorted(
                pending_or_unannounced,
                key=lambda t: (
                    state["tasks"][t].get("round", 1),
                    1 if state["tasks"][t].get("persona") == "chief" else 0,
                ),
            )
            for tid in ordered_tids:
                rmeta = remote_tasks.get(tid)
                if not rmeta or rmeta.get("status") not in ("SUBMITTED", "APPROVED"):
                    continue
                local_meta = state["tasks"][tid]
                res_obj = rmeta.get("result") or {}
                html_msg = format_muse_turn_html(
                    local_meta["persona"],
                    local_meta["round_label"],
                    res_obj,
                )
                queue_outbox_message(
                    state,
                    local_meta["persona"],
                    html_msg,
                    dedup_key=f"task:{tid}",
                    reply_to_message_id=local_meta.get("reply_to_msg_id"),
                )
                plain_excerpt = re.sub(r"<[^>]+>", "", html_msg)[:8000]
                local_meta["announced"] = True
                local_meta["summary_text"] = plain_excerpt
                state.setdefault("transcript", []).append(
                    {
                        "ts": time.time(),
                        "speaker": PERSONAS.get(local_meta["persona"], {}).get("badge", local_meta["persona"]),
                        "text": plain_excerpt,
                    }
                )

    # 4. Nếu đủ ít nhất 3/4 (hoặc 4/4) Muse Phụ Vòng 1 xong -> kích hoạt Vòng 2 Phản biện & Muse Chính Chốt
    if hub is not None and state.get("round1_enqueued") and not state.get("round2_enqueued"):
        r1_tasks = [m for m in state.get("tasks", {}).values() if m.get("round") == 1]
        r1_done = [m for m in r1_tasks if m.get("announced")]
        if len(r1_tasks) > 0 and len(r1_done) == len(r1_tasks):
            r1_map = {m["persona"]: m["summary_text"] for m in r1_done}
            user_fb = [u["text"] for u in state.get("user_messages", []) if not u["text"].startswith("/")]
            r2_triples = build_round2_and_chief_specs(session_id, topic, r1_map, user_fb)
            enq2 = hub.enqueue_specs([sp for _, _, sp in r2_triples])
            meta_by_dedup = {sp["dedup"]: (pk, rlabel) for pk, rlabel, sp in r2_triples}
            for item in enq2:
                pk, rlabel = meta_by_dedup[item["dedup"]]
                state["tasks"][item["id"]] = {
                    "persona": pk,
                    "round": 2,
                    "round_label": rlabel,
                    "dedup": item["dedup"],
                    "announced": False,
                    "summary_text": "",
                    "reply_to_msg_id": None,
                }
            state["round2_enqueued"] = True

    # 5. Xử lý các câu hỏi / lệnh mới của Chủ dự án trong nhóm Telegram
    for umsg in state.get("user_messages", []):
        if umsg.get("handled"):
            continue
        txt = umsg["text"].strip()
        mid = umsg.get("message_id")
        low = txt.lower()
        if low in ("/start", "/here", "bat dau", "bắt đầu", "alo", "ok"):
            queue_outbox_message(
                state,
                "chief",
                (
                    f"<b>👑 MUSE CHÍNH (Tổng Đạo Diễn)</b>\n"
                    f"✅ Đã kết nối phòng họp nhóm Telegram thành công! "
                    f"Các bài phát biểu của đội Muse trên <code>muse.ai</code> sẽ được phát trực tiếp tại đây. "
                    f"Bạn cứ nhắn câu hỏi hoặc chỉ đạo tự nhiên bất kỳ lúc nào nhé!"
                ),
                dedup_key=f"ack:{mid}",
                reply_to_message_id=mid,
            )
            umsg["handled"] = True
        elif low.startswith("/status"):
            total_t = len(state.get("tasks", {}))
            done_t = sum(1 for m in state.get("tasks", {}).values() if m.get("announced"))
            queue_outbox_message(
                state,
                "chief",
                (
                    f"📊 <b>Trạng thái Phòng Họp Bàn Tròn Muse</b>\n"
                    f"• Chủ đề: <b>{html.escape(topic)}</b>\n"
                    f"• Lượt phát biểu Muse hoàn tất: <b>{done_t}/{total_t}</b>\n"
                    f"• Worker hoạt động 15p gần nhất trên :8110: <code>{html.escape(json.dumps(active_15m))}</code>"
                ),
                dedup_key=f"status:{mid}",
                reply_to_message_id=mid,
            )
            umsg["handled"] = True
        elif low.startswith("/qc ") or (umsg.get("media") and (umsg["media"] or {}).get("kind") in ("video", "photo")):
            media_obj = umsg.get("media") or {}
            local_media_path: pathlib.Path | None = None
            if low.startswith("/qc "):
                cand = pathlib.Path(txt[4:].strip().strip('"'))
                if cand.is_file():
                    local_media_path = cand
            elif media_obj.get("file_id"):
                local_media_path = bridge.download_telegram_file(
                    str(media_obj["file_id"]), DATA_DIR / "council_inbox"
                )

            if local_media_path and local_media_path.is_file():
                is_vid = local_media_path.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")
                if is_vid:
                    rep = run_qa_qc_exchange_for_video(local_media_path)
                    sheet_url = rep.get("contact_sheet_url") or ""
                    t1_html = (
                        f"<b>🛡️ QC TẦNG 1 (0-TOKEN · qc_engine.py)</b>\n"
                        f"• Tệp: <code>{html.escape(local_media_path.name)}</code>\n"
                        f"• Kết luận Tầng 1: <b>{html.escape(str(rep.get('verdict')))}</b> "
                        f"(Điểm kỹ thuật: <b>{rep.get('score_tier1')}/{rep.get('score_tier1_max')}</b>)\n"
                        f"• Lỗi cứng: <code>{html.escape(json.dumps(rep.get('fail_reasons') or [], ensure_ascii=False))}</code>\n"
                        f"• Cảnh báo: <code>{html.escape(json.dumps(rep.get('warn_reasons') or [], ensure_ascii=False))}</code>\n"
                        + (f"• Contact Sheet 3x2: {html.escape(sheet_url)}\n" if sheet_url else "")
                        + "⏳ <i>Đã chuyển Contact Sheet sang Sảnh :8110 để 🛡️ Muse Phụ 4 (QC) &amp; 👑 Muse Chính chấm Tầng 2!</i>"
                    )
                    if chat_id and sheet_url:
                        bridge.send_photo_url(chat_id, sheet_url, caption_html=t1_html[:950], reply_to_message_id=mid)
                    else:
                        queue_outbox_message(state, "qc", t1_html, dedup_key=f"qct1:{mid}", reply_to_message_id=mid)

                    if hub is not None:
                        qc_spec = {
                            "dedup": f"{session_id}:qc2:{mid}",
                            "project": "research",
                            "assigned_to": "verify",
                            "kind": "council_tier2_video_qc",
                            "auto_verify": False,
                            "payload": {
                                "round": f"QC Tầng 2 · Chấm Video Thực Tế ({local_media_path.name})",
                                "persona": PERSONAS["qc"]["badge"],
                                "topic": topic,
                                "contact_sheet_url": sheet_url,
                                "tier1_report_summary": {
                                    "verdict": rep.get("verdict"),
                                    "score_tier1": rep.get("score_tier1"),
                                    "fail_reasons": rep.get("fail_reasons"),
                                    "warn_reasons": rep.get("warn_reasons"),
                                    "audio": rep.get("audio"),
                                },
                                "objectives": [
                                    "1. Mở xem trực tiếp ảnh Contact Sheet 3x2 (`contact_sheet_url`) kết hợp thông số Tầng 1.",
                                    "2. Chấm điểm Tầng 2 dưới góc nhìn khán giả xem Truyện Ma Dân Gian Việt Nam (Hook 3s đầu, ánh sáng u ám có bị bệt tối không, tạo hình thuần Việt hay bị lai cổ trang Trung Quốc, phụ đề có dễ đọc không).",
                                    "3. Chỉ rõ mốc giây cần sửa và đề xuất phương án Bản B cụ thể.",
                                ],
                            },
                        }
                        for item in hub.enqueue_specs([qc_spec]):
                            state["tasks"][item["id"]] = {
                                "persona": "qc",
                                "round": 3,
                                "round_label": f"QC Tầng 2 · {local_media_path.name}",
                                "dedup": item["dedup"],
                                "announced": False,
                                "summary_text": "",
                                "reply_to_msg_id": mid,
                            }
                else:
                    import file_exchange

                    up = file_exchange.upload_temp_share(local_media_path)
                    img_url = str(up.get("url") or "")
                    queue_outbox_message(
                        state,
                        "visual",
                        f"🖼️ Đã nhận ảnh mẫu <code>{html.escape(local_media_path.name)}</code> ({html.escape(img_url)}) — đang chuyển cho 🎨 Muse Hình Ảnh &amp; 🛡️ Muse QC phân tích!",
                        dedup_key=f"imgack:{mid}",
                        reply_to_message_id=mid,
                    )
                    if hub is not None and img_url:
                        img_spec = {
                            "dedup": f"{session_id}:imgqc:{mid}",
                            "project": "research",
                            "assigned_to": "engineer",
                            "kind": "council_image_style_qc",
                            "auto_verify": False,
                            "payload": {
                                "round": f"Thẩm định Ảnh Mẫu ({local_media_path.name})",
                                "persona": PERSONAS["visual"]["badge"],
                                "image_url": img_url,
                                "user_caption": txt,
                                "objectives": [
                                    "Mở xem ảnh tại `image_url`, đánh giá độ thuần Việt cho chủ đề Truyện Ma Dân Gian Việt Nam, kiểm tra lỗi AI/chữ lạ và viết Prompt chuẩn hóa giữ đồng nhất nhân vật."
                                ],
                            },
                        }
                        for item in hub.enqueue_specs([img_spec]):
                            state["tasks"][item["id"]] = {
                                "persona": "visual",
                                "round": 3,
                                "round_label": f"Thẩm định Ảnh · {local_media_path.name}",
                                "dedup": item["dedup"],
                                "announced": False,
                                "summary_text": "",
                                "reply_to_msg_id": mid,
                            }
            else:
                queue_outbox_message(
                    state,
                    "qc",
                    "⚠️ Không tìm thấy hoặc chưa tải được tệp cần QC. Hãy kiểm tra lại đường dẫn `/qc <path>` hoặc gửi tệp dưới 20MB.",
                    dedup_key=f"qcerr:{mid}",
                    reply_to_message_id=mid,
                )
            umsg["handled"] = True
        elif hub is not None:
            # Nếu Vòng 1 vẫn đang diễn ra và chưa sang Vòng 2 -> vừa xác nhận đã ghi vào Vòng 2 vừa giao lượt trả lời riêng!
            queue_outbox_message(
                state,
                "chief",
                (
                    f"📝 <b>👑 MUSE CHÍNH:</b> Đã nhận ý kiến của <b>{html.escape(umsg['user'])}</b> — "
                    f"tôi đang chuyển ngay vào Sảnh <code>:8110</code> để Muse chuyên trách &amp; tôi phản hồi trực tiếp!"
                ),
                dedup_key=f"ack-live:{mid}",
                reply_to_message_id=mid,
            )
            f_specs = build_followup_specs(
                session_id, topic, umsg["user"], txt, int(mid or int(time.time())), state.get("transcript", [])
            )
            enq_f = hub.enqueue_specs([sp for _, _, sp, _ in f_specs])
            f_map = {sp["dedup"]: (pk, rlabel, rmid) for pk, rlabel, sp, rmid in f_specs}
            for item in enq_f:
                pk, rlabel, rmid = f_map[item["dedup"]]
                state["tasks"][item["id"]] = {
                    "persona": pk,
                    "round": 3,
                    "round_label": rlabel,
                    "dedup": item["dedup"],
                    "announced": False,
                    "summary_text": "",
                    "reply_to_msg_id": rmid,
                }
            umsg["handled"] = True

    # 6. Đẩy outbox ra nhóm Telegram nếu đã biết group_chat_id
    sent_now = flush_outbox(state, bridge, chat_id)
    pending_outbox = sum(1 for x in state.get("outbox", []) if not x.get("sent"))
    done_tasks = sum(1 for m in state.get("tasks", {}).values() if m.get("announced"))

    return {
        "group_chat_id": chat_id,
        "sent_now": sent_now,
        "pending_outbox": pending_outbox,
        "tasks_total": len(state.get("tasks", {})),
        "tasks_announced": done_tasks,
        "new_user_msgs": len(new_msgs),
    }


def _acquire_single_instance() -> bool:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.is_file():
        try:
            old_pid = int(LOCK_PATH.read_text(encoding="utf-8").strip())
            if old_pid != os.getpid():
                import psutil

                if psutil.pid_exists(old_pid):
                    proc = psutil.Process(old_pid)
                    cmdline = " ".join(proc.cmdline()).lower()
                    if "muse_telegram_council.py" in cmdline:
                        return False
        except Exception:
            pass
    LOCK_PATH.write_text(str(os.getpid()), encoding="utf-8")
    return True


def run_daemon(poll_seconds: int = 8, max_seconds: int = 0) -> None:
    if not _acquire_single_instance():
        print(json.dumps({"ok": False, "reason": "daemon_already_running"}))
        return

    bridge = TelegramBridge()
    hub = Hub8110Client()
    # Không tự tạo invite / đổi role node trên VPS khi khởi động daemon (chỉ chạy tay khi cần)

    started = time.time()
    bad_token_hash = ""
    last_bad_try_ts = 0.0
    while True:
        cfg_now = load_council_config()
        raw_tok = str(cfg_now.get("bot_token") or "").strip()
        tok_h = re.sub(r"[^A-Za-z0-9]", "", raw_tok)[:12]
        if not raw_tok or (bad_token_hash and tok_h == bad_token_hash and (time.time() - last_bad_try_ts) < 120.0):
            # Nếu đổi sang token khác -> thử ngay sau <=5s; nếu giữ token đang bị lỗi phía Telegram -> tự thử lại mỗi 120s
            time.sleep(5)
            if max_seconds > 0 and (time.time() - started) >= max_seconds:
                break
            continue

        me_check = bridge.api("getMe", timeout=15)
        if not me_check.get("ok"):
            bad_token_hash = tok_h
            last_bad_try_ts = time.time()
            print(
                json.dumps(
                    {
                        "ts": dt.datetime.now().strftime("%H:%M:%S"),
                        "event": "waiting_valid_bot_token",
                        "code": me_check.get("error_code"),
                        "desc": redact_secret(str(me_check.get("description") or "")),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            time.sleep(5)
            continue

        bad_token_hash = ""
        state = load_state()
        summary = step_council_once(state, bridge, hub)
        save_state(state)
        print(
            json.dumps(
                {
                    "ts": dt.datetime.now().strftime("%H:%M:%S"),
                    **summary,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if max_seconds > 0 and (time.time() - started) >= max_seconds:
            break
        time.sleep(max(3, poll_seconds))


def main() -> None:
    parser = argparse.ArgumentParser(description="Muse Roundtable Council ⇄ Telegram Group Bridge")
    parser.add_argument("--once", action="store_true", help="Chạy 1 nhịp duy nhất rồi thoát")
    parser.add_argument("--daemon", action="store_true", help="Chạy nền liên tục đồng bộ :8110 ⇄ Telegram")
    parser.add_argument("--poll-seconds", type=int, default=8)
    parser.add_argument("--max-seconds", type=int, default=0)
    args = parser.parse_args()

    if args.once:
        bridge = TelegramBridge()
        hub = Hub8110Client()
        state = load_state()
        summary = step_council_once(state, bridge, hub)
        save_state(state)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        run_daemon(poll_seconds=args.poll_seconds, max_seconds=args.max_seconds)


if __name__ == "__main__":
    main()
