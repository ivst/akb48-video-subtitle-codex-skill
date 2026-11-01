#!/usr/bin/env python3
"""Compare decoded audio hashes of source and rendered media (FFmpeg required)."""
from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from subtitle_utils import emit, report


def audio_hash(path: Path, timeout: float = 1800) -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not available")
    # PCM hash avoids transport/container/header differences; this validates
    # decoded sample equivalence, not byte-identical compressed packets.
    # Hash in FFmpeg: stdout is one short digest, while stderr goes to disk.
    # subprocess.run enforces the timeout for the entire decode and reaps
    # the process on expiration. Neither pipe can block the other.
    command = [ffmpeg, "-nostdin", "-v", "error", "-xerror", "-i", str(path),
               "-map", "0:a:0", "-acodec", "pcm_s16le", "-f", "hash",
               "-hash", "sha256", "-"]
    with tempfile.TemporaryFile() as log:
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=log,
                              timeout=timeout, check=False)
        if proc.returncode != 0:
            log.seek(0, 2)
            log.seek(max(0, log.tell() - 4096))
            message = log.read().decode(errors="replace")
            raise RuntimeError(f"ffmpeg audio decode exit {proc.returncode}: {message}")
    match = re.fullmatch(rb"SHA256=([0-9a-fA-F]{64})\s*", proc.stdout)
    if not match:
        raise RuntimeError("FFmpeg did not return a valid PCM SHA256 digest")
    return match[1].decode("ascii").lower()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--rendered", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timeout", type=float, default=1800, help="maximum seconds per file")
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")
    errors: list[str] = []
    hashes = {}
    try:
        hashes["source_pcm_sha256"] = audio_hash(args.source, args.timeout)
        hashes["rendered_pcm_sha256"] = audio_hash(args.rendered, args.timeout)
        if hashes["source_pcm_sha256"] != hashes["rendered_pcm_sha256"]:
            errors.append("decoded audio PCM hash mismatch")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))
    result = report("compare_audio", args.rendered if args.rendered.is_file() else None,
                    errors, [], source_file=str(args.source),
                    method="FFmpeg decoded PCM s16le; does not prove identical compressed packets",
                    **hashes)
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
