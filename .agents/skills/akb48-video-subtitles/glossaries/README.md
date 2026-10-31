# AKB48 member name glossaries

This folder is **bundled with the Codex skill**, so copying only `.agents/skills/akb48-video-subtitles/` also installs the name data.

## Coverage and trust

The canonical key is `source_ja`, and all eight language files contain the same 83 people: 45 names from the current-members portion of the contributor's list and 38 historical members. This is a curated subset of AKB48, **not a complete or timeless roster**, and it does not imply that everyone is currently active. The `entity_id` values are fixed catalog identifiers: never recycle them or renumber existing entries.

| Locale | Populated localized forms | Review status |
| --- | ---: | --- |
| ru | 83/83 | user-supplied spellings, preserved verbatim; not independently audited |
| en | 83/83 | 45 current-member romanizations on the AKB48 official site; 38 historical Latin spellings are drafts for verification |
| ko | 45/83 | Korean community reference (not an official or native-reviewed translation); 38 pending |
| zh-Hant | 45/83 | traditional Chinese community reference (not officially endorsed); 38 pending |
| zh-Hans | 45/83 | ICU-converted from the traditional Chinese reference; all 45 require native review |
| es-419 | 83/83 | official or commonly-used Latin spellings carried over as **fallback**, not reviewed Spanish localizations |
| id | 83/83 | Latin-script fallback, not reviewed Indonesian localizations |
| th | 0/83 | Thai transcription not yet verified; `source_romaji` is provided as a clearly labeled fallback |

The 83 Russian values come from the contributor-supplied `member_names.ja-ru.json` and are mirrored in `glossaries/member_names.ja-ru.json`. Do not silently modernize or re-transliterate those values. If the user supplies an episode-specific glossary, it takes precedence over this bundled dataset.

## CSV format

Files in `members/{locale}.csv` use the repository's shared glossary schema:

- `entity_id`: stable AKB48 member identifier, shared by all locale files.
- `source_ja`: exact Japanese person-name key; do not infer member identities from the video image alone.
- `source_romaji`: English/Latin reference spelling; first 45 sourced from the official AKB48 member list, remaining historical entries need an independent re-check.
- `target_locale`, `target_form`, `kind`: locale, localized form (may be empty), and entity type.
- `source_url`: where this particular localized form was sourced; intentionally blank for contributor-supplied or unverified forms.
- `reviewer`, `reviewed_on`: reserved for documented fluent reviews. Empty does **not** mean verified.
- `confidence`: high, medium, low; not a probability.
- `review_status`: machine-readable provenance listed below.
- `notes`: caveats and fallbacks.

Possible `review_status`: `user_supplied`, `official_romanization`, `secondary_romanization_draft`, `community_reference`, `derived_unreviewed`, `romanized_fallback`, `pending_native_review`.

**Do not treat every nonempty target_form as approved.** `user_supplied` is authoritative only for this contributor's Russian subtitling workflow. `community_reference`, `derived_unreviewed`, and `romanized_fallback` must remain disclosed as such. For `pending_native_review`, leave the name in Japanese or temporarily use `source_romaji` with an explicit fallback label, rather than inventing a Thai/Korean/Chinese name.

## Lookup

Use the stdlib-only script from any working directory:

    python .agents/skills/akb48-video-subtitles/scripts/lookup_member.py --locale ru "武藤小麟"

To inspect the backing provenance, the script emits a JSON object with `source_ja`, `name`, `review_status`, and `source_url`. It recognizes the few explicit, documented variants listed in `aliases.csv`, e.g. `高橋彩音` → `髙橋彩音`; it does not normalize arbitrary Japanese names by guesswork.

To restrict outputs to contributor-approved Russian or official romanization, add `--strict`. For a missing localized form, the default exits nonzero and reports an unverified Latin fallback; add `--allow-fallback` only if an explicit fallback is acceptable. An unknown name is never silently invented.

## Sources and maintenance

- Official AKB48 roster and Latin names (current members): https://www.akb48.co.jp/about/members
- Korean community-language name list: https://d.namu.moe/w/AKB48/%EB%A9%A4%EB%B2%84%20%EC%9D%BC%EB%9E%8C
- Traditional Chinese community-name list: https://zh.wikipedia.org/wiki/AKB48%E6%88%90%E5%93%A1%E5%88%97%E8%A1%A8
- Russian spellings: contributor's `member_names.ja-ru.json` supplied for this repository, not independently web-sourced.

Future contributors should add evidence and a named fluent reviewer/date **per record**, rather than changing the status of a whole language file. When adding members, append a new stable ID in every locale; leave uncertain forms empty and set `pending_native_review`. Historical membership and spellings change, and this dataset should not be used as a live roster.

Run the tests: `python -m unittest discover -s tests -v` from the repository root.
