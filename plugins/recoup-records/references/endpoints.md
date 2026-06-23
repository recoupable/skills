# Endpoints reference

Full curl examples for every production `/api/research/*` endpoint, plus
parameter rules, response shapes, latency budgets, and platform source enums.

These are the **current production endpoints** documented at
<https://developers.recoupable.com> (see the `/api-reference/research/*` pages).
The research API is backed by **Songstats**, so entity IDs are short
alphanumeric strings like `wjcgfd9i` (artists) or `1ik97vot` (tracks).

All examples assume:

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

No key? Get one instantly (no dashboard, no email verification):

```bash
export RECOUP_API_KEY=$(curl -s -X POST "https://api.recoupable.com/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"agent+'$(date +%s)-$RANDOM'@recoupable.com"}' | jq -r .api_key)
```

---

## 1. Search (the discovery primitive)

`GET /research` — find a provider `id` to pass into the ID-based lookups
(`albums`, `track`, `track/playlists`). Most artist endpoints accept a plain
`artist=` name, so you only need search when you want an exact ID or are
disambiguating between same-named entities.

```bash
curl -s "$RECOUP_API/research?q=Drake&type=artists" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

Query params:

- `q` (**required**) — a name (`Drake`, `Flowers`) **or** a streaming URL
  (`https://open.spotify.com/artist/...`).
- `type` — `artists` (default), `tracks`, or `labels`. **These are the only
  three valid types.**
- `limit` — max results (default `10`).
- `offset` — pagination offset (default `0`).

Response (`type=artists`):

```jsonc
{
  "status": "success",
  "results": [
    {
      "id": "wjcgfd9i",              // provider-neutral ID — pass into detail endpoints
      "songstats_artist_id": "wjcgfd9i",
      "name": "Drake",
      "avatar": "https://i.scdn.co/image/...",
      "site_url": "https://songstats.com/artist/wjcgfd9i/drake"
    }
    // ...
  ]
}
```

`type=tracks` results carry `songstats_track_id`, `release_date`, `is_remix`,
and an `artists[]` array; `id` is the track ID for `/research/track`.

> **No `beta`, no `platforms`, no `match_strength`.** The old beta engine and
> its `match_strength` scoring are gone. Disambiguate by reading `name`,
> `avatar`, `site_url`, and (for tracks) `release_date`/`artists[]` on the
> results instead. When `results` is empty, fall through to Graceful
> Degradation (web → enrich → deep).

---

## 2. Artist endpoints (accept `artist=` name **or** `id=` provider ID)

Every endpoint in this section takes **either** `artist=<name>` **or**
`id=<provider artist id>`. Use the name for convenience; use the `id` (from
search/lookup) when you need an exact entity.

```bash
# URL → artist resolution (Spotify URL or Spotify ID only)
curl -s "$RECOUP_API/research/lookup?url=https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.artist_info.name'
curl -s "$RECOUP_API/research/lookup?spotifyId=3TVXtAsR1Inumwj472S9r4" \
  -H "x-api-key: $RECOUP_API_KEY" | jq

# Profile — name, bio, genres, country, platform links, related artists
# NOTE: profile carries NO follower/listener counts. Use /metrics for those.
curl -s "$RECOUP_API/research/profile?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq '.artist_info'

# Platform metrics — current snapshot stats for one source (see source enum below)
curl -s "$RECOUP_API/research/metrics?artist=Drake&source=spotify" -H "x-api-key: $RECOUP_API_KEY" | jq '.stats'

# Audience demographics — platform: instagram | tiktok | youtube (default instagram)
curl -s "$RECOUP_API/research/audience?artist=Drake&platform=tiktok" -H "x-api-key: $RECOUP_API_KEY" | jq

# Similar artists (competitors, collab targets) — weighted by audience/genre/mood/musicality
curl -s "$RECOUP_API/research/similar?artist=Drake&audience=high&genre=high&limit=20" -H "x-api-key: $RECOUP_API_KEY" | jq '.artists'

# Playlist placements — see "Playlist semantics" below
curl -s "$RECOUP_API/research/playlists?artist=Drake&platform=spotify&status=current" -H "x-api-key: $RECOUP_API_KEY" | jq '.placements'

# All tracks (catalog)
curl -s "$RECOUP_API/research/tracks?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq '.tracks'

# Career activity feed
curl -s "$RECOUP_API/research/career?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq '.career'

# AI-surfaced observations
curl -s "$RECOUP_API/research/insights?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq '.insights'

# Activity feed — playlist adds, chart entries, notable events
curl -s "$RECOUP_API/research/milestones?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq '.milestones'

# Social + streaming URLs
curl -s "$RECOUP_API/research/urls?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq '.urls'
```

---

## 3. ID-based detail endpoints

Discover the `id` via `GET /research?q=...&type=...` first.

```bash
# Albums — note: artist_id (provider ID), NOT name. is_primary=true (default) excludes features/compilations
curl -s "$RECOUP_API/research/albums?artist_id=wjcgfd9i&is_primary=true&limit=50" -H "x-api-key: $RECOUP_API_KEY" | jq '.albums'

# Full track metadata + audio analysis (id from search type=tracks)
curl -s "$RECOUP_API/research/track?id=1ik97vot" -H "x-api-key: $RECOUP_API_KEY" | jq '.track_info'

# Playlists a specific track appears on (5 credits per call, paginates)
curl -s "$RECOUP_API/research/track/playlists?id=1ik97vot&platform=spotify&status=current" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.placements'
```

`track/playlists` also accepts `q=` + optional `artist=` in place of `id=` for
name-based lookup, plus `status`, `since`, `until`, `limit`, `offset`, `sort`,
and the filter flags documented below.

---

## 4. Web intelligence (POST)

All POSTs send `Content-Type: application/json` + `x-api-key`.

```bash
# Web search — ranked results with snippets
curl -s -X POST "$RECOUP_API/research/web" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"Drake brand partnerships 2026","max_results":10,"country":"US"}' | jq

# Deep research — comprehensive multi-source report with citations
curl -s -X POST "$RECOUP_API/research/deep" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"Full deep dive on Drake: label relationships, brand deals, tour grosses, cultural moments in the last 18 months"}' | jq

# People search — multi-source profiles (LinkedIn etc.)
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

Request-body notes:

- `web` — `query` (required), `max_results` (1–20, default 10), `country` (2-letter ISO).
- `deep` — `query` (required) only.
- `people` — `query` (required), `num_results` (1–100, default 10).
- `extract` — `urls` (required, 1–10), `objective` (optional, ≤3000 chars), `full_content` (default `false`).
- `enrich` — `input` (required), `schema` (required, **must have `"type":"object"` at the top level**), `processor` (`base` default / `core` / `ultra`).

### Latency — do not abort early

The POST endpoints do multi-source web browsing and take real wall-clock time:

| Endpoint | Typical latency |
| -------- | --------------- |
| `/research/enrich` | **60–90 seconds** (`core`; `ultra` longer) |
| `/research/deep` | **2+ minutes** for comprehensive cited reports |
| `/research/people`, `/research/web`, `/research/extract` | seconds to tens of seconds |

If you wrap these with a default 30s client timeout, they'll appear "hung" and
you'll abort successful calls. **Set client timeouts to ≥3 minutes for
`/enrich` and `/deep`**, or stream / queue them if the UX allows.

---

## Playlist semantics

Two endpoints return playlists. They behave differently — read this before
calling either.

### `/research/playlists` (artist-level)

Returns the artist's current/past playlist placements. Parameters:

- `artist=` or `id=` — the artist
- `platform` — `spotify` (default), `applemusic`, `deezer`, `amazon`, `youtube`
- `status` — `current` (default) or `past`
- `limit` — default `20`

**No editorial/indie/curator filter flags here** (those live on the
track-level endpoint). Each placement:

```jsonc
{
  "playlist_id": "37i9dQZF1DXcBWIGoYBM5M",   // platform playlist ID
  "playlist_name": "Today's Top Hits",
  "external_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
  "followers_total": "34.3M",                 // human-readable string, e.g. "34.3M"
  "image_url": "https://i.scdn.co/image/..."
}
```

### `/research/track/playlists` (track-level)

Returns playlists featuring a specific track. Discover the track `id` via
`GET /research?q=...&type=tracks`, or pass `q=` + optional `artist=`. **Costs 5
credits per request.** Parameters: `id` or `q`(+`artist`), `platform`
(`spotify` default / `applemusic` / `deezer` / `amazon`), `status`
(`current`/`past`), `limit`, `offset`, `since`, `until`, `sort`, plus filter
flags.

**Filter flags (track-level only):** `editorial`, `indie`, `majorCurator`,
`popularIndie`, `personalized`, `chart`, `newMusicFriday`, `thisIs`, `radio`,
`brand`.

**Default with no flags:** `editorial + indie + majorCurator + popularIndie =
true`. **The moment you pass ANY flag, the unset ones flip to `false`** —
`?editorial=true` means "ONLY editorial," not "editorial in addition to the
defaults." To get editorial *plus* the defaults, pass all four:
`?editorial=true&indie=true&majorCurator=true&popularIndie=true`.

| You want | Query |
| -------- | ----- |
| Editorial **plus** curator/indie | `?editorial=true&indie=true&majorCurator=true&popularIndie=true` |
| Only editorial | `?editorial=true` |
| Default categories (curator/indie mix) | (no flags) |
| Everything | pass all 10 flags `=true` |

Paginate with `offset=0, 100, 200, …` until `placements` is empty.

---

## Platform sources (for `/research/metrics?source=`)

The endpoint **accepts 16 `source` values**, but only some actually carry data
(verified live against a major artist — don't assume "accepted" means "populated"):

- **Return data (10):** `spotify`, `instagram`, `tiktok`, `twitter`, `facebook`,
  `youtube_channel`, `youtube_artist`, `soundcloud`, `deezer`, `bandsintown`.
- **Accepted but usually empty (6):** `twitch`, `line`, `melon`, `wikipedia`
  (inert — the current provider doesn't supply them), plus `radio` / `sxm` (only
  populated for radio-active artists). Don't burn a call expecting data here
  unless you have a reason to.

Two gotchas:

- For `metrics`, **YouTube uses `youtube_channel` or `youtube_artist`** — not
  plain `youtube`.
- `/research/audience` is a different endpoint with its own narrower enum:
  `platform=instagram|tiktok|youtube` (default `instagram`). Do **not** send
  `youtube_channel` there.

A `metrics` call may return `202` with `{ status: "pending", state:
"refresh_pending" }` while the provider refreshes. Retry the same call shortly.

> **Provider gap (not yet queryable).** The underlying provider (Songstats) also
> supplies `apple_music`, `amazon`, `shazam`, `itunes`, `tidal`, `beatport`,
> `traxsource`, and `1001tracklists` data — and you'll even see some of these
> `source` values appear inside `/research/career` and `/research/milestones`
> activity feeds — but `/research/metrics` currently **rejects them**
> (`status: "error"`). They are not available as metric snapshots today; don't
> pass them to `metrics`. (Tracked as an API-side gap to expose.)

---

## Credit costs

Some endpoints cost more credits than others. If the account returns
`{ "error": "insufficient_credits" }`, the response includes `remaining_credits`,
`required_credits`, and a `checkoutUrl` for the user to add credits.

| Cost tier | Endpoints |
| --------- | --------- |
| Free / 1 credit | `search`, `profile`, `metrics`, `audience`, `similar`, `playlists`, `insights`, `tracks`, `career`, `milestones`, `urls`, `web` |
| 5 credits | `lookup`, `albums`, `track`, `track/playlists` |
| Higher (varies) | `enrich`, `deep`, `people`, `extract` (POST endpoints) |

Credit costs are approximate and may change. When you get a `402` or
`insufficient_credits` error, surface it to the user with the checkout link —
don't silently fail or retry.
