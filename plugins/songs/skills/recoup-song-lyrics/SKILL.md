---
name: recoup-song-lyrics
description: Transcribe a song's lyrics from its audio into a sectioned lyric sheet using Recoup's audio language model (Music Flamingo). Use when asked to "transcribe the lyrics", "get the lyrics from this song", "make a lyric sheet", "write out the words", "find explicit lines", or "make a clean/radio lyric reference". Needs a public audio URL. Output is a draft for human review.
---

# Song Lyrics Transcriber (Music Flamingo)

Turn a song's audio into a draft lyric sheet with section headers
(`[Verse]`, `[Chorus]`, `[Bridge]`, …).

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md`. Read it before calling.

## When to use

- "Transcribe the lyrics" / "get the words"
- "Make a lyric sheet"
- "Find the explicit lines" / "make a clean/radio reference"

For full catalog metadata, use `recoup-song-metadata`.

## Preset chain

- **Required:** `lyric_transcription`
- **Usually add:** `content_advisory` when the user asks about explicit content,
  brand safety, clean edits, or radio readiness
- **Optional:** `song_description` or a custom prompt for lyrical themes / hook /
  story interpretation

## Steps

1. Resolve a **public `audio_url`** (no local file upload).
2. Call `lyric_transcription`. Add `content_advisory` if the user cares about
   explicit/brand-safety/radio.
3. Format the lyrics with section headers into `lyrics.md`.
4. Surface uncertain lines and any explicit terms for review.

## Output

- `lyrics.md` — lyrics with `[Verse]` / `[Chorus]` / `[Bridge]` headers.
- `lyrics-review.md` *(optional)* — uncertain lines, explicit terms, manual
  verification notes.
- `content_advisory.json` *(optional)* — profanity / theme / radio-friendliness
  fields.

If inside an artist workspace, save under `songs/{song-slug}/lyrics/`.

## Guardrails

- **Draft, not final.** Treat the transcription as a draft — require human review
  before publishing, registering, distributing, or sending to DSPs.
- **Preserve uncertainty.** Mark unclear audio as `[inaudible]` or
  `[unclear: …]`. Do not invent lines to make the sheet feel complete.
- **Copyright.** Do not reproduce third-party copyrighted lyrics unless the user
  owns or supplied the song. For reference tracks, summarize instead of quoting.
- **Public URL required**; no local file upload. **No `account_id` in the body.**

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas.
