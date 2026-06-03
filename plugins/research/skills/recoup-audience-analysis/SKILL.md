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

## Decision tree

- **"Who are the fans?"** → `/research/audience` (IG/TikTok/YT) → synthesize demographics
- **"Where are the fans?"** → `/research/cities` + `/research/audience` → geographic overlay
- **"Is TikTok converting to Spotify?"** → TikTok-to-Spotify Pipeline workflow
- **"Where should we tour?"** → Tour Routing Intelligence workflow
- **"Which markets should we expand into?"** → Market Expansion Scouting workflow
- **"What's the geographic strategy?"** → combine all geographic data sources

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

# Listener cities (Spotify-based)
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY"
```

## TikTok-to-Spotify Pipeline Analysis

Is TikTok virality translating to Spotify growth?

```bash
# 1. TikTok metrics over time
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"

# 2. Spotify metrics over the same period
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"

# 3. TikTok audience demographics
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "x-api-key: $RECOUP_API_KEY"

# 4. Spotify listener cities
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 5. Top Instagram posts (often cross-posted from TikTok)
curl -s "$RECOUP_API/research/instagram-posts?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Correlation between TikTok follower spikes and Spotify listener
growth. Geographic mismatch = opportunity (e.g. TikTok viral in Brazil but
Spotify listeners mostly in US → Brazil is untapped).

## Tour Routing Intelligence

Where should this artist tour next?

```bash
# 1. Top listener cities
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 2. Festivals
curl -s "$RECOUP_API/research/festivals" -H "x-api-key: $RECOUP_API_KEY"

# 3. Past venues (capacity history)
curl -s "$RECOUP_API/research/venues?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 4. Similar artists' cities (for co-headlining)
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=20" -H "x-api-key: $RECOUP_API_KEY"

# 5. Audience by platform
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Ranked cities by streaming engagement × historical venue
capacity. Cities where similar artists tour but this artist hasn't = expansion.

## Market Expansion Scouting

Which new markets should we focus on?

```bash
# 1. Current listener geography
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 2. Platform-specific audience breakdown
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" -H "x-api-key: $RECOUP_API_KEY"

# 3. Similar artists' top cities
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&genre=high&limit=10" -H "x-api-key: $RECOUP_API_KEY"
# For each:
curl -s "$RECOUP_API/research/cities?artist={similar_artist}" -H "x-api-key: $RECOUP_API_KEY"

# 4. Regional chart context
curl -s "$RECOUP_API/research/charts?platform=spotify&country=BR&interval=weekly" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Cities where similar artists thrive but the target artist is
weak = expansion opportunities. Cross-reference with playlist coverage — markets
with fans but no playlist presence need pitching.

## Interpretation rules

- **Follower-to-listener ratio above 20%** = dedicated fan base
- **Top cities international but playlists US-only** = untapped international opportunity
- **High listeners in a city never toured** = tour opportunity
- **Gender skew** → content strategy (visual style, messaging)
- **Age concentration** → platform priority (Gen Z = TikTok, 25–34 = Instagram)
- **Country mismatch** between audience and cities = content localization opportunity
- **TikTok up but Spotify flat** = virality isn't converting, add Spotify-specific CTAs

## Critical gotchas

- **`/research/audience?platform=` accepts only `instagram | tiktok | youtube`.**
  Not `spotify` or `soundcloud`.
- **`/research/metrics` uses `youtube_channel` or `youtube_artist`**, not plain
  `youtube`. For TikTok, use `tiktok`.
- **Cities data is Spotify-based only.** No TikTok or Instagram city data from
  this endpoint.
- **Audience demographics may be unavailable for smaller artists.** Fall back to
  cities + web research.

## References

- **`references/endpoints.md`** — curl examples, platform source enums
- **`references/workflows.md`** — Workflows 2 (TikTok Pipeline), 3 (Tour Routing), 8 (Market Expansion)
