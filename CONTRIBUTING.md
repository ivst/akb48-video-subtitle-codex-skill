# Contributing

Language packs and review notes are welcome. Before adding a target-language profile:

1. Start from `.agents/skills/akb48-video-subtitles/references/languages/` and state the intended locale and review status.
2. Record name forms with a Japanese source form, approved target form, source/reference, and reviewer/date. Do not add guessed member spellings.
3. Keep examples synthetic unless the contributor has permission to publish the source material and translation.
4. Have a fluent editor review speech levels, address terms, idioms, typography, line breaks, and reading speed in actual frames.
5. Mark unresolved choices as draft; do not present machine output as native-reviewed.

For code changes, run `python .agents/skills/akb48-video-subtitles/scripts/check_environment.py` and `python .agents/skills/akb48-video-subtitles/scripts/check_srt.py examples/demo.srt`. Do not include videos, full episode subtitle files, credentials, cookies, or private fan glossaries in pull requests.

Run `python -m unittest discover -s tests -v` before submitting helper-script changes. The test suite mocks external tool calls and does not require FFmpeg. When changing `examples/demo.ass`, verify an actual synthetic FFmpeg render on a libass-enabled build; do not add unlicensed program frames to this test fixture.

For member names, edit `glossaries/members/{locale}.csv` inside the skill folder. Keep `entity_id` and `source_ja` stable and aligned across eight locales; document each form's `review_status`, `source_url`, and actual reviewer/date when applicable. Do not replace contributor-approved Russian spellings without explicit agreement. Leave unverified names blank or visibly labeled as fallbacks. Run `python -m unittest discover -s tests -v`.

Terminology lexicon: change `glossaries/terms/{locale}.csv` for the corresponding target language, preserving stable `term_id` and Japanese source keys across all eight locales. Terminology is a **separate** dataset from names; its Russian values are editorial proposals, not user-approved translations. Reviewers should document evidence and actual reviewer/date per term before marking it reviewed. The Thai columns are intentionally blank. Run `python -m unittest discover -s tests -v` and verify no missing term records in any locale.
