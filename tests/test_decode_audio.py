"""Regressions for full video decoding and bounded audio subprocesses."""
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/akb48-video-subtitles/scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIO = load("compare_audio")
DECODE = load("check_decode")
REAL_RUN = subprocess.run


class AudioTests(unittest.TestCase):
    def test_large_stderr_does_not_block_stdout(self):
        script = "import sys;sys.stderr.write('x'*2000000);print('SHA256='+'a'*64)"
        def run(command, **kwargs):
            return REAL_RUN([sys.executable, "-c", script], **kwargs)
        with patch.object(AUDIO.shutil, "which", return_value="ffmpeg"), patch.object(AUDIO.subprocess, "run", side_effect=run):
            self.assertEqual(AUDIO.audio_hash(Path("source.mp4"), 5), "a" * 64)

    def test_timeout_covers_entire_decode(self):
        def run(command, **kwargs):
            return REAL_RUN([sys.executable, "-c", "import time;time.sleep(10)"], **kwargs)
        with patch.object(AUDIO.shutil, "which", return_value="ffmpeg"), patch.object(AUDIO.subprocess, "run", side_effect=run):
            with self.assertRaises(subprocess.TimeoutExpired):
                AUDIO.audio_hash(Path("source.mp4"), .1)

    def test_invalid_hash_and_decoder_error_fail(self):
        for code, output in ((0, b"not a hash"), (1, b"SHA256=" + b"a" * 64)):
            with self.subTest(code=code), patch.object(AUDIO.shutil, "which", return_value="ffmpeg"), patch.object(AUDIO.subprocess, "run", return_value=subprocess.CompletedProcess([], code, output)):
                with self.assertRaises(RuntimeError):
                    AUDIO.audio_hash(Path("source.mp4"))


class DecodeTests(unittest.TestCase):
    def test_only_completed_success_with_frames_passes(self):
        for code, output, valid in ((0, b"frame= 60\nprogress=end\n", True),
                                    (1, b"frame=60\nprogress=end\n", False),
                                    (0, b"frame=60\nprogress=continue\n", False),
                                    (0, b"frame=0\nprogress=end\n", False)):
            with self.subTest(code=code, output=output), patch.object(DECODE.shutil, "which", return_value="ffmpeg"), patch.object(DECODE.subprocess, "run", return_value=subprocess.CompletedProcess([], code, output)):
                if valid:
                    self.assertEqual(DECODE.decode(Path("video.mp4"))["decoded_video_frames"], 60)
                else:
                    with self.assertRaises(RuntimeError):
                        DECODE.decode(Path("video.mp4"))

    def test_frame_loss_is_a_failure(self):
        with patch.object(DECODE, "decode", side_effect=[{"decoded_video_frames": 60}, {"decoded_video_frames": 59}]), contextlib.redirect_stdout(io.StringIO()) as out:
            code = DECODE.main(["--source", "source.mp4", "--rendered", "rendered.mp4", "--json"])
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out.getvalue())["details"]["frame_count_matches"])

    def test_media_timeout_rejects_invalid_values(self):
        with contextlib.redirect_stderr(io.StringIO()):
            for value in ("0", "nan", "inf", "-1"):
                with self.subTest(value=value), self.assertRaises(SystemExit) as exc:
                    DECODE.main(["--source", "x", "--rendered", "y", "--timeout", value])
                self.assertEqual(exc.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
