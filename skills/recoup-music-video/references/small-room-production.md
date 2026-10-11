# Small Room: evidence and execution contract

Reviewed 2026-09-07. This record reconstructs the final build completed 2026-09-03;
it is not the generic Higgsfield Pipeline or the superseded v1 shot list.

## Evidence behind the sequence

Source records in the marketing workspace, under `content/small-room/`:

| Stage | Evidence |
|---|---|
| Song | `gen-song.mjs`, `audio/small-room-take1.json`, the 120.2-second WAV, `audio/scribe.json` |
| Bible and audit | `BIBLE.md`: Higgsfield character-design order, scene-engine audit, owner review choices; `SCRIPT.md` records bible approval |
| Character | `gen-character.mjs`, `gen-sheet.mjs`, `cast/IDENTITY.md` |
| Screen test | `gen-audition.mjs`, two five-second takes; take 1 copied to `cast/projectionist-locked-take.mp4` |
| Props then plates | `gen-props.mjs`, `gen-plates.mjs`; saved artifacts follow the character audition |
| Scene plan and stills | `SCRIPT.md`, `gen-scene.mjs`; shared style, identity and reference glossary |
| Revised clip plan | `SCRIPT.md` v2: 26 planned shots consolidated to 17 clips; `gen-endframes.mjs` |
| Final motion | `gen-motion.mjs`, selected `clips/*.json` and MP4s; these carry later fixes not present in every table cell |
| Edit | `video/index.html`, `video/package.json`, `video/mux.sh`, original and revised renders |
| Publication | `post.config.mjs`, `post-results.json`, marketing `posts-log.md` entries for 2026-09-03 |

These paths are provenance, not required files in an installed skill. The workflow and
settings needed for a new film are carried in this skill. Small Room's final film was
124.2 seconds: 120.2 seconds of song plus an approved four-second end card. The publication
ledger records $9.76 billed for that production. Neither figure is a new-project budget.

The old `SCRIPT.md` title and final build checklist still say draft / 26 shots; the current
v2 table, 17 selected clip files and final timeline establish what actually shipped.
The final motion generator also supersedes some v2 prose: M24 is locked off rather than a
push-in; C06, M12, M18, C23 and C26 reuse start images as end anchors. Small Room was not
an all-locked-camera film: other selected rows still use push-ins or a tilt.

## Generation settings used in the completed build

| Operation | Actual model / settings |
|---|---|
| Song | `minimax/music-3`, requested 120 seconds. For new songs use the owner's later `recoup-song` decision: Recoup API, maximum duration headroom, four approvals. |
| Transcription | ElevenLabs Scribe, saved word timestamps |
| Character, prop, location and scene stills | `meta/muse-image/text-to-image` and `meta/muse-image/edit`; PNG; scene frames 9:16, character panels 3:4, prop sheets 16:9 |
| Audition | `minimax/h3-max-turbo/image-to-video`, 5 seconds, 768P, `prompt_expansion_mode: disabled`; two takes, first selected |
| Scene motion | Same H3 Max Turbo model, 768P, 5–15-second integer requests; approved start image, optional end image, `prompt_expansion_mode: disabled` |
| Composition | HyperFrames 0.7.5, selected clips trimmed onto the song map, timed captions |
| Mux | FFmpeg, copy rendered video, song at −1 dB linear gain, AAC 256 kbps, silence through the approved end card |

The old Seedance test proposal was not the scene-generation path. There was no OmniHuman,
lip-sync pass, Soul training, recasting pass or separate narrator. Candidate/model options
left in generator code are not evidence that those options made the final film.

## Transport, capabilities and spend

For a new film, preserve the session's authorized providers, accounts and spend limits;
never copy a credential or private import path out of the old scripts.

Before paying for an audition or motion batch, verify the chosen route supports the actual
model and settings above. Name the route, model, take count and current quote in the spend
plan. Retain an approved budget on resume; extra takes beyond it need approval. Do not
silently substitute a different model and call it the Small Room configuration.

**Known Recoup route gap, verified against API implementation on 2026-09-07:**
`POST https://api.recoupable.dev/api/content/video` selects H3 Max (not Turbo), accepts
`balanced` / `quality` prompt expansion, and rejects `disabled`. Passing an invented `model`
field cannot select Turbo. If the session requires this route, report the mismatch and
resolve the model/route choice with the user before motion spend. Direct-provider access
is not automatically authorized by a requirement to match historical settings.

Sources: [video model](https://github.com/recoupable/api/blob/071ff9b6dd02fa338128b193713604dd989f5dc1/lib/content/video/generateVideo.ts),
[video validator](https://github.com/recoupable/api/blob/071ff9b6dd02fa338128b193713604dd989f5dc1/lib/content/video/validateCreateVideoBody.ts),
[image routing](https://github.com/recoupable/api/blob/071ff9b6dd02fa338128b193713604dd989f5dc1/lib/content/image/buildImageInput.ts).
Recheck before a new production; this is a dated capability snapshot. Historical promotional
rates have expired or may change, so get a fresh quote and distinguish reported spend from
estimates. Preserve provider request IDs and local artifacts when calls are slow; reconcile
uncertain submissions instead of duplicating them.

## Why the linked skills are adapted

Small Room used the character-design and scene-engine methods, plus shotlist-director's
shared style, reference glossary and sequence checks. Its artifact was a Markdown script
and its animation was H3 Max Turbo. The upstream shotlist skill's Seedance prompt grammar,
HTML interface, Soul/Elements setup and automatic 15-second envelopes were not used.
Its silent audition also did not require dialogue, a separate voice model or lip-sync.
Use the applicable methods without importing those unused production branches.
