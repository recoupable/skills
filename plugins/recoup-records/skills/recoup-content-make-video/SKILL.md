---
name: recoup-content-make-video
description: Make finished short-form video for an artist — a 9:16 TikTok/Reel/Short of the artist + song, a lyric video, a no-text visualizer/Spotify Canvas, or per-platform reformats of existing footage. Use for "make a TikTok/Reel/Short", "lyric video", "visualizer/Canvas", or "reformat this for TikTok". Modes: short, lyric, visualizer, reformat. Verifies the render before claiming done; stops at the asset. For the clip-worthy moment first, use recoup-song-find-hook.
---

# Recoup Content — Make Video

Every motion job, one skill. Read the bundled references first:
`references/workspace-context.md`, `references/account-resolver.md`,
`references/research-context.md`, `references/content-api.md` (the video modes +
async create→poll), `references/song-sourcing.md` (real audio, no placeholders),
`references/analyze-gate.md` (verify before claiming done).

## Backbone

Resolve the artist (use the **`account_id`**, not row `id` — wrong one 404s), read
context first, layer live signals, generate, **analyze-gate** (you can't see motion —
analyze and regenerate on failure), persist + commit. Real audio only.

## Modes

- **short** — finished 9:16 of the artist + song. The look is a **template**
  (bedroom/stage/outside/album-record-store; default `artist-caption-bedroom`; list
  via `/content/templates`). Fire `POST /content/create`, poll `/tasks/runs?runId=`
  every ~10s until terminal, read `output.{videoSourceUrl,captionText}`. The async
  path is agent-safe (sync `/content/video` times out).
- **lyric** — transcribe for word-level timings (`POST /content/transcribe`,
  `audio_urls` array → `segments:[{start,end,text}]`), generate/use an on-brand
  background, **burn in synced lyrics**, mux full-length. Don't reproduce third-party
  lyrics.
- **visualizer** — seamless loop, **no text/logos** (Spotify rejects them), 9:16,
  3–8s; use `first-last` with identical start/end frames; analyze-gate the seam.
- **reformat** — edit, don't generate: master → genuinely distinct per-platform cuts
  (never identical re-uploads — platforms suppress them). Lead 9:16 with the hook
  (use recoup-song-find-hook for the in-point); captions clear of UI safe zones.

## Guardrails

- **Verify before delivery** — analyze-gate every render; never claim an unverified
  asset is done.
- **Real audio only** (`references/song-sourcing.md`).
- **Stop at the asset** — no posting.

## References

- `references/workspace-context.md` · `references/account-resolver.md` ·
  `references/research-context.md` · `references/content-api.md` ·
  `references/song-sourcing.md` · `references/analyze-gate.md`
