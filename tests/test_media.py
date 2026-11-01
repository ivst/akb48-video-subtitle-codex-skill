"""Regression tests for styled ASS and FFprobe media metadata."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "akb48-video-subtitles" / "scripts"


def run_ass(text: str, *flags: str) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "test.ass"
        path.write_bytes(text.encode("utf-8"))
        proc = subprocess.run([sys.executable, str(SCRIPTS / "check_ass.py"),
                               str(path), *flags, "--json"], capture_output=True,
                              encoding="utf-8", text=True)
        if not proc.stdout:
            raise AssertionError(proc.stderr)
        return proc.returncode, json.loads(proc.stdout)


def load_probe():
    spec = importlib.util.spec_from_file_location("probe_media", SCRIPTS / "probe_media.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ASSTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = (ROOT / "examples" / "demo.ass").read_text(encoding="utf-8")

    def test_demo_allows_overlays_and_drawn_panels(self):
        code, body = run_ass(self.demo, "--width", "1920", "--height", "1080", "--duration", "6")
        self.assertEqual(code, 0, body["errors"])
        self.assertEqual(body["details"]["dialogue_events"], 8)
        self.assertTrue(body["details"]["overlays_allowed"])

    def test_undefined_style_and_bad_timing(self):
        code, body = run_ass(self.demo.replace(",Speaker,", ",Nonexistent,"))
        self.assertEqual(code, 1)
        self.assertTrue(any("undefined style" in e for e in body["errors"]))
        code, body = run_ass(self.demo.replace("0:00:05.00", "0:00:15.00"), "--duration", "6")
        self.assertEqual(code, 1)
        self.assertTrue(any("after source" in e for e in body["errors"]))

    def test_playres_scaling_is_warning_unless_strict(self):
        code, body = run_ass(self.demo, "--width", "1280", "--height", "720")
        self.assertEqual(code, 0)
        self.assertTrue(any("PlayRes" in w for w in body["warnings"]))
        code, body = run_ass(self.demo, "--width", "1280", "--height", "720",
                             "--strict-resolution")
        self.assertEqual(code, 1)

    def test_line_break_warning(self):
        data = self.demo.replace("Welcome back!\\NWho's ready?",
                                 "Welcome!\\NWho's here?\\NIt's time!")
        code, body = run_ass(data, "--max-lines", "2")
        self.assertEqual(code, 0)
        self.assertTrue(any("hard-broken" in w for w in body["warnings"]))

    def test_empty_text_fails(self):
        code, body = run_ass(self.demo.replace("I am! Let's do this.", r"{\bord1}"))
        self.assertEqual(code, 1)
        self.assertTrue(any("empty Dialogue" in e for e in body["errors"]))

    def test_invalid_dimensions_and_no_events(self):
        code, body = run_ass(self.demo.replace("PlayResX: 1920", "PlayResX: no"))
        self.assertEqual(code, 1)
        code, body = run_ass(self.demo.replace("[Events]", "[No Events]"))
        self.assertEqual(code, 1)
        self.assertIn("no Dialogue events", body["errors"])


class ProbeTests(unittest.TestCase):
    def test_ffprobe_parses_fractional_fps_and_stream_languages(self):
        module = load_probe()
        fake = {"format": {"duration": "6.000", "format_name": "mov,mp4"},
                "streams": [
                    {"index": 0, "codec_type": "video", "codec_name": "h264",
                     "width": 1920, "height": 1080, "avg_frame_rate": "30000/1001"},
                    {"index": 1, "codec_type": "audio", "codec_name": "aac",
                     "channels": 2, "tags": {"language": "jpn"}},
                    {"index": 2, "codec_type": "subtitle", "codec_name": "ass",
                     "tags": {"language": "rus"}}
                ]}
        fake_proc = SimpleNamespace(returncode=0, stdout=json.dumps(fake), stderr="")
        with patch.object(module.shutil, "which", return_value="ffprobe"), \
             patch.object(module.subprocess, "run", return_value=fake_proc):
            data = module.inspect(Path("/tmp/synthetic.mp4"))
        self.assertEqual(data["fps"]["numerator"], 30000)
        self.assertEqual(data["fps"]["denominator"], 1001)
        self.assertEqual(data["audio"][0]["language"], "jpn")
        self.assertEqual(data["subtitles"][0]["language"], "rus")

    def test_missing_ffprobe_is_error(self):
        module = load_probe()
        with patch.object(module.shutil, "which", return_value=None):
            with self.assertRaises(RuntimeError):
                module.inspect(Path("video.mp4"))


if __name__ == "__main__":
    unittest.main()
