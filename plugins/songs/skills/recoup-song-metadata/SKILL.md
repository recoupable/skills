---
name: recoup-song-metadata
description: Turn a song's audio into structured catalog metadata using Recoup's audio language model (Music Flamingo). Use when asked to "tag this song", "generate catalog metadata", "get BPM/key/genre/mood", "create searchable metadata", "fill release metadata from audio", or to enrich a track or small catalog for DSPs, catalog systems, and release docs. Needs a public audio URL.
---

# Song Metadata Tagger (Music Flamingo)

Convert raw audio into clean, structured metadata you can drop into a catalog
system, DSP delivery, search index, or release doc.

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md`. Read it before calling.

## When to use

- "Tag this song" / "generate metadata"
- "What's the BPM, key, genre, mood?"
- "Make searchable metadata for these tracks"
- "Fill release metadata from the audio"

For lyrics specifically, use `recoup-song-lyrics`. For a playlist
pitch, use `recoup-song-playlist-pitch`.

## Preset chain

- **Required:** `catalog_metadata` (genre, mood, BPM, key, instruments, vocals,
  energy, danceability, similar artists, one-line description)
- **Usually add:** `mood_tags`, `music_theory`, `content_advisory`
- **Optional:** `lyric_transcription` when the user wants lyrics in the metadata

Run only what the user needs — each preset is a separate model call.

## Steps

1. Resolve a **public `audio_url`** (the endpoint cannot take a local file).
2. Call `catalog_metadata` first; add the optional presets only if asked.
3. Normalize into one `metadata.json` object (see shape below).
4. Summarize the key fields for the user; persist the JSON if in a workspace.

## Output

`metadata.json` — a single normalized object:

```json
{
  "genre": "",
  "subgenres": [],
  "primary_mood": "",
  "mood_tags": [],
  "bpm": 0,
  "key": "",
  "time_signature": "",
  "energy": "",
  "danceability": "",
  "instruments": [],
  "vocals": "",
  "similar_artists": [],
  "content_rating": "",
  "one_line_description": ""
}
```

If inside an artist workspace, save to `songs/{song-slug}/analysis/metadata.json`,
and `lyrics.md` when transcription was requested. Surface suggested updates to a
release doc's identifiers/metadata, narrative, and DSP sections rather than
editing those files silently.

## Guardrails

- **Public URL required**; no local file upload.
- **No `account_id` in the request body.**
- Treat model output as a strong draft — confirm BPM/key against a detector if
  the value drives a creative or contractual decision.

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas.
