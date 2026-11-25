"""Unit tests cho Muse Roundtable Council ⇄ Telegram 2-Way Group Bridge."""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

RAG_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

import muse_telegram_council as mtc


class FakeBridge:
    def __init__(self, config_path: pathlib.Path):
        self.config_path = config_path
        self.updates_queue: list[dict] = []
        self.sent_messages: list[dict] = []

    def discover_and_bind_group(self, state: dict) -> tuple[str, list[dict]]:
        cfg = mtc.load_council_config(self.config_path)
        gid = str(cfg.get("group_chat_id") or "")
        new_msgs = []
        while self.updates_queue:
            u = self.updates_queue.pop(0)
            gid = str(u["chat_id"])
            cfg["group_chat_id"] = gid
            mtc.save_council_config(cfg, self.config_path)
            if u.get("text"):
                new_msgs.append(
                    {
                        "message_id": u.get("message_id", 10),
                        "chat_id": gid,
                        "user": u.get("user", "Chủ dự án"),
                        "text": u["text"],
                        "ts": 1700000000,
                        "handled": False,
                    }
                )
        return gid, new_msgs

    def send_html(self, chat_id: str, html_text: str, reply_to_message_id: int | None = None) -> dict:
        self.sent_messages.append(
            {"chat_id": chat_id, "text": html_text, "reply_to": reply_to_message_id}
        )
        return {"ok": True, "result": {"message_id": len(self.sent_messages) + 100}}


class FakeHub:
    def __init__(self):
        self.tasks: dict[str, dict] = {}
        self._seq = 0

    def enqueue_specs(self, specs: list[dict]) -> list[dict]:
        out = []
        for sp in specs:
            for tid, existing in self.tasks.items():
                if existing["dedup"] == sp["dedup"]:
                    out.append({"id": tid, "dedup": sp["dedup"], "assigned_to": sp["assigned_to"], "kind": sp["kind"], "created": False})
                    break
            else:
                self._seq += 1
                tid = f"task-{self._seq}"
                self.tasks[tid] = {
                    "id": tid,
                    "dedup": sp["dedup"],
                    "assigned_to": sp["assigned_to"],
                    "kind": sp["kind"],
                    "status": "QUEUED",
                    "result": None,
                }
                out.append({"id": tid, "dedup": sp["dedup"], "assigned_to": sp["assigned_to"], "kind": sp["kind"], "created": True})
        return out

    def fetch_tasks_status(self, task_ids: list[str]) -> dict:
        return {
            "ok": True,
            "active_15m": [["research", 3], ["verify", 1], ["engineer", 1]],
            "tasks": {tid: self.tasks[tid] for tid in task_ids if tid in self.tasks},
        }


class MuseTelegramCouncilTests(unittest.TestCase):
    def test_redact_secret_strips_bot_token_and_invite(self):
        sample = "Error at https://api.telegram.org/bot1234567890:AAH_testTokenSecret1234567890abcdef/getMe and MUSE-ABCDEFGH123456"
        cleaned = mtc.redact_secret(sample)
        self.assertNotIn("AAH_testTokenSecret", cleaned)
        self.assertNotIn("MUSE-ABCDEFGH123456", cleaned)
        self.assertIn("bot[REDACTED_BOT_TOKEN]", cleaned)
        self.assertIn("[REDACTED_INVITE]", cleaned)

    def test_full_roundtable_flow_and_two_way_reply(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = pathlib.Path(tmp) / "telegram_council.json"
            mtc.save_council_config({"bot_token": "dummy", "group_chat_id": ""}, cfg_path)
            bridge = FakeBridge(cfg_path)
            hub = FakeHub()
            state = mtc.load_state(pathlib.Path(tmp) / "state.json")

            # Bước 1: Chưa có group_chat_id -> vẫn tạo lời khai mạc + 4 task Vòng 1 trên :8110, chờ ở outbox
            s1 = mtc.step_council_once(state, bridge, hub)
            self.assertEqual(s1["tasks_total"], 4)
            self.assertEqual(s1["pending_outbox"], 1)
            self.assertEqual(len(bridge.sent_messages), 0)

            # Bước 2: Người dùng thêm Bot vào nhóm và nhắn "bắt đầu" -> tự nhận group_chat_id và xả outbox
            bridge.updates_queue.append({"chat_id": "-10099887766", "text": "bắt đầu", "message_id": 55})
            s2 = mtc.step_council_once(state, bridge, hub)
            self.assertEqual(s2["group_chat_id"], "-10099887766")
            self.assertEqual(len(bridge.sent_messages), 2)  # Khai mạc + xác nhận kết nối

            # Bước 3: 4 Muse Phụ hoàn thành Vòng 1 trên :8110 -> phát biểu lên nhóm + tự tạo 2 task Vòng 2
            for tid, tdata in list(hub.tasks.items()):
                tdata["status"] = "SUBMITTED"
                tdata["result"] = {
                    "outcome": "ok",
                    "dialogue_speech": f"Phát biểu bàn tròn từ {tdata['kind']} về Ma Da & Chó Đội Nón Mê.",
                    "limitations": ["Cần test render khung tối trên điện thoại."],
                }
            s3 = mtc.step_council_once(state, bridge, hub)
            self.assertEqual(s3["tasks_announced"], 4)
            self.assertEqual(s3["tasks_total"], 6)  # +2 task Vòng 2 (QC phản biện + Muse Chính chốt)
            self.assertEqual(len(bridge.sent_messages), 6)

            # Bước 4: Chủ dự án hỏi sâu về âm thanh -> tự giao Muse Âm Thanh + Muse Chính trả lời
            bridge.updates_queue.append(
                {"chat_id": "-10099887766", "text": "Chọn giọng đọc miền Nam hay Bắc cho tập Ma Da?", "message_id": 88}
            )
            s4 = mtc.step_council_once(state, bridge, hub)
            self.assertEqual(s4["tasks_total"], 8)
            audio_live = [t for t in hub.tasks.values() if "usr:88:audio" in t["dedup"]]
            self.assertEqual(len(audio_live), 1)


if __name__ == "__main__":
    unittest.main()
