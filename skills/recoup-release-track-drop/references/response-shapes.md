# Response shapes (production `api.recoupable.dev`)

When you need a field not verified below, **dump it first** rather than
guessing:

```bash
curl -s "$RECOUP_API/<path>" -H "x-api-key: $RECOUP_API_KEY" | jq 'keys'
curl -s "$RECOUP_API/<path>" -H "x-api-key: $RECOUP_API_KEY" | jq '.<array>[0] | keys'
```

## The common envelope

Every endpoint returns `status: "success"` plus flat top-level fields (no `data`
wrapper). `status: "success"` with an **empty array is a valid, common
response** — treat it as "no data," not an error or a zero.

## Verified shapes

### Spotify endpoints → Spotify Web API objects

`GET /spotify/search?q=&type=artist` returns `artists.items[]`; `type=track`
returns `tracks.items[]`. `GET /spotify/artist?id=` returns the artist object:

```jsonc
{ "id": "137W8MRPWKqSmrBGDBFSop", "name": "Wiz Khalifa",
  "followers": { "total": 12345678 }, "popularity": 78,
  "genres": ["hip hop", "pittsburgh rap"], "images": [{ "url": "...", "width": 640, "height": 640 }] }
```

`GET /spotify/artist/albums` returns `items[]` of albums with `id`, `name`,
`release_date`, `album_type`, `images`; `GET /spotify/album?id=` returns the
album with `tracks.items[]` (each with `id`, `name`, `external_ids.isrc`),
`label` and `copyrights`. There is **no** monthly-listener field anywhere.

### `GET /artists/{id}/socials` → `socials[]`
One entry per connected profile: platform, profile URL, follower count, and
the row id used by the scrape endpoint. A `0`/`null` follower count means
"not stored" — omit it.

### `GET /research/playcounts?spotify_album_id=` → `album{}` + `playcounts[]`
```jsonc
{ "status": "success",
  "album": { "spotify_album_id": "4GtuTU…", "name": "Knock Knock", "label": null, "copyright": null },
  "playcounts": [
    { "isrc": "USA2P2015962", "spotify_track_id": "1yBPcg…", "name": "Good Evening",
      "platform_displayed_play_count": 18604195, "captured_at": "2026-08-27T22:52:00Z",
      "data_source": "apify_spotify_playcount" }
  ] }
```
404 when the album has never been captured — create a `current` measurement job.

### `GET /research/track/stats?isrc=` → `stats[]`
```jsonc
{ "status": "success", "result": "success",
  "stats": [ { "source": "spotify", "data": { "streams_total": 1412349476 },
               "data_source": "apify_spotify_playcount", "captured_at": "2026-08-27T22:51:34Z" } ] }
```
One entry, Spotify only. 404 when nothing is stored for the ISRC and no album
mapping exists to refresh from.

### `GET /research/track/historic-stats?isrc=` → `stats[].data.history[]`
`history[]` of `{ date, streams_total, data_source }`, ascending, one point per
capture date, bounded by `start_date` / `end_date`. Older points may carry a
legacy `data_source`; new points are `apify_spotify_playcount`.

### `GET /research/tracks/{isrc}/measurements` → `series[]`
`{ status, id, platform: "spotify", metric: "platform_displayed_play_count",
series: [ { date, value, data_source } ] }`, capped at 1,000 points.

### `GET /research/track/playcount-deltas?isrc=&since=` → `deltas[]`
`{ platform, metric, since, until, delta, days, run_rate_annualized }` between
the nearest captures. Empty `deltas` = not enough history (needs two captures
≥7 days apart), not zero.

### `POST /research/measurement-jobs` → 202
`{ status, source: "current", id, state: "queued", album_count,
estimated_cost_usd }` — `id` is the snapshot id; `reused: true` appears when an
existing fresh capture was handed back.

### `POST /research/web` → `results[]` + `formatted`
`results[]` of `{ title, url, snippet }` plus a `formatted` summary string.
Leads, not facts — keep the URL next to anything you quote.

### `POST /research/events {artist_id}` → `events[]`
One row per show with venue, city, country, date, ticket link and lineup. 404
when the artist has no connected live-events profile.

## The discipline

If a field you expect isn't documented above, stop and `jq keys` the live
response before coding against it — trust what the response actually shows.
