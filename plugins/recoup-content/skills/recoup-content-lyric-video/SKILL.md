---
name: recoup-content-lyric-video
description: Make a lyric video — the whole song's words animated on screen, timed to the audio, over a visual background (a motion video, not a still card). Use when the user says "lyric video", "make a video with the lyrics", "put the words on screen", "kinetic typography for [song]", or "animated lyrics for [song]". Transcribes the song to get word timings, generates or uses a background visual, and burns in the synced lyrics. For a single static lyric on one image, use recoup-content-graphic. Works with or without artist context.
---

# Lyric Video

Turn a song into a video where the lyrics appear in time with the audio. The job is
**timed text over a visual** — distinct from a featuring-artist clip (`recoup-content-video`)
or a no-text loop (`recoup-content-visualizer`).

Read `references/content-api.md` for the endpoints and async pattern,
`references/song-sourcing.md` for getting the audio, and `references/analyze-gate.md`
before claiming the result is done. (All ship alongside this skill.)

## Inputs

- **Song audio** (required) — see `references/song-sourcing.md`. No real audio → stop.
- **Background** (optional) — a generated visual, a supplied image/video, or the artist's
  aesthetic from `context/artist.md`. Generic mode: take the user's prompt or footage.
- **Lyrics** (optional) — if the user supplies an accurate lyric sheet, prefer it over the
  transcript for spelling; still use the transcript for **timing**.

## Steps

### 1. Get word-level timings

```bash
curl -sS -X POST "$BASE/content/transcribe" "${AUTH[@]}" -H "Content-Type: application/json" \
  -d "$(jq -n --arg u "$SONG_URL" '{audio_urls:[$u]}')" | jq '.segments'
```

`audio_urls` is an **array** (one or more public audio URLs). The response is
`{audioUrl, fullLyrics, segments:[{start,end,text}], segmentCount}`; `.segments` drives when
each line appears. If the user gave an official lyric sheet, align it to these timings rather
than trusting the raw transcript spelling.

### 2. Create the background

- **Context mode:** generate a visual on-brand with `context/artist.md` (or animate
  `context/images/face-guide.png`).
- **Generic mode:** generate from the user's prompt, or use footage they supply.
- A still works (loop it) or a slow motion clip via the `prompt`/`animate` video modes.

### 3. Burn in the synced lyrics

Use the edit endpoint to overlay text per timed segment over the background, then mux the
song for the full duration (see the edit ops + async pattern in `references/content-api.md`).
Keep text legible: large, high-contrast, inside safe margins, one line/phrase at a time.

### 4. Verify, then deliver

Run the analyze gate (`references/analyze-gate.md`) — check the words are readable, on
time, and not clipped. Regenerate any failing stage before presenting.

## Persist

In a workspace, save to `artists/{slug}/releases/{release-slug}/` (or `content/lyric-video/`)
and commit `{what}: {why}`. See `references/workspace-context.md`. No workspace → return
the URL.

## Guardrails

- **Timing comes from the transcript**, spelling from the official sheet when provided.
- **Don't reproduce third-party copyrighted lyrics** — this is the artist's own song; for
  covers or samples, confirm rights with the user.
- **Never fake the audio** (`references/song-sourcing.md`).
