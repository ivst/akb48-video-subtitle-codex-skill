# Workflow and review boundaries

## Inputs

Prefer a local source video supplied by the user. Record its source URL/title, duration, frame size/rate, audio language, and available captions. A YouTube URL alone does not guarantee that downloading or redistributing a copy is permitted. Do not store cookies, account tokens, or API keys in the project.

Collect the target language, desired deliverables (SRT, ASS, rendered video), cast list, approved name spellings, and any style reference. If the user already gave these, proceed without asking again.

## Evidence and translation

Keep the Japanese source text and its time range alongside each translated event. Record a short source/evidence note for disputed names, punchlines, song lines, and visible text. ASR, auto-captions, OCR, face presence, and previous episodes are clues; none alone proves the words or speaker.

Translate speech, lyrics, and inscriptions as separate classes. Do not omit signs merely because dialogue subtitles exist. Preserve jokes and incomplete turns when the source supports them; do not add an explanation to dialogue unless the user wants translator notes.

Use stable entity IDs in glossaries and keep Japanese, romanized, and target-language spellings as separate fields. Do not infer a member identity from a close-up alone. If attribution remains uncertain, use a neutral role label or omit a name.

## Timing and presentation

Use source timing as the anchor. Split on a confirmed change of speaker or turn, not every dash or clause. A split inferred from approximate ASR alignment must remain reviewable and should be disclosed when material.

SRT is for portability. ASS can preserve positioning, color, and layout. A burned-in video is a separate rendered artifact; keep source audio untouched where requested. Short translations should not cover faces, permanent name tags, or essential graphics. Keep speaker names distinct from the dialogue and use colors as redundant cues, not the only identity signal.

## Review and delivery

Review a spread of frames, plus each key title card, sign, result, and scene with overlapping voices. Inspect the final rendered file, not only a subtitle preview. Report what was checked and what remains uncertain. Do not claim full human verification if only sampled frames or automated checks were used.

Minimum final checks, when the requested output includes a render:

- Subtitle timestamps fall within the source duration; cues do not overlap unintentionally. Supply source duration in seconds via `check_srt.py --duration` when validating an SRT track.
- Main text and speaker labels fit at the actual video resolution and remain readable over busy scenes.
- Final video decodes to completion; frame rate and duration match the source within expected encoder tolerance.
- Audio stream is present and its packet hash matches the source if audio was meant to remain unchanged.
- ZIP or other package opens and contains the current subtitle files, not an earlier revision.

An output report should distinguish language review, speaker/visual review, and technical media checks.

Name validation: consult `glossaries/members/{locale}.csv` and `glossaries/aliases.csv` in the installed skill folder. Preserve row-level `review_status` and never call an unverified spelling approved. Episode-specific contributor glossaries take precedence. If the localized field is blank, request verification or explicitly disclose a fallback instead of inventing a spelling.

## Subtitle terminology

Consult `glossaries/terms/{locale}.csv` for member-facing event terms, fan terminology, and theater stages; use `scripts/lookup_term.py` for a JSON lookup with semantic cautions. The locale forms are marked `editorial_draft` except blank Thai entries, which remain pending. Prefer an episode-specific user-approved lexicon over this starter dataset. Do not treat the Russian name glossary as approval of newly introduced Russian term translations. Historical formats (such as elections and former team arrangements) must be interpreted in the period described by the program.

## Durable translation state and report

Long episodes must use the chunk contract in [translation-protocol.md](translation-protocol.md), with stable IDs in source and translated JSON. A new episode workspace is created using `scripts/init_project.py`, never overwriting a previous run. Write a real file at each stage rather than relying on conversational memory.

`scripts/run_checks.py --project PROJECT --require-translation` executes installed validators and generates `report.json` from actual commands, exit codes, hashes and missing checks. A report is **incomplete** if a required artifact is absent. Manual frame/audio review and speaker/translation correctness are separate evidence and must never be asserted as automated validation.

## Definition of done and model setting

Use [deliverables.md](deliverables.md) for concrete validation commands and for interpreting `report.json`. Static ASS validation permits intentional overlays and drawing events. Media metadata and audio checks require actual source/output files; do not claim results from tools that were not run. If audio must be unchanged, set `"audio_preservation": "unchanged"` in the episode manifest; set `"not_required"` only for intended modifications or silent sources, then report audio as unverified. Decoded PCM hashes are not proof of identical compressed audio packets.

For difficult Japanese speech, GPT-6.1 Sol at Medium reasoning effort or higher is the recommended starting model when available. It does not remove the obligation to check Japanese audio, glossary forms, translated IDs and final rendered frames.
