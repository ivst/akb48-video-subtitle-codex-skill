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

    def test_init_records_relative_video_from_invocation_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "original.mp4"
            source.write_bytes(b"source path fixture")
            result = subprocess.run([sys.executable, str(SCRIPTS / "init_project.py"),
                "--project", "episode", "--episode-id", "relative-source",
                "--source-video", "original.mp4"], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "episode/episode.json").read_text(encoding="utf-8"))
            self.assertEqual(Path(manifest["source"]["media"]), source.resolve())

    def test_init_rejects_invalid_locale_and_file_as_project(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "episode"
            result = invoke("init_project.py", "--project", path, "--episode-id", "bad-locale",
                            "--locale", "../../outside")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(path.exists())
            path.write_text("preserve me", encoding="utf-8")
            result = invoke("init_project.py", "--project", path, "--episode-id", "file-path")
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(path.read_text(encoding="utf-8"), "preserve me")

    def test_manifest_cannot_disable_checks_through_invalid_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "episode"
            self.assertEqual(invoke("init_project.py", "--project", root,
                                    "--episode-id", "invalid-policy").returncode, 0)
            path = root / "episode.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            for field, value in [("audio_preservation", "unchange"),
                                 ("requested_outputs", []), ("requested_outputs", ["vidoe"]),
                                 ("requested_outputs", ["srt", "unsupported"]),
                                 ("locale", "../en")]:
                with self.subTest(field=field, value=value):
                    data = dict(original)
                    data[field] = value
                    path.write_text(json.dumps(data), encoding="utf-8")
                    result = invoke("run_checks.py", "--project", root, "--json")
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertFalse((root / "report.json").exists())

    def test_bom_manifest_is_readable_by_runner(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "episode"
            self.assertEqual(invoke("init_project.py", "--project", root,
                                    "--episode-id", "bom-manifest").returncode, 0)
            path = root / "episode.json"
            path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8-sig")
            result = invoke("run_checks.py", "--project", root, "--json")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "incomplete")

    def test_name_checkers_reject_malformed_alias_arrays(self):
        with tempfile.TemporaryDirectory() as folder:
            episode = Path(folder) / "episode.json"
            for entry in [{"aliases": "Мизуки"}, {"forbidden": "Мидзуки"},
                          {"aliases": [""]}, {"target": None}, []]:
                episode.write_text(json.dumps({"names": {"山内瑞葵": entry}}), encoding="utf-8-sig")
                commands = [
                    ("check_names.py", "--source", SAMPLES / "ja.srt", "--target", SAMPLES / "ru.srt"),
                    ("check_translation.py", "--input", SAMPLES / "source.json", "--translated", SAMPLES / "translated.json"),
                ]
                for script, *flags in commands:
                    with self.subTest(script=script, entry=entry):
                        result = invoke(script, *flags, "--episode", episode, "--json")
                        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                        self.assertNotIn("Traceback", result.stderr)

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

    def test_runner_fails_when_reviewed_translation_is_lost_in_display(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "episode"
            self.assertEqual(invoke("init_project.py", "--project", root,
                                    "--episode-id", "coverage").returncode, 0)
            manifest = root / 'episode.json'
            data = json.loads(manifest.read_text(encoding='utf-8'))
            data.update(duration_seconds=14, requested_outputs=['srt', 'ass'])
            manifest.write_text(json.dumps(data), encoding='utf-8')
            for src, dst in [('ja.srt', 'source/dialogue.ja.srt'),
                             ('source.json', 'work/chunks/source.json'),
                             ('translated.json', 'work/chunks/translated.json')]:
                shutil.copyfile(SAMPLES / src, root / dst)
            translated = json.loads((SAMPLES/'translated.json').read_text(encoding='utf-8'))['cues']
            presentation = {'schema_version': 1, 'speakers': {},
                'turns': {c['id']: {'speaker_id': None} for c in translated},
                'events': [{'id': 'd'+c['id'], 'kind': 'dialogue',
                    'start_ms': i*2000, 'end_ms': (i+1)*2000,
                    'rows': [{'speaker_id': None, 'source_ids': [c['id']], 'text': c['text']} ]}
                    for i, c in enumerate(translated)]}
            work = root/'work/presentation.json'
            def build_and_check():
                work.write_text(json.dumps(presentation), encoding='utf-8')
                built = invoke('build_presentation.py', '--input', work, '--episode', manifest,
                               '--output-dir', root/'output', '--overwrite')
                self.assertEqual(built.returncode, 0, built.stderr)
                return invoke('run_checks.py', '--project', root, '--require-translation', '--json')
            result = build_and_check()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            presentation['events'].pop()
            result = build_and_check()
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertIn('check_presentation', report['failed_checks'])
            self.assertNotIn('check_translation', report['failed_checks'])


if __name__ == "__main__":
    unittest.main()
