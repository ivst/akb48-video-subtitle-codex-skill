# Third-party visual examples

The two JPG files in this directory are **source-attributed excerpts for
technical commentary**, not MIT-licensed assets. The original episode
videos are not redistributed here. Read the discussion immediately beneath
each image in [English README](../README.md#preview) or
[Russian README](../README.ru.md#примеры), together with [NOTICE](../NOTICE).

| File | AKB48 original publication | Original video | Technical purpose |
| --- | --- | --- | --- |
| `preview-episode-12.jpg` | `AKB48の全力エンタメ学園`, episode 12, 18 April 2026 | [YouTube](https://www.youtube.com/watch?v=aPznmLtjedw) | Speaker-name label and compact subtitle panel; how they remain distinguishable |
| `preview-episode-13.jpg` | `AKB48の全力エンタメ学園`, episode 13, 25 April 2026 | [YouTube](https://www.youtube.com/watch?v=mHF3TEk6lwQ) | Panel placement and readability during the handshake segment |

Rights to the underlying source frames, on-screen graphics and performers'
depictions remain with their respective rights holders. These files are
excluded from the repository's MIT license. Attribution does not itself
authorize redistribution; applicability of any Japanese-law quotation
exception is case-specific, as described in [NOTICE](../NOTICE).

For a freely redistributable **synthetic layout reference**, use the current renderer previews below. `demo.ass` is an older static illustration.

## Current compact renderer

`compact.ass` and `compact-preview.jpg` are synthetic, original MIT-licensed examples of the current default. Generate them from the installed skill assets `presentation.example.json` and `presentation.settings.json` using `build_presentation.py`; see the [presentation guide](../.agents/skills/akb48-video-subtitles/references/presentation.md). `demo.ass` remains a legacy static illustration for parser tests, not the recommended new layout.


## Episode-12 preset (current default)

The source-attributed episode 12 frame is the design reference, not output from a separate generic text-box style. The renderer now follows its panel geometry, translucent fill, semibold type, separate speaker name/rail and purple/cyan sign design. It keeps the improved 30 logical px lower margin (20px at 720p). Fonts can change exact pixels; the checked-in previews use Segoe UI Semibold, not bundled with the skill.

- [Single speaker with sign](compact-single-preview.jpg)
- [Paired replies](compact-preview.jpg)
- [Two-line dialogue with sign](compact-long-preview.jpg)

These three original synthetic JPGs and `compact.ass` are MIT-licensed. Regenerate them from the repository root into a new folder:

```sh
python .agents/skills/akb48-video-subtitles/scripts/render_style_previews.py --output-dir work/style-previews
```

The script uses the bundled ten-second example and the production renderer, and saves font-selection logs. On systems without the reference font, explicitly choose an installed alternative with `--font Arial` (or another language-capable family), then review line fit. No font files or source episode frames are needed for these synthetic previews.
