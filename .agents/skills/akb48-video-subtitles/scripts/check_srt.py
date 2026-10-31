#!/usr/bin/env python3
"""Basic SRT syntax, timing, overlap, and readability report (stdlib only)."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

TIME = re.compile(r"^(\d{2,}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2,}:\d{2}:\d{2},\d{3})(?:\s+.*)?$")
TAG = re.compile(r"<[^>]+>")

def ms(value: str) -> int:
    h, m, tail = value.split(":")
    s, milli = tail.split(",")
    return ((int(h)*60+int(m))*60+int(s))*1000+int(milli)

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('srt', type=Path)
    ap.add_argument('--max-cps', type=float, default=23.0, help='warn above this characters/second (default: 23)')
    ap.add_argument('--max-lines', type=int, default=2, help='warn above this many lines per cue (default: 2)')
    args=ap.parse_args()
    try: raw=args.srt.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as e: print(f'ERROR: {e}', file=sys.stderr); return 2
    blocks=[b.strip() for b in re.split(r'\n\s*\n', raw.replace('\r\n','\n').replace('\r','\n')) if b.strip()]
    errors=[]; warnings=[]; parsed=[]
    for n, block in enumerate(blocks,1):
        lines=block.splitlines()
        ti=1 if lines and lines[0].strip().isdigit() else 0
        if len(lines)<ti+2:
            errors.append(f'cue {n}: expected index (optional), timing, and text'); continue
        match=TIME.match(lines[ti].strip())
        if not match:
            errors.append(f'cue {n}: invalid timing line'); continue
        start,end=map(ms,match.groups())
        if end<=start: errors.append(f'cue {n}: end must be after start'); continue
        text='\n'.join(lines[ti+1:]).strip()
        if not text: errors.append(f'cue {n}: empty text'); continue
        parsed.append((n,start,end,text))
        plain=TAG.sub('', text)
        cps=len(re.sub(r'\s','',plain))/((end-start)/1000)
        if cps>args.max_cps: warnings.append(f'cue {n}: {cps:.1f} chars/s exceeds {args.max_cps:g}')
        if len(text.splitlines())>args.max_lines: warnings.append(f'cue {n}: {len(text.splitlines())} lines exceeds {args.max_lines}')
    for prev,cur in zip(parsed,parsed[1:]):
        if cur[1]<prev[2]: errors.append(f'cue {cur[0]} overlaps cue {prev[0]}')
    for msg in errors: print('ERROR:',msg)
    for msg in warnings: print('WARN:',msg)
    print(f'{len(parsed)} cues parsed; {len(errors)} errors; {len(warnings)} readability warnings.')
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
