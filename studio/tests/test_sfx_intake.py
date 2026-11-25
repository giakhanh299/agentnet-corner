import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studio"))
import sfx_intake  # noqa: E402

SAMPLE = ROOT / "stickman-shorts" / "src" / "assets" / "audio" / "sfx" / "footsteps.ogg"


class SfxIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        sfx_intake.LIB = Path(self.tmp.name) / "sfx"
        sfx_intake.MANIFEST = sfx_intake.LIB / "manifest.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_license_rules(self):
        self.assertEqual(sfx_intake.normalize_license("CC0"), "CC0-1.0")
        self.assertEqual(sfx_intake.normalize_license("Pixabay Content License"), "Pixabay-Content-License")
        self.assertIsNone(sfx_intake.normalize_license("BBC Sound Effects RemArc"))
        self.assertIsNone(sfx_intake.normalize_license("CC BY-NC 4.0 non-commercial"))
        self.assertIsNone(sfx_intake.normalize_license(""))

    def test_extract_json_from_summary(self):
        res = {"summary": 'Đã tìm xong.\n{"sounds":[{"name":"Mưa lá chuối","category":"rain"}]}\nGiới hạn: ...'}
        self.assertEqual(sfx_intake.extract_sounds(res)[0]["name"], "Mưa lá chuối")
        nested = {"summary": '{"task_id":"x","result":{"category":"water","sounds":[{"title":"river.wav"}]}}'}
        self.assertEqual(sfx_intake.extract_sounds(nested)[0]["title"], "river.wav")

    def test_ingest_end_to_end_and_reject(self):
        self.assertTrue(SAMPLE.is_file())
        rows = [{
            "id": "task-0001", "status": "SUBMITTED",
            "result": {"summary": json.dumps({"sounds": [
                {"name": "Bước chân lá khô", "category": "footsteps", "license": "CC0",
                 "download_url": SAMPLE.as_uri(), "source_page_url": "https://example.org/x", "score": 7},
                {"name": "Mưa BBC", "category": "rain", "license": "BBC RemArc", "download_url": SAMPLE.as_uri()},
                {"name": "Chỉ có trang", "category": "rain", "license": "CC0", "download_url": ""},
                {"name": "Gió CC-BY thiếu tác giả", "category": "leaves_wind", "license": "CC-BY 4.0",
                 "download_url": SAMPLE.as_uri()},
            ]}, ensure_ascii=False)},
        }]
        stats = sfx_intake.run(rows)
        self.assertEqual(stats.get("ADDED"), 1)
        self.assertEqual(stats.get("REJECT"), 2)
        self.assertEqual(stats.get("PENDING"), 1)
        m = json.loads(sfx_intake.MANIFEST.read_text(encoding="utf-8"))
        entry = m["sounds"]["footsteps/buoc_chan_la_kho"]
        out = sfx_intake.LIB / entry["file"]
        self.assertTrue(out.is_file())
        self.assertLessEqual(out.stat().st_size, sfx_intake.MAX_OUT_BYTES)
        self.assertEqual(entry["license"], "CC0-1.0")

        # chạy lại cùng task + cùng link thì giữ nguyên không tải lại
        self.assertEqual(sfx_intake.run(rows).get("SAME"), 1)

        # task khác có bản điểm thấp hơn không được thay
        rows[0]["id"] = "task-0002"
        rows[0]["result"]["summary"] = json.dumps({"sounds": [
            {"name": "Bước chân lá khô", "category": "footsteps", "license": "CC0",
             "download_url": SAMPLE.as_uri(), "score": 3}]})
        self.assertEqual(sfx_intake.run(rows).get("KEEP_OLD"), 1)


if __name__ == "__main__":
    unittest.main()
