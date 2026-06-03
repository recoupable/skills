---
name: recoup-song-playlist-pitch-maker
description: Turn a song's audio into playlist and editorial pitch materials using Recoup's audio language model (Music Flamingo). Use when asked to "write a playlist pitch", "pitch this to Spotify", "what playlists does this fit", "make a DSP pitch from this audio", or "give me positioning for this single". Needs a public audio URL.
---

# Song Playlist Pitch Maker (Music Flamingo)

Convert a track into a Spotify/editorial pitch plus the positioning notes a team
needs to place it.

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md`. Read it before calling.

## When to use

- "Write a playlist pitch" / "pitch this to Spotify"
- "What playlists does this fit?"
- "Give me positioning for this single"

For a sync/licensing brief instead, use `recoup-song-sync-brief-maker`.

## Preset chain

- **Required:** `playlist_pitch`
- **Usually add:** `song_description`, `audience_profile`, `similar_artists`,
  `mood_tags`
- **Optional:** `catalog_metadata` for factual grounding (genre/BPM/key)

## Steps

1. Resolve a **public `audio_url`** (no local file upload).
2. Call `playlist_pitch`; add the supporting presets the pitch needs.
3. Assemble a short editorial pitch plus an internal rationale.

## Output

- A Spotify/editorial pitch **under 500 characters** (the editorial submission
  limit) plus a longer internal rationale.
- Suggested playlist lanes and comparable tracks.
- Marketing hook and a one-paragraph audience note.

If inside an artist workspace, save to `songs/{song-slug}/analysis/playlist-pitch.md`
and surface suggested updates to the release doc's narrative, marketing, and DSP
sections rather than editing them silently.

## Guardrails

- Keep the editorial pitch tight and specific; lead with why it fits the lane.
- Ground claims in the audio analysis — don't invent stats or placements.
- **Public URL required**; no local file upload. **No `account_id` in the body.**

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas.
