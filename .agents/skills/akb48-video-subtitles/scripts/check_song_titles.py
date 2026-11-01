#!/usr/bin/env python3
"""Validate explicitly annotated song titles and flag possible unreviewed ones."""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

from check_translation import cues_at
from lookup_song import CATALOG, key, load_songs, match_song
from subtitle_utils import emit, report


def has_exact_title(text: str, title: str) -> bool:
    # Match canonical spelling and capitalization; do not accept invented
    # English meaning, transliteration variants, or a fragment of a longer word.
    normalized_text = unicodedata.normalize("NFKC", text)
    normalized_title = unicodedata.normalize("NFKC", title)
    return bool(re.search(r"(?<!\w)" + re.escape(normalized_title) + r"(?!\w)", normalized_text))


def check_titles(source: list[dict], translated: list[dict], entries: list[dict],
                 strict: bool) -> tuple[list[str], list[str], list[dict]]:
    errors: list[str] = []
    warnings: list[str] = []
    found: list[dict] = []
    target_by_id = {str(item["id"]): item["text"] for item in translated}
    for cue in source:
        cue_id = str(cue["id"])
        text = cue["text"]
        annotations = cue.get("song_ids", [])
        if isinstance(annotations, str):
            annotations = [annotations]
        if not isinstance(annotations, list) or not all(isinstance(x, str) and x for x in annotations):
            errors.append(f"cue {cue_id}: song_ids must be a list of nonempty IDs")
            continue
        identified: dict[str, bool] = {}
        for song_id in annotations:
            record = match_song(song_id, entries)
            if not record:
                errors.append(f"cue {cue_id}: unknown annotated song {song_id}; source verification needed")
            elif record["song_id"] != song_id:
                errors.append(f"cue {cue_id}: song_ids must reference stable IDs, not Japanese/Latin titles")
            else:
                identified[record["song_id"]] = True
        # If source clearly marks this as a song-title-only cue, its Japanese
        # text should resolve; otherwise flag it for human verification.
        if cue.get("kind") == "song_title" and not identified:
            matched = match_song(text.strip("「」『』\"' \t"), entries)
            if matched:
                identified[matched["song_id"]] = True
            else:
                errors.append(f"cue {cue_id}: unrecognized explicit song_title; do not translate by meaning")
        # Unannotated exact Japanese occurrences may be normal speech/lyrics:
        # flag possible lost titles as warnings, NEVER hard errors.
        candidate_ids = set(identified)
        for record in entries:
            if record["source_ja"] in text:
                candidate_ids.add(record["song_id"])
        output = target_by_id.get(cue_id)
        if output is None:
            if candidate_ids:
                errors.append(f"cue {cue_id}: translated cue ID missing for song check")
            continue
        for song_id in sorted(candidate_ids):
            record = match_song(song_id, entries)
            if record is None:
                continue
            confirmed = song_id in identified
            latin = record["preferred_latin"]
            valid = has_exact_title(output, latin)
            found.append({"cue_id": cue_id, "song_id": song_id,
                          "source_ja": record["source_ja"],
                          "expected_latin": latin, "matched": valid,
                          "confirmed_title": confirmed,
                          "review_status": record["review_status"]})
            if not valid:
                message = (f"cue {cue_id}: song {song_id} expected '{latin}' "
                           f"(not a translated meaning or invented romaji); "
                           f"{'confirmed' if confirmed else 'unconfirmed possible mention'}")
                if strict and confirmed:
                    errors.append(message)
                else:
                    warnings.append(message)
    return errors, warnings, found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="source JSON cues with optional song_ids")
    parser.add_argument("--translated", type=Path, required=True, help="translated JSON cues")
    parser.add_argument("--songs", type=Path, default=CATALOG)
    parser.add_argument("--episode", type=Path, help="optional episode manifest with approved song titles")
    parser.add_argument("--strict", action="store_true",
                        help="fail confirmed annotated title mismatches; guesses remain warnings")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        original = cues_at(args.input)
        target = cues_at(args.translated)
        entries = load_songs(args.songs, args.episode)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    errors, warnings, matches = check_titles(original, target, entries, args.strict)
    result = report("check_song_titles", args.translated, errors, warnings,
                    source_file=str(args.input), catalog=str(args.songs),
                    confirmed=sum(item["confirmed_title"] for item in matches),
                    potential=sum(not item["confirmed_title"] for item in matches),
                    matched=sum(item["matched"] for item in matches),
                    matches=matches)
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
