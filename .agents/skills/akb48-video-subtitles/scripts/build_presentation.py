#!/usr/bin/env python3
"""Generate speaker-labeled SRT and compact ASS from reviewed presentation JSON."""
import argparse
import json
from pathlib import Path
from presentation import render


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--episode",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--overwrite",action="store_true")
    a=p.parse_args(argv)
    try:
        data=json.loads(a.input.read_text(encoding="utf-8-sig"))
        episode=json.loads(a.episode.read_text(encoding="utf-8-sig"))
        ass,tracks,warnings=render(data,episode)
        locale=episode.get("locale","ru")
        if not isinstance(locale,str) or not locale or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-" for c in locale):
            raise ValueError("invalid locale")
        files={f"subtitles.{locale}.ass":ass}
        files.update({f"{k}.{locale}.srt":v for k,v in tracks.items() if v})
        # Refuse stale lyric files when lyrics are now omitted.
        lyric=a.output_dir/f"lyrics.{locale}.srt"
        if not tracks['lyrics'] and lyric.exists():
            raise ValueError("remove/archive stale lyric SRT before building an omit-lyrics package")
        if not a.overwrite and any((a.output_dir/n).exists() for n in files):
            raise ValueError("output already exists; use a new folder or --overwrite after backup")
        a.output_dir.mkdir(parents=True,exist_ok=True)
        for name,text in files.items():
            (a.output_dir/name).write_text(text,encoding="utf-8-sig")
        for warning in warnings:print("WARN:",warning)
        print("Generated:",", ".join(files))
    except (OSError,ValueError,TypeError,KeyError) as e:
        p.error(str(e))
    return 0


if __name__=="__main__":raise SystemExit(main())
