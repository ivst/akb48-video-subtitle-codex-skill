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

For a freely redistributable **synthetic layout reference** rather than a
real AKB48 still, use [demo.ass](demo.ass).

## Current compact renderer

`compact.ass` and `compact-preview.jpg` are synthetic, original MIT-licensed examples of the current default. Generate them from the installed skill assets `presentation.example.json` and `presentation.settings.json` using `build_presentation.py`; see the [presentation guide](../.agents/skills/akb48-video-subtitles/references/presentation.md). `demo.ass` remains a legacy static illustration for parser tests, not the recommended new layout.
