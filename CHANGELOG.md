# Changelog

## 0.6.5 — 2026-11-01
- Rewrote all eight README prompt examples around deliverables and visual intent; explicitly preserve original audio while leaving lyrics untranslated.
- Added scoped source-to-display ID coverage checks to detect translation cues dropped during presentation assembly, including split-turn and sign mappings.
- Reject malformed name override arrays, invalid audio policies, unknown requested outputs and unsafe/unsupported locales rather than skipping checks or accepting character-by-character aliases.
- Resolve source-video paths from the initializer's working directory, handle file-valued project paths cleanly, and accept UTF-8 BOM manifests in the runner and name/translation checks.
- Reject numbered unknown-voice placeholders; added regression and end-to-end coverage tests. Corrected the stale song catalogue count.
- Restore full decode checks on FFmpeg 4.4 (Ubuntu 22.04) using compatible frame passthrough while preserving exact decoded frame counts; verified with FFmpeg 4.4 and 8.1.

## 0.6.4 — 2026-11-01
- Preserved the local unnamed-voice fix: no invented names, roles, rails or placeholder labels for unestablished voices; paired rows require two established voices.
- Added an editorial review pass and a single uncertainty ledger, with a text/layout checkpoint before full encoding. Reuse established attribution evidence within its supported context.
- Reuse unchanged setup/style checks; run targeted diagnostics while editing and full media checks on the final revision.
- Made panel geometry and dialogue/sign colors configurable through the validated presentation renderer, retaining the episode-12 defaults and output correspondence checks.

## 0.6.3 — 2026-11-01
- Added OpenCode to the compatibility matrix: native `.agents/skills` discovery plus the `.opencode/skills` and `.claude/skills` roots, and the `skill` tool as the entry point (OpenCode 1 has no `/name` command). Added the `opencode` topic.

## 0.6.2 — 2026-11-01
- Renamed the repository to `akb48-video-subtitle-skill` to match its host-neutral scope; updated clone URLs in all eight READMEs. GitHub keeps redirects from the old name, but update local remotes and external links.

## 0.6.1 — 2026-11-01
- Documented host compatibility: native `.agents/skills` discovery in Codex and DeepSeek Harness, format-compatible installation for Claude Code (`.claude/skills`), and the open Agent Skills baseline for other clients. Added per-host install and invocation paths to the English and Russian READMEs; other locales link to the compatibility section.
- Added repository topics and refreshed the repository description so the project is discoverable as a host-neutral Agent Skills workflow.

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
