#!/usr/bin/env python3
"""Fully decode primary video/all audio and compare actual decoded frame counts."""
from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from subtitle_utils import emit, report


def decode(path: Path, timeout: float = 1800) -> dict:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not available")
    # Passthrough prevents the output muxer from duplicating/dropping frames.
    # Numeric -vsync 0 is also understood by Ubuntu 22.04's FFmpeg 4.4;
    # -fps_mode passthrough requires a newer FFmpeg despite equivalent semantics.
    # Force software decoding and fail on decoder errors, including concealed ones.
    command = [ffmpeg, "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
               "-i", str(path), "-map", "0:v:0", "-map", "0:a?",
               "-vsync", "0", "-progress", "pipe:1", "-nostats",
               "-f", "null", "-"]
    with tempfile.TemporaryFile() as log:
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=log,
                              timeout=timeout, check=False)
        log.seek(0, 2)
        size = log.tell()
        log.seek(max(0, size - 4096))
        message = log.read().decode(errors="replace").strip()
    if proc.returncode != 0 or size:
        raise RuntimeError(f"full decode failed (exit {proc.returncode}): {message}")
    progress = proc.stdout.decode("ascii", errors="replace")
    frames = re.findall(r"(?m)^frame=\s*(\d+)\s*$", progress)
    if "progress=end" not in progress or not frames or int(frames[-1]) <= 0:
        raise RuntimeError("decode did not report completion with video frames")
    return {"file": str(path), "exit_code": proc.returncode,
            "decoded_video_frames": int(frames[-1]), "completed": True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--rendered", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=1800, help="maximum seconds per file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")
    errors, details = [], {}
    try:
        details["source_decode"] = decode(args.source, args.timeout)
        details["rendered_decode"] = decode(args.rendered, args.timeout)
        equal = (details["source_decode"]["decoded_video_frames"] ==
                 details["rendered_decode"]["decoded_video_frames"])
        details["frame_count_matches"] = equal
        if not equal:
            errors.append("decoded video frame count differs from source")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))
    result = report("check_decode", args.rendered if args.rendered.is_file() else None,
                    errors, [], **details)
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
