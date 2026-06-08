---
name: recoup-audience-analysis
description: Audience demographics, geographic analysis, market expansion scouting, tour routing, and TikTok-to-Spotify pipeline analysis via the Recoup research API. Use when asked about audience demographics, where fans are, market expansion, tour routing, TikTok conversion, geographic strategy, or "where should we focus". Triggers on "audience", "demographics", "who are the fans", "where are the fans", "tour routing", "which markets", "TikTok to Spotify", "market expansion", "geographic strategy".
---

# Audience Analysis

Audience demographics, geographic intelligence, market expansion scouting, and
cross-platform pipeline analysis through the Recoup research API.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

> **Geography note:** the dedicated `cities`, `venues`, and `festivals`
> endpoints were removed in the Songstats migration. Geographic/demographic data
> now comes from `/research/audience` (country breakdown per platform), and
> venue/festival/touring detail comes from web/deep research.

## Decision tree

- **"Who are the fans?"** → `/research/audience` (IG/TikTok/YT) → synthesize demographics
- **"Where are the fans?"** → `/research/audience` country breakdown across platforms
- **"Is TikTok converting to Spotify?"** → TikTok-to-Spotify Pipeline workflow
- **"Where should we tour?"** → Geographic & Tour Strategy workflow
- **"Which markets should we expand into?"** → Market Expansion Scouting workflow
- **"What's the geographic strategy?"** → combine audience across all platforms

## Audience demographics

```bash
# Instagram audience (default)
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" \
  -H "x-api-key: $RECOUP_API_KEY"

# TikTok audience
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" \
  -H "x-api-key: $RECOUP_API_KEY"

# YouTube audience
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" \
  -H "x-api-key: $RECOUP_API_KEY"
```

The `audience` array carries age, gender, and country breakdowns. It is often
`[]` for smaller artists — that's a coverage gap, not an error. Fall back to
another platform or to web research.

## TikTok-to-Spotify Pipeline Analysis

Is TikTok virality translating to Spotify growth?

```bash
# 1. TikTok metrics snapshot
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"

# 2. Spotify metrics snapshot
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"

# 3. TikTok audience demographics + geography
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "x-api-key: $RECOUP_API_KEY"

# 4. Instagram audience for geographic cross-check
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"

# 5. Narrative context for any spike
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} viral TikTok moment 2026","max_results":10}'
```

**Synthesize:** Compare TikTok scale against Spotify conversion. Geographic
mismatch between the TikTok audience and Spotify audience = opportunity (e.g.
TikTok skews Brazil but Spotify skews US → Brazil is untapped). Metrics are
snapshots, so to measure week-over-week change store today's reading and diff.

## Geographic & Tour Strategy

Where is the artist strong, and where should they tour?

```bash
# 1. Audience geography across platforms (the geography source)
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" -H "x-api-key: $RECOUP_API_KEY"

# 2. Similar artists' geography (for co-headlining / routing comps)
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=20" -H "x-api-key: $RECOUP_API_KEY"

# 3. Venue history, capacity, festival fit — web/deep research (no venues/festivals endpoint)
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} tour dates venues capacity 2025 2026","max_results":10}'
```

**Synthesize:** Ranked markets by audience concentration, cross-checked with
where similar artists tour (from web research) and the artist's own venue
history. Markets with audience but no recent touring = expansion opportunities.

## Market Expansion Scouting

Which new markets should we focus on?

```bash
# 1. Platform-specific audience country breakdown
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" -H "x-api-key: $RECOUP_API_KEY"

# 2. Similar artists' audience geography
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&genre=high&limit=10" -H "x-api-key: $RECOUP_API_KEY"
# For each:
curl -s "$RECOUP_API/research/audience?artist={similar_artist}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"

# 3. Regional/scene context for a candidate market
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{GENRE} scene streaming growth Brazil 2026","max_results":10,"country":"BR"}'
```

**Synthesize:** Markets where similar artists over-index but the target artist is
weak = expansion opportunities. Cross-reference with playlist coverage — markets
with fans but no playlist presence need pitching.

## Interpretation rules

- **Follower-to-listener ratio above ~20%** (`followers_total ÷ monthly_listeners_current` from `/metrics`) = dedicated fan base
- **Audience country skew vs platform mix** = localization opportunity (e.g. big Brazil audience, no Portuguese content)
- **Gender skew** → content strategy (visual style, messaging)
- **Age concentration** → platform priority (Gen Z = TikTok, 25–34 = Instagram)
- **TikTok scale far ahead of Spotify conversion** = virality isn't converting; add Spotify-specific CTAs

## Critical gotchas

- **`/research/audience?platform=` accepts only `instagram | tiktok | youtube`.**
  Not `spotify` or `soundcloud`.
- **`/research/metrics` uses `youtube_channel` or `youtube_artist`**, not plain
  `youtube`. For TikTok, use `tiktok`. Metrics may return `202` `refresh_pending`
  — retry shortly.
- **No `cities` / `venues` / `festivals` / `charts` endpoints.** Geography →
  `/audience`; venues/festivals/touring → web/deep research.
- **Audience demographics are frequently empty for smaller artists.** Fall back to
  another platform or web research — don't fabricate a breakdown.

## References

- **`references/endpoints.md`** — curl examples, platform source enums
- **`references/workflows.md`** — Workflows 2 (TikTok Pipeline), 3 (Geographic & Tour), 8 (Market Expansion)
