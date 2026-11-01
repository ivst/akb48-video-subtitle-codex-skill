"""Real FFmpeg integration; skipped where media tools are not installed."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents/skills/akb48-video-subtitles/scripts"


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/FFprobe unavailable")
class FullMediaTests(unittest.TestCase):
    def invoke(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8", timeout=60)

    def test_real_frames_audio_and_episode_report(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            media = root / "source.mp4"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                            "color=c=blue:s=160x90:r=10:d=1", "-f", "lavfi", "-i",
                            "sine=frequency=440:duration=1", "-c:v", "mpeg4", "-c:a", "aac",
                            str(media)], check=True, capture_output=True, timeout=30)
            decoded = self.invoke("check_decode.py", "--source", media, "--rendered", media, "--json")
            self.assertEqual(decoded.returncode, 0, decoded.stdout + decoded.stderr)
            self.assertEqual(json.loads(decoded.stdout)["details"]["source_decode"]["decoded_video_frames"], 10)
            hashed = self.invoke("compare_audio.py", "--source", media, "--rendered", media, "--json")
            self.assertEqual(hashed.returncode, 0, hashed.stdout + hashed.stderr)
            project = root / "episode"
            created = self.invoke("init_project.py", "--project", project, "--episode-id", "media-test", "--locale", "en")
            self.assertEqual(created.returncode, 0, created.stderr)
            manifest = project / "episode.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["source"]["media"] = str(media)
            data["output"]["video"] = str(media)
            data["requested_outputs"] = ["srt", "video"]
            data["duration_seconds"] = 1
            manifest.write_text(json.dumps(data), encoding="utf-8")
            for path in ("source/dialogue.ja.srt", "output/dialogue.en.srt"):
                (project / path).write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")
            result = self.invoke("run_checks.py", "--project", project, "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((project / "report.json").read_text(encoding="utf-8"))
            checks = {c["tool"]: c for c in report["checks"]}
            self.assertEqual(checks["check_decode"]["status"], "pass")
            self.assertEqual(checks["compare_audio"]["status"], "pass")
            # The same report must fail when the rendered file is not decodable.
            damaged = root / "damaged.mp4"
            damaged.write_bytes(b"not a media file")
            data["output"]["video"] = str(damaged)
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.invoke("run_checks.py", "--project", project, "--json")
            self.assertEqual(result.returncode, 1)
            report = json.loads((project / "report.json").read_text(encoding="utf-8"))
            self.assertIn("check_decode", report["failed_checks"])


if __name__ == "__main__":
    unittest.main()
