---
name: recoup-song-analyzer
description: Analyze a song, track, or audio file with Recoup's audio language model (Music Flamingo). Use when asked to "analyze this song", "what does this track sound like", "run Music Flamingo", "use the audio model", "get a full report on this audio", "what key/BPM/mood/genre is this", "transcribe the lyrics", or any request to understand a piece of audio from its sound. This is the default entry point for audio analysis — it resolves the audio URL, picks the right preset, calls the endpoint, and routes to focused workflows (metadata, lyrics, playlist pitch, sync brief, mix feedback) when the ask is specific.
---

# Song Analyzer (Music Flamingo)

Turn a song's **audio** into structured intelligence — genre, key, BPM, mood,
lyrics, mix notes, sync fit, audience, and more — using Recoup's audio language
model. This is the entry point for "analyze this track" requests.

The endpoint contract (auth, base URL, request/response, every preset, call
patterns, gotchas) lives in `references/flamingo-api.md`. Read it before calling.

## Decision tree

Match the user's ask to the smallest useful action:

- **"Analyze / what does this sound like / give me a full report"** → run the
  analysis below. Use `full_report` only when they want everything.
- **"What key / BPM / genre / mood is this?"** → single preset `catalog_metadata`
  (add `music_theory` for chords/sections).
- **"Tag this / catalog metadata / searchable metadata"** → hand off to
  `recoup-song-metadata`.
- **"Transcribe the lyrics / get the words / lyric sheet"** → hand off to
  `recoup-song-lyrics`.
- **"Playlist pitch / pitch to Spotify / what playlists fit"** → hand off to
  `recoup-song-playlist-pitch`.
- **"Sync brief / where could this be placed / brand safe for sync"** → hand off
  to `recoup-song-sync-brief`.
- **"Critique the mix / mix notes / what should I fix"** → hand off to
  `recoup-song-mix-feedback`.
- **"Find the hook / best 15 seconds / what to clip / where's the drop"** → hand
  off to `recoup-song-hook`.

Each `recoup-song-*` skill is self-contained — if one is installed, prefer it for
its job. If only this skill is present, run the relevant preset directly.

## Steps

1. **Resolve the audio input.** The endpoint needs a **public `audio_url`** — it
   cannot take a local file. If the user gives a URL (or a Recoup/chat attachment
   URL), use it. If they only have a local file, explain the URL requirement and
   ask for a hosted link rather than pretending the file can be sent.
2. **Choose the smallest useful preset.** Do not default to `full_report`. Pick
   the one preset (or short chain) that answers the question. See the preset table
   in `references/flamingo-api.md`. When unsure which preset fits, list them with
   `GET /api/songs/analyze/presets`.
3. **Call the endpoint.** Prefer REST (works with the sandbox bearer token or an
   API key); use MCP `analyze_music` if the host exposes it; use the `recoup`
   CLI only when `RECOUP_API_KEY` is set. Exact commands are in
   `references/flamingo-api.md`.
4. **Interpret the result.** Summarize what matters for the user's goal — do not
   dump raw JSON at them.
5. **Persist if in a workspace** (see below).

## Choosing presets

| User wants | Preset(s) |
|---|---|
| Genre / mood / BPM / key / instruments | `catalog_metadata` |
| Vibe tags only | `mood_tags` |
| Chords, scale, sections | `music_theory` |
| Lyrics | `lyric_transcription` |
| Explicit / brand-safety / radio check | `content_advisory` |
| Marketing blurb | `song_description` |
| Comparable artists | `similar_artists` |
| Sample/interpolation risk | `sample_detection` |
| Best moment to clip for short-form | `sync_brief_match` + `music_theory` (or `recoup-song-hook`) |
| Everything | `full_report` (13 presets in parallel — slower, more spend) |

## Saving outputs

If you are inside an artist workspace, save durable results under
`songs/{song-slug}/analysis/`:

- `music-flamingo-full-report.json` — raw `full_report` output
- `{preset}.json` or `{preset}.md` — targeted preset output
- `analysis-summary.md` — your human-readable synthesis

If there is no workspace, just return the synthesis in the conversation.

## Guardrails

- **Public URL required.** No local file upload. Ask for a hosted `audio_url`.
- **Don't over-spend.** `full_report` runs 13 model calls; reach for single
  presets first.
- **No `account_id` in the request body.** Auth determines the account.
- **Reference tracks:** you may analyze audio the user supplies, but treat
  transcribed lyrics and detected samples as drafts needing human verification,
  and don't reproduce third-party copyrighted lyrics wholesale — summarize.

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, full preset
  table, REST/CLI/MCP call patterns, and gotchas.
