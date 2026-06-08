---
name: recoup-scout
description: A&R discovery and emerging artist scouting. Find emerging artists by starting from an anchor artist or genre scene, then validating cross-platform momentum.
---

# /recoup-scout [anchor artist or genre] [options]

Find emerging artists before they blow up.

## What it does

1. Starts from an **anchor artist** (or surfaces candidate names from web
   research for a genre/scene) — there is no server-side genre/growth discovery
   endpoint anymore
2. Fans out to similar artists weighted by `musicality`/`genre`
3. Validates each candidate's cross-platform position (Spotify + TikTok metrics
   snapshots) and filters by listener range **client-side**
4. Checks editorial playlist pickup as a label-interest signal
5. Pulls AI insights for each promising candidate
6. Ranks candidates and produces a scouting report

## Usage

```
/recoup-scout "Sabrina Carpenter" --find-similar --listeners 50000-200000
/recoup-scout R&B --country US        # web-sourced candidate names, then validate
/recoup-scout "PinkPantheress" --tiktok-first
```

## Skills used

- `recoup-trend-detection` (primary)
- `recoup-artist-research` (for deep dives on top candidates)
- `recoup-web-intelligence` (candidate sourcing + cultural context)

## Output

A ranked scouting report (metrics are current snapshots, not 7-day growth —
the API does not expose time-series velocity):

| Artist | Monthly listeners | Popularity | TikTok followers | Editorial playlists | Signal |
|--------|-------------------|------------|------------------|---------------------|--------|
| ... | 120K | 58 | 450K | 2 | 🔥 |

## Options

- `--country XX` — bias web-sourced candidate search by country (2-letter code)
- `--listeners MIN-MAX` — Spotify monthly listener range (applied client-side to the metrics snapshot)
- `--tiktok-first` — sort by TikTok follower scale
- `--find-similar` — use the first argument as the anchor artist, fan out via `/research/similar`
- `--limit N` — number of candidates to evaluate (default 20)

> Removed: there is no `--emerging-only`/`career_stage` filter — rank candidates
> by their `/research/metrics` snapshot (lower listeners + rising editorial
> pickup = the breakout window).
