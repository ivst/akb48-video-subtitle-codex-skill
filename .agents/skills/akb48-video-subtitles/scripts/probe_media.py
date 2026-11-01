#!/usr/bin/env python3
"""Report media metadata from FFprobe in JSON; preserve exact rational FPS."""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from subtitle_utils import emit, report


def inspect(path: Path) -> dict:
    executable = shutil.which("ffprobe")
    if not executable:
        raise RuntimeError("ffprobe is not available")
    proc = subprocess.run(
        [executable, "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=35
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe exit {proc.returncode}: {proc.stderr.strip()[:250]}")
    body = json.loads(proc.stdout)
    streams = body.get("streams", [])
    fmt = body.get("format", {})
    video = [s for s in streams if s.get("codec_type") == "video"]
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    subtitles = [s for s in streams if s.get("codec_type") == "subtitle"]
    def describe(stream: dict) -> dict:
        return {
            "index": stream.get("index"), "codec": stream.get("codec_name"),
            "language": stream.get("tags", {}).get("language"),
            "channels": stream.get("channels"),
            "width": stream.get("width"), "height": stream.get("height")
        }
    duration = fmt.get("duration")
    if duration is not None:
        duration = float(duration)
        if not math.isfinite(duration) or duration < 0:
            raise ValueError("invalid media duration")
    fps = None
    if video:
        value = video[0].get("avg_frame_rate") or video[0].get("r_frame_rate")
        if value and value != "0/0":
            frac = Fraction(value)
            if frac > 0:
                fps = {"numerator": frac.numerator, "denominator": frac.denominator,
                       "decimal": round(float(frac), 6)}
    return {
        "duration_seconds": duration,
        "video": [describe(s) for s in video],
        "audio": [describe(s) for s in audio],
        "subtitles": [describe(s) for s in subtitles],
        "fps": fps,
        "format": fmt.get("format_name")
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors: list[str] = []
    info: dict = {}
    try:
        info = inspect(args.media)
        if args.require_audio and not info["audio"]:
            errors.append("no audio stream")
        if not info["video"]:
            errors.append("no video stream")
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError, ZeroDivisionError, subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))
    result = report("probe_media", args.media if args.media.is_file() else None, errors, [], **info)
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
