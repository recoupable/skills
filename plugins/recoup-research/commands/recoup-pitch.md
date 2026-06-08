---
name: recoup-pitch
description: Generate playlist pitch targets for an artist. Finds playlists that similar artists are on but the target artist isn't.
---

# /recoup-pitch [artist name]

Find the best playlist pitch targets for an artist.

## What it does

1. Finds similar artists slightly bigger than the target (good benchmarks)
2. Pulls editorial playlist placements for each similar artist
3. Identifies playlists that multiple peers share but the target artist is missing
4. Checks for past placements that dropped off (re-pitch opportunities)
5. Resolves curator details for top targets
6. Produces a ranked pitch list

## Usage

```
/recoup-pitch "Joy Crookes"
/recoup-pitch Drake --editorial-only
/recoup-pitch "Artist Name" --include-repitch
```

## Skills used

- `recoup-playlist-intelligence` (primary)
- `recoup-artist-research` (for initial artist context)
- `recoup-competitive-analysis` (for peer identification)

## Output

A ranked pitch list:

| Playlist | Followers | Curator | Peers On It | Artist Status | Priority |
|----------|-----------|---------|-------------|---------------|----------|
| R&B Rotation | 450K | Spotify Editorial | 5/10 | Never on | 🔴 High |
| Chill Vibes | 200K | @curator | 3/10 | Dropped 3mo ago | 🟡 Re-pitch |

Plus a recommended pitch order and timing notes.

## Options

- `--editorial-only` — focus on editorial playlists only
- `--include-repitch` — include past placements as re-pitch targets
- `--peers N` — number of similar artists to analyze (default 20)
