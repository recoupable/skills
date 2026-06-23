# Response shapes (production `api.recoupable.com`, songstats-based)

The research backend is **songstats-based**. When you need a field not verified
below, **dump it first** rather than guessing:

```bash
curl -s "$RECOUP_API/research/<ep>?artist=..." -H "x-api-key: $RECOUP_API_KEY" | jq 'keys'
curl -s "$RECOUP_API/research/<ep>?artist=..." -H "x-api-key: $RECOUP_API_KEY" | jq '.<array>[0] | keys'
```

## The common envelope

Most endpoints return a wrapper, the data in a named array, and an `artist_info`
identity block:

```jsonc
{
  "status": "success",
  "result": "success",
  "message": "Data Retrieved.",
  "<data>": [ ... ],          // results | artists | audience | stats | playlists | tracks | ...
  "artist_info": {
    "songstats_artist_id": "1l65tk4s",
    "id": "1l65tk4s",
    "name": "Wiz Khalifa",
    "avatar": "https://...",
    "site_url": "https://songstats.com/artist/1l65tk4s/wiz-khalifa"
  },
  "source_ids": []            // platform source ids the data was drawn from (often empty)
}
```

`status: "success"` with an **empty data array is a valid, common response** —
treat it as "no data for this artist/platform," not an error or a zero.

## Verified shapes

### `GET /research` (search) → `results[]`
```jsonc
{ "status": "success", "results": [
  { "songstats_artist_id": "1l65tk4s", "id": "1l65tk4s", "name": "Wiz Khalifa", "avatar": "...", "site_url": "..." }
] }
```
The `id` (== `songstats_artist_id`) is what you pass as `id=` to the artist
endpoints, or `artist_id=` to `/research/albums`. No score/`match_strength` — the
first sensible result is the match; disambiguate by `name`/`avatar` if needed.

### `GET /research/similar` → `artists[]`
Same per-artist shape as search (`songstats_artist_id`, `id`, `name`, `avatar`,
`site_url`) — no scores or follower counts. To compare peers, fetch each peer's
`/research/metrics` / `/research/profile` separately.

### `GET /research/profile` → `artist_info{}`
`artist_info` carries `name`, `country`, `bio`, `avatar`, `site_url`, genres/label
where available. There is **no** top-level `sp_followers`. For follower/listener
numbers use `/research/metrics`.

### `GET /research/audience` → `audience[]`
`{ ..., "audience": [], "artist_info": {...}, "source_ids": [] }`. The `audience`
array is **frequently empty even for major artists**. Empty = no demographic
data; do not invent demographics — fall back to `/research/similar` behavior +
`POST /research/web`.

### `GET /research/metrics` → `stats[]`
Requires `source*`. Returns `{ ..., "stats": [ ... ], "artist_info": {...},
"source_ids": [] }` — `stats` is the time-series/metric payload for that source.
Take the latest entry for the current value; introspect with `jq '.stats[0]'`.

## Not-yet-introspected (same envelope — confirm inner fields with `jq keys`)

`urls`, `career`, `insights`, `milestones`, `tracks`, `playlists`, `albums`,
`track`, `track/playlists` all return the common envelope with their own data
array. Their exact inner field names are **not pinned here** — run
`jq '.<array>[0] | keys'` once before coding against them, and prefer the names
the live response actually shows.

- **`milestones`** — `status: "success"` with `milestones: []` is common and legit; don't retry. Fall back to `insights` / `career`.
- **`tracks` / `track`** — track objects carry an `id` you pass to `/research/track` and `/research/track/playlists`. Per-song TikTok fields may or may not be present per track; if absent, report "no data" (never fabricate — see `recoup-research-artist-overview` tiktok mode).
- **`playlists`** (artist-level) — has no editorial/indie filter flags; use `platform` + `status`. For editorial/indie filtering and pagination, use `/research/track/playlists` per track.

## The discipline

If a field you expect isn't documented above, stop and `jq keys` the live
response before coding against it — trust what the response actually shows.
