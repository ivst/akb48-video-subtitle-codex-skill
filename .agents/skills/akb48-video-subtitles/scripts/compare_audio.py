#!/usr/bin/env python3
"""Compare decoded audio hashes of source and rendered media (FFmpeg required)."""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path
from subtitle_utils import emit, report


def audio_hash(path: Path) -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not available")
    # PCM hash avoids transport/container/header differences; this validates
    # decoded sample equivalence, not byte-identical compressed packets.
    command = [ffmpeg, "-nostdin", "-v", "error", "-i", str(path),
               "-map", "0:a:0", "-acodec", "pcm_s16le", "-f", "s16le", "-"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    digest = hashlib.sha256()
    try:
        assert proc.stdout is not None and proc.stderr is not None
        while True:
            chunk = proc.stdout.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        message = proc.stderr.read(4096)
        code = proc.wait(timeout=180)
        if code != 0:
            raise RuntimeError(f"ffmpeg audio decode exit {code}: {message.decode(errors='replace')}")
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    return digest.hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--rendered", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors: list[str] = []
    hashes = {}
    try:
        hashes["source_pcm_sha256"] = audio_hash(args.source)
        hashes["rendered_pcm_sha256"] = audio_hash(args.rendered)
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
