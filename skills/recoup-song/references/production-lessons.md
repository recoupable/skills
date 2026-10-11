# Production lessons to carry forward

Reviewed 2026-09-07. These are project observations, not controlled benchmarks or
universal claims about MiniMax Music 3.

Primary foundation: [recoup-minimax-music-3](https://github.com/recoupable/skills/blob/main/skills/recoup-minimax-music-3/SKILL.md).
Detailed measured cases: [past-song prompt library](https://github.com/recoupable/skills/blob/main/skills/recoup-minimax-music-3/references/prompt-library.md).

| Song / project | Recorded finding | How it changes the workflow |
|---|---|---|
| ROUGH DRAFT, 2026-08-25 | Playful indie/bedroom pop, generated through Recoup. The 60s take cut off mid-word and never reached verse two. | Default to maximum API duration to give the full song room to finish; still check that every approved section survived. |
| SMALL LIGHTS, 2026-09-02 | Indie electronic ballad. Section-specific instrumentation followed the prompt, but the long outro looped a garbled last line. 110.13s output; film cut at 89.7s. | Describe arrangement changes and a natural ending after the approved sections; do not fill maximum headroom with an extended outro. Transcribe and find the last clean word before building scene timings. |
| PENNIES, local project log | Cumbia and tropical attempts were judged not idiomatic. A subsequent lo-fi prompt produced a song the owner liked but said did not sound like lo-fi. | Prompted genre is not observed genre. Request a listening judgment; do not claim authentic genre execution from the prompt alone. |
| SMALL ROOM, local saved request | Used a structured caption; the song file was recorded as 120.2s in the scene plan. | Reuse the caption structure and build video timings from the returned recording, not the requested duration. This record alone does not establish a genre-quality score. |
| NOBODY OFF THE STAGE, approved bible, 2026-09-03 | Approved modern hard-rock/arena-rock duet, 146 BPM, D major. Requested 130s; recorded 121.6s. Owner response recorded as “I love it.” | Positive local evidence for this specific rock duet. Duration and approval belong to the returned take, not the request. |

Local provenance under the marketing workspace: `content/pennies/SCRIPT.md` (genre note),
`content/small-room/audio/small-room-take1.json`, `content/small-room/SCRIPT.md`,
`content/off-the-stage/audio/off-the-stage-take1.json`, and `content/off-the-stage/BIBLE.md`.
These paths identify the source records, not required dependencies for an installed skill.
The table carries the necessary lessons when those private workspace files are unavailable.

User decision, 2026-09-07: let the idea and arrangement determine the song's length, and
request the maximum supported API duration by default (currently 300 seconds). This replaces
choosing a shorter request from an estimated runtime, which risks cutting off the song.
Do not pad the composition to consume that headroom. Billing normally follows actual output,
with a requested-duration precheck and a fallback charge when output duration is unavailable;
see `references/recoup-api.md` for the contract. This is the user's workflow preference,
not a controlled finding that maximum duration eliminates all cutoffs.

The previous skill's “ten lines per minute” is a rough house estimate, not an API rule.
Treat too many and too few lyrics as opposite timing failures; evaluate syllables and phrase
lengths rather than blindly applying a line count. The claim that this removes all failures
was too strong: genre mismatch was also documented in PENNIES.

The old genre note calls indie electronic ballad a thin area. The verified 1,000-card library
separates electronic/synth/ambient pop (59), cinematic pop/ballad (54), and general pop/ballad
(29). Route by the actual musical identity; do not infer that every ballad or electronic style
is poorly supported.

Historical provider spend and sample rates in these records are observations, not current
Recoup pricing or guaranteed output specifications. Always measure the returned recording.
