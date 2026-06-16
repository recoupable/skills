---
name: recoup-song-analyze
description: Understand a song from its audio using Recoup's audio language model (Music Flamingo) — a full report, catalog metadata (BPM/key/genre/mood), a lyric sheet, or a mix critique. Use when asked to "analyze this song", "what does this track sound like", "what key/BPM/genre is this", "tag this song", "transcribe the lyrics", "make a lyric sheet", or "critique this mix". For the clip-worthy hook use recoup-song-hook; for playlist/sync placement materials use recoup-song-pitch-kit. Needs a public audio URL.
---

# Song Analyze (Music Flamingo)

Turn a song's **audio** into structured intelligence — genre, key, BPM, mood,
lyrics, mix notes, and more — using Recoup's audio language model. This is the
entry point for "understand this track" requests. For the clip-worthy hook hand
off to `recoup-song-hook`; for playlist/sync placement materials hand off to
`recoup-song-pitch-kit`.

The endpoint contract (auth, base URL, request/response, every preset, call
patterns, gotchas) lives in `references/flamingo-api.md`. Read it before calling.

## What you can ask for (modes)

| Ask | Mode | Lead preset(s) |
|---|---|---|
| "Analyze / full report / what does this sound like" | **report** | `full_report` (only when they want everything) |
| "Tag this / catalog metadata / BPM/key/genre/mood" | **metadata** | `catalog_metadata` (+ `mood_tags`, `music_theory`) |
| "Transcribe the lyrics / lyric sheet / explicit lines" | **lyrics** | `lyric_transcription` (+ `content_advisory`) |
| "Critique the mix / mix notes / is the low end muddy" | **mix** | `mix_feedback` (+ `music_theory`) |

For "find the hook" → `recoup-song-hook`. For "playlist pitch" or "sync brief" →
`recoup-song-pitch-kit`.

## Steps

1. **Resolve a public `audio_url`.** The endpoint cannot take a local file. If the
   user only has a local file, ask for a hosted link — don't pretend it can be sent.
2. **Pick the smallest useful preset** for the mode (see table). Don't default to
   `full_report` (13 model calls). When unsure, `GET /api/songs/analyze/presets`.
3. **Call the endpoint** (REST preferred — works with sandbox bearer or API key).
4. **Interpret the result** for the user's goal — don't dump raw JSON.
5. **Persist if in a workspace** (below).

## Mode details

### metadata
Lead with `catalog_metadata`; usually add `mood_tags`, `music_theory`,
`content_advisory`; add `lyric_transcription` only if lyrics are wanted. Normalize
into one `metadata.json`:

```json
{ "genre": "", "subgenres": [], "primary_mood": "", "mood_tags": [], "bpm": 0,
  "key": "", "time_signature": "", "energy": "", "danceability": "",
  "instruments": [], "vocals": "", "similar_artists": [], "content_rating": "",
  "one_line_description": "" }
```

Treat output as a strong draft — confirm BPM/key against a detector if the value
drives a creative or contractual decision.

### lyrics
Lead with `lyric_transcription`; add `content_advisory` for explicit/brand-safety/
radio checks. Format with `[Verse]` / `[Chorus]` / `[Bridge]` headers into
`lyrics.md`. **Draft, not final** — mark unclear audio `[inaudible]`/`[unclear: …]`,
never invent lines, and for reference tracks summarize rather than reproducing
third-party copyrighted lyrics.

### mix
Lead with `mix_feedback`; add `music_theory` for arrangement/harmony, or a custom
prompt for a targeted concern ("vocal harshness and mono compatibility"). Organize
notes by band — low end, vocal/midrange, high end (air/harshness), stereo image,
dynamics, concrete fixes — plus a **prioritized revision checklist**. The model is
a critique aid, not a replacement for an engineer's ears or metering.

### report
`full_report` runs all 13 presets in parallel — slower, more spend. Use only when
the user explicitly wants everything, never blindly across a catalog.

## Saving outputs

Inside an artist workspace, save durable results under `songs/{song-slug}/`:
`analysis/music-flamingo-full-report.json`, `analysis/metadata.json`,
`analysis/mix-feedback.md`, `lyrics/lyrics.md` (+ `lyrics/lyrics-review.md`).
No workspace → return the synthesis in the conversation.

## Guardrails

- **Public URL required.** No local file upload. Ask for a hosted `audio_url`.
- **Don't over-spend.** Reach for single presets before `full_report`.
- **No `account_id` in the request body.** Auth determines the account.
- **Drafts need review:** transcribed lyrics and detected samples are drafts; don't
  reproduce third-party copyrighted lyrics wholesale — summarize.

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, full preset
  table, REST/CLI/MCP call patterns, and gotchas.
