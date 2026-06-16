---
name: recoup-artist-competition
description: Competitive roster analysis, career positioning, collaboration finding, and release strategy timing via the Recoup research API. Use when asked to compare artists, analyze competitive position, find collaborators, benchmark a roster, or time a release. Triggers on "compare [artist] vs [artist]", "competitive analysis", "roster comparison", "who should we collab with", "collaboration targets", "when should we release", "release timing", "career positioning", "benchmark".
---

# Competitive Analysis

Roster benchmarking, career positioning, collaboration intelligence, and release
timing strategy through the Recoup research API. The API is backed by
**Songstats** — IDs are short alphanumeric strings, not numeric Chartmetric IDs.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Decision tree

- **"Compare [A] vs [B]"** → Head-to-Head Comparison
- **"How does our roster compare?"** → Competitive Roster Analysis
- **"Who should we collaborate with?"** → Collaboration Finder
- **"When should we release?"** → Release Strategy Timing
- **"How big are they?"** → `/research/metrics?source=spotify` (there is no `career_stage` or `rank` field — size artists by their metrics snapshot)

## Head-to-Head Comparison

Compare two artists across all dimensions:

```bash
# For EACH artist, run:
curl -s "$RECOUP_API/research/profile?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=current" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Side-by-side table comparing the `/metrics` snapshots (monthly
listeners, followers, popularity, editorial playlists, playlist reach), audience
demographics, and geographic strength. Identify where each artist
under-indexes. There is no single global rank — use the metrics snapshot for
headline numbers.

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
curl -s "$RECOUP_API/research/playlists?artist={your_artist}&status=current" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/playlists?artist={competitor_artist}&status=current" -H "x-api-key: $RECOUP_API_KEY"

# 4. Audience demographics + geography
curl -s "$RECOUP_API/research/audience?artist={your_artist}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={competitor_artist}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"

# 5. Headline numbers (no /rank endpoint — compare metrics snapshots)
curl -s "$RECOUP_API/research/metrics?artist={competitor_artist}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
```

## Collaboration Finder

Which artists should we collaborate with?

```bash
# 1. Shared fanbase
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=30" -H "x-api-key: $RECOUP_API_KEY"

# 2. Genre/sound overlap
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&genre=high&musicality=high" -H "x-api-key: $RECOUP_API_KEY"

# 3. Size each candidate (similar has no metrics) + playlist synergy
curl -s "$RECOUP_API/research/metrics?artist={collab_target}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/playlists?artist={collab_target}&status=current" -H "x-api-key: $RECOUP_API_KEY"

# 4. Geographic overlap (shared markets = tour collab)
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={collab_target}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"

# 5. Enrich collaborator (label, management)
curl -s -X POST "$RECOUP_API/research/enrich" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":"{collab_target} musician","schema":{"type":"object","properties":{"label":{"type":"string"},"manager":{"type":"string"}}}}'
```

**Synthesize:** Ranked collaboration targets by audience overlap, size (slightly
bigger via `/metrics` = ideal exposure uplift), and playlist synergy. Shared
playlists + shared audience markets = strongest collab case.

## Release Strategy Timing

When should we release, and how should we roll it out?

```bash
# 1. Past releases (albums needs the provider artist_id — resolve via search)
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists" -H "x-api-key: $RECOUP_API_KEY"   # get id
curl -s "$RECOUP_API/research/albums?artist_id={artist_id}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/career?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 2. Past playlist adds after previous releases
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=past" -H "x-api-key: $RECOUP_API_KEY"

# 3. Similar artists' release cycles
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=10" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research?q={similar_artist}&type=artists" -H "x-api-key: $RECOUP_API_KEY"   # get peer id
curl -s "$RECOUP_API/research/albums?artist_id={peer_artist_id}" -H "x-api-key: $RECOUP_API_KEY"

# 4. Current platform momentum
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=youtube_channel" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Release timing grounded in historical patterns (from
`career`/`milestones`), peer release cycles, and which platform has the most
momentum right now.

## Interpretation rules

- **Size and stage come from `/metrics`, not a stage label.** Compare
  `monthly_listeners_current`, `followers_total`, and `playlists_editorial_current`
  across artists — there is no `career_stage` or `recent_momentum` field anymore.
- A peer with materially higher listeners + similar genre = ideal collab target
  (exposure uplift)
- Same size + different geographic strength (from `/audience`) = mutual-benefit collab
- Peers with playlists you're NOT on = pitch targets (hand off to playlist-intelligence)

## Critical gotchas

- **`/research/similar` returns a flat list with no scores or stage** — size each
  peer with `/research/metrics` to rank them.
- **`/research/enrich` schemas must include `"type":"object"` at the top level.**
- **`/research/enrich` takes 60–90s.** Set client timeout to ≥3 min.
- **`/research/albums` needs the provider artist ID** (`artist_id=`, alphanumeric),
  not the name. Resolve via search first.
- **No `/research/rank` and no `/research/cities`.** Headline numbers → `/metrics`;
  geography → `/audience`.

## References

- **`references/endpoints.md`** — curl examples, ID-based endpoints
- **`references/response-shapes.md`** — similar artists + metrics JSON shapes
- **`references/workflows.md`** — Workflows 6 (Roster), 9 (Collab), 10 (Release Timing)
