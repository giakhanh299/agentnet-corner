"""Phase 5B: Telegram Bot '1% Human Gate' for AgentNet V2.0 Auto-99%.

Pure Python stdlib client (zero pip dependencies, never stores tokens in git):
- Reads credentials at runtime from `~/.agentnet-corner/telegram.json` (0600)
  or environment variables `AGENTNET_TELEGRAM_BOT_TOKEN` & `AGENTNET_TELEGRAM_CHAT_ID`.
- Pushes QC-passed Staging Ready episodes (with direct MP4 preview if <45 MB,
  scorecard, LUFS, WPM, ASR %, and Drive link) to the owner's Telegram.
- Provides 1-tap Inline Keyboard buttons:
    [✅ Duyệt 11:30]   [🌙 Duyệt 20:00]
    [🔁 Render lại]    [❌ Loại + Bài học]
- Verifies `chat_id` whitelist on every incoming update.
- Captures optional 1-line reply notes on Reject / Rerender -> stores into
  Queue `lessons` table AND auto-teaches `PronunciationLexicon` when formatted
  as `phat am: Word -> Phonetic` (or `phát âm: Word -> Phonetic`).
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
from pathlib import Path
import re
import time
from typing import Protocol
from urllib.request import Request, urlopen
import uuid

from .tts_auto_heal import PronunciationLexicon, ensure_windows_cuda_dlls_and_utf8

MAX_DIRECT_VIDEO_BYTES = 45 * 1024 * 1024  # Safe margin under Telegram 50 MB Bot API limit


class StagingBackend(Protocol):
    def list_staging(self) -> list[dict]: ...
    def decide_staging(self, staging_id: str, decision: str, note: str = "", telegram_msg_id: int | None = None) -> dict: ...
    def add_lesson(self, note: str, slug: str = "", category: str = "telegram_feedback") -> dict: ...


class LocalQueueStagingBackend:
    """In-process adapter over `ResearchQueue`."""
    def __init__(self, queue):
        self.queue = queue
        self.chief_node = {"id": "telegram-gate", "role": "controller"}

    def list_staging(self) -> list[dict]:
        return self.queue.get(self.chief_node, "/staging")

    def decide_staging(self, staging_id: str, decision: str, note: str = "", telegram_msg_id: int | None = None) -> dict:
        body: dict = {"decision": decision, "note": note}
        if telegram_msg_id is not None:
            body["telegram_msg_id"] = telegram_msg_id
        return self.queue.post(self.chief_node, f"/staging/{staging_id}/decision", body)

    def add_lesson(self, note: str, slug: str = "", category: str = "telegram_feedback") -> dict:
        return self.queue.post(self.chief_node, "/lessons", {"note": note, "slug": slug, "category": category})


class HttpQueueStagingBackend:
    """HTTP adapter over Tailscale controller `:8110` using controller credential."""
    def __init__(self, controller_url: str, bearer_token: str):
        self.base = controller_url.rstrip("/")
        self.token = bearer_token

    def _req(self, path: str, body: dict | None = None):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = Request(self.base + path, data=data, headers=headers)
        with urlopen(req, timeout=15) as r:
            return json.load(r)

    def list_staging(self) -> list[dict]:
        return self._req("/staging")

    def decide_staging(self, staging_id: str, decision: str, note: str = "", telegram_msg_id: int | None = None) -> dict:
        body: dict = {"decision": decision, "note": note}
        if telegram_msg_id is not None:
            body["telegram_msg_id"] = telegram_msg_id
        return self._req(f"/staging/{staging_id}/decision", body)

    def add_lesson(self, note: str, slug: str = "", category: str = "telegram_feedback") -> dict:
        return self._req("/lessons", {"note": note, "slug": slug, "category": category})


def load_telegram_credentials(state_dir: Path | None = None) -> tuple[str, int]:
    state = state_dir or (Path.home() / ".agentnet-corner")
    env_tok = os.environ.get("AGENTNET_TELEGRAM_BOT_TOKEN", "").strip()
    env_chat = os.environ.get("AGENTNET_TELEGRAM_CHAT_ID", "").strip()
    if env_tok and env_chat:
        return env_tok, int(env_chat)

    cfg_file = state / "telegram.json"
    if not cfg_file.exists():
        raise FileNotFoundError(
            f"Telegram config not found at {cfg_file}. "
            "Run `python -m auto99.telegram_gate init-config` or set AGENTNET_TELEGRAM_BOT_TOKEN & AGENTNET_TELEGRAM_CHAT_ID."
        )
    cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
    tok = str(cfg.get("bot_token", "")).strip()
    chat_id = int(cfg["chat_id"])
    if not tok:
        raise ValueError("Empty bot_token in telegram.json")
    return tok, chat_id


def _encode_multipart(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----AgentNetBoundary{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for k, v in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        chunks.append(f"{v}\r\n".encode("utf-8"))

    mime = mimetypes.guess_type(file_path.name)[0] or "video/mp4"
    chunks.append(f"--{boundary}\r\n".encode())
    chunks.append(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"\r\n'.encode("utf-8")
    )
    chunks.append(f"Content-Type: {mime}\r\n\r\n".encode())
    chunks.append(file_path.read_bytes())
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


class TelegramTransport:
    """Thin wrapper around Telegram Bot HTTP API (mockable in tests)."""
    def __init__(self, bot_token: str, api_base: str = "https://api.telegram.org"):
        self.base = f"{api_base.rstrip('/')}/bot{bot_token}"

    def call_json(self, method: str, payload: dict) -> dict:
        req = Request(
            f"{self.base}/{method}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(req, timeout=35) as r:
            resp = json.load(r)
        if not resp.get("ok"):
            raise RuntimeError(f"Telegram API error on {method}: {resp.get('description')}")
        return resp["result"]

    def send_video(self, chat_id: int, video_path: Path, caption: str, reply_markup: dict) -> dict:
        body, ctype = _encode_multipart(
            {
                "chat_id": str(chat_id),
                "caption": caption[:1024],
                "reply_markup": json.dumps(reply_markup, ensure_ascii=False),
                "supports_streaming": "true",
            },
            "video",
            video_path,
        )
        req = Request(f"{self.base}/sendVideo", data=body, headers={"Content-Type": ctype})
        with urlopen(req, timeout=90) as r:
            resp = json.load(r)
        if not resp.get("ok"):
            raise RuntimeError(f"Telegram sendVideo failed: {resp.get('description')}")
        return resp["result"]


def format_staging_caption(item: dict) -> str:
    status = item.get("status", "PENDING_HUMAN")
    header = "🚨 [CẦN CHỦ XỬ LÝ - QUÁ SỐ LẦN TỰ SỬA]" if status == "ESCALATED" else "✅ [AUTO-QC ĐẠT CHUẨN — CHỜ 1% DUYỆT ĐĂNG]"
    qc_info = {}
    if item.get("qc_summary"):
        try:
            qc_info = json.loads(item["qc_summary"])
        except Exception:
            qc_info = {}
    measured = qc_info.get("measured", {})
    lufs = measured.get("lufs", "n/a")
    dur = measured.get("duration_s", "n/a")
    score = item.get("qc_score")
    score_str = f"{score:.1f}/100" if isinstance(score, (int, float)) else "n/a"
    lines = [
        header,
        f"🎬 Tập: {item.get('title') or item.get('slug')}",
        f"📊 Điểm QC: {score_str} | ⏱ {dur}s | 🔊 {lufs} LUFS",
        f"🕒 Khung giờ gợi ý: {item.get('slot_hint') or '11:30 / 20:00'}",
    ]
    if item.get("drive_url"):
        lines.append(f"☁️ Drive: {item['drive_url']}")
    reasons = qc_info.get("reasons") or []
    if reasons:
        lines.append("⚠️ Ghi chú QC: " + "; ".join(reasons[:3]))
    return "\n".join(lines)


def build_inline_keyboard(staging_id: str) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Duyệt 11:30", "callback_data": f"a1130:{staging_id}"},
                {"text": "🌙 Duyệt 20:00", "callback_data": f"a2000:{staging_id}"},
            ],
            [
                {"text": "🔁 Render lại", "callback_data": f"reren:{staging_id}"},
                {"text": "❌ Loại (+Bài học)", "callback_data": f"rejct:{staging_id}"},
            ],
        ]
    }


def maybe_learn_pronunciation_from_note(note: str, lexicon: PronunciationLexicon | None = None) -> tuple[str, str] | None:
    """Detect notes like `phát âm: Moraine -> Mô-rên` and persist to lexicon."""
    m = re.search(r"(?:phát\s*âm|phat\s*am|pronounce)\s*:\s*([^\->=]+?)\s*(?:->|=>|=)\s*(.+)", note, flags=re.IGNORECASE)
    if not m:
        return None
    written, spoken = m.group(1).strip(), m.group(2).strip()
    if not written or not spoken:
        return None
    lex = lexicon or PronunciationLexicon()
    lex.learn_word(written, spoken, persist=True)
    return written, spoken


class TelegramHumanGate:
    """Synchronizes Queue Staging items <-> Owner Telegram phone buttons & feedback."""

    def __init__(
        self,
        backend: StagingBackend,
        transport: TelegramTransport,
        owner_chat_id: int,
        lexicon: PronunciationLexicon | None = None,
        offset_file: Path | None = None,
    ):
        self.backend = backend
        self.transport = transport
        self.owner_chat_id = int(owner_chat_id)
        self.lexicon = lexicon or PronunciationLexicon()
        self.offset_file = offset_file or (Path.home() / ".agentnet-corner" / "telegram_offset.json")
        self.awaiting_note_for: dict[int, tuple[str, str]] = {}  # chat_id -> (staging_id, decision)

    def _load_offset(self) -> int:
        if self.offset_file.exists():
            try:
                return int(json.loads(self.offset_file.read_text(encoding="utf-8")).get("offset", 0))
            except Exception:
                return 0
        return 0

    def _save_offset(self, offset: int) -> None:
        self.offset_file.parent.mkdir(parents=True, exist_ok=True)
        self.offset_file.write_text(json.dumps({"offset": offset}), encoding="utf-8")

    def push_unnotified_staging(self) -> list[str]:
        pushed: list[str] = []
        items = self.backend.list_staging()
        for item in items:
            if item.get("status") not in ("PENDING_HUMAN", "ESCALATED"):
                continue
            if item.get("telegram_msg_id"):
                continue
            sid = item["id"]
            caption = format_staging_caption(item)
            kb = build_inline_keyboard(sid)
            vpath = Path(item["video_path"]) if item.get("video_path") else None

            if vpath and vpath.exists() and vpath.stat().st_size <= MAX_DIRECT_VIDEO_BYTES:
                res = self.transport.send_video(self.owner_chat_id, vpath, caption, kb)
            else:
                res = self.transport.call_json(
                    "sendMessage",
                    {"chat_id": self.owner_chat_id, "text": caption, "reply_markup": kb},
                )
            msg_id = int(res["message_id"])
            self.backend.decide_staging(sid, "mark_notified", telegram_msg_id=msg_id)
            pushed.append(sid)
        return pushed

    def process_updates_once(self, timeout_s: int = 0) -> int:
        offset = self._load_offset()
        updates = self.transport.call_json("getUpdates", {"offset": offset, "timeout": timeout_s})
        handled = 0

        for upd in updates:
            upd_id = int(upd["update_id"])
            self._save_offset(upd_id + 1)

            if "callback_query" in upd:
                cb = upd["callback_query"]
                msg = cb.get("message") or {}
                chat_id = int((msg.get("chat") or {}).get("id", 0))
                if chat_id != self.owner_chat_id:
                    continue
                data = str(cb.get("data", ""))
                if ":" not in data:
                    continue
                code, sid = data.split(":", 1)
                action_map = {
                    "a1130": ("approve_1130", "✅ Đã duyệt lịch đăng 11:30!"),
                    "a2000": ("approve_2000", "🌙 Đã duyệt lịch đăng 20:00!"),
                    "reren": ("rerender", "🔁 Đã đưa lại vào hàng đợi Render! Bạn có thể nhắn tiếp 1 câu ghi chú sửa lỗi (hoặc bỏ qua)."),
                    "rejct": ("reject", "❌ Đã đánh dấu Loại! Hãy nhắn 1 dòng lý do để hệ thống ghi vào Kho Bài Học (vd: `phát âm: Moraine -> Mô-rên`)."),
                }
                if code not in action_map:
                    continue
                decision, toast = action_map[code]
                self.backend.decide_staging(sid, decision)
                self.transport.call_json("answerCallbackQuery", {"callback_query_id": cb["id"], "text": toast[:190]})
                self.transport.call_json("sendMessage", {"chat_id": chat_id, "text": f"[{sid[:8]}] {toast}"})
                if decision in ("rerender", "reject"):
                    self.awaiting_note_for[chat_id] = (sid, decision)
                handled += 1

            elif "message" in upd:
                msg = upd["message"]
                chat_id = int((msg.get("chat") or {}).get("id", 0))
                if chat_id != self.owner_chat_id:
                    continue
                text = (msg.get("text") or "").strip()
                if not text or text.startswith("/"):
                    continue
                learned = maybe_learn_pronunciation_from_note(text, self.lexicon)
                if chat_id in self.awaiting_note_for:
                    sid, prev_dec = self.awaiting_note_for.pop(chat_id)
                    self.backend.decide_staging(sid, prev_dec, note=text)
                    reply = f"📝 Đã lưu bài học cho tập [{sid[:8]}]: \"{text}\""
                else:
                    self.backend.add_lesson(note=text, category="telegram_note")
                    reply = f"📝 Đã ghi vào Kho Bài Học chung: \"{text}\""
                if learned:
                    reply += f"\n🔤 Đã tự học từ điển phát âm: `{learned[0]}` -> `{learned[1]}`"
                self.transport.call_json("sendMessage", {"chat_id": chat_id, "text": reply})
                handled += 1

        return handled


def main() -> int:
    ensure_windows_cuda_dlls_and_utf8()
    p = argparse.ArgumentParser(description="AgentNet V2.0 Telegram 1% Human Gate")
    sub = p.add_subparsers(dest="cmd", required=True)

    init_p = sub.add_parser("init-config", help="Save bot_token & owner chat_id safely outside git")
    init_p.add_argument("--token", required=True, help="Telegram Bot token from @BotFather")
    init_p.add_argument("--chat-id", required=True, type=int, help="Owner numeric Telegram chat_id")

    run_p = sub.add_parser("daemon", help="Run continuous push + callback polling loop")
    run_p.add_argument("--controller-url", default="http://100.67.236.124:8110")
    run_p.add_argument("--state", default=str(Path.home() / ".agentnet-corner"))
    run_p.add_argument("--interval", type=int, default=15)

    args = p.parse_args()
    state = Path(args.state) if hasattr(args, "state") else (Path.home() / ".agentnet-corner")
    state.mkdir(parents=True, exist_ok=True)

    if args.cmd == "init-config":
        cfg_file = state / "telegram.json"
        fd = os.open(cfg_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"bot_token": args.token.strip(), "chat_id": args.chat_id}, f)
        print(f"Saved Telegram config safely at {cfg_file}")
        return 0

    bot_token, chat_id = load_telegram_credentials(state)
    conn = json.loads((state / "connection.json").read_text(encoding="utf-8"))
    backend = HttpQueueStagingBackend(conn.get("controller_url") or args.controller_url, conn["application_token"])
    gate = TelegramHumanGate(backend, TelegramTransport(bot_token), chat_id, offset_file=state / "telegram_offset.json")
    print(f"Telegram 1% Human Gate running for chat_id={chat_id}...")
    while True:
        try:
            gate.push_unnotified_staging()
            gate.process_updates_once(timeout_s=10)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"[telegram-gate] transient error: {exc}")
            time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
