---
name: akb48-video-subtitles
description: Translate and subtitle Japanese AKB48 and 48 Group videos, including dialogue, speaker attribution and on-screen text; song lyrics only when explicitly requested. Use when preparing, reviewing, or packaging a localized video from a user-provided or authorized source.
---

# AKB48 video subtitles

Localize an authorized source into the requested formats. Keep dialogue and visible text as separate evidence-backed tracks. Omit background/performance lyrics unless explicitly requested; record that request in `episode.json`. A request to translate signs does not include lyrics or authorize publication.

## Workflow

1. Identify source, episode, cast, captions, target language and deliverables. Reuse prior user choices. Initialize `episode.json` once with `scripts/init_project.py`; resume existing work by stable IDs. Read the selected profile in `references/languages/`, bundled member/term glossaries for that locale and episode overrides. User-approved episode spellings take precedence.
2. Assess caption coverage before transcription. Use reliable Japanese captions as the starting transcript; check disputed words, names, numbers, jokes and omissions against audio. Use local ASR for missing/poor captions or targeted cross-checks; a second full transcription is not mandatory. Read [transcription.md](references/transcription.md) only when ASR is needed. Read signs in frames; ASR/OCR are drafts, not ground truth.
3. Translate using [translation-protocol.md](references/translation-protocol.md). Keep source/target IDs and order intact; 40–60-cue chunks are a working size, with shorter scene boundaries when useful. Save progress and run `scripts/check_translation.py` on changed chunks. Preserve unsupported wording as uncertainty rather than filling gaps by guesswork.
4. Perform the [editorial review](references/editorial-review.md): check meaning and omissions, natural target-language phrasing, jokes/register, names and terms. Keep one uncertainty ledger in existing chunk notes or a working review file; do not duplicate evidence into multiple reports. Reuse a confirmed voice attribution within its supported scene/context; verify changes and ambiguous turns individually. An unestablished voice gets `speaker_id: null`, no visible name/role/placeholder, and a separate timed event. Never merge different or unknown voices by proximity.
5. Read [presentation.md](references/presentation.md) before styled delivery. Build `work/presentation.json` with source-turn mappings (retain original chunk IDs when splitting/renaming turns so final source-coverage checks can detect omissions) and use `scripts/build_presentation.py`. The `episode-12` preset is a default template; adapt its documented `style` settings and inscription boxes to the episode/user reference, preserving separate names/rails for established voices. Keep default lower margin 30 logical pixels at 1080p; justify raised scenes. Do not hand-edit generated ASS: change the generating data and rebuild.
6. **Before full encoding**, finish the editorial pass, resolve material issues or explicitly preserve/disclose uncertainty, and inspect actual-episode short/long/paired/sign frames with the selected font/settings. Confirm key card boundaries. Reuse setup and synthetic style previews when installation, renderer, fonts and style are unchanged; see [resources.md](references/resources.md). Do not launch an expensive render while known text/layout fixes remain.
7. During editing run affected lightweight validators; run `scripts/run_checks.py --project PROJECT --require-translation` on the final revision. Keep full decode, frame-count/duration/FPS comparison, intended audio preservation and archive integrity checks. Inspect the finished video and deliver direct file paths with unresolved limitations. `report.json` records actual automated diagnostics, not editorial acceptance. See [deliverables.md](references/deliverables.md).

## Glossaries and title policy

Consult `glossaries/README.md` for name provenance and coverage (83 selected current/historical 48 Group personalities, not a live roster). Use documented `glossaries/aliases.csv` aliases; `user_supplied` means contributor-approved spelling, not independent verification. Do not invent `pending_native_review` forms. `scripts/lookup_member.py` provides provenance-aware lookup.

Fan/event/stage terms are a separate dataset in `glossaries/terms/{locale}.csv`, with draft status explained in `glossaries/terms/README.md`; use `scripts/lookup_term.py`. Distinguish `卒業公演` from `卒業コンサート` and `選抜` from `選抜総選挙`.

For song-title references, read `glossaries/songs/README.md`, consult `glossaries/songs.csv` / `scripts/lookup_song.py`, and retain established Latin release spelling/romaji rather than translated meanings. Prefer official label spelling, then specialized 48 Group wikis; verify unknown titles. Original English titles such as `Heavy Rotation` stay unchanged. Official localized-cover titles apply only to that recording or a user-approved override. Annotate confirmed source references with `song_ids` and run `scripts/check_song_titles.py --strict`. Actual lyrics are a separate opt-in track.

## Checks and review scope

Use `scripts/check_srt.py --profile ru --duration SECONDS` for Russian syntax/readability/carryovers; use the selected language profile for other locales. `scripts/check_names.py --source SOURCE_JA.srt --target TARGET.srt --episode episode.json --json` checks cross-track names; missing exact names can reflect legitimate split/merge/pronoun use, while forbidden forms remain errors. Chinese script alone is not a carryover in Chinese localization.

Setup and synthetic preview checks are conditional, not a per-chunk ritual. Run `scripts/check_environment.py --require-ass` for a new/changed environment and `scripts/render_style_previews.py` for a new/changed renderer/font/style; inspect font-selection logs. Always inspect actual-episode frames. The bundled `assets/presentation.example.json` is the current self-contained renderer example; repository `examples/demo.ass` is legacy.

Final rendered-video checks fully decode source/output and compare decoded primary-video frame counts. Missing artifacts are incomplete, not passed. `--media-timeout SECONDS` bounds each media check (default 1800 per file). Changes to delivered media invalidate its previous decode/audio results; never reuse a pass for different bytes. Language, voice identity and visual fit require editorial review beyond scripts. Draft language profiles require fluent-speaker review before production use.

## Model preference

For complex Japanese dialogue, GPT-6.1 Sol with Medium reasoning effort or higher is a nonbinding starting recommendation when available, not a runtime dependency or a validated guarantee. Model selection is controlled by the host/user; skill text does not establish which model ran. Record the actual model/setting only when known, and verify difficult lines against source evidence regardless of model.
