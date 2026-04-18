# Endpoints reference

Full curl examples for every `/api/research/*` endpoint, plus filter and pagination semantics, latency budgets, and platform source enums.

All examples assume:

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://recoup-api.vercel.app/api"
```

---

## 1. Search (the discovery primitive)

`GET /research` — find Chartmetric IDs to pass into the ID-based lookups (`albums`, `track`, `playlist`, `curator`, `track/playlists`).

```bash
curl -s "$RECOUP_API/research?q=Drake&type=artists&beta=true" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

Query params: `q` (required), `type` (`artists|tracks|albums|playlists|curators|stations`, default `artists`), `limit`, `offset`, `beta` (`true|false` — **always pass `beta=true` for ambiguous queries**; beta results carry a numeric `match_strength` and rank far better than the default engine), `platforms` (e.g. `cm,spotify`, only with `beta=true`).

`q` can also be a streaming URL (e.g. `https://open.spotify.com/artist/...`).

**Interpreting `match_strength` (beta only):** real matches score orders of magnitude above 1 — Drake comes back at ~52,000, smaller artists score in the hundreds. Noise/wrong-category hits sit below 1 (often 0.005–0.1). **Treat a top result with `match_strength < 1` as "not found"** and fall through to Graceful Degradation. Don't pass sub-1 IDs into detail endpoints — you'll get the wrong entity back.

---

## 2. Artist data (accept `artist=` name or Recoup UUID)

**For URL-based entry, use `/research/lookup?url=` first** and chain the resolved name into the endpoints below. Passing a streaming URL directly to `/profile?artist=...` works sometimes but can return `404` or `406` depending on the URL shape (trailing `?si=`, `http` vs `https`, non-artist URLs). `/research/lookup` is the canonical URL resolver.

```bash
# URL → artist resolution (canonical entry for any platform URL)
curl -s "$RECOUP_API/research/lookup?url=https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.name'
# Then chain the name into every other endpoint:
curl -s "$RECOUP_API/research/profile?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq
```

```bash
# Profile — bio, genres, social URLs, label, career stage, aggregate counts
curl -s "$RECOUP_API/research/profile?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Time-series platform metrics ({ followers, listeners, popularity, ... })
curl -s "$RECOUP_API/research/metrics?artist=Drake&source=spotify" -H "x-api-key: $RECOUP_API_KEY" | jq

# Audience demographics — platform: instagram | tiktok | youtube (default instagram)
curl -s "$RECOUP_API/research/audience?artist=Drake&platform=tiktok" -H "x-api-key: $RECOUP_API_KEY" | jq

# Top listener cities
curl -s "$RECOUP_API/research/cities?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Similar artists (competitors, collab targets)
curl -s "$RECOUP_API/research/similar?artist=Drake&audience=high&genre=high&limit=20" -H "x-api-key: $RECOUP_API_KEY" | jq

# Playlist placements — see "Playlist filter & pagination semantics" below
curl -s "$RECOUP_API/research/playlists?artist=Drake&editorial=true&sort=followers" -H "x-api-key: $RECOUP_API_KEY" | jq

# All tracks with popularity
curl -s "$RECOUP_API/research/tracks?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Career timeline
curl -s "$RECOUP_API/research/career?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# AI-surfaced observations
curl -s "$RECOUP_API/research/insights?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Activity feed — playlist adds, chart entries, notable events (with star ratings)
curl -s "$RECOUP_API/research/milestones?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Social + streaming URLs
curl -s "$RECOUP_API/research/urls?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Top Instagram posts and reels, sorted by engagement
curl -s "$RECOUP_API/research/instagram-posts?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Venues the artist has performed at (capacity + location)
curl -s "$RECOUP_API/research/venues?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq

# Single-integer global Chartmetric rank
curl -s "$RECOUP_API/research/rank?artist=Drake" -H "x-api-key: $RECOUP_API_KEY" | jq
```

---

## 3. Chartmetric ID-based detail endpoints

Always discover the `id` via `GET /research?q=...&type=...&beta=true` first.

```bash
# Albums — note: artist_id, NOT name. is_primary=true (default) excludes features/compilations
curl -s "$RECOUP_API/research/albums?artist_id=3380&is_primary=true&limit=50" -H "x-api-key: $RECOUP_API_KEY" | jq

# Full track metadata
curl -s "$RECOUP_API/research/track?id=15194376" -H "x-api-key: $RECOUP_API_KEY" | jq

# Playlist metadata (NOT Spotify's base62 ID — Chartmetric's numeric ID)
curl -s "$RECOUP_API/research/playlist?platform=spotify&id=848051" -H "x-api-key: $RECOUP_API_KEY" | jq

# Curator profile — platforms: spotify | applemusic | deezer
curl -s "$RECOUP_API/research/curator?platform=spotify&id=2" -H "x-api-key: $RECOUP_API_KEY" | jq

# Playlists a specific track appears on (5 credits per call, paginates)
curl -s "$RECOUP_API/research/track/playlists?id=15194376&platform=spotify&editorial=true" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

`track/playlists` also accepts `q=` + optional `artist=` in place of `id=` for name-based lookup, plus `status`, `since`, `until`, `limit`, `offset`, `sort`, and the filter flags documented below.

---

## 4. Non-artist discovery + reference data

```bash
# Global chart positions — platform examples: spotify, applemusic, tiktok, youtube, itunes, shazam
curl -s "$RECOUP_API/research/charts?platform=spotify&country=US&interval=daily&type=regional" \
  -H "x-api-key: $RECOUP_API_KEY" | jq

# Artist discovery by filters
curl -s "$RECOUP_API/research/discover?country=US&genre=86&sp_monthly_listeners_min=50000&sp_monthly_listeners_max=200000&sort=weekly_diff.sp_monthly_listeners&limit=50" \
  -H "x-api-key: $RECOUP_API_KEY" | jq

# Genre IDs (use with /research/discover)
curl -s "$RECOUP_API/research/genres" -H "x-api-key: $RECOUP_API_KEY" | jq

# Festival list
curl -s "$RECOUP_API/research/festivals" -H "x-api-key: $RECOUP_API_KEY" | jq

# Radio station list (NOT artist-scoped)
curl -s "$RECOUP_API/research/radio" -H "x-api-key: $RECOUP_API_KEY" | jq

# Lookup an artist by platform URL or platform ID
curl -s "$RECOUP_API/research/lookup?url=https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

---

## 5. Web intelligence (POST)

All POSTs send `Content-Type: application/json` + `x-api-key`.

```bash
# Web search
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

`enrich.processor` is one of `base` (fast), `core` (balanced, default), `ultra` (comprehensive).

### Latency — do not abort early

The POST endpoints do multi-source web browsing and take real wall-clock time:

| Endpoint | Typical latency |
| -------- | --------------- |
| `/research/enrich` | **60–90 seconds** (`core` processor; `ultra` longer) |
| `/research/deep` | **2+ minutes** for comprehensive cited reports |
| `/research/people`, `/research/web`, `/research/extract` | seconds to tens of seconds |

If you wrap these with a default 30s client timeout, they'll appear "hung" and you'll abort successful calls. **Set client timeouts to ≥3 minutes for `/enrich` and `/deep`**, or stream / queue them if the UX allows.

---

## Playlist filter & pagination semantics

Single biggest footgun in this skill. Read this before calling either playlist endpoint.

### Filter flags are exclusive when set

Both `/research/playlists` (artist-level) and `/research/track/playlists` (track-level) accept filter flags: `editorial`, `indie`, `majorCurator`, `popularIndie`, `personalized`, `chart`. The track-level endpoint adds `newMusicFriday`, `thisIs`, `radio`, `brand`.

**Defaults with no flags:**

- `/research/track/playlists` — defaults to `editorial + indie + majorCurator + popularIndie = true` (the rest off).
- `/research/playlists` (artist-level) — behaves the same way empirically: no flags → mix of indie/curator placements, editorial excluded.

**The moment you pass ANY flag, the others flip to `false`.** `?editorial=true` doesn't mean "show me editorials in addition to defaults" — it means "show me ONLY editorials." This is how users end up getting `{ placements: [] }` when the artist actually has hundreds of indie/curator placements.

| You want | Query |
| -------- | ----- |
| All editorial **plus** curator/indie | `?editorial=true&indie=true&majorCurator=true&popularIndie=true` |
| Only editorial, nothing else | `?editorial=true` |
| Default categories (curator/indie mix, no editorial) | (no flags) |
| Everything the API will give you | pass all 6 (artist) or all 10 (track) flags `=true` |

### Hard cap: `limit=100`

Both endpoints reject `limit > 100` with a `400`. Empirically verified — `limit=150`, `200`, `500` all fail.

### Pagination

| Endpoint | `offset` | Strategy |
| -------- | -------- | -------- |
| `/research/playlists` (artist-level) | **Ignored** | Single 100-max snapshot. For bulk artist-wide playlist data, enumerate `/research/tracks` then page `/research/track/playlists?id=...&offset=...` per track. |
| `/research/track/playlists` | **Honored** | Page by `offset=0, 100, 200, …` until empty. |

### The aggregate-vs-detail gap

`/research/profile` reports counts like `num_sp_playlists: 3,418,778` (Drake) and `num_sp_editorial_playlists: 2,392`. **The detail endpoints will never return numbers that big.** Profile aggregates are derived from Chartmetric's full graph; `/research/playlists` and `/research/track/playlists` each expose at most ~100 per call, and the track-level total bottoms out well below the aggregate count (often low hundreds per track, sometimes ~40 even with all 10 flags `true`).

**Plan for this:** use profile counts as the signal of "does this artist have playlist support at all?" and the detail endpoints as a sampled list of top placements. For total reach, `/research/profile.sp_playlist_total_reach` and `sp_editorial_playlist_total_reach` are the trustworthy numbers.

---

## Platform sources (for `/research/metrics?source=`)

`spotify`, `instagram`, `tiktok`, `twitter`, `facebook`, `youtube_channel`, `youtube_artist`, `soundcloud`, `deezer`, `twitch`, `line`, `melon`, `wikipedia`, `bandsintown`.

Two gotchas:

- For `metrics`, **YouTube uses `youtube_channel` or `youtube_artist`** — not plain `youtube`.
- `/research/audience` is a different endpoint with its own narrower enum: `platform=instagram|tiktok|youtube` (default `instagram`). Do **not** send `youtube_channel` there.
