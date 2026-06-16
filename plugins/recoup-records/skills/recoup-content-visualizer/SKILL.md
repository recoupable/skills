---
name: recoup-content-visualizer
description: Make a looping audio visualizer or a Spotify Canvas — a short, seamless, no-text motion loop set to the song. Use when the user says "visualizer", "Spotify Canvas", "Canvas video", "looping background for the song", "audio-reactive loop", or "make a Canvas for [song]". Produces a vertical seamless loop (8s, 9:16, silent-friendly, no on-screen text) sized for Spotify Canvas, plus an optional longer visualizer. Works with or without artist context.
---

# Visualizer / Spotify Canvas

A **seamless looping visual** tied to the song's mood — no on-screen text, no hard
cuts. Two common targets: a Spotify **Canvas** (3–8s, 9:16, loops behind the track
on Spotify) and a longer audio visualizer for YouTube/social. Distinct from a
lyric video (has text → `recoup-content-lyric-video`) and a featuring-artist clip
(`recoup-content-video`).

The job is a loop in both senses: the output must loop, and the *process* loops —
**match the mood → generate → verify the seam is invisible → regenerate if it
isn't.** A Canvas with a visible cut at the wrap point is broken, not done.

Read `references/content-api.md` (endpoints, video modes, async),
`references/song-sourcing.md` (audio for mood/sync), and `references/analyze-gate.md`
(verify the loop). All ship alongside this skill.

## Canvas constraints (don't violate these)

- **Aspect:** 9:16 vertical.
- **Length:** 3–8s; Spotify loops it, so it must **loop seamlessly** (last frame
  flows into the first — `first-last` mode with matching start/end frames is ideal).
- **No text / no logos** — Spotify rejects Canvases with CTAs, hashtags, or
  watermarks.
- Motion subtle enough to loop without a visible seam; atmospheric, not frantic.

## Inputs

- **Song** (for mood/energy) — see `references/song-sourcing.md`; never fake audio.
- **Artist** (optional) — context mode supplies aesthetic + seed imagery.
- **Target** — Canvas (default, 8s/9:16) and/or a longer visualizer.

## Procedure

### Phase 1 — Set the mood (concrete, not a vibe word)

Context mode: pull aesthetic from `context/artist.md`; optionally seed from
`context/images/face-guide.png` or the release cover so the Canvas matches the
artwork. Generic mode: the user's prompt. **Match the song's actual energy** —
transcribe/analyze it (`references/song-sourcing.md`) so a slow ballad gets slow,
heavy motion and an uptempo track gets faster movement. Write down the intended
palette + motion feel; you'll check against it in Phase 3.

### Phase 2 — Generate the loop

Use `animate` (still → motion) or, preferably, `first-last` with **identical
start/end frames** for a clean wrap. Target 8s, 9:16 (`references/content-api.md`).
For a longer visualizer, extend or concatenate loops and mux the song for full
duration.

### Phase 3 — Verify the loop (the analyze-gate loop; mandatory)

You cannot see motion by trusting the render succeeded — analyze it
(`references/analyze-gate.md`) and **regenerate on any failure**:

- [ ] **No visible seam** — the last frame flows into the first; play it twice
      mentally and confirm no jump/cut at the wrap.
- [ ] **No text, no logos, no watermark** (Spotify rejects these).
- [ ] **9:16** framing, subject centered for the vertical crop.
- [ ] **No artifacts** (warping, flicker) and motion matches the mood from Phase 1.

A clip that hard-cuts at the end is not a Canvas — fix the seam (re-run with
matched first/last frames) before presenting.

### Phase 4 — Persist

Workspace → `artists/{slug}/releases/{release-slug}/canvas.mp4` (+
`visualizer.mp4`), commit `{what}: {why}` (`references/workspace-context.md`).
Otherwise return the URL.

## Guardrails

- **Canvas = no text, ever.** If the user wants words, that's a lyric video.
- **It must loop.** A visible seam means it's not done — regenerate.
- **Verify before delivery.** An un-analyzed loop is the failure mode here.
- **Never fake the audio** (`references/song-sourcing.md`).

## References

- `references/content-api.md` — video modes (`animate`, `first-last`), async.
- `references/song-sourcing.md` — sourcing real audio for mood/sync.
- `references/analyze-gate.md` — verifying the loop before claiming done.
- `references/workspace-context.md` — read-context-first + write-back.
