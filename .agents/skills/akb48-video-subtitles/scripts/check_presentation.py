#!/usr/bin/env python3
"""Check speaker turns, lyrics opt-in and correspondence to rendered ASS/SRT."""
import argparse
import json
from pathlib import Path
from presentation import render
from subtitle_utils import emit,report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--episode",required=True,type=Path)
    p.add_argument("--ass",type=Path)
    p.add_argument("--srt",type=Path)
    p.add_argument("--json",action="store_true")
    a=p.parse_args(argv);errors=[];warnings=[]
    try:
        data=json.loads(a.input.read_text(encoding="utf-8-sig"))
        episode=json.loads(a.episode.read_text(encoding="utf-8-sig"))
        ass,tracks,warnings=render(data,episode)
        for path,expected in ((a.ass,ass),(a.srt,tracks['dialogue'])):
            if path is not None and path.read_text(encoding="utf-8-sig").replace('\r\n','\n')!=expected:
                errors.append(f"{path.name}: differs from reviewed presentation; rebuild matching ASS/SRT")
        if episode.get('lyrics_policy','omit')=='omit' and a.ass:
            lyric=a.ass.parent/f"lyrics.{episode.get('locale','ru')}.srt"
            if lyric.exists():errors.append("stale lyric SRT present while lyrics policy is omit")
    except (OSError,ValueError,TypeError,KeyError) as e:errors.append(str(e))
    result=report('check_presentation',a.input if a.input.is_file() else None,errors,warnings,
                  limitations='Structured claims and output consistency only; voice identity, hearing and visual fit still require human review.')
    emit(result,a.json)
    return 1 if errors else 0


if __name__=="__main__":raise SystemExit(main())
