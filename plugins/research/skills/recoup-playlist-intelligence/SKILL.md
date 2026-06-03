---
name: recoup-playlist-intelligence
description: Playlist pitching intelligence, gap analysis, and catalog optimization via the Recoup research API. Use when asked about playlist placements, pitch targets, playlist gaps, which playlists an artist should be on, editorial vs algorithmic coverage, track-level playlist analysis, or catalog optimization ("which songs should we push"). Triggers on "playlist pitch", "playlist targets", "which playlists", "playlist gap", "editorial placements", "catalog optimization", "which songs should we push".
---

# Playlist Intelligence

Playlist pitching targets, gap analysis, and catalog optimization through the
Recoup research API. Turns raw playlist data into actionable pitch lists and
catalog strategy.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Decision tree

- **"Which playlists should we pitch?"** → Playlist Pitching Intelligence workflow
- **"Where are we playlisted?"** → `/research/playlists?artist={ARTIST}` → synthesize
- **"Playlist gap analysis"** → compare vs similar artists' placements
- **"Which songs should we push?"** → Catalog Optimization workflow
- **"Track-level playlist coverage"** → resolve track IDs → `/research/track/playlists`
- **"Re-pitch opportunities"** → `/research/playlists?artist={ARTIST}&status=past`

## Playlist Pitching Intelligence

Find the playlists your similar artists are on that you aren't.

```bash
# 1. Find similar artists (benchmarks slightly bigger than you)
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&genre=high&limit=50" \
  -H "x-api-key: $RECOUP_API_KEY"

# 2. For each similar artist, get their editorial playlist placements
curl -s "$RECOUP_API/research/playlists?artist={similar_artist}&editorial=true" \
  -H "x-api-key: $RECOUP_API_KEY"

# 3. Look for curator overlap — playlists adding multiple similar artists

# 4. For promising playlists, resolve Chartmetric IDs via search, then load detail
curl -s "$RECOUP_API/research?q={PLAYLIST_NAME}&type=playlists&beta=true" \
  -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/playlist?platform=spotify&id={cm_playlist_id}" \
  -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/curator?platform=spotify&id={cm_curator_id}" \
  -H "x-api-key: $RECOUP_API_KEY"

# 5. Check if the target artist was ever on these playlists before
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=past" \
  -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Curators who already playlist similar artists but haven't added
yours yet. Prioritize curators who've added 2+ similar artists — they're the
warmest targets.

## Catalog Optimization

Which songs should we push, and where?

```bash
# 1. All tracks
curl -s "$RECOUP_API/research/tracks?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 2. Current placements
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 3. Per-track playlist coverage (resolve CM track IDs first)
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks&beta=true" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/track/playlists?id={cm_track_id}&editorial=true" -H "x-api-key: $RECOUP_API_KEY"

# 4. Albums (needs Chartmetric artist ID)
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists&beta=true" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/albums?artist_id={cm_artist_id}" -H "x-api-key: $RECOUP_API_KEY"

# 5. Platform metrics for trend context
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Track-by-track analysis:
- High playlist reach but low streams = discovery issue (content isn't converting)
- Low playlist but high TikTok = pitch opportunity (organic momentum, needs editorial)
- Old songs suddenly getting playlisted = catalog momentum (amplify it)

## Critical gotchas — Playlists

- **Playlist filter flags are exclusive when set.** `?editorial=true` alone
  returns ONLY editorials, excluding indie / curator / popularIndie defaults.
  To get editorial *plus* the rest, pass all four:
  `&editorial=true&indie=true&majorCurator=true&popularIndie=true`.
- **`/research/playlists` (artist-level) ignores `offset`** — single 100-max
  snapshot. For bulk, page `/research/track/playlists?id=...&offset=...` per
  track instead (that one *does* paginate).
- **Hard cap: `limit=100`** on both playlist endpoints. `150`+ → 400.
- **`/research/profile` aggregate counts are inside `cm_statistics`** (e.g.
  `cm_statistics.num_sp_playlists`, NOT top-level). Use them for magnitude
  and `cm_statistics.sp_playlist_total_reach` for true reach.
- **`placements[].playlist.followers` is often `0`** — use `peak_position` or
  `/research/playlist?platform=spotify&id=` for true reach.
- **Past placements (`status=past`) that dropped off = re-pitch opportunities.**

## Interpretation rules

- 2 editorial playlists for 5M+ listeners = severely under-playlisted (pitch immediately)
- Past placements that dropped off = re-pitch candidates
- Playlists adding multiple peers = warmest pitch targets
- `cm_statistics.sp_playlist_total_reach` from profile gives the magnitude — detail endpoints give the sample

## Output format

Produce a ranked pitch list:

| Playlist | Followers | Curator | Peers On It | Artist Status | Priority |
|----------|-----------|---------|-------------|---------------|----------|
| R&B Rotation | 450K | Spotify Editorial | 5/10 peers | Never on | 🔴 High |
| Chill Vibes | 200K | @vibes_curator | 3/10 peers | Past (dropped 3mo ago) | 🟡 Re-pitch |

## References

- **[references/endpoints.md](../../references/endpoints.md)** — full playlist filter/pagination semantics
- **[references/response-shapes.md](../../references/response-shapes.md)** — placement JSON structure
- **[references/workflows.md](../../references/workflows.md)** — Workflow 1 (Playlist Pitching) and Workflow 5 (Catalog Optimization)
