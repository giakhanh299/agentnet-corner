"""Live 2-Way MTProto DC5 Listener cho Phòng Họp Đa Muse trên nhóm Telegram ('Làm phim ma').

Kết nối trực tiếp @MUSEall1_bot vào Telegram DC5 Singapore (91.108.56.130:443),
lắng nghe tin nhắn mới theo thời gian thực (0-latency), tự động:
1. Nhận câu hỏi/chỉ đạo của Chủ dự án trong nhóm -> giao việc lên Sảnh :8110 -> tự đánh thức phiên muse.ai nhận bài -> phát câu trả lời của Muse Phụ & Muse Chính về nhóm.
2. Nhận Video/Ảnh thả trực tiếp vào nhóm hoặc lệnh `/qc <path>` -> chạy QC Tầng 1 (`qc_engine.py` 0-token), gửi ảnh Contact Sheet 3x2 vào nhóm, đồng thời giao `🛡️ Muse Phụ 4 (QC)` chấm Tầng 2.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import html
import json
import os
import pathlib
import sys
import threading
import time
from typing import Any

from telethon import TelegramClient, events
from telethon.tl.functions.updates import GetDifferenceRequest, GetStateRequest
from telethon.tl.types import PeerChannel, PeerChat

RAG_ROOT = pathlib.Path(__file__).resolve().parent
if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

import muse_dispatch
import muse_telegram_council as mtc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HELPER_ROOT = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "MuseLoginHelper"
SESSION_PATH = str(HELPER_ROOT / "council_dc5")
LISTENER_PID_PATH = RAG_ROOT / "data" / "muse_mtproto_listener.pid"
DC5_IP = "91.108.56.130"
DC5_PORT = 443

_WAKE_LOCK = threading.Lock()


def _wake_muse_workers_bg(roles: list[str]) -> None:
    """Chạy nền đánh thức các phiên muse.ai tương ứng để nhận bài mới ngay lập tức."""
    def _runner():
        if not _WAKE_LOCK.acquire(blocking=False):
            return
        try:
            # Không tạo mã mời / đổi role node trên VPS mỗi lần đánh thức (tránh rác invite + ghi production)
            dummy = RAG_ROOT / "data" / "_use_profiles_only.none"
            role_to_idx = {"research": 0, "verify": 3, "chief": 4}
            for idx_key in roles:
                skip_i = role_to_idx.get(idx_key, 0)
                q_role = "verify" if idx_key == "verify" else "research"
                muse_dispatch.dispatch_accounts(dummy, role=q_role, limit=1, skip=skip_i)
        except Exception as exc:
            print(f"[wake_bg] err={type(exc).__name__}", flush=True)
        finally:
            _WAKE_LOCK.release()

    threading.Thread(target=_runner, daemon=True).start()


def _resolve_peer(gid_str: str):
    gid = int(str(gid_str).strip())
    if str(gid_str).startswith("-100"):
        return PeerChannel(int(str(gid_str)[4:]))
    if gid < 0:
        return PeerChat(abs(gid))
    return PeerChat(gid)


async def _send_html_chunks(client: TelegramClient, peer: Any, html_text: str, reply_to: int | None = None) -> int | None:
    chunks = mtc.split_telegram_html(html_text, max_len=3800)
    last_id = None
    for idx, ch in enumerate(chunks):
        sent = await client.send_message(
            peer,
            ch,
            parse_mode="html",
            link_preview=False,
            reply_to=reply_to if idx == 0 else None,
        )
        last_id = sent.id
        if idx < len(chunks) - 1:
            await asyncio.sleep(1.0)
    return last_id


async def main_loop() -> None:
    LISTENER_PID_PATH.parent.mkdir(parents=True, exist_ok=True)
    LISTENER_PID_PATH.write_text(str(os.getpid()), encoding="utf-8")

    cfg = mtc.load_council_config()
    tok = str(cfg.get("bot_token") or "").strip()
    if not tok:
        raise RuntimeError("Thiếu bot_token trong telegram_council.json")

    # L065: api_id/api_hash đọc từ telegram_council.json (ngoài git) hoặc biến môi trường,
    # không ghi cứng trong mã nguồn. Đăng ký cặp riêng tại my.telegram.org.
    api_id = int(cfg.get("api_id") or os.environ.get("TG_API_ID") or 0)
    api_hash = str(cfg.get("api_hash") or os.environ.get("TG_API_HASH") or "").strip()
    if not api_id or not api_hash:
        raise RuntimeError("Thiếu api_id/api_hash trong telegram_council.json hoặc TG_API_ID/TG_API_HASH")
    client = TelegramClient(SESSION_PATH, api_id, api_hash)
    client.session.set_dc(5, DC5_IP, DC5_PORT)
    await client.connect()
    if not await client.is_user_authorized():
        await client.sign_in(bot_token=tok)

    me = await client.get_me()
    st_u = await client(GetStateRequest())
    await client(GetDifferenceRequest(pts=1, date=st_u.date, qts=0))
    print(json.dumps({"event": "mtproto_online", "bot": me.username, "group": cfg.get("group_chat_id")}), flush=True)

    hub = mtc.Hub8110Client()

    @client.on(events.NewMessage())
    async def on_new_message(event):
        sender = await event.get_sender()
        if getattr(sender, "bot", False):
            return
        chat = await event.get_chat()
        chat_title = getattr(chat, "title", "") or ""
        is_group = hasattr(chat, "participants_count") or getattr(chat, "megagroup", False) or bool(chat_title)
        if not is_group:
            return

        # Cập nhật group_chat_id nếu nhóm mới hoặc nâng cấp supergroup
        raw_cid = event.chat_id
        cfg_cur = mtc.load_council_config()
        if str(raw_cid) != str(cfg_cur.get("group_chat_id") or ""):
            cfg_cur["group_chat_id"] = str(raw_cid)
            if chat_title:
                cfg_cur["group_title"] = chat_title
            mtc.save_council_config(cfg_cur)

        text = (event.raw_text or "").strip()
        low = text.lower()
        uname = (
            " ".join(filter(None, [getattr(sender, "first_name", ""), getattr(sender, "last_name", "")])).strip()
            or getattr(sender, "username", "")
            or "Chủ dự án"
        )
        mid = event.id
        state = mtc.load_state()
        topic = state.get("topic") or "Làm Video Truyện Ma Dân Gian Việt Nam"
        session_id = state.get("session_id") or "ghost-vn"

        # 1. Lệnh trạng thái
        if low.startswith("/status"):
            total_t = len(state.get("tasks", {}))
            done_t = sum(1 for v in state.get("tasks", {}).values() if v.get("announced"))
            await _send_html_chunks(
                client,
                event.input_chat,
                (
                    f"📊 <b>Trạng thái Phòng Họp Đa Muse ({html.escape(chat_title or 'Nhóm')})</b>\n"
                    f"• Chủ đề: <b>{html.escape(topic)}</b>\n"
                    f"• Lượt phát biểu Muse đã hoàn tất: <b>{done_t}/{total_t}</b>\n"
                    f"• Gõ câu hỏi bất kỳ để Muse Phụ + Muse Chính bàn tiếp, hoặc thả Video/Ảnh (hay <code>/qc đường_dẫn</code>) để chạy QC 2 tầng!"
                ),
                reply_to=mid,
            )
            return

        if low in ("/start", "/here", "bắt đầu", "bat dau"):
            await _send_html_chunks(
                client,
                event.input_chat,
                "<b>👑 MUSE CHÍNH:</b> Phòng họp đang trực tuyến 2 chiều! Bạn hãy nhắn câu hỏi, chỉ đạo kịch bản hoặc thả file Video/Ảnh cần QC vào nhóm nhé.",
                reply_to=mid,
            )
            return

        # 2. Nếu có thả file Video/Ảnh hoặc gõ /qc <path>
        has_media = bool(event.Message.media) if hasattr(event, "Message") else bool(event.media)
        if low.startswith("/qc ") or has_media:
            local_path: pathlib.Path | None = None
            if low.startswith("/qc "):
                cand = pathlib.Path(text[4:].strip().strip('"'))
                if cand.is_file():
                    local_path = cand
            elif event.media:
                inbox = RAG_ROOT / "data" / "council_inbox"
                inbox.mkdir(parents=True, exist_ok=True)
                dl = await event.download_media(file=str(inbox))
                if dl:
                    local_path = pathlib.Path(dl)

            if local_path and local_path.is_file():
                if local_path.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm"):
                    await _send_html_chunks(
                        client,
                        event.input_chat,
                        f"🔬 <b>🛡️ MUSE QC:</b> Đang chạy QC Tầng 1 (0-token · <code>qc_engine.py</code>) cho <code>{html.escape(local_path.name)}</code>...",
                        reply_to=mid,
                    )
                    rep = mtc.run_qa_qc_exchange_for_video(local_path)
                    sheet_path = str(rep.get("contact_sheet") or "")
                    sheet_url = str(rep.get("contact_sheet_url") or "")
                    cap = (
                        f"<b>🛡️ KẾT QUẢ QC TẦNG 1 (0-TOKEN)</b>\n"
                        f"• Tệp: <code>{html.escape(local_path.name)}</code>\n"
                        f"• Kết luận: <b>{html.escape(str(rep.get('verdict')))}</b> "
                        f"(Điểm: <b>{rep.get('score_tier1')}/{rep.get('score_tier1_max')}</b>)\n"
                        f"• Lỗi cứng: <code>{html.escape(json.dumps(rep.get('fail_reasons') or [], ensure_ascii=False))}</code>\n"
                        f"• Cảnh báo: <code>{html.escape(json.dumps(rep.get('warn_reasons') or [], ensure_ascii=False))}</code>\n"
                        f"⏳ <i>Đang chuyển Contact Sheet sang Sảnh :8110 để 🛡️ Muse Phụ 4 chấm Tầng 2...</i>"
                    )
                    if sheet_path and pathlib.Path(sheet_path).is_file():
                        await client.send_file(event.input_chat, sheet_path, caption=cap[:1000], parse_mode="html", reply_to=mid)
                    else:
                        await _send_html_chunks(client, event.input_chat, cap, reply_to=mid)

                    qc_spec = {
                        "dedup": f"{session_id}:liveqc:{mid}",
                        "project": "research",
                        "assigned_to": "verify",
                        "kind": "council_tier2_video_qc",
                        "auto_verify": False,
                        "payload": {
                            "round": f"QC Tầng 2 · {local_path.name}",
                            "persona": mtc.PERSONAS["qc"]["badge"],
                            "topic": topic,
                            "contact_sheet_url": sheet_url,
                            "tier1_summary": {
                                "verdict": rep.get("verdict"),
                                "score_tier1": rep.get("score_tier1"),
                                "fail_reasons": rep.get("fail_reasons"),
                                "warn_reasons": rep.get("warn_reasons"),
                            },
                            "objectives": [
                                "Mở xem Contact Sheet 3x2 tại `contact_sheet_url`, chấm điểm Tầng 2 cho Video Truyện Ma Dân Gian Việt Nam (Hook 3s, độ thuần Việt, độ sáng, phụ đề) và nêu rõ mốc giây cần sửa Bản B."
                            ],
                        },
                    }
                    for item in hub.enqueue_specs([qc_spec]):
                        state["tasks"][item["id"]] = {
                            "persona": "qc",
                            "round": 3,
                            "round_label": f"QC Tầng 2 · {local_path.name}",
                            "dedup": item["dedup"],
                            "announced": False,
                            "summary_text": "",
                            "reply_to_msg_id": mid,
                        }
                    mtc.save_state(state)
                    _wake_muse_workers_bg(["verify"])
                    return

        if not text:
            return

        # 3. Câu hỏi / chỉ đạo thảo luận trực tiếp -> giao Muse Phụ chuyên môn + Muse Chính
        await _send_html_chunks(
            client,
            event.input_chat,
            f"📝 <b>👑 MUSE CHÍNH:</b> Đã nhận ý kiến của <b>{html.escape(uname)}</b> — đang chuyển vào bàn tròn <code>:8110</code> để Muse chuyên môn &amp; tôi phản hồi ngay!",
            reply_to=mid,
        )
        f_specs = mtc.build_followup_specs(session_id, topic, uname, text, mid, state.get("transcript", []))
        enq_f = hub.enqueue_specs([sp for _, _, sp, _ in f_specs])
        f_map = {sp["dedup"]: (pk, rlabel, rmid) for pk, rlabel, sp, rmid in f_specs}
        needed_roles = []
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
            needed_roles.append("verify" if mtc.PERSONAS[pk]["queue_role"] == "verify" else ("chief" if pk == "chief" else "research"))
        mtc.save_state(state)
        _wake_muse_workers_bg(needed_roles)

    # Vòng nền kiểm tra kết quả mới trên :8110 mỗi 8s và bắn thẳng vào nhóm
    while True:
        try:
            state = mtc.load_state()
            cfg_cur = mtc.load_council_config()
            gid_str = str(cfg_cur.get("group_chat_id") or "").strip()
            unannounced = [tid for tid, meta in state.get("tasks", {}).items() if not meta.get("announced")]
            if gid_str and unannounced:
                peer = _resolve_peer(gid_str)
                polled = hub.fetch_tasks_status(unannounced)
                remote_tasks = polled.get("tasks") or {}
                ordered = sorted(
                    unannounced,
                    key=lambda t: (
                        state["tasks"][t].get("round", 1),
                        1 if state["tasks"][t].get("persona") == "chief" else 0,
                    ),
                )
                changed = False
                for tid in ordered:
                    rmeta = remote_tasks.get(tid)
                    if not rmeta or rmeta.get("status") not in ("SUBMITTED", "APPROVED"):
                        continue
                    lmeta = state["tasks"][tid]
                    html_msg = mtc.format_muse_turn_html(lmeta["persona"], lmeta["round_label"], rmeta.get("result") or {})
                    await _send_html_chunks(client, peer, html_msg, reply_to=lmeta.get("reply_to_msg_id"))
                    lmeta["announced"] = True
                    lmeta["summary_text"] = html_msg[:8000]
                    state.setdefault("transcript", []).append(
                        {"ts": time.time(), "speaker": mtc.PERSONAS.get(lmeta["persona"], {}).get("badge", lmeta["persona"]), "text": html_msg[:3000]}
                    )
                    changed = True
                if changed:
                    mtc.save_state(state)
        except Exception as exc:
            print(f"[poll_loop] err={type(exc).__name__}: {mtc.redact_secret(str(exc))[:160]}", flush=True)
        await asyncio.sleep(8)


if __name__ == "__main__":
    asyncio.run(main_loop())
