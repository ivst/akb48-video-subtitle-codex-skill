# AKB48 song title glossary

Song titles are **proper names**, not ordinary dialogue or lyrics. For the *original Japanese AKB48 song* keep the established **Latin release title or commonly accepted romaji spelling** across all eight output languages, rather than translating its meaning. This includes mixed-language titles such as `Koi Suru Fortune Cookie` and originally English titles such as `Heavy Rotation`—do **not** invent phonetic romaji for English words.

## Source priority and exceptions

1. **Episode-specific user-approved song title** takes precedence. Record its source and exact spelling in `episode.json` under `songs`.
2. Otherwise, prefer the **official release/discography or artist/label** title when a Latin form is published.
3. Then use **AKB48 Wiki** (https://akb48.fandom.com/wiki/Category:Songs) or another dedicated 48 Group wiki. Keep the original wiki spelling; do not use its separate `English translation` field. A sourced Wikipedia release article or discography can supply a provisional community spelling when a dedicated-wiki entry is unavailable; record that source and retain `community_reference`.
4. If reliable sources disagree, flag the title for review and record both links. Do not generate a new transliteration.
5. For an **officially localized recording/cover** by JKT48, BNK48, MNL48, AKB48 Team SH/TP and so on, the official title of that specific version may differ. Verify the group and release first; do not automatically substitute a cover title for an original AKB48 song.
6. If unknown, keep the Japanese original provisionally, mark `pending_source_verification`, and request a source or review. **Never invent romaji or translate meaning as a substitute.**

Apply these rules when song names appear in **spoken dialogue, on-screen labels, captions, setlists and annotations**. **Translate the lyrics** themselves if requested; keeping the song title does not mean leaving the lyrics untranslated. Do not confuse a song title with a similar ordinary phrase inside lyrics. Where feasible annotate each title-bearing source chunk cue with `"song_ids": ["akb48-..."]` so the deterministic checker can verify it.

## CSV schema

Bundled `songs.csv` contains **78 titles**, reviewed on **2026-11-01**:

- 71 title tracks across two indie releases and major singles 1–68, counting the two tracks of the 45th double A-side separately; the 2008 recording of Sakura no Hanabiratachi has its own entry.
- Seven selected stage, album and coupling songs, including the original seed entry Ai no Imi wo Kangaete Mita, Shonichi, Pajama Drive, Yume no Kawa, First Rabbit, 365nichi no Kamihikouki and Kimi no Koto ga Suki Dakara.

This is **not the complete song catalogue**: most B-sides, stage and album tracks, units, solo releases and sister-group localized recordings remain outside its scope. Japanese release titles were cross-checked against the [official singles discography](https://cdn.akb48.co.jp/about/discography/?category=1). Latin forms cite individual community articles where available, otherwise the [community singles table](https://en.wikipedia.org/wiki/AKB48_discography#Singles); indexed AKB48 Wiki pages are explicitly identified in row notes when direct access was unavailable. No lyrics are included.

Sources use different romanization conventions (`ō` versus `ou`/`oo`, `o` versus `wo`) and capitalization. Preserve the cited form per row rather than generating a new spelling; matching currently accepts the Japanese title, stable ID or stored Latin spelling, **not arbitrary alternate romanizations**. Use episode overrides for an editor-approved convention. `Suzukake Nanchara` is the conventional abbreviated title, not its full official Japanese title.

- `song_id`: stable ID; never recycle.
- `artist`: artist for the referenced original recording.
- `source_ja`: Japanese source title used for matching, not automatically translatable.
- `preferred_latin`: spelling to copy verbatim into localized subtitle tracks for this AKB48 original.
- `source_kind`: `akb48_original` here; official localized versions need separate entries.
- `source_url`: source for the adopted Latin spelling; prefer a record-specific page, otherwise cite the exact discography section and identify it in notes.
- `official_source_url`: optional additional primary reference confirming release/title; a source for the Japanese release **does not by itself validate** the Latin spelling.
- `review_status`: the catalogue conservatively retains `community_reference`; source checking is **not independent fluent review or a claim that every spelling is official**. Individual notes identify direct official evidence when available.
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

Do not use this catalog as an excuse to skip looking up other AKB48 song titles as they appear. Add new sourced rows and tests when real episodes introduce them.
