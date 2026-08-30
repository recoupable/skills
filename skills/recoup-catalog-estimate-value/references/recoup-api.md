# Recoup Research API — endpoints used by this skill

All streaming data comes from Recoup's own measurement store: Spotify play
counts captured through the Spotify play-count actor, provenance-labeled and
dated. There is no third-party stats provider behind these endpoints. Base URL:
`https://api.recoupable.dev/api`.

## Authentication

Send one of:

- `x-api-key: $RECOUP_API_KEY` — a key from `https://chat.recoupable.dev/keys`,
  or in one unauthenticated call:
  ```bash
  export RECOUP_API_KEY=$(curl -s -X POST "https://api.recoupable.dev/api/agents/signup" \
    -H "Content-Type: application/json" \
    -d '{"email":"agent+'$(date +%s)'@recoupable.com"}' | jq -r .api_key)
  ```
- `Authorization: Bearer $RECOUP_ACCESS_TOKEN` — already present inside a Recoup
  sandbox.

`scripts/estimate.py` reads `RECOUP_API_KEY` first, then `RECOUP_ACCESS_TOKEN`.

## Endpoints

### `GET /research/track/stats` — one track's current Spotify play count
`?isrc=<isrc>` (required; `source` is optional and must be `spotify`). Returns
`stats: [{ source: "spotify", data: { streams_total }, data_source, captured_at }]`
from the measurement store — a fresh capture as-is, a stale one after the
recording's album is refreshed through the play-count actor. **404** when
nothing is stored for the ISRC and there is no album mapping to refresh from:
run a measurement job on the album first. Only served calls are charged.

```bash
curl -sS -H "x-api-key: $RECOUP_API_KEY" \
 "https://api.recoupable.dev/api/research/track/stats?isrc=USQY51771120"
```

### `GET /research/track/historic-stats` — one track's dated series
`?isrc=<isrc>` + optional `start_date` / `end_date` (ISO). Returns
`stats[].data.history[]` of `{date, streams_total, data_source}` where
`streams_total` is cumulative as of that date — one point per capture date the
store holds. Trailing-12-month streams = last − first over a 365-day window,
**only** when captures exist at both ends; there is no historical backfill, so
prefer `playcount-deltas` (below) for run-rate.

```bash
curl -sS -H "x-api-key: $RECOUP_API_KEY" \
 "https://api.recoupable.dev/api/research/track/historic-stats?isrc=USQY51771120&start_date=2025-06-09&end_date=2026-06-09"
```

### `GET /spotify/album` — enumerate an album's tracks
Returns the album with `tracks.items[].id` (Spotify track IDs) and
`tracks.items[].external_ids.isrc`, plus `copyrights` (the `℗` line) and
`label`. Used by `scripts/fetch_album_tracks.py`. To assemble a catalog from an
artist: `GET /spotify/search?q=&type=artist` → `GET /spotify/artist/albums?id=`
→ `GET /spotify/album?id=` per album.

### `POST /research/measurement-jobs` — portfolio-scale capture (async)
Body: `{"scope": {exactly one of "catalog_id" / "album_ids": [Spotify album ids]
/ "isrcs": []}, "source": "current"}`. Returns **202** with `id` (the snapshot
id), `album_count`, and `estimated_cost_usd` (~$0.003/album) before any scraper
spend; **429** at the per-org monthly cap. One album captures all of its
tracks. Counts land in the measurement store within minutes.
`POST /research/snapshots` with `{album_ids, schedule: "once" | "monthly"}` is
the same capture with an optional monthly repeat.

```bash
curl -sS -X POST -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
 -d '{"scope":{"album_ids":["70Zkfb99ladZ3q0JVg97co"]},"source":"current"}' \
 "https://api.recoupable.dev/api/research/measurement-jobs"
```

### `GET /research/playcounts` — latest per-track counts for an album
`?spotify_album_id=<id>`. Returns `playcounts[]` of `{isrc, spotify_track_id,
name, platform_displayed_play_count, captured_at, data_source}` from the most
recent capture. 404 when the album has never been captured. Only tracks with
identifier mappings are returned.

### `GET /research/tracks/{isrc}/measurements` — every capture for a track
Returns `series[]` of `{date, value, data_source}` (capped at 1,000 points).

### `GET /research/track/playcount-deltas` — run-rate from snapshot diffs
`?isrc=<isrc>&since=YYYY-MM-DD[&until=YYYY-MM-DD]`. Returns `deltas[]` of
`{platform, metric, since, until, delta, days, run_rate_annualized}` between
the nearest captures — a TTM proxy once two snapshots ≥7 days apart exist.
Empty `deltas` (not an error) when history is insufficient.

## Robustness notes

- For portfolio-scale work, capture first (one measurement job per album set)
  and read `playcounts` per album instead of polling `track/stats` per track —
  the per-track read refreshes a whole album when its capture is stale.
- Run per-track series calls sequentially with a per-call timeout (`curl
  --max-time`); `estimate.py` does this and batches to avoid long single calls.
- Every served read charges 5 credits and may return **402** with a
  `checkoutUrl` when the account is out of credits; 404s are free; measurement
  jobs are uncharged but capped per org per month.
- Calibration: snapshot-derived counts agreed with the previous provider's
  reported totals to ±0.1–1.7% on the 679-track Rostrum calibration set
  (2026-06-09) — label them platform-displayed play counts, not
  royalty-bearing streams.
