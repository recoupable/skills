---
name: recoup-song-analyze-audio
description: Understand one song from its audio using Recoup's audio model (Music Flamingo) — full report, catalog metadata (BPM/key/genre/mood), a sectioned lyric sheet, or a mix critique. Use for "analyze this song", "what key/BPM/genre is this", "tag this track", "transcribe the lyrics", or "critique the mix". Requires a public audio URL. To find the clip-worthy moment use recoup-song-find-hook; for placement materials use recoup-song-placement-pitch.
---

# Recoup Song — Analyze Audio

Everything you can learn from a single song's **audio**, via Music Flamingo. The
endpoint contract (auth, base URL, request/response, presets, gotchas) is in
`references/flamingo-api.md` — read it before calling. Needs a **public `audio_url`**
(no local upload); never put `account_id` in the body.

## Sub-outputs (pick by ask, or give the full report)

- **Full report** — what it sounds like, references, standout qualities.
- **Catalog metadata** — BPM, key, genre, mood/energy (`catalog_metadata`,
  `music_theory`) for tagging/registration.
- **Lyric sheet** — sectioned transcription (`lyric_transcription`).
- **Mix critique** — technical feedback on the mix/master (`mix_feedback`).

Run the presets the ask needs; synthesize a clean report (not raw JSON). In an
artist workspace, save to `songs/{song-slug}/analysis/`.

## Guardrails

- **Audio-grounded only** — every claim (BPM, mood, mix note) comes from the
  Flamingo analysis; never guess from the title or vibes.
- **Public URL required**; no local upload; no `account_id` in the body.
- **Lyrics:** transcribe the artist's own song; don't reproduce third-party lyrics.

## References

- `references/flamingo-api.md` — auth, base URL, request/response, preset table.
