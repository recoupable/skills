# Recoup Research API — endpoints used by this skill

All streaming data is pulled from the Recoup Research API (Songstats-backed).
Base URL: `https://api.recoupable.com/api`.

## Authentication

Send one of:

- `x-api-key: $RECOUP_API_KEY` — a key from `https://chat.recoupable.com/keys`,
  or in one unauthenticated call:
  ```bash
  export RECOUP_API_KEY=$(curl -s -X POST "https://api.recoupable.com/api/agents/signup" \
    -H "Content-Type: application/json" \
    -d '{"email":"agent+'$(date +%s)'@recoupable.com"}' | jq -r .api_key)
  ```
- `Authorization: Bearer $RECOUP_ACCESS_TOKEN` — already present inside a Recoup
  sandbox.

`scripts/estimate.py` reads `RECOUP_API_KEY` first, then `RECOUP_ACCESS_TOKEN`.

## Endpoints

### `GET /research/track/stats` — per-track current stats
Resolve by `isrc`, `songstats_track_id`, `spotify_track_id`, or
`apple_music_track_id`. `source` (required) is a comma list or `all`.
Returns `stats: [{ source, data }]` + `track_info`. The per-source `data`
includes the absolute play count:
- spotify: `streams_total`
- youtube: `video_views_total`, `short_views_total`
- soundcloud: `streams_total`
- tiktok/instagram: `views_total` (UGC — not used for per-stream gross)
`track_info` carries `title`, `labels`, `distributors`, `links` (with `isrc`).

```bash
curl -sS -H "x-api-key: $RECOUP_API_KEY" \
 "https://api.recoupable.com/api/research/track/stats?isrc=USQY51771120&source=all"
```
Note: `streams_total` may be returned as a numeric string (e.g. `"296422273.0"`)
— parse as float.

### `GET /research/track/historic-stats` — per-track time series (annualization)
Same identifiers + `source` (required) + `start_date` / `end_date` (ISO).
Returns `stats[].data.history[]` of `{date, streams_total, ...}` where
`streams_total` is cumulative as of that date. Trailing-12-month streams =
last − first over a 365-day window.

```bash
curl -sS -H "x-api-key: $RECOUP_API_KEY" \
 "https://api.recoupable.com/api/research/track/historic-stats?spotify_track_id=6RmGzvvqPlVwPqiI11vqT3&source=spotify&start_date=2025-06-09&end_date=2026-06-09"
```

### `GET /spotify/album` — enumerate an album's tracks
Returns the album with `tracks.items[].id` (Spotify track IDs) plus
`copyrights` (the `℗` line) and `label`. Used by
`scripts/fetch_album_tracks.py`.

### `GET /research/tracks` — all tracks for an artist (with ISRCs + Songstats ids)
`?artist=<name>` or `?id=<provider id>`. Returns `tracks[]` with `isrcs` and
`songstats_track_id`. Use to assemble a catalog when starting from an artist.

### `GET /research/lookup` — resolve a Spotify artist URL/ID → provider record
`?spotifyId=<id>`. Returns `artist_info.links` across 18 platforms (incl.
MusicBrainz id) — useful for cross-referencing/ownership.

### `GET /research/metrics` — artist-level metrics (context, not per-track)
`?artist=<name>&source=spotify`. Returns artist totals (`streams_total`,
`monthly_listeners_current`, playlists, charts) across 16 sources. Use for a
roster/portfolio context snapshot, not for per-asset valuation (it's the whole
catalog, not one recording).

## Rate-limit / robustness notes

- Historic calls return a full daily series; for many tracks, request only the
  sources you need and run sequentially with a per-call timeout (`curl
  --max-time`). `estimate.py` does this and batches to avoid long single calls.
- Always handle `streams_total` as a possibly-stringified float.
