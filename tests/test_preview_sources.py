"""Ensure all public readmes keep source and rights notices with quoted frames."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READMES = (
    "README.md", "README.ru.md", "README.ko.md", "README.es-419.md",
    "README.id.md", "README.th.md", "README.zh-Hans.md", "README.zh-Hant.md"
)
EXCERPTS = {
    "12": ("aPznmLtjedw", "2026"),
    "13": ("mHF3TEk6lwQ", "2026"),
}


class ScreenshotAttributionTests(unittest.TestCase):
    def test_each_readme_labels_source_below_each_screenshot(self):
        for path in READMES:
            data = (ROOT / path).read_text(encoding="utf-8")
            for ep, (video_id, year) in EXCERPTS.items():
                with self.subTest(readme=path, episode=ep):
                    marker = f"examples/preview-episode-{ep}.jpg)"
                    self.assertEqual(data.count(marker), 1)
                    remainder = data.split(marker, 1)[1]
                    # The first paragraph after the image identifies the video;
                    # do not rely solely on attribution placed before the frame.
                    first_paragraph = remainder.split("\n\n", 2)[1]
                    self.assertIn(f"youtube.com/watch?v={video_id}", first_paragraph)
                    self.assertIn("AKB48の全力エンタメ学園", first_paragraph)
                    self.assertIn(year, first_paragraph)
            self.assertIn("[NOTICE](NOTICE)", data)

    def test_notice_excludes_both_examples_from_mit(self):
        data = (ROOT / "NOTICE").read_text(encoding="utf-8")
        for ep, (video_id, _) in EXCERPTS.items():
            with self.subTest(episode=ep):
                self.assertIn(f"examples/preview-episode-{ep}.jpg", data)
                self.assertIn(video_id, data)
        self.assertIn("NOT licensed", data)
        self.assertIn("Article 32", data)
        self.assertIn("Article 48", data)
        self.assertIn("does not declare", data)

    def test_examples_folder_explains_sources_and_synthetic_alternative(self):
        data = (ROOT / "examples" / "README.md").read_text(encoding="utf-8")
        self.assertIn("preview-episode-12.jpg", data)
        self.assertIn("preview-episode-13.jpg", data)
        self.assertIn("demo.ass", data)
        self.assertIn("../NOTICE", data)


if __name__ == "__main__":
    unittest.main()
