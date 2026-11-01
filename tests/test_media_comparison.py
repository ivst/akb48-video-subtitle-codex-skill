"""Check source/output media comparison and report completeness without FFmpeg."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "akb48-video-subtitles" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


COMPARE = load("compare_media")


class MediaComparisonTests(unittest.TestCase):
    def fixture(self, audio=True, duration=10, size=(1920,1080), fps=24):
        return {
            "video": [{"width": size[0], "height": size[1]}],
            "audio": [{"codec": "aac"}] if audio else [],
            "subtitles": [],
            "duration_seconds": duration,
            "fps": {"decimal": fps, "numerator": fps, "denominator": 1}
        }

    def test_equal_metadata_is_valid(self):
        errors, warnings = COMPARE.compare(self.fixture(), self.fixture(), .5)
        self.assertFalse(errors)
        self.assertFalse(warnings)

    def test_source_audio_lost_fails(self):
        errors, _ = COMPARE.compare(self.fixture(), self.fixture(audio=False), .5)
        self.assertTrue(any("audio stream" in m for m in errors))

    def test_durations_enforced_and_resolution_warning(self):
        errors, warnings = COMPARE.compare(self.fixture(), self.fixture(duration=12, size=(1280,720)), .5)
        self.assertTrue(any("duration" in m for m in errors))
        self.assertTrue(any("size" in m for m in warnings))
        errors, warnings = COMPARE.compare(self.fixture(), self.fixture(size=(1280,720)), .5, strict_size=True)
        self.assertTrue(any("size" in m for m in errors))

    def test_requested_video_without_output_is_incomplete(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            proc = subprocess.run([sys.executable, str(SCRIPTS / "init_project.py"),
                "--project", str(root / "episode"), "--episode-id", "fake-episode"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            project = root / "episode"
            manifest = project / "episode.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["requested_outputs"] = ["video"]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(SCRIPTS / "run_checks.py"),
                "--project", str(project), "--json"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1, proc.stderr)
            body = json.loads((project / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(body["status"], "incomplete")
            self.assertIn("rendered_video", body["missing_checks"])


if __name__ == "__main__":
    unittest.main()
