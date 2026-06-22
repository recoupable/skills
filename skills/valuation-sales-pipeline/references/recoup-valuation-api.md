# Recoup valuation API — pull a lead's catalog directly (no scraping)

The marketing valuation tool (`recoupable.com/valuation`) is just a thin client over **public
Recoup APIs**. Call them directly — `scripts/fetch_catalog.py` does exactly this — instead of
scraping the UI. Base: `https://recoup-api.vercel.app` (or `https://api.recoupable.com`).
Auth: `x-api-key: $RECOUP_API_KEY` (or `Authorization: Bearer $RECOUP_ACCESS_TOKEN`).

## The flow the UI runs

1. **Resolve the artist** — `GET /api/spotify/search?q=<name>&limit=5` → pick the artist id.
2. **List the catalog (with album art)** —
   `GET /api/spotify/artist/albums?id=<artistId>&include_groups=album,single&limit=50&offset=0`
   → `items[]` each with `name`, `id`, `release_date`, `total_tracks`, and `images[]`
   (640/300/64px — use the 300px URL for the PDF).
3. **(optional) warm the store** — `POST /api/research/measurement-jobs` triggers a fresh live
   measurement. The UI calls this first; for an already-measured artist the store already has data.
4. **Per-album play counts** — `GET /api/research/albums/<albumId>/measurements` →
   `measurements[]` of `{isrc, spotify_track_id, name, value, captured_at, data_source}`. Sum
   `value` per album for release-level streams; sum across albums for lifetime streams.
5. **Lead capture** (marketing site only) — `POST /api/valuation/lead` writes the Attio lead.

## Why this beats scraping

- **Album art comes free** from step 2 (`images[]`) — no DOM parsing.
- **Store-served, no 429.** Album measurements return `data_source: "apify_spotify_playcount"` —
  they read Recoup's measurement store, **not** Songstats, so they don't hit the Songstats quota
  that 429s the artist-name research endpoints.
- **More accurate than a UI snapshot.** The live UI can render a release as "0 streams" if its
  measurement job hasn't finished yet. The store backfills within minutes — re-read and it's there.
  Don't infer "dormant catalog" from a `$0` row in the UI; confirm against the measurements endpoint.

## Eventual consistency (read this before trusting a single pass)

Measurements are **eventually consistent**. A single read can be partial — the same artist has read
back as `0 dormant / 34 tracks` on one call and `13 dormant / 22 tracks` minutes later, purely from
in-flight measurement jobs. So:

- `fetch_catalog.py` **retries** empty albums a few times; for a high-stakes report, run it twice and
  keep the larger result, or wait a minute and re-run until track/stream counts stabilize.
- Dedupe tracks by `spotify_track_id`/`isrc` when totalling lifetime streams and track count — some
  tracks are cross-listed across albums (singles that also appear on an album/compilation), so a naive
  per-album sum double-counts. `fetch_catalog.py` does this.
- Optionally `POST /api/research/measurement-jobs` first to warm the store before reading.

## What the API does NOT give you

Dollar figures (catalog value, per-release value) are a **model output**, not an API field. Take
the band the marketing tool displays, or compute it with the `catalog-value-estimator` skill
(streams → annual NLS → × multiple). `fetch_catalog.py` fills streams + art + counts and leaves
the dollar fields for you to add.
