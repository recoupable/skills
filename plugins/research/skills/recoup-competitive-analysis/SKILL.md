---
name: recoup-competitive-analysis
description: Competitive roster analysis, career positioning, collaboration finding, and release strategy timing via the Recoup research API. Use when asked to compare artists, analyze competitive position, find collaborators, benchmark a roster, or time a release. Triggers on "compare [artist] vs [artist]", "competitive analysis", "roster comparison", "who should we collab with", "collaboration targets", "when should we release", "release timing", "career positioning", "benchmark".
---

# Competitive Analysis

Roster benchmarking, career positioning, collaboration intelligence, and release
timing strategy through the Recoup research API.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Decision tree

- **"Compare [A] vs [B]"** → Head-to-Head Comparison
- **"How does our roster compare?"** → Competitive Roster Analysis
- **"Who should we collaborate with?"** → Collaboration Finder
- **"When should we release?"** → Release Strategy Timing
- **"What's their career stage?"** → `/research/similar` → career_stage + recent_momentum

## Head-to-Head Comparison

Compare two artists across all dimensions:

```bash
# For EACH artist, run:
curl -s "$RECOUP_API/research/profile?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&sort=followers" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/rank?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Side-by-side table comparing streaming numbers, playlist reach,
audience demographics, geographic strength, and career stage. Identify where
each artist under-indexes vs the other.

## Competitive Roster Analysis

How does a roster compare to a competitor label?

```bash
# For each artist on the roster:

# 1. Profile + metrics
curl -s "$RECOUP_API/research/profile?artist={your_artist}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={your_artist}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"

# 2. Similar artists (to infer competitor roster)
curl -s "$RECOUP_API/research/similar?artist={your_artist}&audience=high&genre=high" -H "x-api-key: $RECOUP_API_KEY"

# 3. Playlist reach comparison
curl -s "$RECOUP_API/research/playlists?artist={your_artist}&sort=followers" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/playlists?artist={competitor_artist}&sort=followers" -H "x-api-key: $RECOUP_API_KEY"

# 4. Audience demographics
curl -s "$RECOUP_API/research/audience?artist={your_artist}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={competitor_artist}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"

# 5. Geographic overlap
curl -s "$RECOUP_API/research/cities?artist={your_artist}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/cities?artist={competitor_artist}" -H "x-api-key: $RECOUP_API_KEY"

# 6. Global rank for headline deltas
curl -s "$RECOUP_API/research/rank?artist={your_artist}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/rank?artist={competitor_artist}" -H "x-api-key: $RECOUP_API_KEY"
```

## Collaboration Finder

Which artists should we collaborate with?

```bash
# 1. Shared fanbase
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=30" -H "x-api-key: $RECOUP_API_KEY"

# 2. Genre/sound overlap
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&genre=high&musicality=high" -H "x-api-key: $RECOUP_API_KEY"

# 3. Playlist synergy (shared playlists = easy collab pitch)
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&editorial=true" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/playlists?artist={collab_target}&editorial=true" -H "x-api-key: $RECOUP_API_KEY"

# 4. Geographic overlap (shared cities = tour collab)
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/cities?artist={collab_target}" -H "x-api-key: $RECOUP_API_KEY"

# 5. Enrich collaborator (label, management)
curl -s -X POST "$RECOUP_API/research/enrich" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":"{collab_target} musician","schema":{"type":"object","properties":{"label":{"type":"string"},"manager":{"type":"string"}}}}'
```

**Synthesize:** Ranked collaboration targets by audience overlap, career stage
(slightly bigger = ideal), and playlist synergy. Shared playlists + shared
cities = strongest collab case.

## Release Strategy Timing

When should we release, and how should we roll it out?

```bash
# 1. Past releases
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists&beta=true" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/albums?artist_id={cm_artist_id}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/career?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 2. Past playlist adds after previous releases
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=past&since=2024-01-01" -H "x-api-key: $RECOUP_API_KEY"

# 3. Similar artists' release cycles
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=10" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/albums?artist_id={similar_cm_artist_id}" -H "x-api-key: $RECOUP_API_KEY"

# 4. Current platform momentum
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=youtube_channel" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Release timing grounded in historical patterns, peer release
cycles, and which platform has the most momentum right now.

## Interpretation rules

- **`career_stage`:** undiscovered → developing → mid-level → mainstream → superstar → legendary
- **`recent_momentum`:** decline → gradual decline → steady → growth → explosive growth
- Peers all "mainstream" but artist is "mid-level" = breakout potential
- Peers with playlists you're NOT on = pitch targets (hand off to playlist-intelligence)
- Slightly bigger career stage = ideal collab target (exposure uplift)
- Same career stage + different geographic strength = mutual benefit collab

## Critical gotchas

- **`/research/enrich` schemas must include `"type":"object"` at the top level.**
  Endpoint rejects schemas without it.
- **`/research/enrich` takes 60–90s.** Set client timeout to ≥3 min.
- **`/research/albums` needs the numeric Chartmetric artist ID**, not the name.
  Resolve via search first.

## References

- **[references/endpoints.md](../../references/endpoints.md)** — curl examples, ID-based endpoints
- **[references/response-shapes.md](../../references/response-shapes.md)** — similar artists JSON shape
- **[references/workflows.md](../../references/workflows.md)** — Workflows 6 (Roster), 9 (Collab), 10 (Release Timing)
