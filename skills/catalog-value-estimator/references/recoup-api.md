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

### `GET /research/track/historic-stats` — per-track time series (annualization)
Same identifiers + `source` (required) + `start_date` / `end_date` (ISO).
Returns `stats[].data.history[]` of `{date, streams_total, data_source}` where
`streams_total` is cumulative as of that date. Trailing-12-month streams =
last − first over a 365-day window. Spotify history is a stitched store series
(snapshot captures + backfilled Songstats points, labeled per point); tracks
without backfilled history return their snapshot-only series and are
auto-enqueued for backfill — re-query later, or use playcount-deltas below.

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

### `POST /research/snapshots` — portfolio-scale capture (async)
Body: exactly one of `catalog_id` / `album_ids[]` (Spotify album ids) /
`isrcs[]`; optional `schedule: "once" | "monthly"`. Returns **202** with
`snapshot_id`, `album_count`, and `estimated_cost_usd` (~$0.003/album) before
any scraper spend; **429** at the per-org monthly cap. One album captures all
of its tracks. Counts land in the measurement store within minutes.

```bash
curl -sS -X POST -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
 -d '{"album_ids":["70Zkfb99ladZ3q0JVg97co"]}' \
 "https://api.recoupable.com/api/research/snapshots"
```

### `GET /research/playcounts` — latest per-track counts for an album
`?spotify_album_id=<id>`. Returns `playcounts[]` of `{isrc, spotify_track_id,
name, platform_displayed_play_count, captured_at, data_source}` from the most
recent capture. 404 (with a pointer to `POST /snapshots`) when the album has
never been captured. Only tracks with identifier mappings are returned.

### `GET /research/track/playcount-deltas` — run-rate from snapshot diffs
`?isrc=<isrc>&since=YYYY-MM-DD[&until=YYYY-MM-DD]`. Returns `deltas[]` of
`{platform, metric, since, until, delta, days, run_rate_annualized}` between
the nearest captures — a TTM proxy once two snapshots ≥7 days apart exist.
Empty `deltas` (not an error) when history is insufficient.

### `POST /research/measurement-jobs` — ingest current or historical counts (async)
> **Contract-first / pending api (chat#1791).** This is the target REST ingest
> resource; until the api ships it, `estimate.py` logs the seed as unavailable
> and proceeds. Don't assume it returns 202 yet.

One async ingest resource for both capture modes. Body:
`{ scope: {album_ids[] | isrcs[] | catalog_id}, source: "current" | "historical" }`.

- `source:"current"` — Apify capture of present counts (**absorbs `POST /research/snapshots`**).
- `source:"historical"` — enqueue each resolved recording for Songstats deep
  backfill (`rank_score` = all-time streams) so the daily worker fills its full
  daily history. **Idempotent and free:** songs already carrying `songstats`
  history are skipped; no track is fetched from Songstats twice.

Returns **202** + `Location: /research/measurement-jobs/{id}` and
`{ id, state, enqueued, skipped }`. Poll `GET /research/measurement-jobs/{id}` →
`{ state, enqueued, skipped, cost_usd }`. A `historical` job is the **only** way
to backfill at portfolio scale — the snapshot/portfolio read path enqueues
nothing (only a per-track historic-stats read does).

```bash
curl -sS -X POST -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
 -d '{"scope":{"album_ids":["70Zkfb99ladZ3q0JVg97co"]},"source":"historical"}' \
 "https://api.recoupable.com/api/research/measurement-jobs"
```

## Target resource model (chat#1791) — current paths are deprecated aliases

The read endpoints above are RPC-style and consolidate into one `measurements`
collection; the writes consolidate into `measurement-jobs`. `estimate.py` still
calls the legacy paths until the api migration lands, then repoints:

| Legacy path (in use today) | Target |
|---|---|
| `GET /research/track/historic-stats` | `GET /research/tracks/{id}/measurements?granularity=daily` |
| `GET /research/track/playcount-deltas` | `GET /research/tracks/{id}/measurements?aggregate=run_rate&window=365d` |
| `GET /research/playcounts` | `GET /research/albums/{id}/measurements?latest=true` |
| `POST /research/snapshots` | `POST /research/measurement-jobs {source:"current"}` |
| *(dropped `POST /research/backfill`)* | `POST /research/measurement-jobs {source:"historical"}` |

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
