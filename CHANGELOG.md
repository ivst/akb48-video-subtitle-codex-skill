# Changelog

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
