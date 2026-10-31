"""Regression checks for bundled AKB48 terminology catalogs."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "akb48-video-subtitles"
TERMS = SKILL / "glossaries" / "terms"
LOCALES = ("ru", "en", "ko", "es-419", "id", "th", "zh-Hans", "zh-Hant")
CATEGORIES = {"fandom", "historical", "membership", "music", "performance", "event"}


class TerminologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = {}
        for locale in LOCALES:
            with (TERMS / (locale + ".csv")).open(encoding="utf-8-sig", newline="") as src:
                cls.catalog[locale] = list(csv.DictReader(src))

    def test_same_35_terms_across_eight_locales(self):
        keys = [(row["term_id"], row["source_ja"]) for row in self.catalog["ru"]]
        self.assertEqual(len(keys), 35)
        self.assertEqual(len(set(keys)), 35)
        for locale in LOCALES:
            with self.subTest(locale=locale):
                rows = self.catalog[locale]
                self.assertEqual([(r["term_id"], r["source_ja"]) for r in rows], keys)
                self.assertTrue(all(r["target_locale"] == locale for r in rows))
                self.assertTrue(all(r["category"] in CATEGORIES for r in rows))
                self.assertTrue(all(r["notes"] for r in rows))

    def test_unreviewed_terms_are_not_marked_verified(self):
        for locale, rows in self.catalog.items():
            for item in rows:
                with self.subTest(locale=locale, term=item["term_id"]):
                    self.assertFalse(item["reviewer"] or item["reviewed_on"])
                    self.assertTrue(item["source_url"])
                    self.assertEqual(item["review_status"],
                                     "pending_native_review" if locale == "th" else "editorial_draft")
                    self.assertEqual(bool(item["target_form"]), locale != "th")

    def test_distinct_semantics_not_conflated(self):
        for locale, rows in self.catalog.items():
            mapping = {r["term_id"]: r for r in rows}
            for first, second in (("senbatsu", "election"),
                                  ("graduation-stage", "graduation-concert"),
                                  ("final-performance", "graduation-stage"),
                                  ("handshake", "online-talk")):
                with self.subTest(locale=locale, first=first, second=second):
                    self.assertNotEqual(mapping[first]["source_ja"], mapping[second]["source_ja"])
                    self.assertNotEqual(mapping[first]["notes"], mapping[second]["notes"])
            self.assertIn("Historical", mapping["election"]["notes"])

    def test_russian_draft_matches_expected_phrases(self):
        values = {r["term_id"]: r["target_form"] for r in self.catalog["ru"]}
        self.assertIn("ошимен", values["oshi-men"])
        self.assertIn("сэмбацу", values["senbatsu"])
        self.assertIn("сэйтансай", values["birthday-stage"])

    def run_lookup(self, *args):
        proc = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "lookup_term.py"), *args],
            capture_output=True, encoding="utf-8", text=True
        )
        self.assertTrue(proc.stdout, proc.stderr)
        return proc.returncode, json.loads(proc.stdout)

    def test_lookup_by_term_id_and_japanese_alias(self):
        code, item = self.run_lookup("--locale", "ru", "graduation-stage")
        self.assertEqual(code, 0)
        self.assertEqual(item["source_ja"], "卒業公演")
        self.assertEqual(item["review_status"], "editorial_draft")
        code, alias = self.run_lookup("--locale", "ru", "神セブン")
        self.assertEqual(code, 0)
        self.assertEqual(alias["term_id"], "kami-seven")

    def test_thai_missing_is_explicit_and_fallback_is_japanese(self):
        code, error = self.run_lookup("--locale", "th", "選抜")
        self.assertEqual(code, 1)
        self.assertEqual(error["error"], "pending_native_review")
        code, value = self.run_lookup("--locale", "th", "--allow-fallback", "選抜")
        self.assertEqual(code, 0)
        self.assertEqual(value["name"], "選抜")
        self.assertEqual(value["review_status"], "source_fallback")
        self.assertTrue(value["is_unverified_fallback"])

    def test_unknown_term_is_never_synthesized(self):
        code, value = self.run_lookup("--locale", "ru", "架空の用語")
        self.assertEqual(code, 1)
        self.assertEqual(value["error"], "unknown_term")


if __name__ == "__main__":
    unittest.main()
