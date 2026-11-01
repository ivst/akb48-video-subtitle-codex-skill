# Speaker-aware presentation and music scope

The independent trial found three failures despite valid media: short replies
were joined without speaker evidence, neutral text boxes lost the name-label
layout, and two unrequested song fragments were burned into the output.
The supported default now has an executable display contract and renderer.

## Scope first: background songs are omitted by default

New episode manifests set `lyrics_policy` to `omit` and `lyrics_request` to null.
"Translate the video, including signs" is **not** a request for song lyrics.
Omit background singing and performance lyrics from translated display tracks,
ASS, burned video and subtitle packages unless the user explicitly requests them.
Never insert isolated ASR lyric guesses or treat untranslated background music
as unfinished dialogue. Spoken reactions over music remain dialogue if audible.

Keep original ASR evidence intact. Classify content **before** preparing scoped
translation chunks. Record excluded raw source IDs, times and reasons in a
working omission ledger; stable-ID completeness applies to the selected source
chunk, not every non-speech token Whisper produced. Do not silently drop IDs
from an already-reviewed chunk: revise the scoped source and mapping together.
An agent must review classification; the scripts cannot hear music.

For requested lyrics set `lyrics_policy: "requested"` and put the actual user
instruction in `lyrics_request`. Review the Japanese words and the intended
output scope before adding lyric events; do not fabricate consent to pass a
validator. Song **titles** in signs/dialogue still use canonical Latin/romaji
spellings and are a separate content class.

## Work file: work/presentation.json

Use [the bundled example](../assets/presentation.example.json) as the schema
example. The matching [settings](../assets/presentation.settings.json) are only
for the six-second synthetic demo; use the real initialized `episode.json` for
an episode. These assets are included when installing the standalone skill.

- `schema_version`: 1.
- `speakers`: safe stable IDs mapped to concise visible `label` and `color`
  (`#RRGGBB`). Use verified names or evidence-backed neutral voice roles.
- `turns`: source turn ID mapped to `speaker_id` (or null) and attribution
  `evidence`. Record audio time/frame/context that establishes the turn. A shot
  of a person alone does not identify the voice. For a source caption containing
  multiple voices, create separate turn IDs and retain parent source ID/time
  mapping in the working records.
- `events`: display events with unique `id`, integer `start_ms`, `end_ms`,
  and `kind` (`dialogue`, `inscription`, `song_title`, or explicitly requested
  `lyrics`). No `background_music` display kind is accepted.
- A dialogue event has one or two `rows`, each with `text`, `speaker_id` and
  `source_ids`. Each source ID must have an entry in `turns`. Only merge turns
  when they have the **same established** voice. Two null identities do not
  establish the same speaker; the renderer never merges events automatically.
- A short exchange can use two labeled rows in one event. Otherwise split
  it into consecutive timed events. Unknown voices remain separately displayed
  with neutral `Voice ?` / `Голос ?` labels and review warnings. Numbered unknown
  labels in a paired event are local placeholders, not identities across scenes.
- A row containing ` / ` or two em dashes is a mixed-voice review candidate and
  fails by default. For a genuine single-speaker sentence only, provide
  `turn_review: "single_speaker_verified"` and `review_evidence`. Never use this
  escape merely to suppress a split-dialogue error.
- Inscriptions/song titles use `text` and an explicit `box: [x,y,width,height]`
  on the logical 1920x1080 canvas. Position them near their source text while
  avoiding faces and dialogue. Inscriptions have distinct dark colored panels
  and white text; speech has a light panel, dark text, colored name and thin rail.

## Generate and validate

From the repository root, using the synthetic inputs:

```sh
python .agents/skills/akb48-video-subtitles/scripts/build_presentation.py --input .agents/skills/akb48-video-subtitles/assets/presentation.example.json --episode .agents/skills/akb48-video-subtitles/assets/presentation.settings.json --output-dir work/compact-demo
python .agents/skills/akb48-video-subtitles/scripts/check_presentation.py --input .agents/skills/akb48-video-subtitles/assets/presentation.example.json --episode .agents/skills/akb48-video-subtitles/assets/presentation.settings.json --ass work/compact-demo/subtitles.ru.ass --srt work/compact-demo/dialogue.ru.srt --json
```

For a real episode use `--input episodes/demo/work/presentation.json`,
`--episode episodes/demo/episode.json` and `--output-dir episodes/demo/output`.
Generated files include labeled dialogue SRT, inscription SRT when present and
combined ASS. A lyric SRT is generated only for requested lyric events. Existing
outputs require `--overwrite` after backup; stale lyric files must be archived
outside the delivery folder when changing to omit mode.

`run_checks.py` requires this work file for ASS/video delivery (including older
projects without the new key), checks speaker/music structure and regenerates
the expected ASS/SRT in memory to verify correspondence to delivered files.
Missing presentation gives `incomplete`; contradictions or output drift give
`fail`. An old media-only `pass` must not be used to approve a new styled version.
Any style override should preserve the contract, renderer and output checks;
do not hand-edit the ASS after validating its generating work file.

## Placement, fonts and preview

Default `bottom_margin` is **30 logical pixels at 1080p**, scaling to **20 actual
pixels at 720p**. Single-row panels are 82/128 logical pixels high for one/two
lines. A paired exchange stacks two separately named rows above the same lower
baseline; long exchanges must be split, not squeezed into tiny type.

Use optional event-level `bottom_margin` only for a scene with conflicting source
graphics. Values above 60 logical pixels require `placement_reason`; do not
raise the whole video preemptively. Fonts default to Arial; supply a locally
available, language-capable `font` family if necessary. Font files are not bundled.

The renderer uses approximate character widths and requires explicit appropriate
breaks for long unspaced scripts. It deliberately rejects long text instead of
shrinking it indefinitely. Static layout checks do not prove pixel fit, correct
speaker identity, voice boundaries, source classification, or translation meaning.
Preview short/long/paired turns, signs and face positions at the actual resolution
and inspect the final burned video. Technical `pass` is not editorial acceptance.
