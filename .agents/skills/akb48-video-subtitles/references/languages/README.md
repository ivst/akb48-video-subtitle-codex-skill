# Language profiles

Profiles define target-language choices; they do not replace a fluent editor. Load only the selected profile. A profile marked **draft** needs review by a fluent speaker familiar with Japanese idol variety content before it is treated as production-ready.

- [Russian](ru.md) — based on the current AKB translation workflow.
- [Korean](ko.md) — draft; include Korean spacing, speech levels, name verification, and font checks.
- [English](en.md) — draft.
- [Latin American Spanish](es-419.md) — draft.
- [Indonesian](id.md) — draft.
- [Thai](th.md) — draft.
- [Simplified Chinese](zh-Hans.md) — draft.
- [Traditional Chinese](zh-Hant.md) — draft.

When contributing a profile, preserve the shared workflow and document regional variants separately when needed. Never guess an official member spelling or claim native review without a named reviewer and date.

Bundled member-name glossaries live in `../../glossaries/members/{locale}.csv`, relative to this file. Always load the selected language profile *and* matching locale CSV. A listed language profile does not imply names are fluent-reviewed. See [glossary provenance and fallback rules](../../glossaries/README.md). Episode-specific user spellings override bundled names.

Bundled term translations are in `../../glossaries/terms/{locale}.csv` alongside the member names. The 35-term translations are editorial drafts in ru/en/ko/es-419/id/zh-Hans/zh-Hant and blank pending review in th; none should be presented as native-editor-approved. See [terminology notes](../../glossaries/terms/README.md). When in doubt, prefer the episode-specific user-approved glossary.
