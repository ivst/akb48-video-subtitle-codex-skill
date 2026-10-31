#!/usr/bin/env python3
"""Audit Japanese member mentions against the target subtitle track."""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path
from subtitle_utils import emit, read_srt, report

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MEMBERS = ROOT / "glossaries" / "members" / "ru.csv"


def normalized(value: str, *, japanese: bool = False) -> str:
    text = unicodedata.normalize("NFKC", value)
    if japanese:
        text = "".join(chr(ord(c) - 96) if "\u30a1" <= c <= "\u30f6" else c for c in text)
    return re.sub(r"[\s\u3000]+", "", text).casefold()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="source Japanese SRT")
    parser.add_argument("--target", required=True, type=Path, help="translated SRT")
    parser.add_argument("--members", type=Path, default=DEFAULT_MEMBERS, help="locale member CSV")
    parser.add_argument("--episode", type=Path, help="optional episode.json with names overrides and forbidden spellings")
    parser.add_argument("--tolerance", type=float, default=.75, help="timeline matching margin, seconds")
    parser.add_argument("--strict", action="store_true", help="treat unconfirmed mentions as errors, not warnings")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not 0 <= args.tolerance <= 10:
        parser.error("--tolerance must be between 0 and 10 seconds")
    try:
        source, target = read_srt(args.source), read_srt(args.target)
        with args.members.open(encoding="utf-8-sig", newline="") as handle:
            members = list(csv.DictReader(handle))
        overrides = json.loads(args.episode.read_text(encoding="utf-8")).get("names", {}) if args.episode else {}
        if not isinstance(overrides, dict):
            raise ValueError("episode names must be an object")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    warnings: list[str] = []
    errors: list[str] = []
    details: list[dict] = []
    # Matching only source text that explicitly names a person; implicit nicknames
    # and pronouns cannot be proved by this deterministic checker.
    alias_map: dict[str, list[str]] = {}
    alias_file = ROOT / "glossaries" / "aliases.csv"
    with alias_file.open(encoding="utf-8-sig", newline="") as handle:
        for a in csv.DictReader(handle):
            alias_map.setdefault(a["source_ja"], []).append(a["alias_ja"])

    norm_target = [(cue, normalized(cue["text"])) for cue in target]
    flagged_forbidden = set()
    for member in members:
        japanese = member["source_ja"]
        override = overrides.get(japanese, {})
        if not isinstance(override, dict):
            errors.append(f"{japanese}: episode override is not an object")
            continue
        spelling = override.get("target", member.get("target_form", ""))
        accepted = [spelling] if spelling else []
        accepted += override.get("aliases", [])
        forbidden = override.get("forbidden", [])
        if not all(isinstance(x, str) and x.strip() for x in accepted + forbidden):
            errors.append(f"{japanese}: invalid aliases/forbidden forms")
            continue
        source_forms = {normalized(n, japanese=True) for n in [japanese] + alias_map.get(japanese, [])}
        appearances = []
        for cue in source:
            text = normalized(cue["text"], japanese=True)
            if any(form and form in text for form in source_forms):
                appearances.append(cue)
        covered = 0
        missing = []
        for cue in appearances:
            # Allow a source cue to be split or re-timed into multiple target cues.
            overlap = [line for line, norm in norm_target
                       if line["end_ms"] + int(args.tolerance * 1000) >= cue["start_ms"]
                       and line["start_ms"] - int(args.tolerance * 1000) <= cue["end_ms"]]
            stitched = normalized(" ".join(line["text"] for line in overlap))
            if any(normalized(form) in stitched for form in accepted):
                covered += 1
            else:
                missing.append(cue["id"])
                message = f"{japanese}: no approved spelling near source cue {cue['id']} (may be omitted naturally)"
                (errors if args.strict else warnings).append(message)
        for bad in forbidden:
            bad_key = normalized(bad)
            # Do not count as forbidden a substring of the currently approved spelling.
            if any(bad_key == normalized(a) for a in accepted):
                errors.append(f"{japanese}: forbidden spelling is also approved: {bad}")
                continue
            for cue, norm in norm_target:
                if bad_key in norm and (japanese, cue["id"], bad) not in flagged_forbidden:
                    flagged_forbidden.add((japanese, cue["id"], bad))
                    errors.append(f"{japanese}: forbidden form '{bad}' in target cue {cue['id']}")
        if appearances or forbidden:
            details.append({"source_ja": japanese, "target_form": spelling,
                            "source_mentions": len(appearances), "covered": covered,
                            "missing_cue_ids": missing, "forbidden": forbidden})
    unknown_overrides = set(overrides) - {r["source_ja"] for r in members}
    for name in sorted(unknown_overrides):
        warnings.append(f"episode override for unknown member {name}")
    result = report("check_names", args.target, errors, warnings,
                    source=str(args.source), members=str(args.members), names=details,
                    explicit_japanese_mentions_only=True)
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
