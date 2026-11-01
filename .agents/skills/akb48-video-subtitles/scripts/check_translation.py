#!/usr/bin/env python3
"""Validate a translation chunk against its source IDs and bilingual glossary."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from check_srt import suspicious_japanese
from check_names import normalized
from subtitle_utils import emit, report

ROOT = Path(__file__).resolve().parent.parent


def cues_at(path: Path) -> list[dict]:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(document, dict) or not isinstance(document.get("cues"), list):
        raise ValueError(f"{path}: expected an object with a cues array")
    result = document["cues"]
    if not all(isinstance(item, dict) and isinstance(item.get("id"), (str, int))
               and isinstance(item.get("text"), str) for item in result):
        raise ValueError(f"{path}: every cue must have id and text")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="source Japanese chunk JSON")
    parser.add_argument("--translated", type=Path, required=True, help="translated chunk JSON")
    parser.add_argument("--target-lang", default="ru")
    parser.add_argument("--members", type=Path, help="optional member glossary CSV")
    parser.add_argument("--episode", type=Path, help="optional episode.json overrides")
    parser.add_argument("--strict-japanese", action="store_true")
    parser.add_argument("--strict-names", action="store_true")
    parser.add_argument("--allow-japanese", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        originals = cues_at(args.input)
        translated = cues_at(args.translated)
        episode = json.loads(args.episode.read_text(encoding="utf-8")) if args.episode else {}
        if not isinstance(episode,dict):
            raise ValueError("episode must be an object")
        overrides = episode.get("names", {})
        if not isinstance(overrides, dict):
            raise ValueError("episode names must be an object")
        members = []
        if args.members:
            with args.members.open(encoding="utf-8-sig", newline="") as file:
                members = list(csv.DictReader(file))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    errors: list[str] = []
    warnings: list[str] = []
    lyrics_policy=episode.get('lyrics_policy','omit')
    if lyrics_policy not in ('omit','requested'):
        errors.append('lyrics_policy must be omit or requested')
    consent=episode.get('lyrics_request')
    if lyrics_policy=='requested' and (not isinstance(consent,str) or not consent.strip()):
        errors.append('requested lyrics require the user instruction in lyrics_request')
    for item in originals:
        if item.get('kind') in ('lyrics','background_music') and lyrics_policy!='requested':
            errors.append(f"cue {item['id']}: music/lyrics excluded by default; remove from scoped translation input and record omission")
    source_ids = [str(item["id"]) for item in originals]
    target_ids = [str(item["id"]) for item in translated]
    if not source_ids:
        errors.append("source chunk contains no cues")
    if len(set(source_ids)) != len(source_ids):
        errors.append("duplicate IDs in source")
    if len(set(target_ids)) != len(target_ids):
        errors.append("duplicate IDs in translated output")
    if source_ids != target_ids:
        errors.append("translated IDs/order do not exactly match source IDs/order")
    source_by_id = {str(c["id"]): c for c in originals}
    for line in translated:
        cue_id = str(line["id"])
        text = line["text"].strip()
        if not text:
            errors.append(f"cue {cue_id}: missing translation")
            continue
        reason = suspicious_japanese(text, args.target_lang, args.allow_japanese)
        if reason:
            (errors if args.strict_japanese else warnings).append(
                f"cue {cue_id}: {reason}; heuristic requires human review")
        src = source_by_id.get(cue_id)
        if not src:
            continue
        normalized_source = normalized(src["text"], japanese=True)
        normalized_target = normalized(text)
        for member in members:
            source_name = member["source_ja"]
            if normalized(source_name, japanese=True) not in normalized_source:
                continue
            override = overrides.get(source_name, {})
            allowed = [override.get("target", member["target_form"])] + override.get("aliases", [])
            allowed = [value for value in allowed if value]
            forbidden = override.get("forbidden", [])
            if not any(normalized(value) in normalized_target for value in allowed):
                (errors if args.strict_names else warnings).append(
                    f"cue {cue_id}: name {source_name} not confirmed in translation; could be pronoun")
            if any(normalized(value) in normalized_target for value in forbidden if value):
                errors.append(f"cue {cue_id}: forbidden spelling for {source_name}")
    result = report("check_translation", args.translated, errors, warnings,
                    input_file=str(args.input),
                    input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                    source_cues=len(source_ids), translated_cues=len(target_ids),
                    exact_id_alignment=source_ids == target_ids, target_lang=args.target_lang)
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
