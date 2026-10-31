#!/usr/bin/env python3
"""Validate SRT timings, readability, and suspicious untranslated Japanese."""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from pathlib import Path
from subtitle_utils import emit, report, timestamp_ms

TIME = re.compile(r"(?P<start>\d{2,}:\d{2}:\d{2},\d{3})\s+-->\s+(?P<end>\d{2,}:\d{2}:\d{2},\d{3})")
TAG = re.compile(r"<[^>]*>")
KANA = re.compile(r"[\u3040-\u30ff]")
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
PROFILE_DIR = Path(__file__).resolve().parent.parent / "profiles"


def suspicious_japanese(text: str, locale: str, allowed: list[str]) -> str | None:
    if locale == "ja":
        return None
    candidate = text
    for exact in allowed:
        candidate = candidate.replace(exact, "")
    # Kanji overlap with Chinese; do not flag normal Han in a Chinese translation.
    if locale.startswith("zh"):
        return "Japanese kana retained" if KANA.search(candidate) else None
    if not (KANA.search(candidate) or HAN.search(candidate)):
        return None
    significant = [char for char in candidate if char.isalpha()]
    japanese = sum(bool(KANA.fullmatch(ch) or HAN.fullmatch(ch)) for ch in significant)
    return ("largely Japanese text" if significant and japanese / len(significant) >= .8
            else "Japanese script retained")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("srt", type=Path)
    parser.add_argument("--profile", help="named reading profile (currently ru)")
    parser.add_argument("--target-lang", default=None, help="target locale for suspicious Japanese detection")
    parser.add_argument("--strict-japanese", action="store_true", help="treat suspected Japanese leftovers as errors")
    parser.add_argument("--allow-japanese", action="append", default=[], metavar="TEXT",
                        help="exact approved Japanese title/name (repeatable)")
    parser.add_argument("--max-cps", type=float, default=None)
    parser.add_argument("--max-lines", type=int, default=None)
    parser.add_argument("--min-duration", type=float, default=None, help="minimum cue length in seconds (review warning)")
    parser.add_argument("--max-duration", type=float, default=None, help="maximum cue length in seconds (review warning)")
    parser.add_argument("--duration", type=float, default=None, help="source media duration in seconds")
    parser.add_argument("--allow-overlap", action="store_true", help="report overlap as warning instead of error")
    parser.add_argument("--json", action="store_true", help="machine-readable report with actual file SHA256")
    args = parser.parse_args(argv)

    config = {}
    if args.profile:
        file = PROFILE_DIR / (args.profile + ".json")
        if args.profile not in ("ru",) or not file.is_file():
            parser.error("unknown reading profile")
        config = json.loads(file.read_text(encoding="utf-8"))
    maximum = args.max_cps if args.max_cps is not None else config.get("max_cps", 23.0)
    lines_limit = args.max_lines if args.max_lines is not None else config.get("max_lines", 2)
    minimum = args.min_duration if args.min_duration is not None else (
        config.get("min_duration_ms", 0) / 1000 if config else None)
    duration_limit = args.max_duration if args.max_duration is not None else (
        config.get("max_duration_ms", 0) / 1000 if config else None)
    locale = args.target_lang or config.get("locale")
    if not math.isfinite(maximum) or maximum <= 0 or lines_limit < 1:
        parser.error("--max-cps must be finite and positive; --max-lines must be >= 1")
    for name, value in (("--min-duration", minimum), ("--max-duration", duration_limit),
                        ("--duration", args.duration)):
        if value is not None and (not math.isfinite(value) or value <= 0):
            parser.error(f"{name} must be finite and positive")
    if minimum is not None and duration_limit is not None and minimum > duration_limit:
        parser.error("minimum duration exceeds maximum")

    errors: list[str] = []
    warnings: list[str] = []
    cues = []
    try:
        raw = args.srt.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    blocks = [b.strip() for b in re.split(r"\n\s*\n", raw.replace("\r\n", "\n").replace("\r", "\n")) if b.strip()]
    index_mode = None
    if not blocks:
        errors.append("no subtitle cues found")
    for n, block in enumerate(blocks, 1):
        lines = block.splitlines()
        indexed = bool(lines and lines[0].strip().isdigit())
        if index_mode is not None and indexed != index_mode:
            errors.append(f"cue {n}: mixed indexed and unindexed cues")
        index_mode = indexed
        offset = int(indexed)
        if indexed and int(lines[0]) != n:
            errors.append(f"cue {n}: expected index {n}")
        if len(lines) < offset + 2:
            errors.append(f"cue {n}: expected timing and subtitle text")
            continue
        match = TIME.fullmatch(lines[offset].strip())
        if match is None:
            errors.append(f"cue {n}: invalid timing line")
            continue
        try:
            start, end = timestamp_ms(match["start"]), timestamp_ms(match["end"])
        except ValueError as exc:
            errors.append(f"cue {n}: {exc}")
            continue
        if end <= start:
            errors.append(f"cue {n}: end must be after start")
            continue
        if args.duration is not None and end > round(args.duration * 1000):
            errors.append(f"cue {n}: ends after source duration")
        text = "\n".join(lines[offset + 1:]).strip()
        visible_lines = [html.unescape(TAG.sub("", line)).strip() for line in text.splitlines()]
        visible = " ".join(visible_lines).strip()
        if not visible:
            errors.append(f"cue {n}: empty text")
            continue
        cues.append((n, start, end))
        seconds = (end - start) / 1000
        cps = len("".join(visible_lines)) / seconds
        if cps > maximum:
            warnings.append(f"cue {n}: {cps:.1f} chars/s exceeds {maximum:g}")
        if len(visible_lines) > lines_limit:
            warnings.append(f"cue {n}: {len(visible_lines)} lines exceeds {lines_limit}")
        if minimum is not None and seconds < minimum:
            warnings.append(f"cue {n}: duration {seconds:.3f}s below {minimum:.3f}s")
        if duration_limit is not None and seconds > duration_limit:
            warnings.append(f"cue {n}: duration {seconds:.3f}s above {duration_limit:.3f}s")
        if locale:
            reason = suspicious_japanese(visible, locale, args.allow_japanese)
            if reason:
                message = f"cue {n}: {reason} (heuristic, needs human review)"
                (errors if args.strict_japanese else warnings).append(message)
    ordered = sorted(cues, key=lambda c: (c[1], c[2]))
    if [c[0] for c in ordered] != [c[0] for c in cues]:
        errors.append("cue starts before an earlier cue (out of chronological order)")
    max_end, max_n = -1, None
    for n, start, end in ordered:
        if start < max_end:
            message = f"cue {n}: overlaps earlier cue {max_n}"
            (warnings if args.allow_overlap else errors).append(message)
        if end > max_end:
            max_end, max_n = end, n

    result = report("check_srt", args.srt, errors, warnings, parsed_cues=len(cues),
                    profile=args.profile, target_lang=locale, cps_counts_visible_spaces=True,
                    preferred_duration_ms=config.get("preferred_duration_ms"))
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
