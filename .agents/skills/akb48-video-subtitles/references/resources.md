# Setup and resource requirements

The skill itself is plain Markdown. Its SRT checker uses only the Python standard library. The packaged validators require no OpenAI API key, paid translation API, GPU, Docker, or cloud account. Access to Codex or another agent/model is configured separately.

## Required for local subtitle and video work

- Windows 10/11, macOS, or a current Linux distribution.
- Python 3.11 or newer for the included helper scripts.
- FFmpeg and FFprobe available on `PATH`. For ASS rendering, use a build with libass support.
- A local source video that the user is authorized to process.

## Practical machine sizing

For a typical 1080p, 20–40 minute episode, 8 GB RAM and a recent 4-core CPU are a workable starting point for subtitle editing and CPU encoding. 16 GB RAM and 6–8 CPU cores make local ASR and concurrent previews more comfortable. A GPU can speed up supported ASR or encoding but is optional. Keep about 10 GB free per active episode for source, intermediate renders, output, and backups; high-bitrate or 4K footage needs more. These are planning estimates; actual use depends on codec, ASR model, and encoder.

## Optional components

- `yt-dlp` if the user explicitly wants a source downloaded and the source is accessible under applicable terms. It is not required when a local source is provided.
- A local Japanese ASR tool such as faster-whisper if usable Japanese captions are absent. Model files require an initial download; CPU mode works more slowly, while GPU support depends on drivers and the installed backend.
- Image/OCR tools for signs. Treat OCR as a draft and verify against frames.
- Subtitle Edit, Aegisub, mpv, or VLC for manual review and playback. These are optional.

## Install checks

Windows: install a recent FFmpeg build and add its `bin` directory to `PATH`. macOS: `brew install ffmpeg`. Debian/Ubuntu: `sudo apt install ffmpeg`. Then run:

```text
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py --require-ass  # when rendering ASS
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py path/to/subtitles.srt --duration 120
```

No Python packages are needed for these checks. The duration flag is in seconds and should match the source video rather than the synthetic example. Exit 1 means validation failed; exit 2 means a command-line or file-reading problem for the SRT checker. Readability warnings do not fail validation. If you installed the skill into the user skills directory instead of opening this repository, run each script by its path inside that installed skill folder. If optional ASR is installed, follow that project's current platform-specific instructions rather than assuming one CUDA setup works everywhere.

## Optional faster-whisper setup

See [Japanese transcription with faster-whisper](transcription.md) for separate-environment installation on Windows/Linux/macOS, a CPU/int8 example, raw JSON and source SRT output, model downloads, and recognition limitations. This is optional and is not installed automatically. WSL is not required.
