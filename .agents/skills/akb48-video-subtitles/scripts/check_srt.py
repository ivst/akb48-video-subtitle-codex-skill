#!/usr/bin/env python3
"""Validate SRT cues, timing, overlaps, and basic readability (stdlib only)."""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

TIMING = re.compile(r"(?P<start>\d{2,}:\d{2}:\d{2},\d{3})\s+-->\s+(?P<end>\d{2,}:\d{2}:\d{2},\d{3})")
TAG = re.compile(r"<[^>]*>")


def milliseconds(value: str) -> int:
    hours, minutes, remainder = value.split(":")
    seconds, millis = remainder.split(",")
    minute, second = int(minutes), int(seconds)
    if minute > 59 or second > 59:
        raise ValueError(f"invalid minutes/seconds in {value}")
    return ((int(hours) * 60 + minute) * 60 + second) * 1000 + int(millis)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("srt", type=Path)
    parser.add_argument("--max-cps", type=float, default=23.0, help="warn above this visible character count per second (default: 23)")
    parser.add_argument("--max-lines", type=int, default=2, help="warn above this many subtitle lines (default: 2)")
    parser.add_argument("--duration", type=float, help="optional source video duration in seconds; cues must not exceed it")
    args = parser.parse_args(argv)
    if not 0 < args.max_cps < float("inf") or args.max_lines < 1:
        parser.error("--max-cps must be finite and positive; --max-lines must be >= 1")
    if args.duration is not None and not 0 < args.duration < float("inf"):
        parser.error("--duration must be finite and positive")
    try:
        raw = args.srt.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    blocks = [block.strip() for block in re.split(r"\n\s*\n", raw.replace("\r\n", "\n").replace("\r", "\n")) if block.strip()]
    errors: list[str] = []
    warnings: list[str] = []
    parsed: list[tuple[int, int, int]] = []
    has_index: bool | None = None
    if not blocks:
        errors.append("no subtitle cues found")

    for ordinal, block in enumerate(blocks, 1):
        lines = block.splitlines()
        numbered = bool(lines and lines[0].strip().isdigit())
        if has_index is None:
            has_index = numbered
        elif numbered != has_index:
            errors.append(f"cue {ordinal}: mixed indexed and unindexed cues")
        offset = 1 if numbered else 0
        if numbered and int(lines[0].strip()) != ordinal:
            errors.append(f"cue {ordinal}: expected index {ordinal}, got {lines[0].strip()}")
        if len(lines) < offset + 2:
            errors.append(f"cue {ordinal}: expected timing and subtitle text")
            continue
        match = TIMING.fullmatch(lines[offset].strip())
        if match is None:
            errors.append(f"cue {ordinal}: invalid timing line")
            continue
        try:
            start = milliseconds(match.group("start"))
            end = milliseconds(match.group("end"))
        except ValueError as exc:
            errors.append(f"cue {ordinal}: {exc}")
            continue
        if end <= start:
            errors.append(f"cue {ordinal}: end must be after start")
            continue
        if args.duration is not None and end > round(args.duration * 1000):
            errors.append(f"cue {ordinal}: ends after source duration ({args.duration:g}s)")
        subtitle = "\n".join(lines[offset + 1:]).strip()
        visible_lines = [html.unescape(TAG.sub("", line)).strip() for line in subtitle.splitlines()]
        visible = "".join(visible_lines)
        if not visible.strip():
            errors.append(f"cue {ordinal}: empty text")
            continue
        parsed.append((ordinal, start, end))
        cps = len(visible) / ((end - start) / 1000)
        if cps > args.max_cps:
            warnings.append(f"cue {ordinal}: {cps:.1f} chars/s exceeds {args.max_cps:g}")
        if len(visible_lines) > args.max_lines:
            warnings.append(f"cue {ordinal}: {len(visible_lines)} lines exceeds {args.max_lines}")
    for previous, current in zip(parsed, parsed[1:]):
        if current[1] < previous[1]:
            errors.append(f"cue {current[0]} starts before cue {previous[0]}")
        if current[1] < previous[2]:
            errors.append(f"cue {current[0]} overlaps cue {previous[0]}")

    for message in errors:
        print("ERROR:", message)
    for message in warnings:
        print("WARN:", message)
    print(f"{len(parsed)} cues parsed; {len(errors)} errors; {len(warnings)} readability warnings.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
