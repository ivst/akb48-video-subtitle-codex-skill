"""Regression tests for per-episode durable translation and report contracts."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "akb48-video-subtitles"
SCRIPTS = SKILL / "scripts"
SAMPLES = ROOT / "examples" / "quality"


def invoke(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")


class TranslationProtocolTests(unittest.TestCase):
    def test_good_synthetic_chunk_and_mismatches(self):
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "src.json"
            out = Path(temp) / "out.json"
            shutil.copyfile(SAMPLES / "source.json", src)
            shutil.copyfile(SAMPLES / "translated.json", out)
            members = SKILL / "glossaries" / "members" / "ru.csv"
            flags = ("--input", str(src), "--translated", str(out),
                     "--target-lang", "ru", "--members", str(members), "--json")
            good = invoke("check_translation.py", *flags)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertEqual(json.loads(good.stdout)["details"]["source_cues"], 6)

            data = json.loads(out.read_text(encoding="utf-8"))
            data["cues"][1]["id"] = "001"
            out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            bad = invoke("check_translation.py", *flags)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("duplicate IDs", bad.stdout)

            data = json.loads((SAMPLES / "translated.json").read_text(encoding="utf-8"))
            data["cues"][1]["text"] = ""
            out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            empty = invoke("check_translation.py", *flags)
            self.assertEqual(empty.returncode, 1)
            self.assertIn("missing translation", empty.stdout)

    def test_japanese_strict_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out.json"
            content = json.loads((SAMPLES / "translated.json").read_text(encoding="utf-8"))
            content["cues"][1]["text"] = "こんにちは！"
            out.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
            result = invoke("check_translation.py", "--input", str(SAMPLES / "source.json"),
                            "--translated", str(out), "--target-lang", "ru",
                            "--strict-japanese", "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Japanese", result.stdout)

    def test_init_refuses_overwrites(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "episode"
            flags = ("--project", str(project), "--episode-id", "synthetic-001")
            self.assertEqual(invoke("init_project.py", *flags).returncode, 0)
            self.assertTrue((project / "episode.json").is_file())
            self.assertNotEqual(invoke("init_project.py", *flags).returncode, 0)

    def test_report_is_incomplete_without_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "episode"
            self.assertEqual(invoke("init_project.py", "--project", str(project),
                                    "--episode-id", "synthetic-002").returncode, 0)
            proc = invoke("run_checks.py", "--project", str(project), "--require-translation", "--json")
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            details = json.loads((project / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(details["status"], "incomplete")
            self.assertEqual(details["executed_checks"], 0)
            self.assertTrue(details["missing_checks"])

    def test_report_records_actual_commands_and_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "episode"
            self.assertEqual(invoke("init_project.py", "--project", str(project),
                                    "--episode-id", "synthetic-003").returncode, 0)
            episode_path = project / "episode.json"
            episode = json.loads(episode_path.read_text(encoding="utf-8"))
            episode["duration_seconds"] = 14
            episode_path.write_text(json.dumps(episode, ensure_ascii=False), encoding="utf-8")
            for src, dst in (("ja.srt", "source/dialogue.ja.srt"),
                             ("ru.srt", "output/dialogue.ru.srt"),
                             ("source.json", "work/chunks/source.json"),
                             ("translated.json", "work/chunks/translated.json")):
                shutil.copyfile(SAMPLES / src, project / dst)
            proc = invoke("run_checks.py", "--project", str(project),
                          "--require-translation", "--json")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result = json.loads((project / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["executed_checks"], 4)
            self.assertTrue(all(entry["status"] == "pass" for entry in result["checks"]))
            self.assertTrue(all(entry["result"].get("sha256") for entry in result["checks"]))
            self.assertEqual(len(result["checks"]), 4)


if __name__ == "__main__":
    unittest.main()
