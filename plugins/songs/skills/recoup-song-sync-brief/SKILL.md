---
name: recoup-song-sync-brief
description: Turn a song's audio into a music-supervisor-ready sync brief using Recoup's audio language model (Music Flamingo). Use when asked to "make a sync brief", "where could this song be placed", "is this brand safe for sync", "find scenes this track fits", or "audit this for licensing risks". Needs a public audio URL.
---

# Song Sync Brief Maker (Music Flamingo)

Produce a sync brief a music supervisor can act on: scene fit, emotional arc,
brand-safety notes, and sample/interpolation risk.

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md`. Read it before calling.

## When to use

- "Make a sync brief" / "where could this be placed?"
- "Is this brand safe for sync?"
- "Audit this for licensing/sample risk"

For a DSP/playlist pitch instead, use `recoup-song-playlist-pitch`.

## Preset chain

- **Required:** `sync_brief_match`
- **Usually add:** `content_advisory`, `sample_detection`, `mood_tags`
- **Optional:** `music_theory`, `song_description`

## Steps

1. Resolve a **public `audio_url`** (no local file upload).
2. Call `sync_brief_match`; add `content_advisory` and `sample_detection` for
   brand-safety and clearance risk.
3. Assemble the brief below.

## Output

- Visual placement ideas with scene types.
- Emotional arc / energy curve and timestamped sync moments.
- Brand-safety notes and avoid-for contexts.
- Sample / interpolation risk notes **with confidence levels**.
- Supervisor search tags.

If inside an artist workspace, save to `songs/{song-slug}/analysis/sync-brief.md`.

## Guardrails

- **Sample detection is a flag, not a clearance.** Present it as a risk signal
  with confidence; recommend a real rights check before pitching for sync.
- Keep brand-safety calls conservative; note what you are unsure about.
- **Public URL required**; no local file upload. **No `account_id` in the body.**

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas.
