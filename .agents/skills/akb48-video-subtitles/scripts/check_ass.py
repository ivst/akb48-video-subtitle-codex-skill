#!/usr/bin/env python3
"""Static ASS layout validation; not a substitute for rendering a real frame."""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from subtitle_utils import emit, report

CLOCK = re.compile(r"(?P<h>\d+):(?P<m>\d{2}):(?P<s>\d{2})\.(?P<cs>\d{2})$")
TAGS = re.compile(r"\{[^}]*\}")
DRAWING = re.compile(r"\\p[1-9]\d*")
HARD_BREAK = re.compile(r"\\[Nn]")


def ass_ms(value: str) -> int:
    match = CLOCK.fullmatch(value.strip())
    if not match or int(match["m"]) > 59 or int(match["s"]) > 59:
        raise ValueError(f"invalid ASS timestamp: {value}")
    return (int(match["h"]) * 3600 + int(match["m"]) * 60 + int(match["s"])) * 1000 + int(match["cs"]) * 10


def parse_ass(source: str):
    section = ""
    properties: dict[str, int] = {}
    styles: set[str] = set()
    events: list[dict] = []
    errors: list[str] = []
    style_fields: list[str] = []
    event_fields: list[str] = []
    for line_number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line.casefold()
            continue
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip().casefold()
        value = raw_value.strip()
        if section == "[script info]" and key in ("playresx", "playresy"):
            try:
                number = int(value)
                if number <= 0:
                    raise ValueError
                properties[key] = number
            except ValueError:
                errors.append(f"line {line_number}: invalid {key}")
        elif section in ("[v4+ styles]", "[v4 styles]"):
            if key == "format":
                style_fields = [c.strip().casefold() for c in value.split(",")]
            elif key == "style":
                cols = [c.strip() for c in value.split(",", max(0, len(style_fields) - 1))]
                if not style_fields or len(cols) != len(style_fields) or "name" not in style_fields:
                    errors.append(f"line {line_number}: malformed style")
                else:
                    name = cols[style_fields.index("name")]
                    if not name or name in styles:
                        errors.append(f"line {line_number}: empty/duplicate style '{name}'")
                    else:
                        styles.add(name)
        elif section == "[events]":
            if key == "format":
                event_fields = [c.strip().casefold() for c in value.split(",")]
            elif key == "dialogue":
                cols = [c.strip() for c in value.split(",", max(0, len(event_fields) - 1))]
                required = ("start", "end", "style", "text")
                if not event_fields or len(cols) != len(event_fields) or any(x not in event_fields for x in required):
                    errors.append(f"line {line_number}: malformed Dialogue")
                    continue
                event = dict(zip(event_fields, cols))
                event["line_number"] = line_number
                events.append(event)
    return properties, styles, events, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ass", type=Path)
    parser.add_argument("--width", type=int, help="actual video width")
    parser.add_argument("--height", type=int, help="actual video height")
    parser.add_argument("--strict-resolution", action="store_true",
                        help="fail if PlayRes differs from output frame size")
    parser.add_argument("--duration", type=float, help="source video duration, seconds")
    parser.add_argument("--max-lines", type=int, default=2)
    parser.add_argument("--max-cps", type=float, default=23)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if (args.width is None) != (args.height is None):
        parser.error("--width and --height must be used together")
    if args.width is not None and (args.width <= 0 or args.height <= 0):
        parser.error("video dimensions must be positive")
    if args.duration is not None and (not math.isfinite(args.duration) or args.duration <= 0):
        parser.error("--duration must be finite and positive")
    if args.max_lines < 1 or not math.isfinite(args.max_cps) or args.max_cps <= 0:
        parser.error("invalid readability limits")
    try:
        raw = args.ass.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    props, styles, events, errors = parse_ass(raw)
    warnings: list[str] = []
    if not props.get("playresx") or not props.get("playresy"):
        errors.append("missing PlayResX/PlayResY")
    if not styles:
        errors.append("no usable ASS styles")
    if not events:
        errors.append("no Dialogue events")
    if args.width and props.get("playresx") and props.get("playresy"):
        if (props["playresx"], props["playresy"]) != (args.width, args.height):
            message = (f'PlayRes {props["playresx"]}x{props["playresy"]} differs from '
                       f'video {args.width}x{args.height}; ASS coordinates can scale')
            (errors if args.strict_resolution else warnings).append(message)
    last_dialogue_start = -1
    for event in events:
        number = event["line_number"]
        style = event["style"]
        if style not in styles:
            errors.append(f"line {number}: undefined style '{style}'")
        try:
            start, end = ass_ms(event["start"]), ass_ms(event["end"])
            if end <= start:
                errors.append(f"line {number}: non-positive duration")
            if args.duration is not None and end > round(args.duration * 1000):
                errors.append(f"line {number}: ends after source duration")
        except ValueError as exc:
            errors.append(f"line {number}: {exc}")
            continue
        markup = event["text"]
        # Drawn panels and speaker labels intentionally overlap dialogue.
        # Never flag overlapping ASS Dialogue events as errors.
        is_panel = style.casefold().startswith(("panel", "background", "shape"))
        is_speaker = style.casefold().startswith(("speaker", "name"))
        is_vector = bool(DRAWING.search(markup))
        visible = TAGS.sub("", markup).replace(r"\h", " ").strip()
        if not visible:
            errors.append(f"line {number}: empty Dialogue text")
            continue
        if is_panel or is_speaker or is_vector:
            continue
        if start < last_dialogue_start:
            warnings.append(f"line {number}: dialogue events not ordered chronologically")
        last_dialogue_start = start
        segments = HARD_BREAK.split(visible)
        if len(segments) > args.max_lines:
            warnings.append(f"line {number}: {len(segments)} hard-broken dialogue lines")
        cps = len("".join(segments)) / ((end - start) / 1000) if end > start else 0
        if cps > args.max_cps:
            warnings.append(f"line {number}: {cps:.1f} characters/s exceeds {args.max_cps:g}")
    result = report("check_ass", args.ass, errors, warnings,
                    playres=[props.get("playresx"), props.get("playresy")],
                    actual_size=[args.width, args.height], styles=sorted(styles),
                    dialogue_events=len(events), overlays_allowed=True)
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
