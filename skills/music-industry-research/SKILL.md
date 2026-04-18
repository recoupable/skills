---
name: music-industry-research
description: Music industry research via the Recoup `/api/research/*` REST endpoints. Use when the user asks about an artist's analytics, streaming numbers, audience demographics, playlist placements, similar artists, charts, tour/venue data, or any music industry research. Also use for finding people in the industry (managers, A&R), extracting data from URLs, or enriching entities with structured web research. Triggers include "Spotify followers", "monthly listeners", "TikTok trends", "Instagram audience", "playlist pitching", "competitive analysis", "how is [artist] doing", "research [artist]", "find me [people]", or any question about an artist's performance, market position, or industry contacts.
---

# Recoup Research

Music industry research through the Recoup API. All endpoints live under `https://recoup-api.vercel.app/api/research` and authenticate with `x-api-key`.

```bash
export RECOUP_API_KEY="recoup_sk_..."   # already set in Recoup sandboxes
export RECOUP_API="https://recoup-api.vercel.app/api"
```

Reference docs: <https://developers.recoupable.com>

## Decision tree

Start here based on what the user asks:

- **"How is [artist] doing?"** → `metrics?source=spotify` + `cities` + `insights`
- **"Research [artist] for me"** → `profile` → parallel(`metrics`, `audience`, `cities`, `similar`, `playlists`) → `web` or `deep` for narrative → synthesize
- **"Who should I pitch to?"** → `similar?audience=high&genre=high` → `playlists` on each peer → find playlists peers are on and your artist isn't
- **"Where should we tour?"** → `cities` + `audience?platform=youtube` + `festivals` + `venues`
- **"Find me [people]"** → `POST /research/people` with `{ "query": "A&R reps at Atlantic" }`
- **"Tell me about [entity]"** → `POST /research/enrich` for structured data, or `POST /research/deep` for cited narrative
- **"What does this page say?"** → `POST /research/extract` with `{ "urls": [...] }`
- **"Find emerging artists"** → `discover?country=US&genre=GENRE_ID&sp_monthly_listeners_min=...`
- **"What's charting?"** → `charts?platform=spotify&country=US`
- **"Where does this track get played?"** → `track/playlists?id=CM_TRACK_ID`

If none match, start with `POST /research/web`.

Before researching: check if the artist already has a workspace `context/artist.md` — don't re-research what's known.

## Endpoints (quick reference)

Full curl examples, filter flag rules, latency budgets, and platform source enums live in **[references/endpoints.md](references/endpoints.md)**.

| Endpoint | Returns |
| -------- | ------- |
| `GET /research?q=&type=&beta=true` | search → Chartmetric IDs |
| `GET /research/profile?artist=` | bio, label, genres, aggregate counts |
| `GET /research/metrics?artist=&source=` | platform time-series |
| `GET /research/audience?artist=&platform=` | age/gender/country (IG/TT/YT only) |
| `GET /research/cities?artist=` | top listener cities |
| `GET /research/similar?artist=&audience=&genre=&mood=&musicality=` | peer artists |
| `GET /research/playlists?artist=` (filter flags) | placements (single-shot, no offset) |
| `GET /research/tracks?artist=` | catalog |
| `GET /research/career?artist=` | career timeline |
| `GET /research/insights?artist=` | AI observations |
| `GET /research/milestones?artist=` | activity feed |
| `GET /research/urls?artist=` | social/streaming URLs |
| `GET /research/instagram-posts?artist=` | top IG posts |
| `GET /research/venues?artist=` | venue history |
| `GET /research/rank?artist=` | global Chartmetric rank (single int) |
| `GET /research/lookup?url=` | URL → artist (canonical URL entry) |
| `GET /research/albums?artist_id=` | albums (needs CM artist ID) |
| `GET /research/track?id=` | track detail (needs CM track ID) |
| `GET /research/playlist?platform=&id=` | playlist detail (needs CM playlist ID) |
| `GET /research/curator?platform=&id=` | curator detail (needs CM curator ID) |
| `GET /research/track/playlists?id=` (filter flags) | playlists featuring a track (5 credits, paginates) |
| `GET /research/charts?platform=&country=` | global chart positions |
| `GET /research/discover?country=&genre=&...` | artist discovery by filters |
| `GET /research/genres` | genre IDs |
| `GET /research/festivals` | festival list |
| `GET /research/radio` | radio station list |
| `POST /research/web` | web search (~seconds) |
| `POST /research/deep` | comprehensive cited report (~2+ min) |
| `POST /research/people` | industry people search (~seconds-tens) |
| `POST /research/extract` | URL → markdown excerpts (~seconds-tens) |
| `POST /research/enrich` | structured extraction with schema (~60-90s) |

## Critical gotchas

These are the failure modes that will eat your time. Full rationale in [references/endpoints.md](references/endpoints.md) and [references/response-shapes.md](references/response-shapes.md).

- **Playlist filter flags are exclusive when set.** `?editorial=true` alone returns ONLY editorials, excluding the indie / curator / popularIndie defaults. To get editorial *plus* the rest, pass all four: `&editorial=true&indie=true&majorCurator=true&popularIndie=true`.
- **`/research/playlists` (artist-level) ignores `offset`** — single 100-max snapshot. For bulk, page `/research/track/playlists?id=...&offset=...` per track instead (that one *does* paginate).
- **Hard cap: `limit=100`** on both playlist endpoints. `150`+ → 400.
- **`/research/profile` aggregate counts (`num_sp_playlists`, etc.) are NOT reachable via detail endpoints.** Use them for magnitude (and `sp_playlist_total_reach` for true reach), use detail endpoints for sampled top placements.
- **`/research/profile` returns `null` for many fields on less-covered artists.** Fall back to `/similar`, `/metrics`, `/cities`, `/playlists` — they hit platform data direct.
- **Empty `/research/milestones` is legit** — `{ status: "success", milestones: [] }` is common even for ranked artists.
- **Search: `match_strength < 1` = not found.** Real matches score 100s–50,000s; noise is 0.005–0.1. Don't pass sub-1 IDs into detail endpoints — you'll resolve to the wrong entity.
- **For URLs, route through `/research/lookup?url=` first**, then chain the resolved name. `/profile?artist=<URL>` works for some shapes and 404/406s for others.
- **ID-based endpoints (`albums`, `track`, `playlist`, `curator`, `track/playlists`) require numeric Chartmetric IDs.** Get them via `GET /research?q=...&type=...&beta=true`.
- **`/research/metrics` uses `youtube_channel` or `youtube_artist`**, not plain `youtube`. `/research/audience?platform=` accepts only `instagram | tiktok | youtube`.
- **`/research/enrich` schemas must include `"type":"object"` at the top level.** Endpoint rejects schemas without it.
- **POST endpoints have real latency.** `/enrich` 60–90s, `/deep` 2+ min, others seconds-to-tens. Set client timeouts to ≥3 min for `/enrich` and `/deep` or you'll falsely abort successful calls.
- **Don't guess field names.** `recent_momentum` not `trend`; platform counts are top-level (`sp_followers`, `ins_followers`), no `metrics` wrapper. Placements are nested: `placements[].playlist.name`. Full real shapes in [references/response-shapes.md](references/response-shapes.md).

## Graceful degradation

Fall through to web research if **any** of these are true:

- `GET /research?q=...` returns `{ results: [] }`
- Top result has `match_strength < 1`
- `/research/lookup?url=...` returns non-200

Then:

1. `POST /research/web` — ranked results
2. `POST /research/enrich` — structured facts (~60–90s)
3. `POST /research/deep` — cited narrative (~2+ min)

For very emerging artists, Chartmetric may not have data — web + enrich + deep is the fallback.

## How to use the data

Don't dump raw JSON. Combine endpoints, draw conclusions, save to the artist workspace if there is one. Interpretation rules of thumb (follower:listener ratios, audience-vs-cities mismatches, career stage signals) and end-to-end synthesis patterns (geographic strategy, playlist gap analysis, platform pipeline, etc.) are in **[references/workflows.md](references/workflows.md)**.

## References

- **[references/endpoints.md](references/endpoints.md)** — full curl examples per endpoint, playlist filter / pagination semantics, latency budgets, platform source enums
- **[references/response-shapes.md](references/response-shapes.md)** — actual JSON shapes for `/similar`, `/playlists`, `/profile`, plus field-name gotchas
- **[references/workflows.md](references/workflows.md)** — interpretation cheat sheet, synthesis patterns, 11 multi-step workflow chains, and where to save research output
