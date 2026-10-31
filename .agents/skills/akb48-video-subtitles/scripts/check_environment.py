#!/usr/bin/env python3
"""Report whether the basic local subtitle toolchain is available."""
from __future__ import annotations
import shutil, subprocess, sys, platform

def version(command: str) -> str:
    path=shutil.which(command)
    if not path: return 'missing'
    try:
        p=subprocess.run([path,'-version'],capture_output=True,text=True,timeout=10)
        return (p.stdout or p.stderr).splitlines()[0].strip()
    except Exception as e: return f'found, version check failed ({e})'

def main() -> int:
    print(f'Platform: {platform.platform()}')
    print(f'Python: {sys.version.split()[0]} ({"OK" if sys.version_info >= (3,11) else "need 3.11+"})')
    ff=version('ffmpeg'); fp=version('ffprobe')
    print(f'FFmpeg: {ff}')
    print(f'FFprobe: {fp}')
    if shutil.which('nvidia-smi'): print('NVIDIA GPU utility: available (optional)')
    else: print('NVIDIA GPU utility: not found (GPU is optional)')
    missing=[]
    if sys.version_info<(3,11): missing.append('Python 3.11+')
    if ff=='missing': missing.append('FFmpeg')
    if fp=='missing': missing.append('FFprobe')
    if missing: print('Missing required components: '+', '.join(missing)); return 1
    print('Basic environment is ready. ASS rendering needs an FFmpeg build with libass support.')
    return 0
if __name__=='__main__': raise SystemExit(main())
