---
name: recoup-trend-detection
description: A&R discovery, chart analysis, and viral song analysis via the Recoup research API. Use when asked to find emerging artists, discover new talent, analyze charts, understand why a song went viral, or scout for trends. Triggers on "find emerging artists", "A&R scouting", "discover artists", "what's charting", "why did this go viral", "viral song", "trending", "chart analysis", "emerging [genre]", "breakout artists".
---

# Trend Detection

A&R discovery, chart intelligence, and viral song analysis through the Recoup
research API. Find emerging artists before they blow up, understand what's
driving virality, and identify market opportunities.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Decision tree

- **"Find emerging [genre] artists"** → A&R Discovery workflow
- **"What's charting?"** → `/research/charts?platform={}&country={}`
- **"Why did [song] go viral?"** → Viral Song Autopsy workflow
- **"Find TikTok breakouts"** → TikTok-driven scouting workflow
- **"Genre trends"** → `/research/genres` → chart analysis per genre

## A&R Discovery

Find emerging artists before they blow up:

```bash
# 0. List genre IDs — REQUIRED before using /discover. IDs are in the 501xxx+ range.
#    e.g. pop=501120, hip-hop/rap=501121, rock=501122, r&b/soul=501125
curl -s "$RECOUP_API/research/genres" -H "x-api-key: $RECOUP_API_KEY"

# 1. Discover by filters OR start from an anchor artist
curl -s "$RECOUP_API/research/discover?genre=501121&country=US&sp_monthly_listeners_min=50000&sp_monthly_listeners_max=200000&sort=weekly_diff.sp_monthly_listeners&limit=50" \
  -H "x-api-key: $RECOUP_API_KEY"

# Or start from a known artist and find similar emerging ones:
curl -s "$RECOUP_API/research/similar?artist={ANCHOR}&musicality=high&genre=high&limit=50" \
  -H "x-api-key: $RECOUP_API_KEY"

# 2. For promising candidates, check trajectory on two platforms
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"

# 3. Editorial placements = label interest signal
curl -s "$RECOUP_API/research/playlists?artist={candidate}&editorial=true" -H "x-api-key: $RECOUP_API_KEY"

# 4. AI-generated insights
curl -s "$RECOUP_API/research/insights?artist={candidate}" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Emerging artists with similar sound but smaller audience, sorted
by growth velocity. Filter for `career_stage` = "undiscovered" or "developing".

## Viral Song Autopsy

Why did this song go viral? Can we replicate it?

```bash
# 1. Resolve + fetch track details
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks&beta=true" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/track?id={cm_track_id}" -H "x-api-key: $RECOUP_API_KEY"

# 2. Metrics around release date
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"

# 3. Playlist timeline for this track (5 credits)
curl -s "$RECOUP_API/research/track/playlists?id={cm_track_id}&status=current" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/track/playlists?id={cm_track_id}&status=past&since=2025-01-01" -H "x-api-key: $RECOUP_API_KEY"

# 4. Milestone feed — chart entries, big playlist adds
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 5. AI insights
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 6. Similar trajectory artists
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&musicality=high" -H "x-api-key: $RECOUP_API_KEY"

# 7. Cultural context via web search
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"{TRACK_NAME} {ARTIST} viral TikTok moment\",\"max_results\":10}"
```

**Synthesize:** Timeline of the viral moment — what platform it started on,
which playlists amplified it, which demographics drove sharing. Compare with
similar artists' trajectories to judge replicability.

## TikTok-Driven Scouting

Find tracks blowing up on TikTok and the indie artists behind them:

```bash
# 1. TikTok charts
curl -s "$RECOUP_API/research/charts?platform=tiktok&country=US" -H "x-api-key: $RECOUP_API_KEY"

# 2. Discovery by filters
curl -s "$RECOUP_API/research/discover?country=US&genre={GENRE_ID}&sp_monthly_listeners_min=10000&sp_monthly_listeners_max=100000" \
  -H "x-api-key: $RECOUP_API_KEY"

# 3. Validate each candidate's pipeline
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"

# 4. Check editorial pickup
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&editorial=true" -H "x-api-key: $RECOUP_API_KEY"
```

## Discovery endpoint filters

Available filters for `/research/discover`:

- `country` — 2-letter ISO code (e.g. `US`, `BR`, `GB`)
- `genre` — numeric genre ID from `/research/genres` (e.g. `501121` for hip-hop/rap, `501125` for r&b/soul). **IDs are in the 501xxx+ range — NOT single/double digit numbers.**
- `band` — true/false
- `pronoun` — she/her, he/him, they/them
- `sp_monthly_listeners_min` / `sp_monthly_listeners_max`
- `sp_followers_min` / `sp_followers_max`
- `tiktok_followers_min` / `tiktok_followers_max`
- `ins_followers_min` / `ins_followers_max`
- `youtube_subscribers_min` / `youtube_subscribers_max`
- `cpp` — cost per play threshold
- `festival-id` — numeric festival ID
- `sort` — e.g. `weekly_diff.sp_monthly_listeners`, `latest.sp_monthly_listeners`
- `limit` / `offset`

**Fallback:** If `/research/discover` returns `{ artists: [] }`, use the
anchor-artist approach instead: start from a known artist →
`/research/similar?musicality=high&genre=high` → filter results by
`career_stage` and platform metrics.

## Critical gotchas

- **TikTok charts: NO `country_code` parameter.** Just `platform=tiktok`.
- **Amazon charts: NO `country_code`** — use `genre` + `type`.
- **`/research/milestones` empty is legit** — even for ranked artists. Fall back
  to `/insights` or `/career`.
- **Discovery `sort` columns:** `latest.sp_monthly_listeners`,
  `weekly_diff.sp_monthly_listeners`, `monthly_diff.tt_followers`, etc.
- **Genre IDs are numeric.** Call `/research/genres` once to get the mapping.

## References

- **[references/endpoints.md](../../references/endpoints.md)** — discover filters, chart params
- **[references/workflows.md](../../references/workflows.md)** — Workflows 4 (A&R Discovery), 7 (Viral Autopsy)
