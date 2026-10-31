# Russian profile

**Status:** working profile; adapt it to the specific cast and user style request.

- Preserve official member spellings from the supplied AKB glossary. Keep stage names/nicknames separate from legal or full names.
- Use conversational Russian. Preserve the source's politeness and relationship cues without mechanically copying every Japanese honorific.
- Do not invent gender, subject, or speaker identity from the image alone. Prefer a neutral role label when the voice is not established.
- Translate visible titles, rules, prompts, results, and notices as separate on-screen-text events. Keep persistent source logos and name badges unless the task requests replacement.
- For the established compact style: light near-white panel with thin muted border; speaker name in a narrow colored rail; dark body text; distinct, consistent colors for hosts and members. Color must not be the only indication of speaker.
- Starting readability targets for Russian are body text around 23 characters/second, at most two lines for ordinary single-speaker cues, and 700 ms minimum display except brief reactive cues. Treat these as review flags, not inflexible laws. Longer paired exchanges may need a different layout.
- Produce dialogue SRT separately from inscription SRT when both are requested; ASS may combine them with positioning/styles.

Name spellings are episode-dependent. Use a project-supplied glossary and record its revision.

**Member glossary:** `../../glossaries/members/ru.csv` preserves the contributor's 83 Russian spellings verbatim (`user_supplied`), without independent audit. Respect the supplied forms unless the episode's glossary explicitly overrides them.

## Machine-readable timing profile

Use `../../profiles/ru.json` (relative to this language-profile file): minimum 700 ms, preferred 900 ms, maximum 10 s (review warning), maximum 23 visible characters per second (spaces included), and two lines. These are **review thresholds**, not automatic reasons to rewrite a valid translation. Apply `check_srt.py --profile ru`; explicitly set `--target-lang ru` without the profile. The Japanese-script detector is a heuristic and needs exceptions for titles/names. Validate member mentions with `scripts/check_names.py` and prefer episode-specific approved names over the bundled catalog.
