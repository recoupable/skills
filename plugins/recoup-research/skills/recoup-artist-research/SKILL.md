---
name: recoup-artist-research
description: Full artist research sweep via the Recoup research API. Use when asked to research an artist, get an overview, understand how an artist is performing, or prepare an artist brief. Triggers on "research [artist]", "how is [artist] doing", "tell me about [artist]", "artist overview", "artist brief", or any request for a comprehensive look at an artist's streaming, social, audience, and competitive position. This is the default entry point for all artist research — it orchestrates profile, metrics, audience, playlists, similar artists, and insights into a synthesized brief.
---

# Artist Research

Full-stack artist research through the Recoup API. This skill is the **default
entry point** — it runs the complete research sweep and synthesizes findings
into an actionable brief.

All endpoints live under `https://api.recoupable.com/api/research` and
authenticate with `x-api-key`. The API is backed by **Songstats** — entity IDs
are short alphanumeric strings (e.g. `wjcgfd9i`), not numeric Chartmetric IDs.

```bash
export RECOUP_API_KEY="recoup_sk_..."   # already set in Recoup sandboxes
export RECOUP_API="https://api.recoupable.com/api"
```

Reference docs: <https://developers.recoupable.com>

## Decision tree

Start here based on what the user asks:

- **"Research [artist]"** → full sweep (below)
- **"How is [artist] doing?"** → `metrics?source=spotify` + `audience` + `insights` → synthesize
- **"Tell me about [artist]"** → `profile` → `insights` → `career` → synthesize
- **"What do we know about [artist]?"** → check workspace `context/artist.md` first; if empty, run full sweep
- **Playlist questions** → hand off to `recoup-playlist-intelligence`
- **Audience/market questions** → hand off to `recoup-audience-analysis`
- **Competitor/roster comparison** → hand off to `recoup-competitive-analysis`
- **Trending/discovery questions** → hand off to `recoup-trend-detection`
- **People/outreach questions** → hand off to `recoup-people-outreach`

Before researching: check if the artist already has a workspace
`context/artist.md` — don't re-research what's known.

## Full research sweep

Run these in parallel where possible, then synthesize. Every artist endpoint
accepts `artist=<name>`; pass `id=<provider id>` instead when you need an exact
entity. Scripts and curl examples ship in `references/endpoints.md` alongside
this skill.

```bash
# 1. (Optional) Search — resolve the name to a provider id for exact lookups
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.results[0]'

# 2. Profile — name, bio, genres, country, platform links, related artists
curl -s "$RECOUP_API/research/profile?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.artist_info'

# 3. Spotify metrics — followers, monthly listeners, popularity, playlist reach
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.stats[0].data'

# 4. TikTok metrics — follower/engagement snapshot
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.stats[0].data'

# 5. Similar artists — competitive landscape
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&genre=high&limit=20" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.artists'

# 6. Playlist placements — current reach
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=current" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.placements'

# 7. Audience demographics + geography — IG or TikTok
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.audience'

# 8. AI-surfaced observations
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.insights'

# 9. Social + streaming URLs
curl -s "$RECOUP_API/research/urls?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.urls'
```

## Reading the data correctly

Two endpoints carry the numbers people ask for, and they're split:

- **`/research/profile` carries NO follower/listener counts.** It returns
  identity data only: `artist_info.{name, bio, genres, country, links,
  related_artists}`. Don't look for `sp_followers` or `cm_statistics` — those
  fields no longer exist.
- **`/research/metrics?source=spotify` carries the counts**, as a *current
  snapshot* under `stats[0].data`:

```jsonc
// /research/metrics?artist=X&source=spotify → .stats[0].data
{
  "monthly_listeners_current": 99477872,
  "followers_total": 112185098,
  "popularity_current": 100,
  "playlists_current": 176085,
  "playlists_editorial_current": 568,
  "playlist_reach_current": 993868411,
  "charts_current": 179
}
```

Call `/metrics` once per platform you need (`spotify`, `tiktok`, `instagram`,
`youtube_channel`). The `data` keys vary by source — `jq '.stats[0].data | keys'`
for an unfamiliar one.

## Synthesis template

After gathering data, synthesize into this structure:

### Artist Brief: {Name}

**Genres:** {from profile.genres} | **Country:** {profile.country} | **Label:** {if surfaced via /enrich or web}

**Streaming Snapshot** (from /metrics per source):
- Spotify: {monthly_listeners_current} listeners / {followers_total} followers ({followers÷listeners ratio}%), popularity {popularity_current}
- TikTok: {followers / engagement from metrics?source=tiktok}
- Instagram: {followers from metrics?source=instagram}
- YouTube: {subscribers from metrics?source=youtube_channel}

**Audience Profile:** {age/gender/country breakdown from /audience}

**Playlist Position:**
- {playlists_editorial_current} editorial / {playlists_current} total (from Spotify /metrics)
- Total playlist reach: {playlist_reach_current}
- Notable placements: {top 3 from /playlists by followers_total}

**Competitive Position:** {peer set from /similar; size peers via /metrics to judge stage}

**Key Insights:** {from /insights endpoint}

**Recommendations:** {synthesized from all data — what to do next}

## Critical gotchas

These failure modes will eat your time:

- **Search has no `match_strength` / `beta`.** Disambiguate same-named results by
  `name`, `avatar`, `site_url`, and (tracks) `release_date`/`artists[]`. Empty
  `results` → Graceful Degradation (web/enrich/deep).
- **`/research/profile` has no metrics.** Counts live on `/research/metrics`
  (`stats[0].data`), not on profile.
- **`/research/metrics` uses `youtube_channel` or `youtube_artist`**, not plain
  `youtube`. It may return `202` `refresh_pending` — retry shortly.
- **`/research/audience?platform=` accepts only `instagram | tiktok | youtube`.**
  It's also the only geographic source (the `cities` endpoint was removed).
- **For URLs, route through `/research/lookup?url=` (Spotify URL or `spotifyId`).**
- **POST endpoints have real latency.** `/enrich` 60–90s, `/deep` 2+ min. Set
  client timeouts to ≥3 min.
- **Don't guess field names.** No `career_stage`, `recent_momentum`,
  `cm_statistics`, or `rank` anywhere. IDs are alphanumeric, not numeric.

## Credit awareness

Some endpoints cost more credits than others (see `references/endpoints.md`).
If any call returns `{ "error": "insufficient_credits" }`, the response includes
`remaining_credits`, `required_credits`, and a `checkoutUrl`. Surface this to
the user — don't silently skip the data or retry.

The full research sweep above uses mostly free/1-credit endpoints. The
credit-heavier calls are: `/lookup` (5), `/albums` (5), `/track` (5),
`/track/playlists` (5), and the POST web intelligence endpoints.

## Graceful degradation

If structured data is unavailable (search returns empty `results`, or
`/profile` and `/metrics` come back thin), fall through:

1. `POST /research/web` — ranked web results
2. `POST /research/enrich` — structured facts (~60–90s)
3. `POST /research/deep` — cited narrative (~2+ min)

For very emerging artists, Songstats may not have data — web + enrich + deep is
the fallback. See `recoup-web-intelligence` skill for details.

## Saving research

If working in an artist workspace, save research results to `research/` with
timestamps:

```
research/artist-intel-2026-05-17.md
```

Don't overwrite `context/artist.md` with research data. Static context (who the
artist IS) is separate from dynamic research (how they're performing NOW). If
the research reveals something that should update the static profile, suggest it
— don't auto-update.

## Endpoint quick reference

Full curl examples, filter rules, latency budgets, and platform source enums
are in **`references/endpoints.md`** (ships alongside this skill).

| Endpoint | Returns |
| -------- | ------- |
| `GET /research?q=&type=artists\|tracks\|labels` | search → provider IDs |
| `GET /research/profile?artist=` | bio, genres, country, links, related artists |
| `GET /research/metrics?artist=&source=` | current snapshot stats per platform |
| `GET /research/audience?artist=&platform=` | age/gender/country (geography source) |
| `GET /research/similar?artist=` | peer artists (flat list) |
| `GET /research/playlists?artist=` | current/past placements |
| `GET /research/tracks?artist=` | catalog |
| `GET /research/albums?artist_id=` | discography (needs provider id) |
| `GET /research/track?id=` | track detail + audio analysis |
| `GET /research/track/playlists?id=` | per-track playlist coverage (5 credits) |
| `GET /research/career?artist=` | career activity feed |
| `GET /research/insights?artist=` | AI observations |
| `GET /research/milestones?artist=` | activity feed (activity_tier) |
| `GET /research/urls?artist=` | social/streaming URLs |
| `GET /research/lookup?url=` | Spotify URL/ID → artist resolution |

## References

- **`references/endpoints.md`** — full curl examples, pagination, latency
- **`references/response-shapes.md`** — actual JSON shapes
- **`references/workflows.md`** — multi-step workflow chains
