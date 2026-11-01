"""Small stdlib-only subtitle parsing and report helpers."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SRT_TIME = re.compile(r"(?P<a>\d{2,}:\d{2}:\d{2},\d{3})\s+-->\s+(?P<b>\d{2,}:\d{2}:\d{2},\d{3})")


def timestamp_ms(value: str) -> int:
    h, m, remainder = value.split(":")
    s, ms = remainder.split(",")
    if int(m) > 59 or int(s) > 59:
        raise ValueError(f"invalid minutes/seconds in {value}")
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def read_srt(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    cues = []
    for ordinal, block in enumerate(re.split(r"\n\s*\n", raw), 1):
        if not block.strip():
            continue
        lines = block.strip().splitlines()
        offset = int(bool(lines and lines[0].strip().isdigit()))
        if len(lines) < offset + 2:
            raise ValueError(f"cue {ordinal}: missing timing or text")
        match = SRT_TIME.fullmatch(lines[offset].strip())
        if not match:
            raise ValueError(f"cue {ordinal}: malformed timing")
        start = timestamp_ms(match["a"])
        end = timestamp_ms(match["b"])
        if end <= start:
            raise ValueError(f"cue {ordinal}: non-positive duration")
        body = "\n".join(lines[offset + 1:]).strip()
        if not body:
            raise ValueError(f"cue {ordinal}: empty text")
        cues.append({"id": lines[0].strip() if offset else str(len(cues) + 1),
                     "start_ms": start, "end_ms": end, "text": body})
    if not cues:
        raise ValueError("no subtitle cues")
    return cues


def report(tool: str, source: Path | None, errors: list[str],
           warnings: list[str], **details) -> dict:
    result = {"tool": tool, "status": "fail" if errors else "pass",
              "errors": errors, "warnings": warnings, "details": details}
    if source:
        result["path"] = str(source)
        try:
            digest = hashlib.sha256()
            with source.open("rb") as file:
                for chunk in iter(lambda: file.read(1024 * 1024), b""):
                    digest.update(chunk)
            result["sha256"] = digest.hexdigest()
        except OSError:
            pass
    return result


def emit(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return
    for message in result["errors"]:
        print("ERROR:", message)
    for message in result["warnings"]:
        print("WARN:", message)
    print(f'{result["tool"]}: {len(result["errors"])} errors; {len(result["warnings"])} warnings')
