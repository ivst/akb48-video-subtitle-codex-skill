#!/usr/bin/env python3
"""Render synthetic single, paired and long/sign previews with the real renderer."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from presentation import render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--font', help='Explicit installed font override, e.g. Arial')
    args = parser.parse_args()
    assets = Path(__file__).resolve().parents[1] / 'assets'
    data = json.loads((assets / 'presentation.example.json').read_text(encoding='utf-8'))
    episode = json.loads((assets / 'presentation.settings.json').read_text(encoding='utf-8'))
    if args.font:
        data['font'] = args.font
    names = {'compact-single-preview.jpg': 1, 'compact-preview.jpg': 4.5,
             'compact-long-preview.jpg': 6.5}
    output = args.output_dir.resolve()
    if any((output / name).exists() for name in [*names, 'compact.ass']):
        parser.error('preview files already exist; use a new output folder')
    if not shutil.which('ffmpeg'):
        parser.error('FFmpeg with libass is required')
    try:
        ass, _, _ = render(data, episode)
        with tempfile.TemporaryDirectory(prefix='akb48-preview-') as tmp:
            temp = Path(tmp)
            (temp / 'preview.ass').write_text(ass, encoding='utf-8-sig')
            for name, seconds in names.items():
                # Relative ASCII filter path avoids shell/filter quoting on Windows.
                result = subprocess.run([
                    'ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'info',
                    '-f', 'lavfi', '-i', 'color=c=0x536571:s=1280x720:d=10:r=24',
                    '-vf', 'ass=preview.ass', '-ss', str(seconds),
                    '-frames:v', '1', '-q:v', '2', '-update', '1', str(temp / name)
                ], cwd=temp, capture_output=True, text=True, encoding='utf-8',
                    errors='replace', timeout=60)
                (temp / (name + '.log')).write_text(result.stderr, encoding='utf-8')
                if result.returncode:
                    raise ValueError('FFmpeg preview failed: ' + result.stderr[-2000:])
            output.mkdir(parents=True, exist_ok=True)
            (output / 'compact.ass').write_text(ass, encoding='utf-8-sig')
            for name in names:
                shutil.copy2(temp / name, output / name)
                shutil.copy2(temp / (name + '.log'), output / (name + '.log'))
        print('Rendered three style previews and compact.ass; inspect fontselect logs.')
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
