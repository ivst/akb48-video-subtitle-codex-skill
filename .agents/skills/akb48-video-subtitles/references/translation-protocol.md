# Chunked translation contract

The skill remains an **agent workflow**, not a one-command video production pipeline. For a long episode, translate roughly **40–60 source cues per chunk**, splitting earlier at scene, song, or speaker boundaries.

## Contract

Each input and output JSON file is an object containing `{"cues":[...]}`. Source cues look like `{"id":"001","text":"こんにちは","start_ms":1000,"end_ms":2500}`. Translation cues look like `{"id":"001","text":"Привет!"}`. The same unique `id` values **must appear in exactly the same order** in both files, with no missing, added, or empty translations. Extra fields for speakers, uncertainty and evidence are allowed. The validator checks structure, suspicious Japanese script, and optional member-name consistency; it does not determine semantic correctness.

Stable IDs are a working translation contract, *not* a restriction on final SRT/ASS presentation. After validating chunks, cues may be merged or split for readability with an explicit source-to-display mapping. Do not silently omit source content or attribute uncertain speakers.

Song names are a separate category from translated dialogue or lyrics. Preserve officially established Latin/romaji titles from `glossaries/songs.csv` (consult `glossaries/songs/README.md` for source priority). For a confirmed mention add `"song_ids": ["akb48-ai-no-imi"]` to the **source** cue JSON; do not drop it during review. `check_song_titles.py --strict` checks exact Latin spelling on the matching target ID, while unannotated apparent titles trigger only warnings. Never substitute a wiki's English *translation* of the title. Track official localized sister-group cover titles separately. See `examples/quality/song_source.json` and `song_translated.json`.

Use an episode-specific, user-approved glossary first. Keep Japanese transcripts immutable and record uncertainty rather than inventing wording. Japanese lyric and signage tracks should be checked separately.

## Working directory and resumability

Initialize once (never overwrite existing data):

```sh
python .agents/skills/akb48-video-subtitles/scripts/init_project.py --project episode-001 --episode-id episode-001 --locale ru
```

This creates:
```text
episode-001/
  episode.json
  source/dialogue.ja.srt
  work/chunks/source.json
  work/chunks/translated.json
  output/dialogue.ru.srt
  output/subtitles.ru.ass
  reports/
  report.json         # created when checks actually run
```

The manifest stores paths, media metadata (when known), requested outputs, and glossary revision; it may contain `names` and `songs` overrides, for example:
```json
{"names":{"武藤小麟":{"target":"Муто Орин","aliases":["Орин"],"forbidden":["Муто Олин"]}}}
```

When resuming, read existing chunks by ID and preserve completed text. Never blindly regenerate already approved chunks.

## Commands

```sh
python .agents/skills/akb48-video-subtitles/scripts/check_translation.py --input examples/quality/source.json --translated examples/quality/translated.json --target-lang ru --members .agents/skills/akb48-video-subtitles/glossaries/members/ru.csv --json
python .agents/skills/akb48-video-subtitles/scripts/check_song_titles.py --input examples/quality/song_source.json --translated examples/quality/song_translated.json --strict --json
python .agents/skills/akb48-video-subtitles/scripts/run_checks.py --project episode-001 --require-translation --json
```

`run_checks.py` executes available validators and writes `report.json`: actual arguments, exit statuses, warnings, input/output hashes (where exposed), and checks not run. It reports `incomplete` rather than claiming everything passed when required inputs are missing. The report is **evidence of tools invoked**, not proof of translation accuracy or visual quality. An agent must distinguish technical validation from sample-based human review and media rights.

For a synthetic six-cue exchange, see `examples/quality/ja.srt`, `ru.srt`, `source.json`, `translated.json`, and `episode.json`. No copyrighted episode media is included.

## Recommended model for difficult language work
For longer Japanese variety-show episodes, prefer **GPT-6.1 Sol, Medium reasoning effort or higher**, if available to the user/workspace. For puns, cultural context, ambiguous speakers and difficult passages, higher effort or another more capable model may be appropriate. This preference does not guarantee improvement; always verify dialogue against the original audio and keep native review for non-approved language profiles. The skill must remain usable without a specific model.
