---
name: recoup-artist-playlists
description: Playlist strategy for an artist across their whole catalog, from Recoup research data (not a single audio file) — which playlists to target, placement gaps, editorial vs algorithmic coverage, track-level analysis, and which catalog songs to push. Use when asked "which playlists should this artist be on", "playlist targets", "playlist gaps", "editorial placements", "catalog optimization", or "which songs should we push". For a pitch built from ONE song's audio, use recoup-song-pitch-kit instead.
---

# Playlist Intelligence

Playlist pitching targets, gap analysis, and catalog optimization through the
Recoup research API. Turns raw playlist data into actionable pitch lists and
catalog strategy. The API is backed by **Songstats** — IDs are short
alphanumeric strings, not numeric Chartmetric IDs.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Decision tree

- **"Which playlists should we pitch?"** → Playlist Pitching Intelligence workflow
- **"Where are we playlisted?"** → `/research/playlists?artist={ARTIST}&status=current` → synthesize
- **"Playlist gap analysis"** → compare vs similar artists' placements
- **"Which songs should we push?"** → Catalog Optimization workflow
- **"Track-level / editorial playlist coverage"** → resolve track ID → `/research/track/playlists`
- **"Re-pitch opportunities"** → `/research/playlists?artist={ARTIST}&status=past`

## Playlist Pitching Intelligence

Find the playlists your similar artists are on that you aren't.

```bash
# 1. Find similar artists (benchmarks slightly bigger than you)
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&genre=high&limit=50" \
  -H "x-api-key: $RECOUP_API_KEY"

# 2. For each similar artist, get their current playlist placements
curl -s "$RECOUP_API/research/playlists?artist={similar_artist}&platform=spotify&status=current" \
  -H "x-api-key: $RECOUP_API_KEY"

# 3. Look for overlap — playlists hosting multiple similar artists

# 4. For per-track editorial detail, resolve a track id, then page the track-level endpoint
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks" \
  -H "x-api-key: $RECOUP_API_KEY"                                  # get track id
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&editorial=true&indie=true&majorCurator=true&popularIndie=true" \
  -H "x-api-key: $RECOUP_API_KEY"

# 5. Check if the target artist was ever on these playlists before
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=past" \
  -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Playlists that already host similar artists but haven't added
yours yet. Prioritize playlists hosting 2+ similar artists — they're the warmest
targets.

## Catalog Optimization

Which songs should we push, and where?

```bash
# 1. All tracks
curl -s "$RECOUP_API/research/tracks?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 2. Current placements
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=current" -H "x-api-key: $RECOUP_API_KEY"

# 3. Per-track playlist coverage (resolve track ID first; 5 credits)
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&editorial=true&indie=true&majorCurator=true&popularIndie=true" -H "x-api-key: $RECOUP_API_KEY"

# 4. Albums (needs the provider artist ID — resolve via search)
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists" -H "x-api-key: $RECOUP_API_KEY"   # get id
curl -s "$RECOUP_API/research/albums?artist_id={artist_id}" -H "x-api-key: $RECOUP_API_KEY"

# 5. Track detail (genres, audio analysis) for sound fit + metrics for trend context
curl -s "$RECOUP_API/research/track?id={track_id}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Track-by-track analysis:
- Tracks on many playlists but not converting to streams = discovery issue
- Tracks with strong audio-analysis fit for a target playlist = pitch candidates
- Old songs suddenly getting playlisted (from `/milestones`) = catalog momentum

## Critical gotchas — Playlists

- **Two different playlist endpoints.** `/research/playlists` is **artist-level**
  (`status` + `platform` + `limit` only — no editorial/indie filter flags).
  `/research/track/playlists` is **track-level** and is the one with filter flags.
- **Track-level filter flags are exclusive when set.** On `/research/track/playlists`,
  `?editorial=true` alone returns ONLY editorials. To get editorial *plus* the
  defaults, pass all four:
  `&editorial=true&indie=true&majorCurator=true&popularIndie=true`. With no flags
  it defaults to `editorial + indie + majorCurator + popularIndie`.
- **`placements[].followers_total` is a formatted string** (`"34.3M"`) on
  artist-level placements, not an integer. Parse it if you need to sort numerically.
  There is no `peak_position` or nested `playlist`/`track` wrapper anymore.
- **For editorial magnitude, read `playlists_editorial_current` from
  `/research/metrics?source=spotify`** — that's the aggregate count.
- **No `/research/playlist` (singular) or `/research/curator` detail endpoint.**
  Use the `external_url` on each placement to open the playlist directly.
- **Past placements (`status=past`) that dropped off = re-pitch opportunities.**

## Interpretation rules

- Low `playlists_editorial_current` (from /metrics) for an artist with millions of listeners = severely under-playlisted (pitch immediately)
- Past placements that dropped off = re-pitch candidates
- Playlists hosting multiple peers = warmest pitch targets
- `playlist_reach_current` from `/metrics` gives the magnitude; `/playlists` gives the sampled list

## Output format

Produce a ranked pitch list:

| Playlist | Followers | Peers On It | Artist Status | Priority |
|----------|-----------|-------------|---------------|----------|
| RapCaviar | 15.7M | 5/10 peers | Never on | 🔴 High |
| Chill Vibes | 200K | 3/10 peers | Past (dropped 3mo ago) | 🟡 Re-pitch |

(Curator names aren't returned by the API anymore — link the playlist via its
`external_url` instead.)

## References

- **`references/endpoints.md`** — full playlist filter/pagination semantics
- **`references/response-shapes.md`** — placement JSON structure
- **`references/workflows.md`** — Workflow 1 (Playlist Pitching) and Workflow 5 (Catalog Optimization)
