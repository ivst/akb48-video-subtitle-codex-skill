# AKB48 Video Subtitle Skill for Codex

[English](README.md) · [Русский](README.ru.md) · [한국어](README.ko.md) · [Español (LatAm)](README.es-419.md) · [Bahasa Indonesia](README.id.md) · [ไทย](README.th.md) · [简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md)

Localized README files are community-ready drafts and should be reviewed by fluent speakers before being treated as authoritative.


A reusable workflow for translating and subtitling AKB48 and 48 Group videos. It helps Codex keep dialogue, speaker attribution, songs, and on-screen text organized; use verified name spellings; and check subtitle and rendered-video deliverables.

The repository contains a Codex skill, language-profile starters, a basic SRT checker, setup notes, and two visual examples from recent Russian-localized episodes. Russian reflects a workflow used on full episodes. Korean is a draft pending fluent-speaker review; the other language profiles are starter guidance for contributors.

## Quick install

Prerequisites: Git, Python 3.11+, FFmpeg/FFprobe with libass, and access to Codex. These commands clone the repository and check the tools; they do not install prerequisites. Open the cloned folder in Codex and start a new chat.

```sh
git clone https://github.com/ivst/akb48-video-subtitle-codex-skill.git
cd akb48-video-subtitle-codex-skill
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py --require-ass
```

## Example prompt

```text
Use $akb48-video-subtitles to translate [local video path or authorized URL] into English, including on-screen text.
Deliver separate SRT and ASS, a video with burned-in subtitles, and the checks report. Use the current compact layout near the bottom edge. Separate speakers with verified names or neutral roles; do not merge unknown voices.
Omit background music and song lyrics. Review names, dialogue meaning, signs and final video frames; record uncertainties. Do not publish anything.
```

## Preview

**Episode 12 — speaker label and compact subtitle panel** ([source video](https://www.youtube.com/watch?v=aPznmLtjedw))

![Episode 12 subtitle example](examples/preview-episode-12.jpg)

*Source excerpt: AKB48, **AKB48の全力エンタメ学園**, episode 12 (18 April 2026), [original YouTube video](https://www.youtube.com/watch?v=aPznmLtjedw).* The still is included to examine the localized speaker-name label and its relationship to the compact dialogue panel. The example lets readers assess how the two elements distinguish the speaker from spoken text without relying on color alone.

**Episode 13 — compact panel during the final handshake segment** ([source video](https://www.youtube.com/watch?v=mHF3TEk6lwQ))

![Episode 13 subtitle example](examples/preview-episode-13.jpg)

*Source excerpt: AKB48, **AKB48の全力エンタメ学園**, episode 13 (25 April 2026), [original YouTube video](https://www.youtube.com/watch?v=mHF3TEk6lwQ).* This still illustrates how the translated subtitle panel is positioned during a handshake segment. It is used to discuss readable placement alongside the original scene and on-screen graphics, rather than to reproduce the episode for entertainment.

The two images above are **separately attributed excerpts for technical commentary on subtitle design**, not freely reusable examples or a replacement for the source episodes. The original program footage, performer images, branding, and other third-party elements remain subject to their respective rights; the MIT license does **not** cover the screenshots. Source links and attribution do not themselves grant permission to republish them. See [NOTICE](NOTICE) for the sources, limitations, and relevant Japanese quotation-law context. No source video or full-episode subtitles are distributed.

## Install for other projects

For other projects, copy `.agents/skills/akb48-video-subtitles/` into your Codex skills directory (usually `%USERPROFILE%\.codex\skills\akb48-video-subtitles` on Windows or `$CODEX_HOME/skills/akb48-video-subtitles` when configured). Start a new Codex session after installing.

## Additional checks

Check an existing SRT below, replacing the example path.

```powershell
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py path\to\dialogue.srt
```

For a rendered ASS deliverable, require a working libass-enabled FFmpeg build with `python .agents/skills/akb48-video-subtitles/scripts/check_environment.py --require-ass`. You can pass the video length to the SRT checker using `--duration 120` (seconds). SRT errors cause exit code 1; readability warnings are informational and exit 0.

The included scripts use the Python standard library; no `pip install` step is needed. See the skill's [resource requirements](.agents/skills/akb48-video-subtitles/references/resources.md) for machine sizing and optional ASR/download tools.

## Reproduce a synthetic ASS subtitle panel

The repository includes [`examples/demo.ass`](examples/demo.ass): a **synthetic** layout with a speaker rail, background panel, and captions at 1920×1080. It contains no frames or translations from an AKB48 episode. After checking `--require-ass`, run the following from the repository root (requires FFmpeg's standard MPEG-4 encoder):

```sh
ffmpeg -f lavfi -i "color=c=0x263443:s=1920x1080:d=6:r=24" -vf "ass=examples/demo.ass" -c:v mpeg4 -q:v 5 -y demo-preview.mp4
```

The generated six-second MP4 is silent and intentionally synthetic. The demo gives a reproducible *style reference*, not a one-command speech recognition, translation, or finished-episode pipeline. Font substitution can change line metrics across systems; inspect the final frames when using real video. The original screenshots above are visual references, not part of the MIT-licensed assets.

## Regression tests

```sh
python -m unittest discover -s tests -v
```

Tests run in GitHub Actions on Ubuntu and Windows with Python 3.11 and 3.13. The checker does not evaluate translation accuracy or correct speaker identity. Its characters-per-second count includes visible spaces, strips simple formatting tags, decodes HTML entities, and excludes line breaks; adapt the threshold to the target language.

## Workflow

1. Verify the Japanese source transcript and capture signs, titles, rules, and results separately.
2. Translate into the requested language using its profile and a reviewed episode glossary.
3. Attribute speakers only when evidence supports it; leave ambiguous reactions neutral.
4. Create portable SRT, styled ASS, and/or rendered MP4 as requested.
5. Review frames throughout the episode and inspect the final render. Check decode, timing, packaging, and audio preservation when applicable.

Read the skill's [workflow reference](.agents/skills/akb48-video-subtitles/references/workflow.md) and choose a profile from [language profiles](.agents/skills/akb48-video-subtitles/references/languages/README.md).

## Multilingual member name glossaries

The installed Codex skill bundles member-name CSV files for **all eight supported target languages** inside `.agents/skills/akb48-video-subtitles/glossaries/members/`. This keeps the names available when only the skill folder is installed.

The 83 Japanese name keys cover selected current and historical AKB48 / 48 Group members, **not the entire 48 Group or a live roster**. Some historical entries belong to sister groups (for example former NGT48 member 荻野由佳), not AKB48 itself. Russian forms preserve the contributor's original `member_names.ja-ru.json`. Official AKB48 romanizations cover 45 names in English; historical Latin names need additional checking. Korean and Traditional Chinese now have 83 community-reference forms each, Simplified Chinese has 83 unreviewed derived forms, Spanish and Indonesian use explicit Latin-name fallbacks, and Thai spelling is pending.

Each CSV row records its source, confidence, and review status. Read the [glossary guide](.agents/skills/akb48-video-subtitles/glossaries/README.md) before treating any name as approved. The lookup tool produces machine-readable results:

```sh
python .agents/skills/akb48-video-subtitles/scripts/lookup_member.py --locale ru "武藤小麟"
```

The lookup also supports `--strict` (trusted only) and `--allow-fallback` (explicitly labeled Latin fallback). Episode-specific contributor glossaries take precedence.

## AKB48 terms for subtitles

The skill also bundles **35 recurring terms** in eight locale files (`glossaries/terms/{locale}.csv`), covering oshimen, senbatsu, graduation, theater stages, handshakes, online talks, and other AKB48 conventions. Russian and six other target languages contain *editorial drafts*, not user-approved or fluent-reviewed translations; Thai entries remain explicitly pending. The member-name JSON is **not** used as a source for terminology. See the [terminology guide](.agents/skills/akb48-video-subtitles/glossaries/terms/README.md).

```sh
python .agents/skills/akb48-video-subtitles/scripts/lookup_term.py --locale ru "選抜"
```

The CLI reports each term's review status and semantic caveat to prevent confusing, for example, `卒業公演` with `卒業コンサート`.

## Resource requirements

For a typical 1080p, 20–40 minute episode, 8 GB RAM and a recent 4-core CPU are a workable baseline; 16 GB RAM and 6–8 cores are more comfortable for local ASR. Keep roughly 10 GB free for source, intermediates, output, and backup. GPU acceleration is optional. 4K or high-bitrate media may need substantially more disk and memory. These are planning estimates; actual use depends on codec, ASR model, and encoder.

## Rights and privacy

Only process and publish material you are authorized to use. Keep local episode transcripts, full subtitle files, credentials, cookies, and private glossaries out of public pull requests unless they are licensed for redistribution. The demonstration frames show subtitle layout; rights in the underlying program material remain with its owners.

## License

See the [Codex skills guide](https://developers.openai.com/plugins/build/skills) for the skill format. Original documentation, scripts, and the synthetic ASS demo are MIT-licensed. The third-party program screenshots and depicted material are **not** covered by MIT; see [NOTICE](NOTICE) and [LICENSE](LICENSE). GitHub's license detection does not establish permissions for third-party images.

## Quality checks for translated SRT

Translation accuracy still requires an editor, but the bundled scripts flag suspicious Japanese text and check name consistency. The `--profile ru` reading profile has a **700 ms minimum** review threshold and a **900 ms preferred** target; neither is a hard linguistic rule. CPS includes visible spaces.

```sh
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py examples/quality/ru.srt --profile ru --duration 14 --json
python .agents/skills/akb48-video-subtitles/scripts/check_names.py --source examples/quality/ja.srt --target examples/quality/ru.srt --members .agents/skills/akb48-video-subtitles/glossaries/members/ru.csv --episode examples/quality/episode.json --json
```

For suspected untranslated Japanese, set `--target-lang ru` (enabled by `--profile ru`), and optionally `--strict-japanese`. Kanji are also used in Chinese and may appear as titles, so detection is deliberately **heuristic**, with `--allow-japanese` for approved expressions. For intentionally simultaneous SRT cues, `--allow-overlap` downgrades overlap to warnings. `check_names.py` flags unconfirmed translated names as warnings unless `--strict` is set, to avoid penalizing natural pronouns and nicknames. Explicit forbidden name variants are errors. Neither tool establishes semantic translation completeness.

## Translation chunks and execution report

The [ID-stable translation protocol](.agents/skills/akb48-video-subtitles/references/translation-protocol.md) uses source/translated JSON chunks of 40–60 cues, requires matching IDs and nonempty translations, and separates these working units from eventual SRT/ASS display segmentation.

```sh
python .agents/skills/akb48-video-subtitles/scripts/check_translation.py --input examples/quality/source.json --translated examples/quality/translated.json --target-lang ru --json
python .agents/skills/akb48-video-subtitles/scripts/init_project.py --project my-episode --episode-id episode-001 --locale ru
python .agents/skills/akb48-video-subtitles/scripts/run_checks.py --project my-episode --require-translation
```

The project initializer rejects overwriting an existing workspace. `report.json` is generated from **executed** validators with command arguments, exit codes, file SHA256 and explicit `not_run` entries; the report does not substitute for manual translation or visual review.

## Preferred model and final media checks

For complex Japanese-to-target-language translation, **GPT-6.1 Sol at Medium reasoning effort or higher is recommended when available** (a preference, not a requirement or guaranteed quality improvement). For difficult jokes, voices or cultural context, use a higher setting or a stronger available model, and always verify against Japanese audio.

The skill adds `check_ass.py`, `probe_media.py`, `compare_media.py`, and `compare_audio.py`. The last tool hashes **decoded PCM**, not compressed audio packets, so distinguish audio preservation checks from exact compressed-stream identity. Media tools require FFmpeg/FFprobe in PATH. See [Definition of done](.agents/skills/akb48-video-subtitles/references/deliverables.md) and [CHANGELOG](CHANGELOG.md). Current repository version is in [VERSION](VERSION).

## Song title spelling (romaji rather than semantic translation)

A **song title is a proper name**, not a lyric line to translate. For original AKB48 songs, keep the established Latin release title or **romaji** in all target languages: `愛の意味を考えてみた` → **Ai no Imi wo Kangaete Mita**, not *Thinking About the Meaning of Love*; `恋するフォーチュンクッキー` → **Koi Suru Fortune Cookie**; `ヘビーローテーション` → **Heavy Rotation**. For an officially localized sister-group cover, check the actual version and use its published title only when that recording is being discussed. Translate the lyrics themselves when requested.

Prefer an officially published Latin title; otherwise consult AKB48 Wiki or a dedicated 48 Group wiki. The bundled 78-title glossary retains per-song sources and review statuses; do not invent romaji for titles not yet catalogued. See [song title policy](.agents/skills/akb48-video-subtitles/glossaries/songs/README.md).

```sh
python .agents/skills/akb48-video-subtitles/scripts/lookup_song.py "愛の意味を考えてみた"
python .agents/skills/akb48-video-subtitles/scripts/check_song_titles.py --input examples/quality/song_source.json --translated examples/quality/song_translated.json --strict --json
```

For reliable validation, annotate confirmed mentions with `song_ids` in source translation chunks. Unmarked phrases matching song titles are only warnings, since lyrics or natural speech can contain the same phrase. `run_checks.py` includes this title check whenever translation chunks exist.

## Full video checks

Rendered-video reports now include full software decoding of source and output, decoder errors, and actual decoded frame-count equality (`check_decode.py`). Audio hashing has a timeout covering the entire decode and avoids pipe deadlocks. Use `run_checks.py --media-timeout 1800` to set the maximum seconds per file. Frame-count equality assumes no intentional frame-rate conversion.

## Optional Japanese transcription and detailed workflow

Use **faster-whisper** to draft Japanese speech recognition or cross-check existing captions; translation and speaker attribution remain separate steps. It is an optional dependency installed in its own environment; CPU mode requires neither WSL nor a GPU. See the [installation and transcription example](.agents/skills/akb48-video-subtitles/references/transcription.md). The [detailed English workflow](docs/workflow.en.md) covers signs, speaker turns, styling, rendering and delivery, with portable paths and explicit limits of the bundled tools.

## Speaker-aware compact output (0.5.0)

Styled output now requires reviewed `work/presentation.json`. Use the bundled `build_presentation.py` and `check_presentation.py`: visible names/roles, no automatic merging of unknown voices, separate sign panels, and a default lower margin of 30 logical pixels (20px at 720p). Background/performance lyrics are omitted unless explicitly requested in the manifest. Older ASS/video projects without this work file report incomplete. See the [schema, commands and limits](.agents/skills/akb48-video-subtitles/references/presentation.md). The [synthetic preview](examples/compact-preview.jpg) shows the current default; existing program screenshots illustrate earlier local work.
