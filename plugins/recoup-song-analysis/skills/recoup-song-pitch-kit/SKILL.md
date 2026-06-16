---
name: recoup-song-pitch-kit
description: Turn ONE song's audio into placement materials using Recoup's audio language model (Music Flamingo) — a playlist/editorial pitch and a music-supervisor sync brief. Use when asked to "write a playlist pitch for this single", "pitch this song to Spotify", "make a sync brief", "where could this be placed", or "is this brand safe for sync". Works from one audio file and produces the materials; it does not contact anyone or choose targets across a catalog (for catalog-wide playlist targeting from research data, use recoup-artist-playlists). For the clip-worthy hook use recoup-song-hook; to understand the audio use recoup-song-analyze. Needs a public audio URL.
---

# Song Pitch Kit (Music Flamingo)

Produce the **materials** a team uses to place a track: a playlist/editorial
pitch and a music-supervisor sync brief. This skill drafts the documents — it
does not send them or contact editors/supervisors. For the clip-worthy hook, use
`recoup-song-hook`; to understand the audio itself, use `recoup-song-analyze`.

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md`. Read it before calling.

## What you can ask for (modes)

| Ask | Mode | Lead preset(s) |
|---|---|---|
| "Playlist pitch / pitch to Spotify / what playlists fit" | **playlist** | `playlist_pitch` (+ `song_description`, `audience_profile`, `similar_artists`, `mood_tags`) |
| "Sync brief / where could this be placed / brand safe for sync" | **sync** | `sync_brief_match` (+ `content_advisory`, `sample_detection`, `mood_tags`) |

## Steps

1. Resolve a **public `audio_url`** (no local file upload).
2. Call the mode's lead preset; add the supporting presets it needs.
3. Assemble the output (below). Persist under `songs/{song-slug}/analysis/` if in a workspace.

## Mode details

### playlist
Assemble a Spotify/editorial pitch **under 500 characters** (the submission limit)
plus a longer internal rationale, suggested playlist lanes, comparable tracks, a
marketing hook, and a one-paragraph audience note. Lead with why it fits the lane;
ground every claim in the audio analysis — don't invent stats or placements. Save
to `playlist-pitch.md`; surface suggested release-doc narrative/marketing/DSP
updates rather than editing silently.

### sync
Produce a brief a supervisor can act on: visual placement ideas with scene types,
emotional arc / energy curve with timestamped sync moments, brand-safety notes and
avoid-for contexts, sample/interpolation risk **with confidence levels**, and
supervisor search tags. Save to `sync-brief.md`. **Sample detection is a flag, not
a clearance** — present it as a risk signal and recommend a real rights check; keep
brand-safety calls conservative and note what you're unsure about.

## Guardrails

- **Public URL required.** No local file upload. **No `account_id` in the body.**
- **Ground everything in the analysis** — these feed real submissions; don't invent
  stats, placements, or clearances.

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas.
