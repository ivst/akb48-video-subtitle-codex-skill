---
name: akb48-video-subtitles
description: Translate and subtitle Japanese AKB48 and 48 Group videos, including dialogue, speaker attribution, songs, and on-screen text. Use when preparing, reviewing, or packaging a localized video from a user-provided or authorized source.
---

# AKB48 video subtitles

Use this workflow for a supplied local video or a source the user is authorized to access. Keep dialogue, lyrics, and on-screen text as separate evidence-backed tracks. Produce the formats the user requests; do not assume permission to publish the media or subtitles.

1. Identify the episode, cast, source language, available captions, requested target language, and deliverables. Read the relevant language profile in `references/languages/`, the matching bundled `glossaries/members/{locale}.csv`, `glossaries/terms/{locale}.csv` **and** `glossaries/songs.csv` for fan / stage / event terminology, plus any episode-specific glossary the user supplied (which takes precedence).
2. Build a source transcript from reliable captions or Japanese ASR, then compare uncertain names, numbers, jokes, and omissions against audio. Use frames to translate signs and graphics; do not treat OCR or ASR as ground truth.
3. Use the ID-stable contract in `references/translation-protocol.md`: translate in 40–60-cue chunks (or shorter scene boundaries), preserve exactly the source cue IDs and order, write source and target JSON files, and run `scripts/check_translation.py` before assembling display subtitles. Translate naturally for the selected audience. Preserve uncertainty. Attribute a line only when audio, timing, or clear context supports it; otherwise use a neutral role label or leave attribution off. Split a caption only at a supported speaker/turn boundary.
4. Check member names, fan terms **and song titles** against their distinct glossaries; see the rules below. Song titles are proper names, not content to translate literally.

5. Create standalone subtitles and, if requested, a rendered video. Follow the selected profile for font, line length, punctuation, honorifics, and reading speed. Keep labels compact and away from faces and important source graphics.
6. Review representative frames throughout the video and check the final render. Where media tooling is available, verify full decode, duration/frame rate, subtitle archive integrity, and that the original audio remains unchanged when intended.
7. Record `episode.json` at start (`scripts/init_project.py` for a new folder), and run `scripts/run_checks.py --project PROJECT --require-translation` to write `report.json` from actual diagnostics. Do not call skipped checks passed. Deliver direct paths to the requested files and state any unresolved translation, timing, speaker, or rights limitations.

Read [workflow.md](references/workflow.md) for stage details and review boundaries. Read [resources.md](references/resources.md) before setup or rendering. Load only the chosen target-language profile from `references/languages/`. Profiles marked draft need a fluent speaker's review before production use. Use `scripts/check_srt.py` for SRT syntax, numeric time ranges, cue ordering/indexes, overlap, and readability reports; pass `--duration` when the source length is known. Use `scripts/check_environment.py --require-ass` before ASS rendering. `examples/demo.ass` at the repository root is a synthetic layout example, not a complete translation pipeline. The checks do not assess translation quality.

For provenance, fallback rules and coverage, read `glossaries/README.md`. Bundled glossaries live inside this skill folder and cover 83 selected current and historical 48 Group personalities (including sister groups), not a current AKB48 roster. Read `glossaries/terms/README.md` for the separate 35-term subtitle lexicon and its unreviewed translation status.

Use `scripts/check_srt.py --profile ru` for Russian readability and suspected Japanese-script carryovers. For cross-track name checks run `scripts/check_names.py --source SOURCE_JA.srt --target TARGET.srt --episode episode.json --json`; source and target cues may be split or merged, so missing exact names are warnings by default. Known forbidden variants remain errors. Chinese characters alone do not indicate untranslated text in Chinese localization. See the self-contained synthetic sample in `examples/quality/` at the repository root.

## Glossary rules
- Use only documented aliases from `glossaries/aliases.csv`. Episode-approved names override bundled forms.
- `user_supplied` means contributor-approved Russian naming, not independent verification; `official_romanization` is for sourced Latin member names. Community, derived, historical drafts and fallbacks are not editor-approved.
- `pending_native_review` must not be silently invented. `scripts/lookup_member.py` and `scripts/lookup_term.py` return provenance-aware JSON; bundled terminology is `editorial_draft`.
- Distinguish `卒業公演` from `卒業コンサート`, and `選抜` from `選抜総選挙`. Keep speech, lyrics and visible signs as separate evidence and subtitle tracks.
- **Song-title policy:** For original Japanese AKB48 songs keep the established **Latin release spelling / romaji** across all target languages, not a translated English/Russian/etc. meaning. Prefer official release/label Latin spelling; otherwise verify with AKB48 Wiki or another specialized wiki. `Heavy Rotation` is already an English-form title; do not romanize English words again. Only use an official localized title for the actual localized recording/cover, or a user-approved episode override. Unknown titles require source verification, not invented romanization.
- Read [song title rules](glossaries/songs/README.md) and use `scripts/lookup_song.py`. Mark confirmed title references with `song_ids` in source chunk JSON and run `scripts/check_song_titles.py --strict`; `run_checks.py` includes this when chunk files exist. **Translate song lyrics separately** when requested; never treat a literal lyric phrase as a song name without context.

## Preferred model for Japanese-to-target translation
For complex AKB48 dialogue, **GPT-6.1 Sol with Medium reasoning effort or higher is recommended when available**. Higher settings or a more capable model can be used if accessible. This is a nonbinding starting recommendation, not a validated claim of superior results for every episode or a runtime dependency; always cross-check difficult lines against the Japanese source/audio and obtain native review where required.

## Definition of done
See [deliverables.md](references/deliverables.md) for concrete SRT, names, translation-chunk, ASS, media and optional audio-check commands. `scripts/run_checks.py` writes `report.json` based on actually executed checks; never claim missing validation was performed. Manually inspect rendered frames and ambiguous Japanese speech before delivery.
