---
name: recoup-compare
description: Head-to-head artist comparison across streaming, playlists, audience, geography, and career stage.
---

# /recoup-compare [artist A] vs [artist B]

Compare two artists side-by-side across every dimension.

## What it does

1. Runs a full research sweep on both artists in parallel
2. Builds a comparison table: streaming, playlist reach, audience demographics,
   geographic strength, career stage, and momentum
3. Identifies where each artist under-indexes vs the other
4. Produces a strategic summary with actionable gaps

## Usage

```
/recoup-compare "Drake" vs "Kendrick Lamar"
/recoup-compare "Joy Crookes" vs "Jorja Smith"
```

## Skills used

- `recoup-competitive-analysis` (primary)
- `recoup-artist-research` (for each artist's data)

## Output

A comparison table:

| Dimension | Artist A | Artist B | Gap |
|-----------|----------|----------|-----|
| Spotify Listeners | 5.2M | 8.1M | A under-indexes by 36% |
| Editorial Playlists | 12 | 8 | B under-indexes |
| Top City | London | London | Same market |
| Career Stage | mid-level | mainstream | A has breakout potential |
| TikTok Followers | 200K | 1.2M | A severely under-indexes |

Plus a strategic narrative: what each artist should learn from the other, and
where the real competitive advantages lie.

## Options

- `--deep` — also run web research for cultural context
- `--roster` — compare entire rosters (pass multiple artists per side)
