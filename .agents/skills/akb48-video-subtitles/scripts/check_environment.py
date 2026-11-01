#!/usr/bin/env python3
"""Check Python, FFmpeg/FFprobe, and optional ASS/libass rendering support."""
from __future__ import annotations

import argparse
import platform
import re
import shutil
import subprocess
import sys


def probe(command: str) -> tuple[bool, str, str | None]:
    path = shutil.which(command)
    if not path:
        return False, "missing from PATH", None
    try:
        result = subprocess.run([path, "-version"], capture_output=True, text=True, errors="replace", timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"version check failed ({exc})", path
    if result.returncode != 0:
        return False, f"version check exited {result.returncode}: {(result.stderr or result.stdout).strip()[:200]}", path
    info = (result.stdout or result.stderr).splitlines()
    if not info or not info[0].strip():
        return False, "version check returned no output", path
    return True, info[0].strip(), path


def has_ass_filter(ffmpeg: str) -> tuple[bool, str]:
    try:
        result = subprocess.run([ffmpeg, "-filters"], capture_output=True, text=True, errors="replace", timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"filter check failed ({exc})"
    if result.returncode != 0:
        return False, f"filter check exited {result.returncode}"
    # Both 'ass' and 'subtitles' video filters are provided by libass builds.
    # FFmpeg 8 uses two flags; older builds use three. Match the actual
    # filter name and video signature rather than a fixed flag-column width.
    supported = re.search(r"(?m)^\s*[A-Z.]+\s+(?:ass|subtitles)\s+V->V(?:\s|$)", result.stdout) is not None
    return supported, "available" if supported else "missing (FFmpeg build may lack libass)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-ass", action="store_true", help="fail unless FFmpeg can render ASS subtitles with libass")
    args = parser.parse_args(argv)
    print(f"Platform: {platform.platform()}")
    py_ok = sys.version_info >= (3, 11)
    print(f"Python: {sys.version.split()[0]} ({'OK' if py_ok else 'need 3.11+'})")
    ff_ok, ff_description, ff_path = probe("ffmpeg")
    fp_ok, fp_description, _ = probe("ffprobe")
    print(f"FFmpeg: {ff_description}")
    print(f"FFprobe: {fp_description}")
    ass_ok = False
    if ff_ok and ff_path:
        ass_ok, ass_description = has_ass_filter(ff_path)
        print(f"ASS/libass filter: {ass_description}")
    else:
        print("ASS/libass filter: not checked (FFmpeg unavailable)")
    print(f"NVIDIA GPU utility: {'available' if shutil.which('nvidia-smi') else 'not found'} (optional)")
    missing = []
    if not py_ok:
        missing.append("Python 3.11+")
    if not ff_ok:
        missing.append("working FFmpeg")
    if not fp_ok:
        missing.append("working FFprobe")
    if args.require_ass and not ass_ok:
        missing.append("FFmpeg with libass")
    if missing:
        print("Missing required components: " + ", ".join(missing))
        return 1
    print("Environment is ready" + (" for ASS rendering." if args.require_ass else " for basic subtitle work."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
