# Endpoints reference (matches production `api.recoupable.dev`)

The endpoints this skill uses, verified against the OpenAPI specs at
`docs.recoupable.dev/api-reference/openapi/` and live calls. Artist and
catalog facts come from the Spotify endpoints; measured play counts from the
Apify-backed measurement store; narrative from web research. There is no
structured artist-stats provider (no monthly listeners, demographics, or
playlist feeds) — say so rather than estimate.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.dev/api"
```

## The two-step pattern: resolve, then look up

Resolve the artist once to a Spotify artist id, then reuse it for catalog and
sizing calls. For a rostered artist, the Recoup `account_id` (from `RECOUP.md`
or `GET /api/artists`) is what socials and events take.

```bash
# 1. Search → results[].artists.items[] with id, name, followers.total, popularity, genres
curl -s "$RECOUP_API/spotify/search?q=Wiz%20Khalifa&type=artist&limit=5" -H "x-api-key: $RECOUP_API_KEY" | jq '.artists.items[0] | {id, name, followers, popularity, genres}'

# 2. Pass the id into the artist endpoints
curl -s "$RECOUP_API/spotify/artist?id=137W8MRPWKqSmrBGDBFSop" -H "x-api-key: $RECOUP_API_KEY" | jq '{name, followers, popularity, genres, images}'
```

## Artist + catalog (Spotify)

```bash
curl -s "$RECOUP_API/spotify/artist?id=$SPOTIFY_ARTIST_ID" -H "x-api-key: $RECOUP_API_KEY" | jq                       # followers.total, popularity, genres, images
curl -s "$RECOUP_API/spotify/artist/albums?id=$SPOTIFY_ARTIST_ID&include_groups=album,single&limit=50" -H "x-api-key: $RECOUP_API_KEY" | jq   # release history with release_date
curl -s "$RECOUP_API/spotify/artist/topTracks?id=$SPOTIFY_ARTIST_ID" -H "x-api-key: $RECOUP_API_KEY" | jq             # what carries them today
curl -s "$RECOUP_API/spotify/album?id=$ALBUM_ID" -H "x-api-key: $RECOUP_API_KEY" | jq                                  # tracks.items[] with ids + ISRCs, label, copyrights
```

- `followers.total` and `popularity` (0–100) are current snapshots — store a
  reading and diff it against a prior one to see change.
- Albums paginate (`limit`/`offset`); `include_groups` selects
  `album,single,appears_on,compilation`.

## Connected socials (rostered artists)

```bash
curl -s "$RECOUP_API/artists/$ARTIST_ACCOUNT_ID/socials" -H "x-api-key: $RECOUP_API_KEY" | jq    # per-platform profile + follower count
curl -s -X POST "$RECOUP_API/artist/socials/scrape" -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{"artist_account_id":"'$ARTIST_ACCOUNT_ID'","posts":12}'                                   # refresh counts + recent posts (credits per profile)
```

- `0`/`null` follower counts mean "not stored" — omit the platform, never print zero.

## Measured play counts (measurement store)

```bash
# Capture present counts for whole albums (202; minutes; ~$0.003 per album)
curl -s -X POST "$RECOUP_API/research/measurement-jobs" -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d '{"scope":{"album_ids":["'$ALBUM_ID'"]},"source":"current"}'

curl -s "$RECOUP_API/research/playcounts?spotify_album_id=$ALBUM_ID" -H "x-api-key: $RECOUP_API_KEY" | jq            # latest count per track
curl -s "$RECOUP_API/research/track/stats?isrc=$ISRC" -H "x-api-key: $RECOUP_API_KEY" | jq                           # one track, current (refreshes if stale)
curl -s "$RECOUP_API/research/track/historic-stats?isrc=$ISRC&start_date=2026-01-01" -H "x-api-key: $RECOUP_API_KEY" | jq   # dated series
curl -s "$RECOUP_API/research/tracks/$ISRC/measurements" -H "x-api-key: $RECOUP_API_KEY" | jq                         # every capture
curl -s "$RECOUP_API/research/track/playcount-deltas?isrc=$ISRC&since=2026-01-01" -H "x-api-key: $RECOUP_API_KEY" | jq   # delta + annualized run-rate
```

- `source` on `track/stats` / `historic-stats` is optional and must be `spotify`.
- 404 on a track means nothing is stored and there is no album mapping — run a
  `current` measurement job on its album first. There is no historical backfill.
- Counts are platform-displayed play counts, not royalty-bearing streams.

## Web intelligence + events (POST — `Content-Type: application/json`)

```bash
curl -s -X POST "$RECOUP_API/research/web"     -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"query":"...","max_results":10,"country":"US"}'
curl -s -X POST "$RECOUP_API/research/deep"    -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"query":"..."}'
curl -s -X POST "$RECOUP_API/research/people"  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"query":"A&R reps at Atlantic","num_results":10}'
curl -s -X POST "$RECOUP_API/research/extract" -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"urls":["https://..."],"objective":"...","full_content":false}'
curl -s -X POST "$RECOUP_API/research/enrich"  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"input":"...","schema":{"type":"object","properties":{}},"processor":"core"}'
curl -s -X POST "$RECOUP_API/research/events"  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" -d '{"artist_id":"'$ARTIST_ACCOUNT_ID'"}'
```

- `enrich.schema` MUST include `"type":"object"` at the top level. `processor` ∈ `base|core|ultra`.
- **Latency:** `enrich` 60–90s, `deep` 2+ min; set client timeouts ≥3 min or they look "hung."
- `events` resolves through the artist's connected live-events profile; 404 = none connected.

## Credits

On `insufficient_credits` the response carries `remaining_credits`,
`required_credits`, and a `checkoutUrl`; surface the link rather than retrying.
Web search is 1 credit; the measurement-store reads are 5 credits each and only
charge when they answer (a 404 is free); measurement jobs are uncharged but
capped per organization per month (429 at the cap).
