---
name: music-industry-research
description: Music industry research via the Recoup `/api/research/*` REST endpoints (backed by Songstats). Use when the user asks about an artist's analytics, streaming/follower numbers, audience demographics, playlist placements, similar artists, catalog/tracks, career activity, or any music industry research. Also use for finding people in the industry (managers, A&R), extracting data from URLs, or enriching entities with structured web research. Triggers include "Spotify followers", "monthly listeners", "TikTok followers", "Instagram audience", "playlist pitching", "competitive analysis", "how is [artist] doing", "research [artist]", "find me [people]", or any question about an artist's performance, market position, or industry contacts.
---

# Recoup Research

Music industry research through the Recoup API. All endpoints live under `https://api.recoupable.com/api/research` and authenticate with `x-api-key`. The research API is backed by **Songstats**, so entity IDs are short alphanumeric strings like `wjcgfd9i` (artists) or `1ik97vot` (tracks) — **not** the long numeric Chartmetric IDs older versions of this skill used.

```bash
export RECOUP_API_KEY="recoup_sk_..."   # already set in Recoup sandboxes
export RECOUP_API="https://api.recoupable.com/api"
```

No key? Get one instantly (no dashboard, no email verification):

```bash
export RECOUP_API_KEY=$(curl -s -X POST "https://api.recoupable.com/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"agent+'$(date +%s)-$RANDOM'@recoupable.com"}' | jq -r .api_key)
```

Reference docs: <https://developers.recoupable.com>

## Decision tree

Start here based on what the user asks:

- **"How is [artist] doing?"** → `metrics?source=spotify` + `insights` (+ `milestones` for recent events)
- **"Research [artist] for me"** → `profile` → parallel(`metrics`, `audience`, `similar`, `playlists`, `tracks`) → `web` or `deep` for narrative → synthesize
- **"Who should I pitch to?"** → `similar?audience=high&genre=high` → `playlists` on each peer → find playlists peers are on and your artist isn't
- **"Where is the audience?"** → `audience?platform=instagram|tiktok|youtube` (city-level geography is no longer a direct endpoint — use `web`/`deep` for it)
- **"Find me [people]"** → `POST /research/people` with `{ "query": "A&R reps at Atlantic" }`
- **"Tell me about [entity]"** → `POST /research/enrich` for structured data, or `POST /research/deep` for cited narrative
- **"What does this page say?"** → `POST /research/extract` with `{ "urls": [...] }`
- **"Where does this track get played?"** → search `type=tracks` for the track `id` → `track/playlists?id=<track id>`
- **"Find emerging / related artists"** → `similar` on a known anchor artist, then `metrics` to size each candidate (there is no `discover` or `charts` endpoint anymore)

If none match, start with `POST /research/web`.

Before researching: check if the artist already has a workspace `context/artist.md` — don't re-research what's known.

## Endpoints (quick reference)

Full curl examples, filter flag rules, latency budgets, and platform source enums live in **`references/endpoints.md`**.

| Endpoint | Returns |
| -------- | ------- |
| `GET /research?q=&type=artists\|tracks\|labels` | search → provider IDs |
| `GET /research/lookup?url=` or `?spotifyId=` | Spotify URL/ID → `artist_info` |
| `GET /research/profile?artist=` or `?id=` | bio, genres, country, links, related artists (**no** counts) |
| `GET /research/metrics?artist=&source=` | current snapshot stats (followers / listeners / playlists) |
| `GET /research/audience?artist=&platform=instagram\|tiktok\|youtube` | age / gender / country |
| `GET /research/similar?artist=&audience=&genre=&mood=&musicality=` | peer artists (flat list, no scores) |
| `GET /research/playlists?artist=&platform=&status=` | artist playlist placements (flat, single-shot) |
| `GET /research/tracks?artist=` | catalog |
| `GET /research/career?artist=` | career activity feed |
| `GET /research/insights?artist=` | AI observations |
| `GET /research/milestones?artist=` | activity feed (playlist adds, chart entries) |
| `GET /research/urls?artist=` | social / streaming URLs |
| `GET /research/albums?artist_id=` | albums (provider artist ID, 5 credits) |
| `GET /research/track?id=` | track detail + audio analysis (provider track ID, 5 credits) |
| `GET /research/track/playlists?id=` (filter flags) | playlists featuring a track (5 credits, paginates) |
| `POST /research/web` | web search (~seconds) |
| `POST /research/deep` | comprehensive cited report (~2+ min) |
| `POST /research/people` | industry people search (~seconds-tens) |
| `POST /research/extract` | URL → markdown excerpts (~seconds-tens) |
| `POST /research/enrich` | structured extraction with schema (~60-90s) |

## Critical gotchas

These are the failure modes that will eat your time. Full rationale in `references/endpoints.md` and `references/response-shapes.md`.

- **Provider IDs are short alphanumeric strings** (`wjcgfd9i`), not numeric Chartmetric IDs. Get them via `GET /research?q=...&type=...`. There is **no `beta` flag and no `match_strength` score** anymore — search returns `results[]`; disambiguate by `name` / `avatar` / `site_url` (and `release_date` / `artists[]` for tracks). Empty `results` → fall through to graceful degradation.
- **Removed endpoints (these all 404 — don't call them):** `cities`, `charts`, `discover`, `genres`, `festivals`, `radio`, `venues`, `rank`, `instagram-posts`, `playlist` (singular), `curator`. Geography now comes from `audience` (+ `web`/`deep`); discovery from `similar` + `web`.
- **`/research/profile` carries NO follower/listener counts** (and no `career_stage`). Those numbers live in `/research/metrics`, which returns a **current snapshot**, not a time series.
- **Most artist endpoints accept `artist=<name>` OR `id=<provider id>`.** Use the name for convenience; use the id (from search/lookup) for an exact entity. ID-only detail endpoints (`albums`, `track`, `track/playlists`) need the provider id.
- **Playlist filter flags live on `track/playlists` only, and are exclusive when set.** `?editorial=true` alone returns ONLY editorials; to get editorial *plus* the defaults pass all four: `&editorial=true&indie=true&majorCurator=true&popularIndie=true`. The artist-level `/research/playlists` has **no** filter flags and returns a flat `placements[]` snapshot (no `offset` paging).
- **`/research/track` has NO per-song TikTok fields** (`tt_uses`, `tt_views`, etc.) — the API does not expose per-song TikTok counts. Don't look for them and don't fabricate them.
- **`/research/metrics` uses `youtube_channel` or `youtube_artist`**, not plain `youtube`. `/research/audience?platform=` accepts only `instagram | tiktok | youtube`.
- **`/research/enrich` schemas must include `"type":"object"` at the top level.** The endpoint rejects schemas without it.
- **POST endpoints have real latency.** `/enrich` 60–90s, `/deep` 2+ min, others seconds-to-tens. Set client timeouts to ≥3 min for `/enrich` and `/deep` or you'll falsely abort successful calls.
- **Empty arrays are legit.** `/research/milestones` and `/research/audience` commonly return `[]` even for established artists — that's not an error; don't retry or escalate, degrade instead.
- **Cold-cache calls can return a transient error/`202` — retry before giving up.** The research API caches provider data, so a *cold* GET (`career`, `playlists`, `metrics`, etc.) can come back `status: "error"` or `202 { state: "refresh_pending" }` and then succeed on the very next call. Retry once or twice with a short sleep before treating it as "no data" — a single transient error is **not** proof the artist has no data. (Distinct from a genuinely empty `[]` above, which is stable across retries.)
- **Don't guess field names.** Importance on activity feeds is `activity_tier` (integer, lower = more significant), not a star rating; placements are flat (`placements[].playlist_name`), and `followers_total` is a human-readable string like `"34.3M"`. Full real shapes in `references/response-shapes.md`.

## Graceful degradation

Fall through to web research if **any** of these are true:

- `GET /research?q=...` returns `{ results: [] }`
- `GET /research/lookup?url=...` returns non-200
- `/research/profile` comes back with mostly `null` fields

Then:

1. `POST /research/web` — ranked results
2. `POST /research/enrich` — structured facts (~60–90s)
3. `POST /research/deep` — cited narrative (~2+ min)

For very emerging artists, the provider may have no structured data — web + enrich + deep is the fallback.

## How to use the data

Don't dump raw JSON. Combine endpoints, draw conclusions, save to the artist workspace if there is one. Interpretation rules of thumb (follower:listener ratios, audience-vs-placement mismatches, snapshot diffing over time) and end-to-end synthesis patterns (geographic strategy, playlist gap analysis, platform pipeline, etc.) are in **`references/workflows.md`**.

## References

These reference files ship alongside this skill, in its own `references/` folder:

- **`references/endpoints.md`** — full curl examples per endpoint, playlist filter / pagination semantics, latency budgets, platform source enums
- **`references/response-shapes.md`** — actual JSON shapes for `/search`, `/profile`, `/metrics`, `/similar`, `/playlists`, `/track`, activity feeds, plus field-name gotchas
- **`references/workflows.md`** — interpretation cheat sheet, synthesis patterns, multi-step workflow chains, and where to save research output
