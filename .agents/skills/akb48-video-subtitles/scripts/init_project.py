#!/usr/bin/env python3
"""Initialize a safe per-episode workspace without overwriting files."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--locale", default="ru")
    parser.add_argument("--source-video", help="optional local path (not copied)")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", args.episode_id):
        parser.error("episode ID must be 1-96 safe characters")
    root = args.project.resolve()
    if root.exists() and any(root.iterdir()):
        parser.error("refusing to overwrite nonempty project directory")
    for name in ("source", "work/chunks", "output", "reports"):
        (root / name).mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 1, "episode_id": args.episode_id,
        "locale": args.locale, "source_locale": "ja",
        "duration_seconds": None, "video_width": None, "video_height": None,
        "glossary_revision": "unreviewed", "requested_outputs": ["srt"],
        "audio_preservation": "unchanged",
        "lyrics_policy": "omit", "lyrics_request": None,
        "source": {"srt": "source/dialogue.ja.srt", "media": args.source_video},
        "work": {"input": "work/chunks/source.json",
                 "translated": "work/chunks/translated.json",
                 "presentation": "work/presentation.json"},
        "output": {"srt": f"output/dialogue.{args.locale}.srt",
                   "ass": f"output/subtitles.{args.locale}.ass", "video": None},
        "names": {}, "songs": {}
    }
    manifest = root / "episode.json"
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
