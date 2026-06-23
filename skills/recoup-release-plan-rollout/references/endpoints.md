# Endpoints reference (matches production `api.recoupable.com`)

The live `/api/research/*` surface, verified against the OpenAPI spec at
`developers.recoupable.com/api-reference/openapi/research.json` and live calls.
**The research backend is songstats-based** — responses wrap data in an
`artist_info` envelope and use `songstats_artist_id` / `id`.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## The two-step pattern: resolve, then look up

Most artist endpoints take **either** `artist=` (a name) **or** `id=` (the
songstats artist id from search). For ambiguous names, search first to get the
`id`, then pass `id=` for stable results.

```bash
# 1. Search → returns results[] with id / songstats_artist_id
curl -s "$RECOUP_API/research?q=Wiz%20Khalifa&type=artists" -H "x-api-key: $RECOUP_API_KEY" | jq '.results[0]'
# -> { "songstats_artist_id": "1l65tk4s", "name": "Wiz Khalifa", "id": "1l65tk4s", "avatar": "...", "site_url": "..." }

# 2. Pass the name OR the id into any artist endpoint
curl -s "$RECOUP_API/research/profile?id=1l65tk4s" -H "x-api-key: $RECOUP_API_KEY" | jq '.artist_info'
```

## Search

`GET /api/research` — the discovery primitive.

- Params: `q*`, `type` (`artists` | `tracks` | `labels`; default `artists`), `limit`, `offset`.
- `q` may be a name or a streaming URL.

## Artist endpoints (all accept `artist=`name OR `id=`songstats-id)

```bash
curl -s "$RECOUP_API/research/profile?artist=Wiz%20Khalifa"     -H "x-api-key: $RECOUP_API_KEY" | jq   # bio, country, genres, label
curl -s "$RECOUP_API/research/urls?artist=Wiz%20Khalifa"        -H "x-api-key: $RECOUP_API_KEY" | jq   # social + streaming URLs
curl -s "$RECOUP_API/research/similar?artist=Wiz%20Khalifa&limit=20" -H "x-api-key: $RECOUP_API_KEY" | jq  # related artists
curl -s "$RECOUP_API/research/audience?artist=Wiz%20Khalifa&platform=instagram" -H "x-api-key: $RECOUP_API_KEY" | jq  # demographics (may be empty)
curl -s "$RECOUP_API/research/metrics?artist=Wiz%20Khalifa&source=spotify" -H "x-api-key: $RECOUP_API_KEY" | jq  # source REQUIRED
curl -s "$RECOUP_API/research/career?artist=Wiz%20Khalifa"      -H "x-api-key: $RECOUP_API_KEY" | jq   # career timeline / stage
curl -s "$RECOUP_API/research/insights?artist=Wiz%20Khalifa"    -H "x-api-key: $RECOUP_API_KEY" | jq   # AI-surfaced observations
curl -s "$RECOUP_API/research/milestones?artist=Wiz%20Khalifa"  -H "x-api-key: $RECOUP_API_KEY" | jq   # activity feed (date, summary, star rating)
curl -s "$RECOUP_API/research/tracks?artist=Wiz%20Khalifa"      -H "x-api-key: $RECOUP_API_KEY" | jq   # all tracks w/ popularity + track ids
curl -s "$RECOUP_API/research/playlists?artist=Wiz%20Khalifa&platform=spotify&status=current&limit=50" -H "x-api-key: $RECOUP_API_KEY" | jq
```

- **`similar`** supports weighting (`audience`/`genre`/`mood`/`musicality` = `high|medium|low`) **when the backend supports it**; otherwise it returns the closest related set. Don't depend on the weights.
- **`metrics`** — `source*` is REQUIRED. Enum: `spotify, instagram, tiktok, twitter, facebook, youtube_channel, youtube_artist, soundcloud, deezer, twitch, line, melon, wikipedia, bandsintown, radio, sxm`. For YouTube use `youtube_channel`/`youtube_artist`, never plain `youtube`.
- **`audience`** — `platform` is `instagram|tiktok|youtube` only. The `audience` array is **frequently empty** even for big artists; treat empty as "no demographic data," not zero.
- **`playlists`** (artist-level) — params are `artist`/`id`, `platform` (`spotify|applemusic|deezer|amazon|youtube`), `status` (`current|past`), `limit`. **There are NO `editorial`/`indie`/`majorCurator` filter flags at the artist level** — those live only on `track/playlists`.

## ID-based detail endpoints

```bash
# Albums — needs artist_id (the songstats id), not a name
curl -s "$RECOUP_API/research/albums?artist_id=1l65tk4s&is_primary=true&limit=50" -H "x-api-key: $RECOUP_API_KEY" | jq

# Full track metadata — needs a track id (from /research/tracks or search type=tracks)
curl -s "$RECOUP_API/research/track?id=TRACK_ID" -H "x-api-key: $RECOUP_API_KEY" | jq

# Playlists featuring a track (5 credits; paginates; supports filter flags)
curl -s "$RECOUP_API/research/track/playlists?id=TRACK_ID&platform=spotify&editorial=true" -H "x-api-key: $RECOUP_API_KEY" | jq

# Lookup an artist by platform URL or Spotify id
curl -s "$RECOUP_API/research/lookup?url=https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" -H "x-api-key: $RECOUP_API_KEY" | jq
curl -s "$RECOUP_API/research/lookup?spotifyId=3TVXtAsR1Inumwj472S9r4" -H "x-api-key: $RECOUP_API_KEY" | jq
```

## Web intelligence (POST — `Content-Type: application/json`)

```bash
curl -s -X POST "$RECOUP_API/research/web"     -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"query":"...","max_results":10,"country":"US"}'
curl -s -X POST "$RECOUP_API/research/deep"    -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"query":"..."}'
curl -s -X POST "$RECOUP_API/research/people"  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"query":"A&R reps at Atlantic","num_results":10}'
curl -s -X POST "$RECOUP_API/research/extract" -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"urls":["https://..."],"objective":"...","full_content":false}'
curl -s -X POST "$RECOUP_API/research/enrich"  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"input":"...","schema":{"type":"object","properties":{}},"processor":"core"}'
```

- `enrich.schema` MUST include `"type":"object"` at the top level. `processor` ∈ `base|core|ultra`.
- **Latency:** `enrich` 60–90s, `deep` 2+ min; set client timeouts ≥3 min or they look "hung."

## Credits

On `insufficient_credits` the response carries `remaining_credits`,
`required_credits`, and a `checkoutUrl`. `track`, `track/playlists`, `albums`,
`lookup` cost more; surface the checkout link rather than retrying.
