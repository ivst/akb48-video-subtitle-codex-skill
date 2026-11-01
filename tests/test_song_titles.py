"""Song title policy regressions: sourced Latin names, no translated meaning."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "akb48-video-subtitles"
CATALOG = SKILL / "glossaries" / "songs.csv"
SCRIPTS = SKILL / "scripts"


def run(name: str, *args: str) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(SCRIPTS / name), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")
    if not proc.stdout:
        raise AssertionError(f"script {name} did not return JSON: {proc.stderr}")
    return proc.returncode, json.loads(proc.stdout)


class SongCatalogTests(unittest.TestCase):
    def test_small_sourced_seed_has_unique_stable_ids(self):
        with CATALOG.open(encoding="utf-8-sig", newline="") as file:
            entries = list(csv.DictReader(file))
        self.assertEqual(len(entries), 5)
        self.assertEqual(len({r["song_id"] for r in entries}), 5)
        self.assertEqual(len({r["source_ja"] for r in entries}), 5)
        self.assertTrue(all(r["source_url"].startswith("https://") for r in entries))
        self.assertTrue(all(r["review_status"] == "community_reference" for r in entries))
        self.assertEqual({r["source_ja"]: r["preferred_latin"] for r in entries}["ヘビーローテーション"],
                         "Heavy Rotation")

    def test_lookup_differentiates_romaji_and_meaning(self):
        code, data = run("lookup_song.py", "愛の意味を考えてみた")
        self.assertEqual(code, 0)
        self.assertEqual(data["title"], "Ai no Imi wo Kangaete Mita")
        self.assertEqual(data["review_status"], "community_reference")
        code, value = run("lookup_song.py", "akb48-heavy-rotation")
        self.assertEqual(code, 0)
        self.assertEqual(value["title"], "Heavy Rotation")
        code, result = run("lookup_song.py", "Thinking About the Meaning of Love")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"], "unknown_song")

    def test_unknown_requires_source_or_explicit_japanese_fallback(self):
        code, result = run("lookup_song.py", "未知の曲")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"], "unknown_song")
        code, result = run("lookup_song.py", "--allow-fallback", "未知の曲")
        self.assertEqual(code, 0)
        self.assertIsNone(result["preferred_latin"])
        self.assertEqual(result["review_status"], "source_fallback")

    def test_episode_override_must_be_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            episode = Path(folder) / "episode.json"
            data = {"songs": {"akb48-heavy-rotation": {
                "preferred_latin": "Heavy Rotation",
                "review_status": "user_approved",
                "source_url": "https://akb48.fandom.com/wiki/Heavy_Rotation"
            }, "episode-new-song": {
                "source_ja": "架空の新曲", "preferred_latin": "Sample Song",
                "review_status": "user_approved"
            }}}
            episode.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            code, item = run("lookup_song.py", "--episode", str(episode), "架空の新曲")
            self.assertEqual(code, 0)
            self.assertEqual(item["title"], "Sample Song")
            self.assertEqual(item["review_status"], "user_approved")
            code, item = run("lookup_song.py", "--episode", str(episode), "ヘビーローテーション")
            self.assertEqual(code, 0)
            self.assertEqual(item["review_status"], "user_approved")

    def _check(self, source, translation, *flags):
        with tempfile.TemporaryDirectory() as folder:
            src = Path(folder) / "source.json"
            out = Path(folder) / "translated.json"
            src.write_text(json.dumps({"cues": source}, ensure_ascii=False), encoding="utf-8")
            out.write_text(json.dumps({"cues": translation}, ensure_ascii=False), encoding="utf-8")
            return run("check_song_titles.py", "--input", str(src), "--translated",
                       str(out), "--json", *flags)

    def test_annotated_song_titles_strictly_keep_latin(self):
        cue = {"id": "001", "text": "次の曲は「愛の意味を考えてみた」です",
               "song_ids": ["akb48-ai-no-imi"]}
        good = {"id": "001", "text": "Следующая песня — Ai no Imi wo Kangaete Mita."}
        code, report = self._check([cue], [good], "--strict")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["details"]["confirmed"], 1)
        self.assertEqual(report["details"]["matched"], 1)
        bad = {"id": "001", "text": "Следующая песня — «Размышления о смысле любви»."}
        code, report = self._check([cue], [bad], "--strict")
        self.assertEqual(code, 1)
        self.assertTrue(any("expected 'Ai no Imi wo Kangaete Mita'" in x for x in report["errors"]))

    def test_unannotated_phrase_is_warning_not_hard_error(self):
        cue = {"id": "001", "text": "会いたかった"}
        target = {"id": "001", "text": "Я так хотела тебя увидеть."}
        code, report = self._check([cue], [target], "--strict")
        self.assertEqual(code, 0)
        self.assertEqual(report["details"]["potential"], 1)
        self.assertTrue(report["warnings"])
        self.assertFalse(report["errors"])

    def test_explicit_title_without_catalog_fails_and_existing_english_title_works(self):
        cue = {"id": "001", "kind": "song_title", "text": "架空の知らない曲"}
        code, report = self._check([cue], [{"id": "001", "text": "Invented title"}], "--strict")
        self.assertEqual(code, 1)
        self.assertTrue(any("unrecognized explicit" in e for e in report["errors"]))
        known = {"id": "002", "kind": "song_title", "text": "ヘビーローテーション"}
        code, report = self._check([known], [{"id": "002", "text": "Heavy Rotation"}], "--strict")
        self.assertEqual(code, 0, report["errors"])

    def test_unknown_annotated_song_never_invents_title(self):
        source = [{"id": "001", "text": "架空の知らない曲",
                   "song_ids": ["nonexistent-song"]}]
        code, report = self._check(source, [{"id": "001", "text": "Invented Title"}], "--strict")
        self.assertEqual(code, 1)
        self.assertIn("unknown annotated song", report["errors"][0])


if __name__ == "__main__":
    unittest.main()
