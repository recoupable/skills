# Compose and verify the approved film

This guide ships with the customer skill. It needs no separate Recoup composition skill
or private example project. Preserve the approved bible, clip table, recording and Scribe
word timings; assembly does not authorize new generation, transcription or publication.

## Check the host before starting

The host needs Node.js 22 or later, HyperFrames **0.7.5**, FFmpeg/ffprobe, an available
Chromium-compatible rendering browser, and authorized access to the selected local media.
Browser checks and rendering must be possible in this host. Check the installed versions
and capabilities; do not claim a check passed because its command appears below.
Use only the host's already installed, reviewed tools. Do not download packages,
remote code, browser dependencies or additional skills during this workflow.

If a capability is missing, name it. The agent can prepare the timeline and review plan
from available approved inputs, but must label the unperformed checks and withhold a
verified-film claim. A hosted preset is a separate workflow, not an automatic substitute.

## Start from an empty composition

Use a new project directory, or reuse a tested project only after preserving its existing
work. Copy an already available, reviewed HyperFrames 0.7.5 blank template or
local harness. If none is available, prepare the clip manifest and edit plan,
report the missing composition environment, and stop before local execution.
Do not bootstrap a project or install dependencies to work around that limit.

Choose the approved aspect ratio. Keep automatic Whisper transcription and extra
skill installation disabled. Reuse `audio/scribe.json` from the approved recording.

Copy the selected clips into the new project's media directory and retain a manifest
mapping each copy to its approved source. Keep source masters unchanged. Set the canvas
dimensions and total duration from the approved film, including only an approved end card.
Replace every blank-template placeholder and remove its example media.

## Build the timeline in index.html

Use the scaffold's root `data-composition-id` and matching paused GSAP timeline in
`window.__timelines`. Keep one composition root with explicit `data-width`, `data-height`
and `data-duration`. A caption or visual animation must seek deterministically on that
timeline; avoid independent timers or autoplay that only works during live playback.

For every row of the active clip table:

- Put the video directly inside the root in `index.html`, with a unique ID and `class="clip"`.
  Keep media out of nested sub-compositions or wrapper elements: the pinned runtime can
  leave nested video blank even when automated checks pass.
- Set `src` to the actual selected clip; use explicit `data-start`, `data-duration`,
  `data-media-start` for trimming, and `data-track-index`. All timing values are seconds.
  Mute the generated clip's audio. Avoid overlaps on the same track unless deliberately
  implemented and reviewed as a transition.
- Place captions on their own track, using the approved Scribe word windows. Do not
  invent missing timings or silently change words to fit a line. Review lyric differences.
- Cover the complete recording. Retain approved still holds or transitions explicitly;
  an accidental black frame is not a hold. Keep the approved visual identity and fonts.

This workflow muxes the unchanged song master after the picture render. Do not leave the
scaffold's example audio active or double the song by mixing it into both stages.

## Check and review before rendering

From the composition directory, run:

```bash
hyperframes lint .
hyperframes validate .
hyperframes inspect .
hyperframes snapshot . --at 0,1.5,4 --describe false
```

Replace the example snapshot times with this film's cuts, caption transitions, end frames
and ending. Inspect the resulting PNGs. `--describe false` disables optional automatic
Gemini analysis; a configured key must not silently submit film frames to another service.
These commands check different things: source structure, browser execution and contrast,
then layout over time. Record failures and fix them before final rendering. Intentional
overflow requires visual evidence, not simply suppression of the warning.

Review moving playback as well as snapshots, and obtain approval of the assembled edit.
Only then render the picture locally:

```bash
hyperframes render . --output renders/picture.mp4 --fps 30 --strict
```

Use the approved frame rate; 30 fps is an example. Keep this a local render; no cloud
upload or publication is implied. Record command/version, output and actual check results.

## Finish the actual deliverable

Mux the approved master with FFmpeg, using the main workflow's measured linear-gain
procedure. Do not normalize or trim the song to hide a timeline mismatch. Add silence
only for an approved end-card tail. Use ffprobe on the final MP4 to measure actual duration,
video continuity and the audio stream; listen to the result and inspect frames at cuts,
caption changes and known trouble spots. Watch movement and the ending.

Capture the inspection times, defects, corrections and final viewing approval. A successful
render, an audio stream or an automated check alone is not proof of visual quality,
faithful sound or synchronized captions. If playback, audio listening or browser inspection
was unavailable, say which review remains and deliver the artifact with that limitation.

## Version evidence

The commands and attributes above were checked against the published
[`hyperframes@0.7.5` package](https://registry.npmjs.org/hyperframes/-/hyperframes-0.7.5.tgz),
including its CLI command declarations, blank template and bundled composition/CLI guides.
Its npm integrity is
`sha512-VUmuyjU5R6DI3p/FFqA8usT5LqXEFAoA/4HOeEtrKZCbxE4TuKUsAY4ne6qBtbJqJwDFr1h3ZD6lPx85dmr8+w==`.
This is a static package inspection, not a film render or a hosted provider test.
The package link records provenance only; do not fetch or execute it from this workflow.
