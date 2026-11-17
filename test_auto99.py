"""Comprehensive test suite for AgentNet V2.0 Auto-99% (Phases 1 -> 5)."""
import ast
import json
import math
from pathlib import Path
import shutil
import tempfile
import time
import unittest

from research_queue import QueueError, ResearchQueue
from auto99.episode_compiler import (
    EpisodeCompiler,
    generate_stickman_scene_code,
    load_episode_spec,
)
from auto99.qc_verify import inspect_episode
from auto99.telegram_gate import (
    LocalQueueStagingBackend,
    TelegramHumanGate,
)
from auto99.tts_auto_heal import (
    PronunciationLexicon,
    TTSAutoHealer,
    expand_numbers_and_symbols_vi,
)
from auto99.worker_daemon import LocalQueueTransport, WorkerDaemon


class FakeTelegramTransport:
    def __init__(self):
        self.sent_videos = []
        self.calls = []
        self.queued_updates = []
        self._next_msg_id = 100

    def send_video(self, chat_id, video_path, caption, reply_markup):
        self._next_msg_id += 1
        self.sent_videos.append({
            "chat_id": chat_id,
            "video_path": str(video_path),
            "caption": caption,
            "reply_markup": reply_markup,
            "message_id": self._next_msg_id,
        })
        return {"message_id": self._next_msg_id}

    def call_json(self, method, payload):
        self.calls.append((method, payload))
        if method == "getUpdates":
            out = list(self.queued_updates)
            self.queued_updates.clear()
            return out
        if method == "sendMessage":
            self._next_msg_id += 1
            return {"message_id": self._next_msg_id}
        return {"ok": True}


class Auto99Phase1QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.q = ResearchQueue(self.root)
        self.chief = {"id": "chief-1", "role": "controller"}
        self.pc_gpu = {"id": "pc-rtx5060ti", "role": "engineer"}
        self.vps_cpu = {"id": "vps1-cpu", "role": "engineer"}
        self.research = {"id": "res-1", "role": "research"}
        self.verify = {"id": "ver-1", "role": "verify"}

    def tearDown(self):
        self.tmp.cleanup()

    def test_gpu_preferred_routes_to_pc_then_falls_back_to_cpu(self):
        # 1) When NO GPU node is active (PC off at night), VPS CPU claims immediately!
        t_night = self.q.post(self.chief, "/tasks", {
            "project": "studio",
            "assigned_to": "engineer",
            "kind": "episode_produce",
            "dedup": "night-job",
            "preferred_capabilities": ["gpu_cuda"],
            "fallback_after_seconds": 60,
            "payload": {"objective": "Night render"},
        })["id"]
        claimed_cpu = self.q.post(self.vps_cpu, "/claim", {"capabilities": ["python3", "cpu_fallback"]})
        self.assertEqual(claimed_cpu["id"], t_night)
        self.q.post(self.vps_cpu, f"/tasks/{t_night}/result", {
            "lease": claimed_cpu["lease"],
            "result": {"outcome": "ok", "summary": "Rendered on CPU fallback"},
        })

        # 2) Register PC GPU as online via /claim poll
        self.assertIsNone(self.q.post(self.pc_gpu, "/claim", {"capabilities": ["python3", "gpu_cuda"]})["id"])

        # Post a new GPU-preferred task while PC GPU is online
        t_day = self.q.post(self.chief, "/tasks", {
            "project": "studio",
            "assigned_to": "engineer",
            "kind": "episode_produce",
            "dedup": "day-job",
            "preferred_capabilities": ["gpu_cuda"],
            "fallback_after_seconds": 60,
            "payload": {"objective": "Day GPU render"},
        })["id"]

        # VPS CPU polls first -> held back so PC GPU gets priority!
        self.assertIsNone(self.q.post(self.vps_cpu, "/claim", {"capabilities": ["python3", "cpu_fallback"]})["id"])

        # PC GPU polls -> claims immediately!
        claimed_gpu = self.q.post(self.pc_gpu, "/claim", {"capabilities": ["python3", "gpu_cuda"]})
        self.assertEqual(claimed_gpu["id"], t_day)

        # 3) If PC GPU is overloaded and task waits past fallback_after_seconds, CPU steps in!
        t_overload = self.q.post(self.chief, "/tasks", {
            "project": "studio",
            "assigned_to": "engineer",
            "kind": "episode_produce",
            "dedup": "overload-job",
            "preferred_capabilities": ["gpu_cuda"],
            "fallback_after_seconds": 30,
            "payload": {"objective": "Overload render"},
        })["id"]
        with self.q.db() as c:
            c.execute("UPDATE tasks SET queued_at=? WHERE id=?", (time.time() - 35, t_overload))
        claimed_fallback = self.q.post(self.vps_cpu, "/claim", {"capabilities": ["python3", "cpu_fallback"]})
        self.assertEqual(claimed_fallback["id"], t_overload)

    def test_dag_pipeline_auto_verify_auto_approve_and_staging(self):
        pipe = self.q.post(self.chief, "/pipelines", {
            "project": "studio",
            "steps": [
                {
                    "step_key": "script",
                    "assigned_to": "research",
                    "kind": "script_draft",
                    "dedup": "pipe1-script",
                    "payload": {"objective": "Draft episode"},
                },
                {
                    "step_key": "produce",
                    "assigned_to": "engineer",
                    "kind": "episode_produce",
                    "dedup": "pipe1-produce",
                    "depends_on_steps": ["script"],
                    "auto_verify": True,
                    "auto_approve": True,
                    "payload": {
                        "objective": "Compile episode",
                        "slug": "ep-canada",
                        "title": "Hồ ở Canada",
                        "stage": "staging_ready",
                        "acceptance_criteria": {"min_score": 85},
                    },
                },
            ],
        })
        script_id = pipe["steps"][0]["id"]
        prod_id = pipe["steps"][1]["id"]
        self.assertEqual(pipe["steps"][1]["status"], "WAITING_DEPS")

        # Engineer cannot claim produce yet (waiting on script)
        self.assertIsNone(self.q.post(self.pc_gpu, "/claim", {"capabilities": ["gpu_cuda"]})["id"])

        # Complete & approve script step -> unlocks produce automatically!
        c1 = self.q.post(self.research, "/claim", {"capabilities": ["research"]})
        self.assertEqual(c1["id"], script_id)
        self.q.post(self.research, f"/tasks/{script_id}/result", {
            "lease": c1["lease"], "result": {"outcome": "ok", "summary": "Script ready"},
        })
        self.q.post(self.chief, f"/tasks/{script_id}/approve", {})

        # Now PC GPU claims produce!
        c2 = self.q.post(self.pc_gpu, "/claim", {"capabilities": ["gpu_cuda"]})
        self.assertEqual(c2["id"], prod_id)
        sub_res = self.q.post(self.pc_gpu, f"/tasks/{prod_id}/result", {
            "lease": c2["lease"],
            "result": {
                "outcome": "completed",  # Studio auto-normalizes 'completed' -> 'ok'
                "slug": "ep-canada",
                "title": "Hồ ở Canada",
                "video_path": "/tmp/final.mp4",
                "summary": "Rendered",
            },
        })
        verify_tid = sub_res["auto_verify_task_id"]
        self.assertTrue(verify_tid)

        # Research cannot read produce task, but assigned Verify CAN read target task!
        with self.assertRaises(QueueError):
            self.q.get(self.research, f"/tasks/{prod_id}")
        target_doc = self.q.get(self.verify, f"/tasks/{prod_id}")
        self.assertEqual(target_doc["result"]["video_path"], "/tmp/final.mp4")

        # Verify claims & submits PASS >= 85 -> auto-approves BOTH tasks & enqueues Staging!
        cv = self.q.post(self.verify, "/claim", {"capabilities": ["verify"]})
        self.assertEqual(cv["id"], verify_tid)
        v_resp = self.q.post(self.verify, f"/tasks/{verify_tid}/result", {
            "lease": cv["lease"],
            "result": {"outcome": "PASS", "hard_gate_passed": True, "score": 93.5, "reasons": []},
        })
        self.assertEqual(v_resp["status"], "APPROVED")
        self.assertEqual(self.q.get(self.chief, f"/tasks/{prod_id}")["status"], "APPROVED")

        staging = self.q.get(self.chief, "/staging")
        self.assertEqual(len(staging), 1)
        self.assertEqual(staging[0]["status"], "PENDING_HUMAN")
        self.assertEqual(staging[0]["qc_score"], 93.5)

    def test_auto_retry_on_qc_fail_and_escalate_after_max_retries(self):
        tid = self.q.post(self.chief, "/tasks", {
            "project": "studio",
            "assigned_to": "engineer",
            "kind": "episode_produce",
            "dedup": "retry-ep",
            "auto_verify": True,
            "auto_approve": True,
            "max_retries": 2,
            "payload": {"objective": "Test self-heal retry", "slug": "ep-retry"},
        })["id"]

        # Attempt 1 -> Verify fails -> Task resets to QUEUED at attempt=2 with feedback!
        c1 = self.q.post(self.pc_gpu, "/claim", {"capabilities": ["gpu_cuda"]})
        r1 = self.q.post(self.pc_gpu, f"/tasks/{tid}/result", {
            "lease": c1["lease"], "result": {"outcome": "ok", "video_path": "/tmp/v1.mp4"},
        })
        cv1 = self.q.post(self.verify, "/claim", {"capabilities": ["verify"]})
        self.assertEqual(cv1["id"], r1["auto_verify_task_id"])
        self.q.post(self.verify, f"/tasks/{cv1['id']}/result", {
            "lease": cv1["lease"],
            "result": {
                "outcome": "RETRYABLE_FAIL",
                "hard_gate_passed": False,
                "score": 72.0,
                "failed_beats": ["beat2"],
                "reasons": ["LUFS -19.2 out of range"],
            },
        })

        requeued = self.q.get(self.chief, f"/tasks/{tid}")
        self.assertEqual(requeued["status"], "QUEUED")
        self.assertEqual(requeued["attempt"], 2)
        self.assertEqual(requeued["payload"]["last_qc_feedback"]["failed_beats"], ["beat2"])

        # Attempt 2 -> Verify fails again -> Reaches max_retries=2 -> ESCALATED!
        c2 = self.q.post(self.pc_gpu, "/claim", {"capabilities": ["gpu_cuda"]})
        self.assertEqual(c2["id"], tid)
        r2 = self.q.post(self.pc_gpu, f"/tasks/{tid}/result", {
            "lease": c2["lease"], "result": {"outcome": "ok", "video_path": "/tmp/v2.mp4"},
        })
        cv2 = self.q.post(self.verify, "/claim", {"capabilities": ["verify"]})
        self.q.post(self.verify, f"/tasks/{cv2['id']}/result", {
            "lease": cv2["lease"],
            "result": {"outcome": "RETRYABLE_FAIL", "hard_gate_passed": False, "score": 70.0, "reasons": ["Still quiet"]},
        })

        escalated = self.q.get(self.chief, f"/tasks/{tid}")
        self.assertEqual(escalated["status"], "ESCALATED")
        staging = self.q.get(self.chief, "/staging")
        self.assertEqual(staging[0]["status"], "ESCALATED")


class Auto99Phase2And3Tests(unittest.TestCase):
    def test_lexicon_and_self_healing_tts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lex_path = root / "lex.json"
            shutil.copy2(Path(__file__).resolve().parent / "auto99" / "pronunciation_lexicon.json", lex_path)
            lex = PronunciationLexicon(lex_path)

            expanded = expand_numbers_and_symbols_vi("Hơn 60% hồ ở Canada, hơn 31.000 hồ.")
            self.assertIn("sáu mươi phần trăm", expanded)
            self.assertIn("ba mươi mốt nghìn", expanded)
            self.assertEqual(
                lex.to_spoken("Đó là Canada."),
                "Đó là Ca-na-đa.",
            )

            # Mock synth generates a 440Hz sine wave scaled so WPM ~158; mock ASR mishears "băng hà"
            import numpy as np

            last_spoken = {"txt": ""}

            def fake_synth(text: str, rate: float):
                last_spoken["txt"] = text
                words = max(1, len(text.split()))
                dur_s = (words / 158.0) * 60.0 * (0.92 / rate)
                n = int(16000 * dur_s)
                t = np.linspace(0, dur_s, n, endpoint=False, dtype=np.float32)
                return 0.25 * np.sin(2 * math.pi * 220.0 * t).astype(np.float32)

            def fake_asr(_wav):
                if "băng hà" in last_spoken["txt"]:
                    return "Mười nghìn năm trước ban ha cào xới"
                return "Mười nghìn năm trước băng tuyết khổng lồ cào xới mặt đất"

            healer = TTSAutoHealer(lexicon=lex, synth_fn=fake_synth, asr_fn=fake_asr, sample_rate=16000)
            res = healer.heal_clause("Mười nghìn năm trước, băng hà cào xới mặt đất.")
            self.assertGreaterEqual(res["round"], 2)
            self.assertIn("băng tuyết khổng lồ", res["caption_text"])
            self.assertGreaterEqual(res["asr_match"], 0.95)

    def test_worker_daemon_heartbeat_and_outbox_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            q = ResearchQueue(root)
            chief = {"id": "chief", "role": "controller"}
            tid = q.post(chief, "/tasks", {
                "project": "studio",
                "assigned_to": "engineer",
                "kind": "custom_slow",
                "dedup": "hb-test",
                "payload": {"objective": "Test heartbeat"},
            })["id"]

            base_transport = LocalQueueTransport(q, "eng-1", "engineer")
            hb_count = 0
            fail_submit_once = {"fail": True}

            class HookedTransport:
                def claim(self, *a, **kw):
                    return base_transport.claim(*a, **kw)

                def heartbeat(self, *a, **kw):
                    nonlocal hb_count
                    hb_count += 1
                    return base_transport.heartbeat(*a, **kw)

                def submit_result(self, *a, **kw):
                    if fail_submit_once["fail"]:
                        fail_submit_once["fail"] = False
                        raise ConnectionError("Simulated Tailscale blip")
                    return base_transport.submit_result(*a, **kw)

                def get_task(self, *a, **kw):
                    return base_transport.get_task(*a, **kw)

            daemon = WorkerDaemon(
                transport=HookedTransport(),
                role="engineer",
                outbox_dir=root / "outbox",
                workspace_dir=root / "work",
                capabilities=["python3"],
                heartbeat_interval_s=0.08,
            )

            def slow_handler(_task):
                time.sleep(0.22)
                return {"outcome": "ok", "summary": "Finished"}

            daemon.register_handler("custom_slow", slow_handler)
            with self.assertRaises(ConnectionError):
                daemon.run_once()

            self.assertGreaterEqual(hb_count, 1)
            self.assertEqual(len(list((root / "outbox").glob("*.json"))), 1)

            # Next poll flushes outbox cleanly!
            self.assertIsNone(daemon.run_once())
            self.assertEqual(len(list((root / "outbox").glob("*.json"))), 0)
            self.assertEqual(q.get(chief, f"/tasks/{tid}")["status"], "SUBMITTED")


class Auto99Phase4And5EndToEndTests(unittest.TestCase):
    def test_stickman_yaml_loader_and_scene_codegen(self):
        ep001_yaml = (
            Path(__file__).resolve().parent
            / "stickman-shorts"
            / "videos"
            / "2026-11-15_ep001-cam-dau-lam-viec"
            / "script.yaml"
        )
        if ep001_yaml.exists():
            spec = load_episode_spec(ep001_yaml)
            self.assertEqual(spec["slug"], "ep001-cam-dau-lam-viec")
            self.assertEqual(len(spec["beats"]), 5)
            fake_timing = {
                "duration_s": 48.0,
                "beats": [
                    {"id": b["id"], "start_s": float(b["start_s"]), "end_s": float(b["end_s"]), "card_title": b["card_title"]}
                    for b in spec["beats"]
                ],
            }
            code = generate_stickman_scene_code(spec, fake_timing)
            ast.parse(code)  # Verifies generated Manim Python is 100% syntactically valid

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe required")
    def test_visual_essay_compile_loudnorm_and_qc_pass(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            spoken_holder = {"txt": ""}

            def synth_tone(text: str, rate: float):
                spoken_holder["txt"] = text
                words = max(1, len(text.split()))
                dur_s = (words / 156.0) * 60.0
                n = int(16000 * dur_s)
                t = np.linspace(0, dur_s, n, endpoint=False, dtype=np.float32)
                # Pleasant harmonic voice-level signal for EBU R128 loudnorm test
                sig = 0.22 * np.sin(2 * math.pi * 190.0 * t) + 0.08 * np.sin(2 * math.pi * 380.0 * t)
                return sig.astype(np.float32)

            healer = TTSAutoHealer(
                synth_fn=synth_tone,
                asr_fn=lambda _wav: spoken_holder["txt"].replace("Ca-na-đa", "Canada"),
                min_asr_match=0.90,
            )
            compiler = EpisodeCompiler(healer=healer)
            spec = {
                "slug": "smoke-visual-essay",
                "title": "Bí mật hồ ở Canada",
                "template": "visual_essay",
                "beats": [
                    {"id": "hook", "card_title": "HƠN NỬA SỐ HỒ", "card_subtitle": "Nằm ở 1 quốc gia?", "spoken": "Một nước giữ hơn nửa số hồ trên cả hành tinh."},
                    {"id": "beat1", "card_title": "ĐÓ LÀ CANADA", "card_subtitle": "60% hồ toàn cầu", "spoken": "Đó là Canada với hơn 60% số hồ lớn trên toàn thế giới."},
                    {"id": "beat2", "card_title": "BĂNG TUYẾT CỔ ĐẠI", "card_subtitle": "10.000 năm trước", "spoken": "Mười nghìn năm trước băng tuyết khổng lồ để lại hàng triệu hố sâu."},
                    {"id": "payoff", "card_title": "BẠN ĐÃ BIẾT CHƯA?", "card_subtitle": "Bình luận ngay nhé!", "spoken": "Bạn đã từng nghe điều này chưa? Bình luận nhé!"},
                ],
            }
            out = compiler.compile(spec, out_dir=root / "ep_out")
            self.assertTrue(Path(out["video_path"]).exists())

            # Verify captions.ass kept "Canada" (display) while voice synthesized "Ca-na-đa"
            ass_text = Path(out["captions_ass"]).read_text(encoding="utf-8")
            self.assertIn("Canada", ass_text)
            self.assertNotIn("Ca-na-đa", ass_text)

            qc = inspect_episode(
                video_path=out["video_path"],
                timing_json_path=out["timing_json"],
                ass_path=out["captions_ass"],
                duration_bounds=(4.0, 65.0),
                min_score=85.0,
            )
            self.assertEqual(qc["outcome"], "PASS", msg=f"QC failed: {qc}")
            self.assertTrue(qc["hard_gate_passed"])
            self.assertGreaterEqual(qc["score"], 85.0)
            self.assertAlmostEqual(qc["measured"]["lufs"], -16.0, delta=1.5)

    def test_telegram_1_percent_human_gate_buttons_and_lexicon_learning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            q = ResearchQueue(root)
            chief = {"id": "chief", "role": "controller"}
            eng = {"id": "pc-gpu", "role": "engineer"}
            ver = {"id": "ver", "role": "verify"}

            # Create & auto-approve an episode into Staging
            tid = q.post(chief, "/tasks", {
                "project": "studio",
                "assigned_to": "engineer",
                "kind": "episode_produce",
                "dedup": "tg-ep1",
                "auto_verify": True,
                "auto_approve": True,
                "payload": {"objective": "Make ep", "slug": "ep-ottawa", "title": "Thủ đô Ottawa", "stage": "staging_ready"},
            })["id"]
            c_eng = q.post(eng, "/claim", {"capabilities": ["gpu_cuda"]})
            dummy_mp4 = root / "final.mp4"
            dummy_mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 1024)
            r_eng = q.post(eng, f"/tasks/{tid}/result", {
                "lease": c_eng["lease"],
                "result": {"outcome": "ok", "slug": "ep-ottawa", "title": "Thủ đô Ottawa", "video_path": str(dummy_mp4)},
            })
            c_ver = q.post(ver, "/claim", {"capabilities": ["verify"]})
            q.post(ver, f"/tasks/{r_eng['auto_verify_task_id']}/result", {
                "lease": c_ver["lease"],
                "result": {"outcome": "PASS", "hard_gate_passed": True, "score": 91.0, "measured": {"duration_s": 46.2, "lufs": -16.0}},
            })

            lex = PronunciationLexicon(root / "lex.json")
            tg = FakeTelegramTransport()
            gate = TelegramHumanGate(
                backend=LocalQueueStagingBackend(q),
                transport=tg,
                owner_chat_id=999888,
                lexicon=lex,
                offset_file=root / "offset.json",
            )

            pushed = gate.push_unnotified_staging()
            self.assertEqual(len(pushed), 1)
            sid = pushed[0]
            self.assertEqual(len(tg.sent_videos), 1)
            self.assertIn("91.0/100", tg.sent_videos[0]["caption"])

            # Unauthorized stranger clicking button -> ignored!
            tg.queued_updates.append({
                "update_id": 1,
                "callback_query": {
                    "id": "cb-hacker",
                    "data": f"a1130:{sid}",
                    "message": {"chat": {"id": 111222}},
                },
            })
            self.assertEqual(gate.process_updates_once(), 0)
            self.assertEqual(q.get(chief, "/staging")[0]["status"], "PENDING_HUMAN")

            # Owner clicks Reject + sends 1-line note with pronunciation rule!
            tg.queued_updates.extend([
                {
                    "update_id": 2,
                    "callback_query": {
                        "id": "cb-owner",
                        "data": f"rejct:{sid}",
                        "message": {"chat": {"id": 999888}},
                    },
                },
                {
                    "update_id": 3,
                    "message": {
                        "chat": {"id": 999888},
                        "text": "Đổi từ thủ đô đọc rõ hơn, phát âm: Ottawa -> Ót-ta-oa",
                    },
                },
            ])
            self.assertEqual(gate.process_updates_once(), 2)
            self.assertEqual(q.get(chief, "/staging")[0]["status"], "REJECTED")
            lessons = q.get(chief, "/lessons")
            self.assertEqual(len(lessons), 1)
            self.assertIn("Ottawa", lessons[0]["note"])
            self.assertEqual(lex.to_spoken("Thủ đô Ottawa"), "Thủ đô Ót-ta-oa")


if __name__ == "__main__":
    unittest.main(verbosity=2)
