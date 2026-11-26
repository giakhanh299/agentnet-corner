import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studio"))
import thumbnail  # noqa: E402


class ThumbnailTests(unittest.TestCase):
    def test_render_cover_and_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            bg = tdp / "bg.jpg"
            Image.new("RGB", (720, 1280), (18, 28, 36)).save(bg, "JPEG")
            spec = {
                "episode": 1,
                "series": "Phim Ma Dân Gian Việt Nam",
                "title": "Ma Da Kéo Giò",
                "aigc_label": True,
                "scenes": [{"id": 1, "voiceover": "Chỉ còn tiếng kéo giò dưới bến… Đêm đó, nước sông Hậu rút cạn."}],
            }
            out_cover = tdp / "ep01_cover_9x16.jpg"
            thumbnail.render_cover(bg, spec, out_cover)
            self.assertTrue(out_cover.is_file())
            with Image.open(out_cover) as im:
                self.assertEqual(im.size, (1080, 1920))
            meta = thumbnail.build_metadata(spec, tdp / "ep01.mp4", out_cover)
            self.assertIn("Ma Da Kéo Giò", meta["publish_title"])
            self.assertIn("#PhimMaDanGian", meta["hashtags"])


if __name__ == "__main__":
    unittest.main()
