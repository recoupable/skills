---
name: recoup-scout
description: A&R discovery and emerging artist scouting. Find emerging artists by genre, growth velocity, and platform momentum.
---

# /recoup-scout [genre or anchor artist] [options]

Find emerging artists before they blow up.

## What it does

1. Either discovers by genre + growth filters, or starts from an anchor artist
   and finds similar emerging ones
2. Validates each candidate's cross-platform trajectory (Spotify + TikTok)
3. Checks editorial playlist pickup as a label interest signal
4. Pulls AI insights for each promising candidate
5. Ranks by growth velocity and produces a scouting report

## Usage

```
/recoup-scout hip-hop --country US --listeners 50000-200000
/recoup-scout "Sabrina Carpenter" --find-similar --emerging-only
/recoup-scout R&B --tiktok-first
```

## Skills used

- `recoup-trend-detection` (primary)
- `recoup-artist-research` (for deep dives on top candidates)
- `recoup-web-intelligence` (cultural context for breakout candidates)

## Output

A ranked scouting report:

| Artist | Listeners | Growth (7d) | TikTok | Editorial | Career Stage | Signal |
|--------|-----------|-------------|--------|-----------|--------------|--------|
| ... | ... | +12% | 450K | 2 playlists | developing | 🔥 |

## Options

- `--country XX` — filter by country (2-letter code)
- `--listeners MIN-MAX` — Spotify monthly listener range
- `--tiktok-first` — sort by TikTok growth velocity
- `--find-similar` — use first argument as anchor artist, find similar emerging
- `--emerging-only` — filter to career_stage = undiscovered or developing
- `--limit N` — number of candidates to evaluate (default 20)
