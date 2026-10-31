"""Cross-platform checks of SRT language heuristics, timing, and name lookup."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "akb48-video-subtitles" / "scripts"
MEMBERS = ROOT / ".agents" / "skills" / "akb48-video-subtitles" / "glossaries" / "members" / "ru.csv"


def srt(*texts):
    return "\n".join(f"{n}\n00:00:{n:02},000 --> 00:00:{n + 1:02},500\n{text}\n"
                     for n, text in enumerate(texts, 1))


class QualityTests(unittest.TestCase):
    def run_script(self, script, files, *options):
        with tempfile.TemporaryDirectory() as d:
            paths = {}
            for name, content in files.items():
                path = Path(d) / name
                path.write_bytes(content.encode("utf-8"))
                paths[name] = str(path)
            args = [sys.executable, str(SCRIPTS / script)] + [next((value for name, value in paths.items() if x == "{" + name + "}"), x) for x in options] + ["--json"]
            proc = subprocess.run(args, capture_output=True, encoding="utf-8", text=True)
            self.assertTrue(proc.stdout, proc.stderr)
            return proc.returncode, json.loads(proc.stdout)

    def test_profile_duration_and_cps(self):
        code, report = self.run_script("check_srt.py", {"clip.srt": "1\n00:00:01,000 --> 00:00:01,400\nHi!\n"},
                                       "{clip.srt}", "--profile", "ru")
        self.assertEqual(code, 0)
        self.assertTrue(any("below 0.700s" in x for x in report["warnings"]))
        self.assertEqual(report["details"]["preferred_duration_ms"], 900)

    def test_strict_japanese_and_allowed_title(self):
        cue = srt("おはようございます")
        code, report = self.run_script("check_srt.py", {"clip.srt": cue}, "{clip.srt}",
                                       "--target-lang", "ru", "--strict-japanese")
        self.assertEqual(code, 1)
        self.assertTrue(any("largely Japanese" in x for x in report["errors"]))
        code, report = self.run_script("check_srt.py", {"clip.srt": cue}, "{clip.srt}",
                                       "--target-lang", "ru", "--strict-japanese",
                                       "--allow-japanese", "おはようございます")
        self.assertEqual(code, 0)
        self.assertFalse(report["errors"])

    def test_chinese_hanzi_are_not_japanese_leaks(self):
        code, report = self.run_script("check_srt.py", {"clip.srt": srt("你好 世界")}, "{clip.srt}",
                                       "--target-lang", "zh-Hans", "--strict-japanese")
        self.assertEqual(code, 0)
        self.assertFalse(any("Japanese" in x for x in report["warnings"] + report["errors"]))

    def test_chinese_kana_still_warns(self):
        code, report = self.run_script("check_srt.py", {"clip.srt": srt("你好 ありがとう")}, "{clip.srt}",
                                       "--target-lang", "zh-Hant")
        self.assertEqual(code, 0)
        self.assertTrue(any("kana retained" in x for x in report["warnings"]))

    def test_overlaps_can_be_allowed_and_are_sorted(self):
        data = ("1\n00:00:01,000 --> 00:00:03,000\nFirst\n\n"
                "2\n00:00:02,000 --> 00:00:04,000\nSecond\n\n"
                "3\n00:00:02,500 --> 00:00:03,500\nThird\n")
        code, report = self.run_script("check_srt.py", {"clip.srt": data}, "{clip.srt}")
        self.assertEqual(code, 1)
        self.assertTrue(any("overlaps" in x for x in report["errors"]))
        code, report = self.run_script("check_srt.py", {"clip.srt": data}, "{clip.srt}",
                                       "--allow-overlap")
        self.assertEqual(code, 0)
        self.assertTrue(any("overlaps" in x for x in report["warnings"]))

    def test_member_approved_spelling_and_forbidden_alias(self):
        original = "1\n00:00:01,000 --> 00:00:03,000\n武藤小麟が来た\n"
        target = "1\n00:00:01,000 --> 00:00:03,000\nПришла Муто Орин\n"
        episode = json.dumps({"names": {"武藤小麟": {"target": "Муто Орин",
                                                  "forbidden": ["Муто Олин"]}}}, ensure_ascii=False)
        code, report = self.run_script("check_names.py",
                  {"ja.srt": original, "ru.srt": target, "episode.json": episode},
                  "--source", "{ja.srt}", "--target", "{ru.srt}", "--episode", "{episode.json}",
                  "--members", str(MEMBERS))
        self.assertEqual(code, 0, report["errors"])
        record = next(item for item in report["details"]["names"] if item["source_ja"] == "武藤小麟")
        self.assertEqual(record["covered"], 1)

        code, report = self.run_script("check_names.py",
                  {"ja.srt": original, "ru.srt": target.replace("Орин", "Олин"), "episode.json": episode},
                  "--source", "{ja.srt}", "--target", "{ru.srt}", "--episode", "{episode.json}",
                  "--members", str(MEMBERS))
        self.assertEqual(code, 1)
        self.assertTrue(any("forbidden" in x for x in report["errors"]))

    def test_missing_name_warns_by_default_and_strict_fails(self):
        original = "1\n00:00:01,000 --> 00:00:03,000\n武藤小麟が来た\n"
        target = "1\n00:00:01,000 --> 00:00:03,000\nОна пришла\n"
        files = {"ja.srt": original, "ru.srt": target}
        options = ("--source", "{ja.srt}", "--target", "{ru.srt}", "--members", str(MEMBERS))
        code, info = self.run_script("check_names.py", files, *options)
        self.assertEqual(code, 0)
        self.assertTrue(info["warnings"])
        code, info = self.run_script("check_names.py", files, *options, "--strict")
        self.assertEqual(code, 1)
        self.assertTrue(info["errors"])


if __name__ == "__main__":
    unittest.main()
