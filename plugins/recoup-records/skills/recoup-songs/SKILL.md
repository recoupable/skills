---
name: recoup-songs
description: Understand and work with ONE song from its AUDIO file, using Recoup's audio language model (Music Flamingo) — it listens to the recording itself. Modes — analyze (full report, catalog metadata BPM/key/genre/mood, lyric sheet, or mix critique), hook (find the most clip-worthy 5–15s moment to lead short-form with), and pitch (playlist/editorial pitch + music-supervisor sync brief). Use for "analyze this song", "what key/BPM/genre is this", "tag this track", "transcribe the lyrics", "critique the mix", "find the hook", "best 15 seconds to clip", "write a playlist pitch", or "make a sync brief". Requires a public audio URL — it analyzes the recording itself. For desk/web research ABOUT a song (why it went viral, news, with citations — no audio) or catalog-wide playlist strategy, use recoup-research; for catalog valuation use recoup-catalogs.
---

# Recoup Song

Everything you can learn or make from a single song's **audio**, via Music
Flamingo (Recoup's audio language model). It **picks a mode from the ask** — a
transcript alone can't tell you where the energy peaks or how the mix sits;
Flamingo's structure/energy/timbre output is what makes these modes work.

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md` — read it before calling. All modes
need a **public `audio_url`** (no local file upload) and never put `account_id`
in the body.

## Mode dispatch

| The user wants… | Mode | Core presets |
|---|---|---|
| "analyze this song", "what does it sound like", "key/BPM/genre/mood", "tag it", "transcribe lyrics", "critique the mix" | **analyze** | `music_theory`, `lyric_transcription`, `mix_feedback`, full report |
| "find the hook", "best 15 seconds", "what to clip", "where's the drop" | **hook** | `sync_brief_match` + `music_theory` + `lyric_transcription` |
| "playlist pitch", "pitch to Spotify", "sync brief", "where could this be placed" | **pitch** | `sync_brief_match`, `music_theory`, `lyric_transcription` |

## Mode: analyze

Understand the track. Sub-outputs (pick by ask, or give the full report):

- **Full report** — what it sounds like, references, standout qualities.
- **Catalog metadata** — BPM, key, genre, mood/energy (for tagging/registration).
- **Lyric sheet** — sectioned transcription (`lyric_transcription`).
- **Mix critique** — technical feedback on the mix/master (`mix_feedback`).

Run the presets the ask needs; synthesize a clean report (not raw JSON). In an
artist workspace, save to `songs/{song-slug}/analysis/`.

## Mode: hook

Find the moments most likely to stop the scroll, for short-form. Run
`sync_brief_match` (energy curve + timestamped moments) + `music_theory` (so a
window snaps to a real section boundary, not an arbitrary cut) +
`lyric_transcription` (the quotable line). Align the highest-energy moments with
section starts and a memorable line — the best hook is where **energy + section
change + a quotable line** coincide. Return **3 ranked windows**, each with
`start`–`end` (target 5–15s; ≈7s if it must loop), the moment type
(drop/chorus/beat-switch/peak), the quotable line, and one line on why it stops
the scroll. Timestamps come from the analysis, not vibes — they feed real edits;
hand them to `recoup-content` (video) to build the clip. Save to
`songs/{song-slug}/analysis/hooks.md`.

## Mode: pitch

Turn the song into placement materials:

- **Playlist/editorial pitch** — a tight pitch matched to playlist/editorial
  fit, grounded in the song's actual sound (genre/mood/energy from the analysis).
- **Sync brief** — a music-supervisor-ready brief (mood, themes, instrumentation,
  comparable cues, clearance-relevant notes) for TV/film/ad placement.

Use `sync_brief_match` + `music_theory` + `lyric_transcription`; ground every
claim in the audio analysis, never invent. Save to `songs/{song-slug}/pitch/`.
For catalog-wide playlist *strategy* (which playlists, gaps — no single audio
file) use `recoup-research` (playlists) instead.

## Guardrails

- **Audio-grounded only** — every claim (BPM, mood, mix note, hook) comes from the
  Flamingo analysis; never guess from the title or vibes.
- **Public URL required**; no local upload; no `account_id` in the body.
- **Hook windows are 5–15s** — a 40s "hook" isn't a hook.
- **Lyrics:** transcribe the artist's own song; don't reproduce third-party
  copyrighted lyrics elsewhere.

## References

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas. Ships alongside this skill.
