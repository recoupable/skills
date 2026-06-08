---
name: recoup-research
description: One-command full artist research sweep. Runs profile, metrics, audience, playlists, similar artists, and insights, then synthesizes into an executive brief.
---

# /recoup-research [artist name or URL]

Run a complete research sweep on an artist and produce a synthesized brief.

## What it does

1. Resolves the artist (name, or a Spotify URL/ID via `/research/lookup`)
2. Pulls profile, Spotify + TikTok metrics, audience demographics + geography,
   similar artists, playlist placements, and AI insights — in parallel
3. Synthesizes everything into an executive brief with recommendations
4. Saves the brief to the artist workspace if one exists

## Usage

```
/recoup-research Drake
/recoup-research https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4
/recoup-research "Joy Crookes"
```

## Skills used

- `recoup-artist-research` (primary)
- `recoup-web-intelligence` (fallback if structured provider data unavailable)

## Output

A structured artist brief covering:
- Streaming snapshot (Spotify, TikTok, Instagram, YouTube)
- Geographic strength (audience country breakdown)
- Audience demographics
- Playlist position and reach
- Competitive positioning (peer landscape, sized via metrics snapshots)
- Key insights and recommendations

## Options

- Add `--deep` to also run a web deep research pass for cultural context
- Add `--save` to force-save to artist workspace even without an existing one
