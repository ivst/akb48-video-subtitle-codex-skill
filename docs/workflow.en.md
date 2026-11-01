# Practical AKB48 video translation workflow

[English](workflow.en.md) · [Русский](workflow.ru.md)

Adapted on 2026-11-01 from the local production notes
`VIDEO_TRANSLATION_WORKFLOW.md`. This guide retains useful episode-production
practices while using portable paths and tools from the public repository. The
full process combines software with language and visual review by an editor or
agent; there is no single command here that automatically produces a reliable
finished translation.

This is a detailed user guide. The installed skill's operating instructions live
in [SKILL.md](../.agents/skills/akb48-video-subtitles/SKILL.md) and its supporting
references; installing the skill does not require this `docs/` folder. The
commands below use a **Russian target-language example**. Change the locale,
filenames and language profile together when working in another language.

## 1. Required tools and optional processing

You need access to Codex or another suitable agent, the source video, Python,
and FFmpeg/FFprobe. The skill's validators use Python's standard library. ASS
rendering needs an FFmpeg build with libass and fonts covering the target
language. A paid translation API is not a required script dependency; access
to the agent and its model is configured separately.

Optional speech recognition can run locally with faster-whisper. It is not
installed automatically with the skill. The [installation and usage guide](../.agents/skills/akb48-video-subtitles/references/transcription.md)
covers a separate environment, CPU/int8 and Japanese word timestamps. WSL and
a GPU are optional. Recognition does not translate into the target language
in this workflow and does not establish who said a line.

For a 20–40 minute 1080p episode, 8 GB RAM and a recent four-core CPU are a
starting estimate; 16 GB and 6–8 cores are more comfortable for local ASR.
Roughly 10 GB free is an initial allowance for source, intermediate files and
output. Model size, 4K, high bitrates and backups may need more. These are
planning estimates, not repository-specific performance measurements.

## 2. Create an episode workspace

Run these commands from the cloned repository root. `episodes/demo` is a local
workspace in these examples; do not commit source videos or episode
translations to the public repository.

```sh
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py --require-ass
python .agents/skills/akb48-video-subtitles/scripts/init_project.py --project episodes/demo --episode-id demo --locale ru
```

The initializer creates `episode.json` and the `source/`, `work/chunks/`,
`output/` and `reports/` folders, refusing to overwrite a nonempty workspace.
Record source, duration, resolution, requested formats and file paths in the
manifest. Its relative paths are resolved from the episode folder. Validators
do not themselves download video, recognize speech or assemble a translation.

## 3. Choose the source and Japanese audio track

Prefer a supplied local source. Record title, URL/provenance, duration, exact
frame rate, resolution and audio-track languages:

```sh
python .agents/skills/akb48-video-subtitles/scripts/probe_media.py episodes/demo/source/original.mp4 --json
```

If an authorized download through yt-dlp is needed, install it separately and
inspect available tracks first. Format IDs and audio-track order are not
constant. Copying a format number from another episode may select an automatic
dub instead of Japanese. Do not publish cookies, temporary direct media URLs
from metadata, or credentials.

The original local process used custom range downloaders and muxing scripts.
They are not distributed in this repository and are not needed when a complete
local source video is available.

## 4. Build the Japanese transcript and episode context

Check whether authored Japanese subtitles exist. YouTube auto-captions and
Whisper are draft evidence and can fail on laughter, numbers, singing and
overlapping voices. Independent recognition can help even when captions exist:
resolve disagreements against audio rather than treating agreement between
two ASR systems as proof.

Before translating, record the cast, host roles, forms of address, game
structure and glossary. Prefer an approved episode-specific glossary; bundled
data is not a complete live roster. Name provenance and review status matter
more than the existence of a CSV row. Previous episodes can clarify context
but do not prove the current speaker's identity.

```sh
python .agents/skills/akb48-video-subtitles/scripts/lookup_member.py --locale ru "武藤小麟"
python .agents/skills/akb48-video-subtitles/scripts/lookup_term.py --locale ru "選抜"
```

Keep verified Latin/romaji song titles according to the [title policy](../.agents/skills/akb48-video-subtitles/glossaries/songs/README.md).
Translating actual lyrics is a separate, explicitly requested task.

## 5. Translate while retaining links to the source

Save Japanese cues and translations in JSON using the [stable-ID contract](../.agents/skills/akb48-video-subtitles/references/translation-protocol.md).
Working chunks usually contain 40–60 cues, but scene boundaries may call for
shorter chunks. Preserve each selected chunk's IDs, order and nonempty
translations. These are translation units, not final display boundaries.

The following command checks an already prepared chunk; it does not create
the input or translation:

```sh
python .agents/skills/akb48-video-subtitles/scripts/check_translation.py --input episodes/demo/work/chunks/source.json --translated episodes/demo/work/chunks/translated.json --target-lang ru --json
```

Check names, who performs an action, negation, numbers, jokes and forms of
address. Do not guess missing substantive content. Translate from Japanese
rather than through an incidental English machine translation. Automated
checks cannot establish semantic accuracy.

## 6. Annotate speakers separately

Establish voice changes from audio and supported context. A close-up alone
does not prove who is speaking. If identity is unknown, use a neutral role or
explicit unknown-voice label. Do not hide several speakers inside a sentence
with a chain of dashes.

Normally use sequential named display events. A very short exchange can use
two separately labeled rows. Color is an additional cue; the visible name or
role remains essential. Extra reading time must not move a line over the next
person's reply.

In earlier local episodes, some boundaries were set manually and others were
provisionally estimated by text length. This was neither automatic diarization
nor phonetic forced alignment. Such boundaries need review and accurate
disclosure of their limitations.

## 7. Read on-screen text throughout the video

Keep a separate inventory of titles, rules, cards, results, editorial captions
and notices. OCR and sampled frames help, but a short sign can appear between
samples. Full coverage requires inspecting transitions and refining the start
and end of each important insertion.

Example sampling command: create the `frames` folder first; this can generate
hundreds of files.

```sh
ffmpeg -nostdin -i episodes/demo/source/original.mp4 -vf "fps=1/4,scale=1280:-2" -q:v 3 episodes/demo/frames/frame-%05d.jpg
```

For each sign, retain timing, translation and frame region. Coordinates belong
to a particular resolution. A working annotation can contain `start_ms`,
`end_ms`, `text`, `kind`, `x`, `y`, `width` and `height`. This is a suggested
annotation format; convert it to the renderer's documented schema, including
its logical-canvas `box`, before building ASS.

Keep signs separate from dialogue even when their wording matches. Logos and
repeated name badges need not be replaced on every frame; document what remains
visible. Sparse frame sampling does not justify claiming complete localization.

## 8. Timing and layout

Review reading speed, lines, pauses and speaker changes. In the Russian profile,
700 ms is a lower review threshold and 900 ms a preferred target. Around 23
characters/second is a review flag, not a universal limit for every language.
Names and spaces also add reading load. Short reactions and paired exchanges
need individual decisions.

The following table describes a historical manual layout reference for
1920×1080, rather than mandatory settings for all videos. For current renderer
defaults and placement overrides use the [presentation guide](../.agents/skills/akb48-video-subtitles/references/presentation.md).

| Element | Reference |
|---|---|
| Lower panel | x=110, width 1700, lower baseline y=1050 (30 px margin) |
| Height | 82 px for one line, 128 px for two |
| Body | 40 px, dark text on a light panel |
| Name | 26 px, or 22 px for a long label; thin colored rail |
| Paired exchange | separately labeled rows, historically 38/32 px depending on wrapping |
| Upper title | two narrow bars without covering faces |

A character count from one font/language does not guarantee a line fits another.
Inspect libass output for short answers, long lines, long names, paired turns
and simultaneous signs. Do not bundle proprietary Segoe UI fonts from the local
workflow; choose an available font with suitable coverage and inspect fallback.
Fonts are already rasterized into the final burned video.

## 9. Build SRT/ASS and inspect previews

Typical deliverables are `dialogue.ru.srt` for speech, `inscriptions.ru.srt`
for signs and `subtitles.ru.ass` for combined styling. SRT does not retain
position or color. In ASS, panels, speaker labels and text may legitimately
overlap in time on separate layers.

The [speaker-aware display contract and renderer](../.agents/skills/akb48-video-subtitles/references/presentation.md)
provide `build_presentation.py` to generate SRT/ASS from reviewed
`work/presentation.json` and `check_presentation.py` to verify structure and
output correspondence. This assembles display events; it is not automatic
translation or diarization. Older local `proof_speech.py`, `make_signs.py`,
`build_subtitles.py` and `package.py` were episode-specific programs, not
installable dependencies of this repository.

```sh
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py episodes/demo/output/dialogue.ru.srt --profile ru --duration 120
python .agents/skills/akb48-video-subtitles/scripts/check_ass.py episodes/demo/output/subtitles.ru.ass --width 1920 --height 1080 --duration 120
```

Replace `120` and the dimensions with real values. Extract preview frames from
the burned result when convenient. If filtering ASS after an input-side `-ss`,
verify the time base: subtitle timing refers to the original video, not time
zero of the extracted clip. A wrong time base may look like missing subtitles.

## 10. Burn subtitles into video

Run this example **from `episodes/demo/output`**, where the ASS file resides.
A relative ASS path avoids extra Windows-drive escaping inside the FFmpeg
filter. Filenames containing apostrophes or colons need additional escaping.
This CPU example assumes MP4-compatible source audio and an available libx264
encoder; that encoder is not a universal requirement of the skill.

```sh
ffmpeg -nostdin -i ../source/original.mp4 -map 0:v:0 -map "0:a:0?" -vf ass=subtitles.ru.ass -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -c:a copy -movflags +faststart video.ru.tmp.mp4
```

Do not force a different frame rate unless conversion is intended. If the first
audio track is not Japanese, change `-map` after inspection. If its codec is
incompatible with MP4, choose an appropriate container or agree on re-encoding
and record that audio changed. Create the render under a temporary name first.

AMD AMF acceleration used in local production was specific to that machine,
not a portable dependency. Removing H.264 SEI was also a workaround for specific
sources: it can delete important metadata and must not be a default operation,
especially for HDR.

## 11. Technical, language and visual acceptance

Set the actual temporary video path, `requested_outputs` and
`audio_preservation` in `episode.json`. Then run from the repository root:

```sh
python .agents/skills/akb48-video-subtitles/scripts/run_checks.py --project episodes/demo --require-translation --media-timeout 1800 --json
```

`report.json` records executed checks and missing stages. Video validation
compares metadata, fully decodes both files, compares actual decoded frame
counts and checks decoded audio when required. `compare_audio.py` uses PCM
s16le; this is not proof of byte-identical compressed audio packets. A skipped
check is not a passed check.

Separately review meaning, speaker identity, sign coverage and actual frames.
Static ASS analysis does not measure every rendered line or detect faces.
Passing technical checks establishes neither translation quality nor publishing
rights. Timeout values are seconds per file and can be raised when necessary;
`progress=end` alone without a successful process exit is insufficient.

## 12. Packaging and revisions

After review, retain the finished video, ASS, separate SRT files, delivery
README, glossary used, preview and report. Add a subtitle ZIP when requested;
check archive integrity and that its contents match the current revision.
Keep source evidence and working annotations locally for corrections.

Before a correction, preserve a backup, rebuild dependent ASS/video, recheck
changed artifacts and update the archive/report. Editing ASS does not update
an already burned MP4. After renaming the temporary video, update manifest and
report paths so delivery links refer to the current result.

Historical cue counts, frame counts and reading-speed measurements from one
episode are not a contract for another. Publish only authorized material;
keep working transcripts and source footage separate from the public tools
repository.

## Changes after the independent trial

Background songs and performance lyrics are omitted from translation and
burned subtitles by default. An exception needs an explicit user request,
`lyrics_policy: "requested"` and `lyrics_request` in `episode.json`. Song
titles and spoken reactions over music are separate classes. Keep raw ASR
and an omitted-ID ledger; ID completeness applies to the selected translation
scope.

ASS/video now requires `work/presentation.json`. Unknown voices cannot be
merged merely because their times are close. Each paired row has a name/role;
unknown authors are visibly marked. The default lower margin is 30 logical
pixels at 1080p, or 20 actual pixels at 720p. Raising a scene needs a reason.
Signs are positioned separately from speech with a distinct visual style.
