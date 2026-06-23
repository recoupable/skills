---
name: recoup-song-placement-pitch
description: Turn one song into placement materials from its audio — a playlist/editorial pitch and a music-supervisor sync brief, grounded in the song's actual sound. Use for "playlist pitch", "pitch to Spotify", "sync brief", or "where could this be placed". Requires a public audio URL. For catalog-wide playlist strategy (no audio) use recoup-research-playlist-targets.
---

# Recoup Song — Placement Pitch

Turn the song into placement materials. Uses Music Flamingo — contract in
`references/flamingo-api.md` (read first). Needs a **public `audio_url`**; never put
`account_id` in the body.

## Outputs

- **Playlist/editorial pitch** — a tight pitch matched to playlist/editorial fit,
  grounded in the song's actual sound (genre/mood/energy from the analysis).
- **Sync brief** — a music-supervisor-ready brief (mood, themes, instrumentation,
  comparable cues, clearance-relevant notes) for TV/film/ad placement.

Use `sync_brief_match` + `music_theory` + `lyric_transcription`; ground every claim
in the audio analysis, never invent. Save to `songs/{song-slug}/pitch/`.

For catalog-wide playlist *strategy* (which playlists, gaps — no single audio file)
use recoup-research-playlist-targets instead.

## Guardrails

- **Audio-grounded only** — every claim traces to the Flamingo analysis.
- **Public URL required**; no `account_id` in the body.
- **Lyrics:** don't reproduce third-party copyrighted lyrics.

## References

- `references/flamingo-api.md` — presets + call patterns.
