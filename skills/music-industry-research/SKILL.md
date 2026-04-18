---
name: music-industry-research
description: Music industry research via the Recoup `/api/research/*` REST endpoints — streaming metrics, audience demographics, playlist placements, competitive analysis, charts, venues, people search, URL extraction, structured enrichment, and web intelligence. Use when the user needs artist analytics, streaming numbers, audience insights, playlist tracking, similar artists, collaboration targets, tour routing data, chart positions, or any music industry research. Also use for finding people in the industry (managers, A&R), extracting data from URLs, or enriching entities with structured web research. Triggers on requests involving Spotify followers, monthly listeners, TikTok trends, Instagram audience, playlist pitching, competitive analysis, "how is [artist] doing," "research [artist]," "find me [people]," or any question about an artist's performance, market position, or industry contacts.
---

# Recoup Research

Music industry research through the Recoup API. Every endpoint lives under `https://recoup-api.vercel.app/api/research` and authenticates with the `x-api-key` header.

```bash
export RECOUP_API_KEY="recoup_sk_..."   # already set in Recoup sandboxes
export RECOUP_API="https://recoup-api.vercel.app/api"
```

Every example below assumes those two variables are exported. Full reference: https://developers.recoupable.com

## Before You Research

1. Check if the artist has a workspace with `context/artist.md` — don't re-research what's already known.
2. Decide what the user actually needs. "How's Drake doing?" needs 2-3 calls, not 20.
3. Pipe responses to `jq` when you need to extract fields (`curl ... | jq '.results[0]'`).

## Decision Tree

Start here based on what the user asks:

**"How is [artist] doing?"** → `GET /research/metrics?source=spotify` + `GET /research/cities` + `GET /research/insights`

**"Research [artist] for me"** → `GET /research/profile` → parallel(`metrics`, `audience`, `cities`, `similar`, `playlists`) → `POST /research/web` or `POST /research/deep` for narrative context → synthesize

**"Who should I pitch to?"** → `GET /research/similar?audience=high&genre=high` → `GET /research/playlists` on each peer → find playlists peers are on and your artist isn't

**"Where should we tour?"** → `GET /research/cities` + `GET /research/audience?platform=youtube` + `GET /research/festivals` + `GET /research/venues`

**"Find me [people]"** → `POST /research/people` with `{ "query": "A&R reps at Atlantic Records" }`

**"Tell me about [entity]"** → `POST /research/enrich` for structured data, or `POST /research/deep` for a cited narrative report

**"What does this page say?"** → `POST /research/extract` with `{ "urls": ["https://..."] }`

**"Find emerging artists"** → `GET /research/discover?country=US&genre=GENRE_ID&sp_monthly_listeners_min=50000&sp_monthly_listeners_max=200000` (list genre IDs via `GET /research/genres`)

**"What's charting on [platform]?"** → `GET /research/charts?platform=spotify&country=US`

**"Where does this track get played?"** → `GET /research/track/playlists?id=CM_TRACK_ID` (get `id` via search first)

If none of these match, start with `POST /research/web` for general research.

---

## Endpoints Reference

### 1. Search (the discovery primitive)

`GET /research` — find Chartmetric `id`s to pass into the ID-based lookups (`albums`, `track`, `playlist`, `curator`, `track/playlists`).

```bash
curl -s "$RECOUP_API/research?q=Drake&type=artists&beta=true" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

Query params: `q` (required), `type` (`artists|tracks|albums|playlists|curators|stations`, default `artists`), `limit`, `offset`, `beta` (`true|false` — **always pass `beta=true` for ambiguous queries**; beta results carry a numeric `match_strength` and rank far better than the default engine), `platforms` (e.g. `cm,spotify`, only with `beta=true`).

`q` can also be a streaming URL (e.g. `https://open.spotify.com/artist/...`).

### 2. Artist data (accept `artist=` name or Recoup UUID)

```bash
# Profile — bio, genres, social URLs, label, career stage
curl -s "$RECOUP_API/research/profile?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Time-series platform metrics ({ followers, listeners, popularity, ... })
curl -s "$RECOUP_API/research/metrics?artist=Drake&source=spotify" -H "x-api-key: $RECOUP_API_KEY" | jq

# Audience demographics — platform: instagram | tiktok | youtube (default instagram)
curl -s "$RECOUP_API/research/audience?artist=Drake&platform=tiktok" -H "x-api-key: $RECOUP_API_KEY" | jq

# Top listener cities
curl -s "$RECOUP_API/research/cities?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Similar artists (competitors, collab targets)
curl -s "$RECOUP_API/research/similar?artist=Drake&audience=high&genre=high&limit=20" -H "x-api-key: $RECOUP_API_KEY" | jq

# Playlist placements (see filter flags below)
curl -s "$RECOUP_API/research/playlists?artist=Drake&editorial=true&sort=followers" -H "x-api-key: $RECOUP_API_KEY" | jq

# All tracks with popularity
curl -s "$RECOUP_API/research/tracks?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Career timeline
curl -s "$RECOUP_API/research/career?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# AI-surfaced observations
curl -s "$RECOUP_API/research/insights?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Activity feed — playlist adds, chart entries, notable events (with star ratings)
curl -s "$RECOUP_API/research/milestones?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Social + streaming URLs (Spotify, IG, TikTok, YT, Twitter, SoundCloud, …)
curl -s "$RECOUP_API/research/urls?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Top Instagram posts and reels, sorted by engagement
curl -s "$RECOUP_API/research/instagram-posts?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Venues the artist has performed at (capacity + location)
curl -s "$RECOUP_API/research/venues?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Single-integer global Chartmetric rank
curl -s "$RECOUP_API/research/rank?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq
```

**`/research/playlists` filter flags** (all optional, all accept `true`/`false`):
`platform` (`spotify|applemusic|deezer|amazon|youtube`), `status` (`current|past`), `editorial`, `indie`, `majorCurator`, `popularIndie`, `personalized`, `chart`, `since=YYYY-MM-DD`, `sort`, `limit`.

### 3. Chartmetric ID-based detail endpoints (require a numeric ID from search)

Always discover the `id` via `GET /research?q=...&type=...&beta=true` first, then call these.

```bash
# Albums — note: artist_id, NOT name. is_primary=true (default) excludes features/compilations
curl -s "$RECOUP_API/research/albums?artist_id=3380&is_primary=true&limit=50" -H "x-api-key: $RECOUP_API_KEY" | jq

# Full track metadata
curl -s "$RECOUP_API/research/track?id=15194376" -H "x-api-key: $RECOUP_API_KEY" | jq

# Playlist metadata (NOT Spotify's base62 ID — Chartmetric's numeric ID)
curl -s "$RECOUP_API/research/playlist?platform=spotify&id=848051" -H "x-api-key: $RECOUP_API_KEY" | jq

# Curator profile — platforms: spotify | applemusic | deezer
curl -s "$RECOUP_API/research/curator?platform=spotify&id=2" -H "x-api-key: $RECOUP_API_KEY" | jq

# Playlists a specific track appears on (5 credits per call)
curl -s "$RECOUP_API/research/track/playlists?id=15194376&platform=spotify&editorial=true" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

`track/playlists` also accepts `q=` + optional `artist=` in place of `id=` for name-based lookup, plus `status`, `since`, `until`, `limit`, `offset`, `sort`, and the same filter flags as `/research/playlists` (`editorial`, `indie`, `majorCurator`, `popularIndie`, `personalized`, `chart`, `newMusicFriday`, `thisIs`, `radio`, `brand`).

### 4. Non-artist discovery + reference data

```bash
# Global chart positions — platform examples: spotify, applemusic, tiktok, youtube, itunes, shazam
curl -s "$RECOUP_API/research/charts?platform=spotify&country=US&interval=daily&type=regional" \
  -H "x-api-key: $RECOUP_API_KEY" | jq

# Artist discovery by filters
curl -s "$RECOUP_API/research/discover?country=US&genre=86&sp_monthly_listeners_min=50000&sp_monthly_listeners_max=200000&sort=weekly_diff.sp_monthly_listeners&limit=50" \
  -H "x-api-key: $RECOUP_API_KEY" | jq

# Genre ID lookup (use the returned IDs with /research/discover)
curl -s "$RECOUP_API/research/genres" -H "x-api-key: $RECOUP_API_KEY" | jq

# Festival list
curl -s "$RECOUP_API/research/festivals" -H "x-api-key: $RECOUP_API_KEY" | jq

# Radio station list (NOT artist-scoped)
curl -s "$RECOUP_API/research/radio" -H "x-api-key: $RECOUP_API_KEY" | jq

# Lookup an artist by platform URL or platform ID
curl -s "$RECOUP_API/research/lookup?url=https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

### 5. Web intelligence (POST)

All POSTs send `Content-Type: application/json` + `x-api-key` and take a JSON body.

```bash
# Web search — ranked results with title/url/snippet + markdown-formatted digest
curl -s -X POST "$RECOUP_API/research/web" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"Drake brand partnerships 2026","max_results":10,"country":"US"}' | jq

# Deep research — comprehensive multi-source report with citations (use instead of the old `report` CLI idea)
curl -s -X POST "$RECOUP_API/research/deep" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"Full deep dive on Drake: label relationships, recent brand deals, tour grosses, cultural moments in the last 18 months"}' | jq

# People search — returns multi-source profiles (LinkedIn, etc.)
curl -s -X POST "$RECOUP_API/research/people" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"A&R reps at Atlantic Records","num_results":10}' | jq

# URL extraction — up to 10 URLs, objective-targeted excerpts or full_content
curl -s -X POST "$RECOUP_API/research/extract" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com/article"],"objective":"tour dates","full_content":false}' | jq

# Structured enrichment — schema MUST include "type":"object" at the top level
curl -s -X POST "$RECOUP_API/research/enrich" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "input":"Drake rapper from Toronto",
    "schema":{"type":"object","properties":{"label":{"type":"string"},"manager":{"type":"string"}}},
    "processor":"core"
  }' | jq
```

`enrich.processor` is one of `base` (fast), `core` (balanced, default), `ultra` (comprehensive).

---

## Response shapes (what the fields actually are)

Don't guess field names. Chartmetric pass-through responses are richer than the OpenAPI schema enumerates (`additionalProperties: true` everywhere), but these are the fields that exist and matter. If you're looking for a field that isn't listed here, it probably doesn't exist — `dump the raw response once with jq '.artists[0] | keys'` before coding against it.

**`/research/similar` → `artists[].*`:**

```jsonc
{
  "id": 3380,                    // Chartmetric artist ID
  "name": "Drake",
  "image_url": "...",
  "code2": "CA",                 // 2-letter country
  "verified": true,
  "band": false,
  "score": 98.74,                // overall match score (0-100)
  "similarity": 0.88,            // audience-config similarity (0-1)
  "rank": 7,                     // global Chartmetric rank
  "career_stage": "superstar",   // undiscovered|developing|mid-level|mainstream|superstar|legendary
  "recent_momentum": "growth",   // decline|gradual decline|steady|growth|explosive growth
  "sp_followers": 109449837,
  "sp_monthly_listeners": 88857078,
  "sp_playlist_count": 3418778,
  "spotify_playlist_total_reach": 905221589,
  "youtube_subscribers": 32000000,
  "youtube_monthly_video_views": 241476550,
  "ins_followers": 141635181,
  "tiktok_followers": 1400000,
  "network_strength": "influential",
  "label": "UMG",
  "primary_genre_smart": { "id": 501121, "name": "hip-hop/rap" },
  "genres": [ { "id": 501121, "name": "hip-hop/rap" }, ... ],
  "normalizedScores": { "sp_followers": 1, "tiktok_followers": 0.36, ... },
  "rank_stats_monthly": [ { "rank": 7, "timestp": "2026-04-17" }, ... ]
}
```

There is **no** `trend` field and **no** `metrics` object. Momentum is `recent_momentum`. Platform counts are top-level (`sp_followers`, `ins_followers`, etc.) — not nested under a wrapper.

**`/research/playlists` → `placements[].*` (NESTED, not flat):**

```jsonc
{
  "playlist": {
    "id": 1805667,                // Chartmetric playlist ID
    "playlist_id": "7aa...",      // Spotify base62 ID
    "name": "My Shazam Tracks",
    "curator_name": "Erica Anne Benoit",
    "owner_name": "Erica Anne Benoit",
    "editorial": false,
    "personalized": false,
    "followers": 0,               // ⚠️  often 0 in placements — not a reliable reach signal here
    "position": 20,
    "peak_position": 2,           // better reach proxy than `followers`
    "added_at": "2025-11-11",
    "num_track": 486,
    "image_url": "...",
    "genres": [...], "moods": [...], "activities": [...], "tags": [...]
  },
  "track": {
    "id": 72120853,
    "name": "When You Were Mine",
    "isrc": "GBARL2100707",
    "spotify_popularity": 57,
    "artist_names": ["Joy Crookes"],
    "album_label": ["Speakerbox Recordings"],
    "release_dates": ["2021-08-24"],
    // ...
  }
}
```

So to filter editorial placements in jq: `.placements[] | select(.playlist.editorial == true)`. To rank by true reach, call `/research/playlist?platform=spotify&id={playlist.id}` for the detail record — the placement `followers` field is usually stale/zero.

---

## Gotcha: nulls in `/research/profile` don't mean "no data"

`/research/profile` is a convenience aggregator and it returns `null` for a lot of fields on less-covered artists (`sp_followers`, `sp_monthly_listeners`, `career_stage`, `num_sp_editorial_playlists`, etc.). Do **not** treat those nulls as "artist has no data" and give up.

The individual endpoints pull direct from platform data and often succeed when profile doesn't:

- `sp_followers` / `sp_monthly_listeners` null? → call `/research/metrics?source=spotify`
- `career_stage` / `recent_momentum` null? → call `/research/similar?artist=...` (the artist's own row is the first result and has these fields populated even when profile is sparse)
- `num_sp_editorial_playlists` null or 0? → call `/research/playlists?editorial=true` and trust the actual result set

**Preflight filter decisions with profile counts.** Before calling `/research/playlists?editorial=true`, check `/research/profile` for `num_sp_editorial_playlists`. If it's 0, an empty editorial result isn't a skill or API bug — the artist genuinely has no editorial placements. Drop the filter or switch to `&indie=true&majorCurator=true&popularIndie=true` to see what they *are* on.

---

## Platform Sources (for `/research/metrics?source=`)

`spotify`, `instagram`, `tiktok`, `twitter`, `facebook`, `youtube_channel`, `youtube_artist`, `soundcloud`, `deezer`, `twitch`, `line`, `melon`, `wikipedia`, `bandsintown`.

Two gotchas:

- For `metrics`, **YouTube uses `youtube_channel` or `youtube_artist`** — not plain `youtube`.
- `audience` is a different endpoint with its own, narrower enum: `platform=instagram|tiktok|youtube` (default `instagram`). Do **not** send `youtube_channel` there.

---

## Interpreting the Data

Raw numbers are noise without interpretation. Here's what to look for:

**Metrics:**
- Follower-to-listener ratio above 20% = dedicated fan base (they follow, not just stream)
- Save-to-listener ratio above 3% = strong catalog stickiness
- Week-over-week listener growth above 5% = momentum
- Popularity score trending up = algorithmic favor

**Cities:**
- If top cities are international but playlists are US-only = untapped international opportunity
- High listeners in a city the artist has never toured = tour opportunity
- Compare with similar artists' cities to find geographic white space

**Similar Artists:**
- `career_stage`: undiscovered → developing → mid-level → mainstream → superstar → legendary
- `recent_momentum`: decline → gradual decline → steady → growth → explosive growth
- If the artist's peers are all "mainstream" but they're "mid-level" = breakout potential
- Peers with playlists you're NOT on = pitch targets

**Playlists:**
- 2 editorial playlists for 5M+ listeners = severely under-playlisted (pitch immediately)
- `placements[].playlist.followers` is often `0` — use `peak_position` or call `/research/playlist?id=` for true reach
- Past placements (`status=past`) that dropped off = re-pitch opportunities

**Audience:**
- Gender skew tells you content strategy (visual style, messaging)
- Age concentration tells you platform priority (Gen Z = TikTok, 25-34 = Instagram)
- Country mismatch between audience and cities = content localization opportunity

**Charts / Rank / Milestones:**
- `/research/rank` gives one number — useful for before/after deltas over time
- `/research/milestones` is the activity feed — filter for high star ratings when summarizing
- `/research/charts` is platform-wide, not artist-scoped — use it to find what's hot on a market/platform, then cross-reference with `similar`

---

## Synthesis Patterns

Don't dump raw JSON. Combine endpoints and draw conclusions:

**Geographic Strategy:** `cities` + `audience?platform=instagram` → "Sao Paulo is #1 (135K listeners) but IG audience is 80% US. Massive Brazilian fan base isn't being served with localized content."

**Playlist Gap Analysis:** `similar` → `playlists` on each peer → "5 of your 10 peers are on 'R&B Rotation' (450K followers), you're not. That's the top pitch target."

**Platform Pipeline:** `metrics?source=tiktok` + `metrics?source=spotify` → "TikTok followers up 40% last month, Spotify listeners flat. Virality isn't converting. Add Spotify-specific CTAs to TikTok content."

**Career Positioning:** `similar` → compare career stages → "You're the only 'mainstream' artist in your peer group — everyone else is 'mid-level'. Leverage for brand deals and festival slots."

**Chart → Catalog:** `charts?platform=tiktok&country=US` + `tracks` → identify sound trends the artist's catalog could slot into.

---

## Saving Research

If working in an artist workspace, save research results to `research/` with timestamps:

```
research/artist-intel-2026-04-17.md
```

Don't overwrite `context/artist.md` with research data. Static context (who the artist IS) is separate from dynamic research (how they're performing NOW). If the research reveals something that should update the static profile, suggest it — don't auto-update.

---

## What Not to Do

- **Don't run 20 endpoints when 3 will answer the question.** Start small, expand if needed.
- **Don't dump raw JSON to the user.** Interpret the data and draw conclusions.
- **Don't re-research what `context/artist.md` already covers.** Read it first.
- **Don't send name strings to ID-based endpoints.** `/albums`, `/track`, `/playlist`, `/curator`, `/track/playlists` require a numeric Chartmetric ID — call `GET /research?q=...&type=...&beta=true` first.
- **Don't use plain `youtube` for `/research/metrics`.** It's `youtube_channel` or `youtube_artist`.
- **Don't assume Chartmetric has every artist.** If `/research?q=...` returns no results, fall back to `POST /research/web` or `POST /research/deep`.
- **Don't forget `"type":"object"` in enrich schemas.** The endpoint rejects schemas without it.
- **Don't guess field names.** If you're unsure of a field, run the curl once and `jq '.<collection>[0] | keys'` before parsing. Common wrong guesses: `trend` (it's `recent_momentum`), `metrics` wrapper (platform counts are top-level: `sp_followers`, `ins_followers`, etc.), flat `playlist_name` (it's nested: `placements[].playlist.name`).
- **Don't read `/research/profile` nulls as "no data".** Profile is an aggregator that commonly returns null fields for less-covered artists. Fall back to `/research/similar`, `/research/metrics`, `/research/cities`, `/research/playlists` — those hit platform data directly.
- **Don't over-filter playlists blind.** `editorial=true` will legitimately return `{ placements: [] }` for artists with no editorial placements. Check `/research/profile`'s `num_sp_editorial_playlists` first, or widen to `&indie=true&majorCurator=true&popularIndie=true`.

---

## Graceful Degradation

If `GET /research?q=...&type=artists&beta=true` returns no results:

1. `POST /research/web` with the artist's name for web-based research
2. `POST /research/enrich` with a schema to extract structured facts
3. For very emerging artists, Chartmetric may not have data yet — web + enrich is the fallback

## More Workflows

Read `references/workflows.md` for complete multi-step workflow chains (playlist pitching, competitive analysis, tour routing, A&R discovery, viral autopsies, and more).
