# Editorial review before encoding

Read the translation against the Japanese source before committing to a full render. Structural passes cannot judge meaning, humor, omitted content or speaker identity.

## What to review

- Check each translated scene for who says what, negation, conditions, tense, numbers and omissions. Compare difficult passages with audio, not just two competing machine transcripts.
- Read the target text as dialogue: natural phrasing, appropriate register, concise readable wording and a supported punchline. Do not add an explanation or stronger claim absent from the source.
- Resolve member identities first, then apply the approved spelling. A correctly spelled name can still identify the wrong person. Check nicknames and references to people outside the visible cast.
- Check fan/event terms in their historical context, song titles as proper names, and sign/result coverage against actual frames. Treat lyrics separately under the recorded scope.

## One uncertainty ledger

Use existing source/translation chunk metadata or one `work/review.md`; no separate duplicate ledger is required. For disputed lines record source ID/time, the current translation, the issue, supporting audio/frame/glossary evidence and its resolution or remaining limitation. Revisit flagged passages after reading the surrounding scene. Correct approved text in place; retain raw source evidence and mapping.

Established speaker evidence may be referenced by multiple source turns within the same supported scene. Keep one evidence entry and point to its ID, time range or existing note in each turn's `evidence` string. This is reuse of established evidence, not an inference that all nearby lines belong to the same speaker. Re-check scene/voice changes, overlaps and off-camera replies. Leave an uncertain voice unnamed instead of inventing a role or blocking the whole episode over a short backchannel.

A second editorial pass is a review activity, not a requirement to call another model, spawn an agent, retranscribe everything or recreate all chunk files. Record what was actually reviewed; do not claim native/audio verification if only source text was checked.

## Pre-encode checkpoint

1. Finish translation and editorial review. Resolve material meaning/name/coverage problems, or retain cautious wording and explicitly disclose a remaining limitation; do not guess to clear a checklist.
2. Validate changed chunks and the source-to-display mapping. Build ASS/SRT from presentation data, using supported style overrides where needed.
3. Inspect actual-episode single/paired/long/sign frames, all key cards/results and their scene boundaries. Check font substitution, text fit and faces before encoding the full episode.
4. Render once the text and layout are ready. If either changes afterwards, update the generating data, regenerate outputs and validate the affected result. Keep archive contents synchronized.

The final report must distinguish editorial/source review, sampled visual review and automated media checks. A technical pass alone is not approval of translation quality.
