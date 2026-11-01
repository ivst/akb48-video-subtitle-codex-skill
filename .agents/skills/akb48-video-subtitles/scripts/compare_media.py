#!/usr/bin/env python3
"""Compare source/rendered dimensions, framerate, duration and audio presence."""
from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path
from probe_media import inspect
from subtitle_utils import emit, report


def compare(source: dict, rendered: dict, tolerance: float, strict_size: bool = False):
    errors: list[str] = []
    warnings: list[str] = []
    if not source["video"] or not rendered["video"]:
        errors.append("source or rendered video stream is missing")
        return errors, warnings
    if source["audio"] and not rendered["audio"]:
        errors.append("source audio stream missing in rendered output")
    a, b = source.get("duration_seconds"), rendered.get("duration_seconds")
    if a is None or b is None:
        warnings.append("duration missing from source or rendered metadata")
    elif abs(a - b) > tolerance:
        errors.append(f"duration mismatch: source={a:g}s rendered={b:g}s exceeds {tolerance:g}s")
    v1, v2 = source["video"][0], rendered["video"][0]
    size1 = (v1.get("width"), v1.get("height"))
    size2 = (v2.get("width"), v2.get("height"))
    if size1 != size2:
        (errors if strict_size else warnings).append(f"video size differs: {size1} vs {size2}")
    fps1, fps2 = source.get("fps"), rendered.get("fps")
    if fps1 and fps2 and abs(fps1["decimal"] - fps2["decimal"]) > 0.01:
        warnings.append(f"frame rate differs: {fps1['decimal']} vs {fps2['decimal']}")
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--rendered", type=Path, required=True)
    parser.add_argument("--duration-tolerance", type=float, default=.5)
    parser.add_argument("--strict-size", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not math.isfinite(args.duration_tolerance) or args.duration_tolerance < 0:
        parser.error("--duration-tolerance must be finite and non-negative")
    errors: list[str] = []
    warnings: list[str] = []
    left, right = {}, {}
    try:
        left, right = inspect(args.source), inspect(args.rendered)
        errors, warnings = compare(left, right, args.duration_tolerance, args.strict_size)
    except (OSError, RuntimeError, ValueError, ZeroDivisionError, subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))
    result = report("compare_media", args.rendered if args.rendered.is_file() else None,
                    errors, warnings, source_file=str(args.source), source_metadata=left,
                    rendered_metadata=right)
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
