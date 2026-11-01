# Definition of done: AKB48 subtitle episode

This is an agent-run quality checklist, **not** a guarantee that a translation or video is perfect. Use an authorized local video and record review scope accurately.

## Inputs and durable state

- `episode.json` records episode ID, target locale, source media, expected duration/size, requested outputs, and glossary revision.
- Source Japanese transcript and stable translation chunk JSON are saved to `source/` and `work/chunks/`.
- Every translation chunk preserves all IDs in order and has nonempty target text. Review source audio for ambiguous phrases, jokes, names and overlapping speakers.
- A member name reported as missing may have been legitimately replaced by a pronoun. Human review decides.
- The approved episode-specific glossary overrides bundled draft terminology.

## Validation commands (from repository root)

```sh
SKILL=.agents/skills/akb48-video-subtitles
python "$SKILL/scripts/check_environment.py" --require-ass
python "$SKILL/scripts/check_translation.py" --input examples/quality/source.json --translated examples/quality/translated.json --target-lang ru --members "$SKILL/glossaries/members/ru.csv" --json
python "$SKILL/scripts/check_srt.py" examples/quality/ru.srt --profile ru --duration 14 --json
python "$SKILL/scripts/check_names.py" --source examples/quality/ja.srt --target examples/quality/ru.srt --episode examples/quality/episode.json --json
python "$SKILL/scripts/check_ass.py" examples/demo.ass --width 1920 --height 1080 --duration 6 --json
python "$SKILL/scripts/probe_media.py" path/to/source.mp4 --json
python "$SKILL/scripts/compare_media.py" --source path/to/source.mp4 --rendered path/to/output.mp4 --json
python "$SKILL/scripts/compare_audio.py" --source path/to/source.mp4 --rendered path/to/output.mp4 --json
python "$SKILL/scripts/run_checks.py" --project path/to/episode --require-translation --json
```

The `path/to/` commands require real media and are illustrative: they must not be reported as completed unless actually executed. The six-second ASS demo is synthetic and contains **no audio**.

## Render and manual review

- Use `check_ass.py` to detect malformed times, missing styles, excessive dialogue lines, invalid/missing PlayRes and out-of-range events. ASS allows legitimate simultaneous dialogue, speaker labels and vector panels; do not globally reject overlapping events.
- `PlayResX/PlayResY` may scale with the player; default size mismatch is a **warning**. Use `--strict-resolution` only if identical pixel coordinates are required.
- Confirm source/output video stream, duration, FPS, frame dimensions and audio presence with FFprobe and `compare_media.py`. Small encoder-duration tolerances are expected.
- When source audio **must remain unchanged**, set `"audio_preservation":"unchanged"` in episode.json. `compare_audio.py` compares decoded PCM SHA256; this is **not** a hash of compressed audio packets, and a re-encode or resample may change it.
- For intentionally modified audio, set `"audio_preservation":"not_required"`; explicitly note that unchanged audio was not verified. For a silent source, this mode may be appropriate.
- Inspect representative frames, scenes containing faces and signs, transitions and all key title cards. Automated ASS checks cannot certify layout readability or avoid covering faces.
- Decode the finished video to completion before delivery. Validate that any ZIP package contains the current revision.
- Use `report.json` from `run_checks.py` to show which checks **really ran**, what failed, and which were skipped. The report does **not** certify semantic translation quality or rights clearance.
- Deliver original source files only if authorized. Avoid adding protected footage or full transcripts to public pull requests.

## Model choice for complex Japanese translation

**Recommended when available:** GPT-6.1 Sol with **Medium reasoning effort or higher**, especially for long variety-show dialogue, jokes, register changes and unclear speaker references. Use a more capable model/reasoning setting when useful, subject to the current account/workspace choices. This is a practical starting preference, not a verified guarantee that any particular model will give a better translation.

Preserve Japanese source text and evidence, review the output against audio, and do not invent unverifiable lines. A stronger model is not a substitute for an approved glossary, structural checks, or fluent human review.
