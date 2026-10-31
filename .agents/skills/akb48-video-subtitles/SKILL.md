---
name: akb48-video-subtitles
description: Translate and subtitle Japanese AKB48 and 48 Group videos, including dialogue, speaker attribution, songs, and on-screen text. Use when preparing, reviewing, or packaging a localized video from a user-provided or authorized source.
---

# AKB48 video subtitles

Use this workflow for a supplied local video or a source the user is authorized to access. Keep dialogue, lyrics, and on-screen text as separate evidence-backed tracks. Produce the formats the user requests; do not assume permission to publish the media or subtitles.

1. Identify the episode, cast, source language, available captions, requested target language, and deliverables. Read the relevant language profile in `references/languages/` and any episode-specific glossary the user supplied.
2. Build a source transcript from reliable captions or Japanese ASR, then compare uncertain names, numbers, jokes, and omissions against audio. Use frames to translate signs and graphics; do not treat OCR or ASR as ground truth.
3. Translate naturally for the selected audience. Preserve uncertainty. Attribute a line only when audio, timing, or clear context supports it; otherwise use a neutral role label or leave attribution off. Split a caption only at a supported speaker/turn boundary.
4. Check name spellings against supplied glossaries and primary references. Keep dialogue, songs, and inscriptions distinguishable in the working data and in separate subtitle tracks where practical.
5. Create standalone subtitles and, if requested, a rendered video. Follow the selected profile for font, line length, punctuation, honorifics, and reading speed. Keep labels compact and away from faces and important source graphics.
6. Review representative frames throughout the video and check the final render. Where media tooling is available, verify full decode, duration/frame rate, subtitle archive integrity, and that the original audio remains unchanged when intended.
7. Deliver direct paths to the requested files and state any unresolved translation, timing, speaker, or rights limitations.

Read [workflow.md](references/workflow.md) for stage details and review boundaries. Read [resources.md](references/resources.md) before setup or rendering. Load only the chosen target-language profile from `references/languages/`. Profiles marked draft need a fluent speaker's review before production use. Use `scripts/check_srt.py` for a basic SRT syntax, timing, overlap, and readability report; it does not assess translation quality.
