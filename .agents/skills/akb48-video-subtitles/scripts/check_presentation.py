#!/usr/bin/env python3
"""Check speaker turns, lyrics opt-in and correspondence to rendered ASS/SRT."""
import argparse
import json
from pathlib import Path
from presentation import render
from check_translation import cues_at
from subtitle_utils import emit,report


def check_coverage(data, source):
    """Account for scoped source cues through displayed turns/signs, not unused notes."""
    errors = []
    expected = {str(cue['id']) for cue in source}
    if not expected or len(expected) != len(source):
        return ['coverage source must contain nonempty unique cue IDs']
    used = set()
    for event in data['events']:
        if event['kind'] == 'dialogue':
            mappings = []
            for row in event['rows']:
                for turn_id in row['source_ids']:
                    turn = data['turns'][turn_id]
                    # Unsplit source turns can retain their original cue ID.
                    mappings.append((turn_id, turn.get('source_ids', [turn_id])))
        else:
            # Signs read directly from frames need not belong to a speech chunk.
            mappings = [(event['id'], event['source_ids'])] if 'source_ids' in event else []
        for label, ids in mappings:
            if not isinstance(ids, list) or not ids or any(
                    type(i) not in (str, int) or not str(i).strip() for i in ids):
                errors.append(f'{label}: source_ids must be a nonempty array of source cue IDs')
                continue
            for cue_id in map(str, ids):
                if cue_id not in expected:
                    errors.append(f'{label}: source cue {cue_id!r} not in scoped source; map split turns via turns.source_ids')
                else:
                    used.add(cue_id)
    missing = expected - used
    if missing:
        errors.append('source cues missing from presentation: ' + ', '.join(sorted(missing)))
    return errors


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--episode",required=True,type=Path)
    p.add_argument("--ass",type=Path)
    p.add_argument("--srt",type=Path)
    p.add_argument("--source",type=Path,help="scoped source chunk JSON for source-to-display coverage")
    p.add_argument("--json",action="store_true")
    a=p.parse_args(argv);errors=[];warnings=[]
    try:
        data=json.loads(a.input.read_text(encoding="utf-8-sig"))
        episode=json.loads(a.episode.read_text(encoding="utf-8-sig"))
        ass,tracks,warnings=render(data,episode)
        if a.source:
            errors.extend(check_coverage(data,cues_at(a.source)))
        for path,expected in ((a.ass,ass),(a.srt,tracks['dialogue'])):
            if path is not None and path.read_text(encoding="utf-8-sig").replace('\r\n','\n')!=expected:
                errors.append(f"{path.name}: differs from reviewed presentation; rebuild matching ASS/SRT")
        output_dir=a.ass.parent if a.ass else a.srt.parent if a.srt else None
        if output_dir is not None:
            for track in ('lyrics','inscriptions'):
                sidecar=output_dir/f"{track}.{episode.get('locale','ru')}.srt"
                expected=tracks[track]
                if not expected and sidecar.exists():
                    errors.append(f"stale {track} SRT present outside presentation scope")
                elif expected and (not sidecar.is_file() or sidecar.read_text(encoding='utf-8-sig').replace('\r\n','\n')!=expected):
                    errors.append(f"{sidecar.name}: missing or differs from reviewed presentation")
    except (OSError,ValueError,TypeError,KeyError) as e:errors.append(str(e))
    result=report('check_presentation',a.input if a.input.is_file() else None,errors,warnings,
                  source_coverage_checked=a.source is not None,
                  limitations='Structured claims and output consistency only; voice identity, hearing and visual fit still require human review.')
    emit(result,a.json)
    return 1 if errors else 0


if __name__=="__main__":raise SystemExit(main())
