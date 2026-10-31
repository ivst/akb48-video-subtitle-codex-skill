#!/usr/bin/env python3
"""Look up Japanese AKB48/48 Group terms with locale and provenance metadata."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "glossaries"
LOCALES = ("ru", "en", "ko", "es-419", "id", "th", "zh-Hans", "zh-Hant")


def normalize(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value)).casefold()


def aliases() -> dict[str, str]:
    with (ROOT / "terms" / "aliases.csv").open(encoding="utf-8-sig", newline="") as stream:
        return {normalize(row["alias_ja"]): normalize(row["source_ja"])
                for row in csv.DictReader(stream)}


def lookup(name: str, locale: str) -> dict[str, str] | None:
    target = normalize(name)
    target = aliases().get(target, target)
    with (ROOT / "terms" / f"{locale}.csv").open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if target in (normalize(row["source_ja"]), normalize(row["term_id"])):
                return row
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", choices=LOCALES, required=True)
    parser.add_argument("--allow-fallback", action="store_true",
                        help="explicitly return the Japanese source term when target locale is not translated")
    parser.add_argument("term", help="Japanese term, documented alias, or stable term ID")
    options = parser.parse_args(argv)
    record = lookup(options.term, options.locale)
    if record is None:
        print(json.dumps({"error": "unknown_term", "query": options.term}, ensure_ascii=True))
        return 1
    translated = record["target_form"]
    status = record["review_status"]
    if not translated and not options.allow_fallback:
        print(json.dumps({"error": "pending_native_review", "source_ja": record["source_ja"],
                          "fallback_ja": record["source_ja"]}, ensure_ascii=True))
        return 1
    fallback = not bool(translated)
    print(json.dumps({
        "term_id": record["term_id"],
        "source_ja": record["source_ja"],
        "locale": options.locale,
        "name": translated if not fallback else record["source_ja"],
        "review_status": "source_fallback" if fallback else status,
        "category": record["category"],
        "meaning_note": record["notes"],
        "source_url": record["source_url"] or None,
        "target_reference_url": record["target_reference_url"] or None,
        "is_unverified_fallback": fallback,
    }, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
