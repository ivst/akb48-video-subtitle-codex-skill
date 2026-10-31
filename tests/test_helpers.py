"""Regression tests for the skill's stdlib-only diagnostic scripts."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "akb48-video-subtitles" / "scripts"


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ENV = load_script("check_environment")


def cue(text="Hello world!", start="00:00:01,000", end="00:00:03,000", index="1"):
    return f"{index}\n{start} --> {end}\n{text}\n" if index is not None else f"{start} --> {end}\n{text}\n"


class SRTTests(unittest.TestCase):
    def run_srt(self, content: str, *flags: str):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "example.srt"
            path.write_bytes(content.encode("utf-8"))
            return subprocess.run([sys.executable, str(SCRIPTS / "check_srt.py"), str(path), *flags], text=True, capture_output=True)

    def test_valid_demo(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "check_srt.py"), str(ROOT / "examples" / "demo.srt")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_empty_and_whitespace_fail(self):
        for value in ("", "  \n  \n"):
            with self.subTest(value=value):
                self.assertEqual(self.run_srt(value).returncode, 1)

    def test_invalid_minute_and_second_fail(self):
        for invalid in ("00:60:00,000", "00:00:60,000", "00:99:00,000"):
            with self.subTest(invalid=invalid):
                result = self.run_srt(cue(start=invalid))
                self.assertEqual(result.returncode, 1)
                self.assertIn("invalid minutes/seconds", result.stdout)

    def test_non_increasing_and_overlap_fail(self):
        self.assertEqual(self.run_srt(cue(end="00:00:00,800")).returncode, 1)
        self.assertIn("overlaps", self.run_srt(cue() + "\n" + cue(start="00:00:02,000", end="00:00:04,000", index="2")).stdout)

    def test_mixed_and_bad_indices_fail(self):
        self.assertEqual(self.run_srt(cue(index="2")).returncode, 1)
        self.assertIn("mixed indexed", self.run_srt(cue() + "\n" + cue(index=None)).stdout)

    def test_unnumbered_and_crlf_bom_allowed(self):
        value = "\ufeff" + cue(index=None).replace("\n", "\r\n")
        self.assertEqual(self.run_srt(value).returncode, 0)

    def test_invalid_timing_and_empty_tags_fail(self):
        self.assertEqual(self.run_srt(cue().replace(" --> ", " -> ")).returncode, 1)
        self.assertEqual(self.run_srt(cue(text="<i> </i>")).returncode, 1)

    def test_outside_source_duration_fails(self):
        result = self.run_srt(cue(), "--duration", "2.5")
        self.assertEqual(result.returncode, 1)
        self.assertIn("ends after source duration", result.stdout)

    def test_readability_counts_spaces_and_decodes_entities(self):
        result = self.run_srt(cue(text="a b &amp; c", end="00:00:02,000"), "--max-cps", "6")
        self.assertEqual(result.returncode, 0)
        self.assertIn("WARN", result.stdout)
        self.assertIn("7.0 chars/s", result.stdout)

    def test_bad_options_rejected(self):
        for flags in (("--max-cps", "0"), ("--max-cps", "nan"), ("--max-lines", "0"), ("--duration", "-1")):
            with self.subTest(flags=flags):
                self.assertEqual(self.run_srt(cue(), *flags).returncode, 2)

    def test_out_of_order_fails(self):
        value = cue(start="00:00:05,000", end="00:00:06,000") + "\n" + cue(index="2")
        self.assertIn("starts before", self.run_srt(value).stdout)


class EnvironmentTests(unittest.TestCase):
    def test_failed_version_exit_is_error(self):
        with patch.object(ENV.shutil, "which", return_value="/usr/bin/ffmpeg"), patch.object(ENV.subprocess, "run", return_value=SimpleNamespace(returncode=3, stdout="", stderr="failed")):
            ok, description, _ = ENV.probe("ffmpeg")
        self.assertFalse(ok)
        self.assertIn("exited 3", description)

    def test_missing_executable_is_error(self):
        with patch.object(ENV.shutil, "which", return_value=None):
            self.assertFalse(ENV.probe("ffmpeg")[0])

    def test_empty_version_output_is_error(self):
        with patch.object(ENV.shutil, "which", return_value="ffmpeg"), patch.object(ENV.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")):
            self.assertFalse(ENV.probe("ffmpeg")[0])

    def test_filters_require_success_and_libass(self):
        for code, output, expected in ((0, " ... subtitles V->V render subtitles\n", True), (0, " ... scale V->V scale\n", False), (1, " ... subtitles V->V\n", False)):
            with self.subTest(code=code, output=output), patch.object(ENV.subprocess, "run", return_value=SimpleNamespace(returncode=code, stdout=output, stderr="")):
                self.assertEqual(ENV.has_ass_filter("ffmpeg")[0], expected)

    def test_require_ass_gate(self):
        with patch.object(ENV, "probe", side_effect=[(True, "ffmpeg version", "ffmpeg"), (True, "ffprobe version", "ffprobe")]), patch.object(ENV, "has_ass_filter", return_value=(False, "missing")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ENV.main(["--require-ass"]), 1)
        with patch.object(ENV, "probe", side_effect=[(True, "ffmpeg version", "ffmpeg"), (True, "ffprobe version", "ffprobe")]), patch.object(ENV, "has_ass_filter", return_value=(False, "missing")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ENV.main([]), 0)

    def test_ffprobe_failing_causes_failure(self):
        with patch.object(ENV, "probe", side_effect=[(True, "ffmpeg version", "ffmpeg"), (False, "exited 2", "ffprobe")]), patch.object(ENV, "has_ass_filter", return_value=(True, "available")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ENV.main([]), 1)


if __name__ == "__main__":
    unittest.main()
