# Speaker-aware presentation and music scope

The independent trial found three failures despite valid media: short replies
were joined without speaker evidence, neutral text boxes lost the name-label
layout, and two unrequested song fragments were burned into the output.
The supported default has an executable display contract and configurable renderer. The `episode-12` default template follows the compact panel in the episode 12 reference: translucent white panel, pale border, colored name and matching rail, and dark semibold dialogue. Ordinary per-text background boxes do not implement this preset.

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
for the ten-second synthetic demo; use the real initialized `episode.json` for
an episode. These assets are included when installing the standalone skill.

- `schema_version`: 1.
- `style_preset`: `"episode-12"` (the default template when omitted). Adapt it using the supported `style` object below; arbitrary preset names fail.
- `speakers`: safe stable IDs mapped to concise visible `label` and `color`
  (`#RRGGBB`). Use verified names only; a role is not a name.
- `turns`: source turn ID mapped to `speaker_id` (or null) and attribution
  `evidence`. Record audio time/frame/context that establishes the turn. A shot
  of a person alone does not identify the voice. For a source caption containing
  multiple voices, create separate turn IDs and retain parent source ID/time
  mapping in the working records. Evidence may reference one existing note/turn/time range shared by established turns within the same supported scene; do not repeat an attribution investigation for every short reply. A shared reference must still support that particular voice and context.
- `events`: display events with unique `id`, integer `start_ms`, `end_ms`,
  and `kind` (`dialogue`, `inscription`, `song_title`, or explicitly requested
  `lyrics`). No `background_music` display kind is accepted.
- A dialogue event has one or two `rows`, each with `text`, `speaker_id` and
  `source_ids`. Each source ID must have an entry in `turns`. Only merge turns
  when they have the **same established** voice. Two null identities do not
  establish the same speaker; the renderer never merges events automatically.
- When the voice is not established, set `speaker_id` to `null`. The row is then
  published as **just the translated line**: no name, no rail, no placeholder.
  Never use `Voice ?` / `Голос ?` / `Unknown`, numbered stand-ins, or an invented
  role such as `Ведущая` / `Участница` / `Сотрудник` — a role does not identify a
  person, and a placeholder reads as a name to viewers. The renderer rejects
  placeholder labels and emits one review warning per unnamed row. Separate
  unnamed turns stay separate timed events; they cannot be paired to imply one
  speaker.
- A short exchange can use two labeled rows in one event only when both voices
  are established. Otherwise split it into consecutive timed events.
- A row containing ` / ` or two em dashes is a mixed-voice review candidate and
  fails by default. For a genuine single-speaker sentence only, provide
  `turn_review: "single_speaker_verified"` and `review_evidence`. Never use this
  escape merely to suppress a split-dialogue error.
- Inscriptions/song titles use `text` and an explicit `box: [x,y,width,height]`
  on the logical 1920x1080 canvas. Position them near their source text while
  avoiding faces and dialogue. Inscriptions have distinct dark colored panels
  and white text with a cyan border; speech has a translucent light panel, dark text, colored name and matching thin rail.

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
Use the supported `style` settings and explicit sign boxes to follow the episode or user reference while preserving speaker separation and output checks. Do not hand-edit ASS; update the generating JSON and rebuild.

## Placement, fonts and preview

Default `bottom_margin` is **30 logical pixels at 1080p**, scaling to **20 actual
pixels at 720p**. Single-row panels are 82/128 logical pixels high for one/two
lines. A paired exchange stacks two separately named rows above the same lower
baseline; long exchanges must be split, not squeezed into tiny type. An unnamed
row keeps the same panel but draws no rail and no name: the dialogue is centred
in the full panel width, so an unknown voice is not presented as a person.

Use optional event-level `bottom_margin` only for a scene with conflicting source
graphics. Values above 60 logical pixels require `placement_reason`; do not
raise the whole video preemptively. The reference font is **Segoe UI Semibold**, used by default, with 40 logical px for a single speaker, 38 px for paired one-line replies and 32 px for a paired two-line reply; names use 26/22 px. The panel spans x=110–1810, with ASS fill alpha `0A`, a 3px pale outline and a same-color outlined name rail. Sign panels use purple fill, a cyan outline and 26px white text.

Segoe UI Semibold is normally available on Windows. Font files are **not bundled**; on other systems or for missing glyph coverage, explicitly set an installed language-capable `font`, such as Arial or Noto Sans. This preserves geometry but can change wrapping and appearance; never claim a pixel-identical match after substitution. Inspect FFmpeg `fontselect` and missing-glyph messages as well as the actual frames.

Generate the three synthetic checks with the **same renderer** for a new/changed installation, renderer, font or style. Reuse already inspected previews when those inputs are unchanged; they are not required again for each chunk or episode:

```sh
python .agents/skills/akb48-video-subtitles/scripts/render_style_previews.py --output-dir work/style-previews
```

Use a new output directory (the command refuses existing files). The script saves ASS, single, paired and two-line-with-sign JPGs, plus FFmpeg font-selection logs. Use `--font Arial` only as an explicit font override. These previews prove the installed renderer can draw the preset; inspect additional frames from the actual episode too. For each production episode inspect actual-episode frames with its selected settings before full encoding; the synthetic preview alone does not verify a customized layout. Old manually styled ASS must be regenerated from reviewed presentation data; a skill update alone does not restyle existing MP4 files.

The renderer uses approximate character widths and requires explicit appropriate
breaks for long unspaced scripts. It deliberately rejects long text instead of
shrinking it indefinitely. Static layout checks do not prove pixel fit, correct
speaker identity, voice boundaries, source classification, or translation meaning.
Preview short/long/paired turns, signs and face positions at the actual resolution
and inspect the final burned video. Technical `pass` is not editorial acceptance.

## Episode style overrides

Keep `style_preset: "episode-12"` as a starting template rather than rebuilding the renderer for each program. Optional top-level `style` keys (RGB, not ASS BGR):

| Key | Default | Allowed values |
| --- | --- | --- |
| `panel_x`, `panel_width` | 110, 1700 | Integer x >= 0, width >= 1200, x + width <= 1920 |
| `panel_fill`, `panel_border` | `#FFFFFF`, `#D5CBD5` | `#RRGGBB` |
| `panel_opacity` | 245/255 | Finite number 0.5–1; 1 is opaque |
| `dialogue_color` | `#252525` | `#RRGGBB` |
| `sign_fill`, `sign_border`, `sign_color` | `#87348F`, `#46BCD7`, `#FFFFFF` | `#RRGGBB` |
| `sign_font_size` | 26 | Integer 22–42 logical px |

For example, adapt a blue/yellow episode without changing the source mappings:

```json
{"style_preset":"episode-12","style":{"panel_x":80,"panel_width":1760,"panel_border":"#38B5D5","sign_fill":"#235E78","sign_border":"#F4D24A","sign_font_size":30}}
```

An inscription/song-title event may also have a `style` object containing only the four `sign_*` keys. Use its existing `box` to match the original card region and color; do not create a large empty panel simply to fit a short label. Inspect contrast, faces and important graphics. Font size is included in the sign fit check. Global panel geometry adjusts text centers and wrapping while preserving names/rails; unsupported keys, invalid colors, oversized panels and too-small sign boxes fail. All customized outputs still pass `check_presentation.py` correspondence checks.

## Editing and encode checkpoint

Follow [editorial-review.md](editorial-review.md) before full encoding. During editing, validate changed translation/presentation files and sample affected frames. Do not rerun environment discovery, reinstall ASR, regenerate synthetic previews or decode the whole episode after each text chunk. Run final media checks on the current delivered revision, and repeat any check whose inputs changed. Never reuse an old media pass for a rebuilt video.
