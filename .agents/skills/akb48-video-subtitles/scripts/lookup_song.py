#!/usr/bin/env python3
"""Find a sourced AKB48 song title without inventing romanization or meaning."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "glossaries" / "songs.csv"


def key(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip().casefold()


def load_songs(path: Path = CATALOG, episode: Path | None = None) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        catalog = list(csv.DictReader(stream))
    required = {"song_id", "source_ja", "preferred_latin", "source_url", "review_status"}
    if not catalog or not required.issubset(catalog[0]):
        raise ValueError("song glossary is missing required columns")
    ids = set()
    japanese = set()
    for item in catalog:
        if not all(item.get(name, "").strip() for name in required):
            raise ValueError("a song row lacks a required field")
        if item["song_id"] in ids or key(item["source_ja"]) in japanese:
            raise ValueError("duplicate song ID or Japanese title")
        ids.add(item["song_id"])
        japanese.add(key(item["source_ja"]))
    if episode:
        data = json.loads(episode.read_text(encoding="utf-8-sig"))
        overrides = data.get("songs", {})
        if not isinstance(overrides, dict):
            raise ValueError("episode songs must be an object")
        for ref, value in overrides.items():
            if not isinstance(value, dict):
                raise ValueError(f"episode song {ref!r} must be an object")
            record = next((r for r in catalog if ref == r["song_id"] or key(ref) == key(r["source_ja"])), None)
            if record is None:
                if not value.get("source_ja") or not value.get("preferred_latin"):
                    raise ValueError(f"new episode song {ref!r} requires source_ja and preferred_latin")
                record = {"song_id": ref, "artist": value.get("artist", ""),
                          "source_ja": value["source_ja"], "preferred_latin": "",
                          "source_kind": "episode_specific", "source_url": "",
                          "official_source_url": "", "review_status": "pending_source_verification",
                          "notes": ""}
                if any(r["song_id"] == ref or key(r["source_ja"]) == key(record["source_ja"]) for r in catalog):
                    raise ValueError(f"duplicate episode song {ref!r}")
                catalog.append(record)
            if value.get("source_ja") and value["source_ja"] != record["source_ja"]:
                raise ValueError(f"cannot change Japanese identity for song {ref!r}")
            for field in ("preferred_latin", "source_url", "review_status", "notes"):
                if field in value:
                    if not isinstance(value[field], str):
                        raise ValueError(f"{field} must be a string")
                    record[field] = value[field]
            if not record.get("preferred_latin", "").strip():
                raise ValueError(f"song {ref!r} has no Latin form")
            if "review_status" not in value:
                record["review_status"] = "episode_override"
    return catalog


def match_song(name: str, entries: list[dict]) -> dict | None:
    query = key(name)
    for record in entries:
        if query in (key(record["song_id"]), key(record["source_ja"]),
                     key(record["preferred_latin"])):
            return record
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title", help="Japanese title, established Latin spelling, or song ID")
    parser.add_argument("--songs", type=Path, default=CATALOG)
    parser.add_argument("--episode", type=Path)
    parser.add_argument("--allow-fallback", action="store_true",
                        help="for an unknown Japanese title, return Japanese as explicitly unverified")
    args = parser.parse_args(argv)
    try:
        entries = load_songs(args.songs, args.episode)
        found = match_song(args.title, entries)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"error": "catalog_error", "detail": str(exc)}, ensure_ascii=True))
        return 2
    if found is None:
        if args.allow_fallback and any("\u3040" <= c <= "\u9fff" for c in args.title):
            print(json.dumps({"title": args.title, "source_ja": args.title,
                              "preferred_latin": None, "review_status": "source_fallback",
                              "is_unverified_fallback": True}, ensure_ascii=True))
            return 0
        print(json.dumps({"error": "unknown_song", "query": args.title,
                          "hint": "Check an official release or a 48 Group wiki; do not invent romanization."},
                         ensure_ascii=True))
        return 1
    print(json.dumps({
        "song_id": found["song_id"], "source_ja": found["source_ja"],
        "title": found["preferred_latin"], "preferred_latin": found["preferred_latin"],
        "artist": found.get("artist") or None,
        "source_kind": found.get("source_kind") or None,
        "source_url": found.get("source_url") or None,
        "official_source_url": found.get("official_source_url") or None,
        "review_status": found["review_status"],
        "is_unverified_fallback": False,
        "note": found.get("notes") or None
    }, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
