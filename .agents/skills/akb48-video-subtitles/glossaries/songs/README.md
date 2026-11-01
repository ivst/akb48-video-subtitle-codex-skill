# AKB48 song title glossary

Song titles are **proper names**, not ordinary dialogue or lyrics. For the *original Japanese AKB48 song* keep the established **Latin release title or commonly accepted romaji spelling** across all eight output languages, rather than translating its meaning. This includes mixed-language titles such as `Koi Suru Fortune Cookie` and originally English titles such as `Heavy Rotation`—do **not** invent phonetic romaji for English words.

## Source priority and exceptions

1. **Episode-specific user-approved song title** takes precedence. Record its source and exact spelling in `episode.json` under `songs`.
2. Otherwise, prefer the **official release/discography or artist/label** title when a Latin form is published.
3. Then use **AKB48 Wiki** (https://akb48.fandom.com/wiki/Category:Songs) or another dedicated 48 Group wiki. Keep the original wiki spelling; do not use its separate `English translation` field.
4. If reliable sources disagree, flag the title for review and record both links. Do not generate a new transliteration.
5. For an **officially localized recording/cover** by JKT48, BNK48, MNL48, AKB48 Team SH/TP and so on, the official title of that specific version may differ. Verify the group and release first; do not automatically substitute a cover title for an original AKB48 song.
6. If unknown, keep the Japanese original provisionally, mark `pending_source_verification`, and request a source or review. **Never invent romaji or translate meaning as a substitute.**

Apply these rules when song names appear in **spoken dialogue, on-screen labels, captions, setlists and annotations**. **Translate the lyrics** themselves if requested; keeping the song title does not mean leaving the lyrics untranslated. Do not confuse a song title with a similar ordinary phrase inside lyrics. Where feasible annotate each title-bearing source chunk cue with `"song_ids": ["akb48-..."]` so the deterministic checker can verify it.

## CSV schema

Bundled `songs.csv` contains a small **five-song seed catalog**, not the complete AKB48 discography.

- `song_id`: stable ID; never recycle.
- `artist`: artist for the referenced original recording.
- `source_ja`: Japanese source title used for matching, not automatically translatable.
- `preferred_latin`: spelling to copy verbatim into localized subtitle tracks for this AKB48 original.
- `source_kind`: `akb48_original` here; official localized versions need separate entries.
- `source_url`: record-specific source for the adopted Latin spelling.
- `official_source_url`: optional additional primary reference confirming release/title; a source for the Japanese release **does not by itself validate** the Latin spelling.
- `review_status`: `community_reference` for these curated wiki-derived candidates, **not official or independently fluent-reviewed**.
- `notes`: ambiguity, translation pitfalls, or version specifics.

A community wiki is evidence of conventional fan usage, not proof that spelling was endorsed by the label. Do not label a row `official` without a direct official Latin-title source.

## Commands

```sh
python .agents/skills/akb48-video-subtitles/scripts/lookup_song.py "愛の意味を考えてみた"
python .agents/skills/akb48-video-subtitles/scripts/lookup_song.py --episode examples/quality/episode.json "akb48-heavy-rotation"
python .agents/skills/akb48-video-subtitles/scripts/check_song_titles.py --input examples/quality/source.json --translated examples/quality/translated.json --json
```

To make the checker enforce the spelling of a **confirmed** song reference, mark its source JSON cue with `"song_ids": ["akb48-ai-no-imi"]`. Unannotated exact Japanese-title matches are only warnings because a line of ordinary speech or lyrics may contain the same words. Pass `--strict` to make confirmed/annotated mismatches hard errors. `run_checks.py` runs this checker for existing translation chunks with `--strict`, while the broader goal of **semantic** translation quality remains a manual review task.

Episode override example:

```json
{"songs": {"akb48-ai-no-imi": {"preferred_latin": "Ai no Imi wo Kangaete Mita", "source_url": "https://akb48.fandom.com/wiki/Ai_no_Imi_wo_Kangaete_Mita", "review_status": "user_approved"}}}
```

Do not use this seed catalog as an excuse to skip looking up other AKB48 song titles as they appear. Add new sourced rows and tests when real episodes introduce them.
