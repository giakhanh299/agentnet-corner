import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studio"))
import script_direction_lint as lint  # noqa: E402

BIBLE = {"characters": [
    {"id": "a_sang", "name": "A Sáng", "speech_style": "xưng con, câu ngắn", "want": "giữ nhà", "secret": "đã mở nắp quan tài"},
    {"id": "dao_si", "name": "Đạo sĩ", "speech_style": "nói ít, ẩn ý", "want": "trấn yểm", "secret": "biết người chết là ai"},
]}


def acted_scene(sid: int, act: int) -> dict:
    return {
        "id": sid, "act": act, "scene_type": "doi_thoai",
        "beat": "A Sáng tưởng bình thường → đạo sĩ trao điều cấm → cậu nghi ngờ",
        "characters_in_scene": ["dao_si", "a_sang"],
        "blocking": "Đạo sĩ đầu quan tài, A Sáng cuối quan tài",
        "action": "Đạo sĩ gõ quạt lên nắp quan tài ba tiếng",
        "dialogue": [
            {"speaker": "dao_si", "to": "a_sang", "line": "Mèo đen. Đèn dầu. Nắp áo quan.", "intent": "ra lệnh"},
            {"speaker": "a_sang", "to": "dao_si", "line": "Nghĩa là sao, thầy?", "intent": "hỏi dồn"},
        ],
        "reaction": {"who": "a_sang", "what": "nuốt khan, siết quai đèn"},
        "shot": {"size": "OTS", "angle": "eye-level", "subject": "đạo sĩ", "purpose": "nhận luật cùng A Sáng", "move": "static"},
        "continuity": {"from_prev": "bắt tiếng bước chân", "carry": "đèn dầu tay phải"},
        "voiceover": "Đạo sĩ gõ quạt lên nắp quan tài. \"Mèo đen. Đèn dầu. Nắp áo quan.\" A Sáng nuốt khan: \"Nghĩa là sao, thầy?\"",
        "motion": "The old Daoist taps his fan on the coffin lid; A Sang swallows and grips the lamp; camera: static OTS.",
    }


def good_episode() -> dict:
    scenes = [acted_scene(i, (i - 1) // 3 + 1) for i in range(1, 13)]
    scenes[0]["scene_type"] = "dan_truyen"
    for k in ("dialogue", "reaction", "blocking", "action"):
        scenes[0].pop(k, None)
    scenes[0]["voiceover"] = "Đêm mưa cuối làng, nhà họ Thẩm thắp nến trắng suốt ba đêm."
    scenes[0]["motion"] = "Rain streams off the eaves as candle flames shiver inside the house; camera: slow crane down to reveal the coffin through the doorway."
    return {"slug": "test_good", "character_bible": BIBLE, "scenes": scenes}


class ScriptDirectionLintTests(unittest.TestCase):
    def test_good_episode_passes(self):
        rep = lint.lint_episode(good_episode())
        self.assertTrue(rep["passed"], rep["issues"])
        self.assertGreaterEqual(rep["acted_ratio"], 0.6)

    def test_legacy_narrated_episode_fails(self):
        legacy = {"slug": "legacy", "character_bible": {"characters": [{"id": "a_sang"}]}, "scenes": [
            {"id": i, "act": (i - 1) // 3 + 1,
             "voiceover": "A Sáng là cháu nội nhà họ Thẩm, hai mươi sáu tuổi, cậu nói cậu nghe tiếng đồn về ba điều cấm.",
             "motion": "Slow push-in on the old Daoist"}
            for i in range(1, 13)
        ]}
        rep = lint.lint_episode(legacy)
        self.assertFalse(rep["passed"])
        codes = rep["issue_counts"]
        for code in ("REPORTED_SPEECH_WIDESPREAD", "PROFILE_DUMP_WIDESPREAD", "GENERIC_MOTION", "ACTED_RATIO_LOW"):
            self.assertIn(code, codes)

    def test_dialogue_scene_requires_reaction_and_known_speaker(self):
        ep = good_episode()
        sc = ep["scenes"][3]
        sc.pop("reaction")
        sc["dialogue"][0]["speaker"] = "nguoi_la"
        rep = lint.lint_episode(ep)
        scene_codes = {i["code"] for i in rep["issues"] if i["scene"] == sc["id"]}
        self.assertIn("REACTION_MISSING", scene_codes)
        self.assertIn("UNKNOWN_SPEAKER", scene_codes)

    def test_exposition_and_long_lines_flagged(self):
        ep = good_episode()
        sc = ep["scenes"][4]
        sc["dialogue"][0]["line"] = "Như cậu biết đấy, nhà họ Thẩm có ba điều cấm khi canh linh cữu mà ai trong làng này cũng đã từng nghe kể lại từ đời ông bà."
        codes = {i["code"] for i in lint.lint_episode(ep)["issues"] if i["scene"] == sc["id"]}
        self.assertIn("EXPOSITION_LINE", codes)
        self.assertIn("LINE_TOO_LONG", codes)

    def test_motivated_camera_move_is_not_generic(self):
        self.assertTrue(lint._is_generic_motion("Slow push-in"))
        self.assertTrue(lint._is_generic_motion("slow tracking shot of the young grandson arriving"))
        self.assertFalse(lint._is_generic_motion("Slow push-in as A Sang turns and stares at the coffin"))

    def test_direct_quote_with_colon_is_not_reported_speech(self):
        self.assertIsNone(lint.REPORTED_SPEECH_RE.search('A Sáng hỏi: "Nghĩa là sao?"'))
        self.assertIsNone(lint.REPORTED_SPEECH_RE.search('Ông nói khẽ, mắt không rời quan tài: "Đừng nhìn."'.replace(", mắt không rời quan tài", " thật khẽ")))
        self.assertIsNotNone(lint.REPORTED_SPEECH_RE.search("ông nói canh linh cữu có ba điều cấm"))

    def test_each_act_needs_confrontation(self):
        ep = good_episode()
        for sc in ep["scenes"]:
            if sc["act"] == 4:
                sc["dialogue"] = sc["dialogue"][:1]
        codes = lint.lint_episode(copy.deepcopy(ep))["issue_counts"]
        self.assertIn("NO_CONFRONTATION", codes)


if __name__ == "__main__":
    unittest.main()
