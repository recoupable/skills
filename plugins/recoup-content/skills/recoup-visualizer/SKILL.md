---
name: recoup-visualizer
description: Make a looping audio visualizer or a Spotify Canvas — a short, seamless, no-text motion loop set to the song. Use when the user says "visualizer", "Spotify Canvas", "Canvas video", "looping background for the song", "audio-reactive loop", or "make a Canvas for [song]". Produces a vertical seamless loop (8s, 9:16, silent-friendly, no on-screen text) sized for Spotify Canvas, plus an optional longer visualizer. Works with or without artist context.
---

# Visualizer / Spotify Canvas

A **seamless looping visual** tied to the song's mood — no on-screen text, no hard cuts.
Two common targets: a Spotify **Canvas** (3–8s, 9:16, loops behind the track on Spotify)
and a longer audio visualizer for YouTube/social. Distinct from a lyric video (has text)
and a featuring-artist clip (`recoup-short-video`).

Read `references/content-api.md` (endpoints, video modes, async),
`references/song-sourcing.md` (audio for mood/sync), and `references/analyze-gate.md`
(verify the loop). All ship alongside this skill.

## Canvas constraints (don't violate these)

- **Aspect:** 9:16 vertical.
- **Length:** 3–8s; Spotify loops it, so it must **loop seamlessly** (last frame flows into
  the first — `first-last` mode with matching start/end frames is ideal).
- **No text / no logos** — Spotify rejects Canvases with CTAs, hashtags, or watermarks.
- Keep it atmospheric; motion subtle enough to loop without a visible seam.

## Steps

1. **Set the mood.** Context mode: pull aesthetic from `context/artist.md`; optionally seed
   from `context/images/face-guide.png` or cover art. Generic mode: use the user's prompt.
   Optionally transcribe/analyze the song (`references/song-sourcing.md`) to match energy.
2. **Generate the loop.** Use `animate` (still → motion) or `first-last` with identical
   start/end frames for a clean loop. Target 8s, 9:16. See `references/content-api.md`.
3. **(Optional) Longer visualizer.** For YouTube/social, extend or concatenate loops and
   mux the song for full duration.
4. **Verify the loop** with the analyze gate — confirm no visible seam, no text, no
   artifacts, 9:16 framing. Regenerate if flagged.

## Persist

Workspace → `artists/{slug}/releases/{release-slug}/canvas.mp4` (+ `visualizer.mp4`), commit
`{what}: {why}` (`references/workspace-context.md`). Otherwise return the URL.

## Guardrails

- **Canvas = no text, ever.** If the user wants words, that's a lyric video, not a Canvas.
- **It must loop.** A clip that hard-cuts at the end is not a Canvas — fix the seam.
- **Never fake the audio** (`references/song-sourcing.md`).
