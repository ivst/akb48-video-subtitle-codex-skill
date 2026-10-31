"""Check multilingual AKB48 name glossary integrity, provenance, and lookup behavior."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "akb48-video-subtitles"
GLOSSARY = SKILL / "glossaries"
LOCALES = ("ru", "en", "ko", "es-419", "id", "th", "zh-Hans", "zh-Hant")
STATUSES = {"user_supplied", "official_romanization", "secondary_romanization_draft",
            "community_reference", "derived_unreviewed", "romanized_fallback", "pending_native_review"}


class GlossaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = {}
        for locale in LOCALES:
            with (GLOSSARY / "members" / f"{locale}.csv").open(encoding="utf-8-sig", newline="") as handle:
                cls.content[locale] = list(csv.DictReader(handle))

    def test_eight_locales_and_83_canonical_members(self):
        source = [(r["entity_id"], r["source_ja"]) for r in self.content["ru"]]
        self.assertEqual(len(source), 83)
        self.assertEqual(len(set(source)), 83)
        self.assertTrue(all(jp and key for key, jp in source))
        for locale in LOCALES:
            with self.subTest(locale=locale):
                self.assertEqual(source, [(r["entity_id"], r["source_ja"]) for r in self.content[locale]])
                self.assertTrue(all(r["target_locale"] == locale and r["kind"] == "person" for r in self.content[locale]))

    def test_provenance_is_complete_and_truthful(self):
        for locale, rows in self.content.items():
            for r in rows:
                with self.subTest(locale=locale, member=r["source_ja"]):
                    self.assertIn(r["review_status"], STATUSES)
                    self.assertIn(r["confidence"], {"high", "medium", "low"})
                    self.assertFalse(r["reviewer"] or r["reviewed_on"], "Do not claim an unrecorded human review")
                    self.assertTrue(r["source_romaji"])
                    if r["review_status"] != "pending_native_review":
                        self.assertTrue(r["target_form"])
                    if r["review_status"] == "pending_native_review":
                        self.assertFalse(r["target_form"])
                    if r["review_status"] in {"official_romanization", "community_reference", "derived_unreviewed"}:
                        self.assertTrue(r["source_url"])

    def test_russian_json_preserves_csv_spellings(self):
        original = json.loads((GLOSSARY / "member_names.ja-ru.json").read_text(encoding="utf-8"))
        self.assertEqual(original, {r["source_ja"]: r["target_form"] for r in self.content["ru"]})
        self.assertTrue(all(r["review_status"] == "user_supplied" for r in self.content["ru"]))
        self.assertEqual(original["武藤小麟"], "Муто Орин")
        self.assertEqual(original["宮澤佐江"], "Миядзава Саэ")

    def test_profile_coverage(self):
        for locale, populated, status in (
            ("en", 83, None), ("ru", 83, None),
            ("ko", 83, "community_reference"), ("zh-Hant", 83, "community_reference"),
            ("zh-Hans", 83, "derived_unreviewed"),
            ("es-419", 83, "romanized_fallback"), ("id", 83, "romanized_fallback"),
            ("th", 0, "pending_native_review"),
        ):
            with self.subTest(locale=locale):
                rows = self.content[locale]
                self.assertEqual(sum(bool(r["target_form"]) for r in rows), populated)
                if status is not None:
                    self.assertTrue(all(r["review_status"] == status for r in rows if r["target_form"] or locale == "th"))

    def test_historical_forms_are_sourced_without_changing_russian(self):
        historical = {
            "宮澤佐江": ("미야자와 사에", "宮澤佐江", "宫泽佐江"),
            "高橋みなみ": ("타카하시 미나미", "高橋南", "高桥南"),
            "岡田奈々": ("오카다 나나", "岡田奈奈", "冈田奈奈"),
            "矢吹奈子": ("야부키 나코", "矢吹奈子", "矢吹奈子"),
        }
        indexed = {locale: {r["source_ja"]: r for r in self.content[locale]}
                   for locale in LOCALES}
        for ja, expected in historical.items():
            for locale, value in zip(("ko", "zh-Hant", "zh-Hans"), expected):
                row = indexed[locale][ja]
                with self.subTest(locale=locale, ja=ja):
                    self.assertEqual(row["target_form"], value)
                    self.assertTrue(row["source_url"])
                    self.assertIn(row["review_status"], {"community_reference", "derived_unreviewed"})
        self.assertIn("former NGT48", indexed["ko"]["荻野由佳"]["notes"])

    def test_official_english_form(self):
        self.assertEqual(self.content["en"][14]["target_form"], "Orin Muto")
        self.assertEqual(self.content["en"][23]["target_form"], "Mayuu Masai")
        self.assertTrue(all(r["review_status"] == "official_romanization" for r in self.content["en"][:45]))

    def test_csv_matches_repository_template(self):
        with (ROOT / "glossaries" / "template.csv").open(encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))
        for locale in LOCALES:
            with (GLOSSARY / "members" / f"{locale}.csv").open(encoding="utf-8", newline="") as handle:
                self.assertEqual(next(csv.reader(handle)), header)

    def lookup(self, *args):
        result = subprocess.run([sys.executable, str(SKILL / "scripts" / "lookup_member.py"), *args],
                                capture_output=True, text=True, encoding="utf-8")
        return result.returncode, json.loads(result.stdout)

    def test_alias_and_russian_contributor_form(self):
        status, record = self.lookup("--locale", "ru", "高橋彩音", "--strict")
        self.assertEqual(status, 0)
        self.assertEqual(record["source_ja"], "髙橋彩音")
        self.assertEqual(record["name"], "Такахаши Аянэ")

    def test_unapproved_and_pending_refuse_silent_guesses(self):
        result, body = self.lookup("--locale", "th", "武藤小麟")
        self.assertEqual(result, 1)
        self.assertEqual(body["error"], "pending_native_review")
        result, body = self.lookup("--locale", "th", "--allow-fallback", "武藤小麟")
        self.assertEqual(result, 0)
        self.assertEqual(body["name"], "Orin Muto")
        self.assertTrue(body["is_unverified_fallback"])
        result, body = self.lookup("--locale", "ko", "--strict", "武藤小麟")
        self.assertEqual(result, 1)
        self.assertEqual(body["error"], "unapproved_spelling")

    def test_unknown_member_does_not_guess(self):
        result, body = self.lookup("--locale", "ru", "完全不存在")
        self.assertEqual(result, 1)
        self.assertEqual(body["error"], "unknown_member")


if __name__ == "__main__":
    unittest.main()
