#!/usr/bin/env python3
"""Look up Japanese AKB48 member names in skill-bundled multilingual glossaries."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MEMBERS_DIR = SKILL_DIR / "glossaries" / "members"
ALIASES = SKILL_DIR / "glossaries" / "aliases.csv"
LOCALES = ("ru", "en", "ko", "es-419", "id", "th", "zh-Hans", "zh-Hant")
APPROVED_STATUSES = {"user_supplied", "official_romanization"}


def normalize(text: str) -> str:
    """Normalize spaces and width only, never merge different names by fuzzy match."""
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


def load_aliases() -> dict[str, str]:
    with ALIASES.open(encoding="utf-8-sig", newline="") as stream:
        return {normalize(r["alias_ja"]): r["source_ja"] for r in csv.DictReader(stream)}


def find(name: str, locale: str) -> dict[str, str] | None:
    key = normalize(name)
    key = normalize(load_aliases().get(key, key))
    with (MEMBERS_DIR / f"{locale}.csv").open(encoding="utf-8-sig", newline="") as stream:
        for record in csv.DictReader(stream):
            if normalize(record["source_ja"]) == key:
                return record
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", choices=LOCALES, required=True)
    parser.add_argument("--strict", action="store_true", help="only return contributor-supplied or officially romanized forms")
    parser.add_argument("--allow-fallback", action="store_true", help="use Latin source_romaji when localized form is missing")
    parser.add_argument("japanese_name", help="Japanese name as written in subtitle/source (known aliases supported)")
    args = parser.parse_args(argv)

    record = find(args.japanese_name, args.locale)
    if record is None:
        print(json.dumps({"error": "unknown_member", "query": args.japanese_name}, ensure_ascii=False))
        return 1

    target = record["target_form"]
    status = record["review_status"]
    if args.strict and status not in APPROVED_STATUSES:
        print(json.dumps({"error": "unapproved_spelling", "source_ja": record["source_ja"],
                          "review_status": status}, ensure_ascii=False))
        return 1
    fallback = False
    if not target:
        if not args.allow_fallback:
            print(json.dumps({"error": "pending_native_review", "source_ja": record["source_ja"],
                              "fallback_romaji": record["source_romaji"]}, ensure_ascii=False))
            return 1
        target = record["source_romaji"]
        status = "romanized_fallback"
        fallback = True

    print(json.dumps({
        "entity_id": record["entity_id"], "source_ja": record["source_ja"],
        "locale": args.locale, "name": target, "review_status": status,
        "confidence": record["confidence"] if not fallback else "low",
        "source_url": record["source_url"] or None,
        "is_unverified_fallback": fallback or status in
        {"secondary_romanization_draft", "derived_unreviewed", "romanized_fallback"},
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
