# Changelog

## 0.6.0 — 2026-11-01
- Made the episode-12 reference panel an explicit renderer preset: semibold dialogue, separate colored names/rails, translucent light panels, pale borders and purple/cyan sign panels. Kept the 30px logical lower margin and speaker/lyrics checks.
- Added reproducible single, paired and long/sign previews using the actual renderer, with FFmpeg font-selection logs and explicit font portability guidance.
- Updated preview placement across all README languages; existing MP4 files require a separate rebuild.

## 0.5.1 — 2026-11-01
- Added a full English practical workflow, EN/RU navigation and English guide links in seven non-Russian READMEs; clarified that these guides are not installed runtime requirements.
- Expanded the sourced song-title catalogue from 5 to 78 entries, preserving existing IDs and documenting coverage, source status and romanization limitations.
- Song lyrics remain opt-in; the catalogue contains titles only.

## 0.5.0 — 2026-11-01
- Added speaker-aware display contract, compact ASS/SRT renderer and mandatory styled-output correspondence check.
- Reject mixed/unknown-voice merges and unsolicited lyrics; store explicit lyric requests in episode manifests.
- Lowered default dialogue baseline to 30 logical pixels (20px at 720p), with reasons required for raised placement.
- New ASS/video checks require presentation data; existing projects must migrate before receiving a pass.

## Earlier documentation updates
- Added optional CPU faster-whisper installation/transcription instructions and a portable Russian workflow adapted from the local production notes; linked both from all eight README languages.

## 0.4.1 — 2026-11-01
- Fixed libass detection for FFmpeg 8 two-flag filter listings as well as older builds.
- Added mandatory full source/output decoding and decoded frame-count comparison to rendered-video reports.
- Replaced sequential audio pipes with FFmpeg PCM hashing, file-backed stderr and whole-process timeouts.
- Added configurable per-file media timeout and regression tests for blocking/error paths.

## 0.4.0 — 2026-11-01
- Added sourced AKB48 song-title seed glossary and strict annotated title checks; keep established Latin/romaji titles across target locales rather than semantic translations (with official localized-recording exceptions).
- Added per-frame AKB48 source citations and technical commentary across eight README languages, with Japanese quotation-law limitations in NOTICE.
- Agent-friendly Russian translation quality checks, name spelling flags and source-aware Japanese-script heuristics.
- Stable per-cue translation chunk protocol, episode workspace and evidence-backed `report.json`.
- Static ASS diagnostics, media/decoded-audio comparison and definition of done.
- Recommended GPT-6.1 Sol at Medium reasoning effort or higher, when available; no model dependency.

## 0.3.0 — 2026-11-01
- Added eight-locale member name and terminology glossaries with per-entry provenance.
- Added multilingual member/term lookup, SRT and environment validators, synthetic ASS demo and cross-platform unit tests.

This changelog documents repository conventions, not a claim that Codex reads a `version` field in skill metadata.
