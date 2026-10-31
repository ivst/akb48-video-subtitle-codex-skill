# AKB48 / 48 Group terminology glossary

This terminology catalog is **separate from member names**. It covers 35 recurring expressions across performance, membership, releases, fan culture, and event formats. Do not treat the terms as proof that a particular event is currently offered; older entries such as `選抜総選挙`, `神7`, `アンダーガールズ`, and `組閣` are marked `historical` where relevant.

## Localization status

Each `terms/{locale}.csv` has identical `term_id` and Japanese keys. Russian, English, Korean, Chinese (simplified and traditional), Latin American Spanish, and Indonesian contain **editorial drafts** for all 35 terms. These were not supplied by the contributor and have **not** been reviewed by fluent editors. The Thai file preserves all 35 Japanese keys with blank target fields marked `pending_native_review`. Do not invent unreviewed Thai renderings or use untranslated Japanese terms as if they were Thai.

The member-name JSON provided by the contributor applies to **names only**. It should not be treated as a source of approved Russian terminology. Document any later user-approved terminology choices per record with `reviewer`, `reviewed_on`, and an appropriate `review_status`.

## Data schema

- `term_id`: stable identifier shared by eight locale files.
- `source_ja`: exact reference form used for matching Japanese speech and on-screen captions.
- `source_reading`: a rough Latin phonetic reference, not a verified transliteration standard.
- `target_form`: preferred draft subtitle expression (blank for Thai).
- `category`: `fandom`, `membership`, `music`, `performance`, `event`, or `historical`.
- `source_url`: a reference about the Japanese concept, **not verification of the localized translation**.
- `target_reference_url`: optional community evidence for the translation; still does not mean native reviewed.
- `review_status`: `editorial_draft` or `pending_native_review` until a documented review.
- `notes`: English semantic guidance, including distinctions that affect the translation.

The Japanese concept references include:
- [AKB48 official beginner's guide](https://www.akb48.co.jp/modal/tutorial.php?h=92) (theater performances and handshakes)
- [Official AKB48 release/event notices](https://www.akb48.co.jp/news/detailpage/450512005/) (individual and online events)
- [Universal Music AKB48 biography](https://www.universal-music.co.jp/akb48/biography/) (group structure and historical election)
- [Korean-language fan terminology reference](https://seore.org/w/AKB48/%EC%9A%A9%EC%96%B4) (community context for some terms)

## Lookup

Run from the repository root or adjust the path to your installed skill:

```sh
python .agents/skills/akb48-video-subtitles/scripts/lookup_term.py --locale ru "選抜"
python .agents/skills/akb48-video-subtitles/scripts/lookup_term.py --locale ru "graduation-stage"
python .agents/skills/akb48-video-subtitles/scripts/lookup_term.py --locale th --allow-fallback "選抜"
```

The lookup returns JSON, including provenance and a semantic note. It refuses missing translations unless `--allow-fallback` is explicitly supplied; fallback output uses the *original Japanese* with `source_fallback`. A small set of exact Japanese aliases is in `terms/aliases.csv`.

## Translation pitfalls

- `卒業` describes a member leaving the group, **not automatically retirement** from entertainment.
- `選抜` (selected lineup) is **not interchangeable** with `選抜総選挙` (the historical election).
- `卒業公演` (theater stage) and `卒業コンサート` (larger concert) are different event types.
- `千秋楽` (last performance of a stage production) does not necessarily mean a member graduates.
- `研究生` is a trainee category; translating it as a university student is wrong.
- `握手会` and `オンラインお話し会` are different participation formats.
- `アンダーガールズ` is a historical named unit, not literally “underground girls.”

Avoid translating terms mechanically in song lyrics; preserve context, tone, timing, and user-approved episode terminology. Keep these CSVs with the skill folder so the same choices can be reused across sessions.
