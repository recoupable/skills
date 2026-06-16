# Recoup Research API — endpoints used by this skill

All streaming data is pulled from the Recoup Research API. Spotify play counts
come from Recoup's own measurement store (Apify-first, provenance-labeled);
other sources are Songstats-backed. Base URL: `https://api.recoupable.com/api`.

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
Returns `stats: [{ source, data, data_source, captured_at? }]` + `track_info`.
Spotify entries are served from the measurement store when an `isrc` is given
(`data_source: "apify_spotify_playcount"`, ~24h freshness, no Songstats quota);
other sources are Songstats (`data_source: "songstats"`). The per-source `data`
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

### `GET /research/tracks/{id}/measurements` — per-track measured series + run-rate
The consolidated read for a track's history (replaces `track/historic-stats` **and**
`track/playcount-deltas`). `{id}` is provider-neutral (ISRC or Spotify track id,
resolved server-side).
- default / `?granularity=daily` → `series[]` of `{date, value, data_source}`
  (`value` is cumulative as of `date`). Trailing-12-month = last − first over a
  365-day window. The stitched store series (Apify snapshots + Songstats backfill,
  labeled per point) carries both the measured year and the recent run-rate.
- `?aggregate=run_rate&window=365d` → `aggregate: {kind, window_days, delta,
  run_rate_annualized}` — a server-computed run-rate projection.

`estimate.py` reads the series and derives `measured_365d` (full-year span) vs
`runrate_<N>d` (short span) itself — one read, no legacy endpoints, no client-side
delta calls. Reads no longer auto-enqueue backfill; seed it explicitly (see
`measurement-jobs`).

```bash
curl -sS -H "x-api-key: $RECOUP_API_KEY" \
 "https://api.recoupable.com/api/research/tracks/USA2P2015959/measurements?granularity=daily"
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

### `GET /research/albums/{id}/measurements` — latest per-track counts for an album
`{id}` = Spotify album id; `?latest=true`. Returns `measurements[]` of
`{isrc, spotify_track_id, name, value, captured_at, data_source}` from the most
recent capture (replaces `GET /research/playcounts`). 404 when the album has never
been captured — create a `current` measurement-job (below). Only mapped tracks
are returned.

```bash
curl -sS -H "x-api-key: $RECOUP_API_KEY" \
 "https://api.recoupable.com/api/research/albums/70Zkfb99ladZ3q0JVg97co/measurements?latest=true"
```

### `POST /research/measurement-jobs` — ingest current or historical counts (async)

One async ingest resource for both capture modes (chat#1796). Body:
`{ scope: {album_ids[] | isrcs[] | catalog_id}, source: "current" | "historical" }`.

- `source:"current"` — Apify capture of present counts (**absorbs `POST /research/snapshots`**).
  Returns **202** `{ status, source:"current", id, state:"queued", album_count, estimated_cost_usd }`
  (`id` is the snapshot job).
- `source:"historical"` — enqueue each resolved recording for Songstats deep
  backfill (`rank_score` = all-time streams) so the daily worker fills its full
  daily history. **Idempotent:** songs already carrying `songstats` history are
  skipped; no track is fetched from Songstats twice. Returns **202**
  `{ status, source:"historical", id:null, enqueued, skipped }`.
  **Requires a card on file** — Songstats is metered, so a cardless account gets
  **402** with a Stripe `checkoutUrl` (free tier) instead of a job;
  `estimate.py`'s seed surfaces that link rather than aborting the run.

A `historical` job is the **only** way to backfill at portfolio scale — the
snapshot/portfolio read path enqueues nothing. There is no per-resource status
endpoint; read run status from the generic `GET /api/tasks/runs?runId=`.

```bash
curl -sS -X POST -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
 -d '{"scope":{"album_ids":["70Zkfb99ladZ3q0JVg97co"]},"source":"historical"}' \
 "https://api.recoupable.com/api/research/measurement-jobs"
```

## Resource model (chat#1796, live in prod)

Reads are one `measurements` collection (track series + `aggregate=run_rate` +
album `latest`); writes are one `measurement-jobs` resource (`source:current` for
Apify capture, `source:historical` for Songstats backfill). The old RPC paths —
`track/historic-stats`, `track/playcount-deltas`, `playcounts`, `snapshots` — are
deprecated and removed from the docs; `estimate.py` uses only the consolidated
resources above plus `track/stats`.

## Rate-limit / robustness notes

- Spotify reads never spend Songstats quota (store-served). The Songstats
  rolling quota (~1,000 hits/30d) applies only to non-Spotify sources; for
  portfolio-scale work, snapshot first instead of per-track polling.
- Historic calls return a full daily series; for many tracks, request only the
  sources you need and run sequentially with a per-call timeout (`curl
  --max-time`). `estimate.py` does this and batches to avoid long single calls.
- Always handle `streams_total` as a possibly-stringified float.
- Every read endpoint charges 5 credits and may return **402** with a
  `checkoutUrl` when the account is out of credits; snapshots are uncharged
  but capped per org per month.
- Calibration: snapshot-derived counts agreed with Songstats `streams_total`
  to ±0.1–1.7% on the 679-track Rostrum calibration set (2026-06-09) — label
  them platform-displayed play counts, not royalty-bearing streams.
