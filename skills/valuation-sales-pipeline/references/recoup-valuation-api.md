# Recoup valuation API — pull a lead's catalog directly (no scraping)

The marketing valuation tool (`recoupable.com/valuation`) is just a thin client over **public
Recoup APIs**. Call them directly — `scripts/fetch_catalog.py` does exactly this — instead of
scraping the UI. Base: `https://recoup-api.vercel.app` (or `https://api.recoupable.com`).
Auth: `x-api-key: $RECOUP_API_KEY` (or `Authorization: Bearer $RECOUP_ACCESS_TOKEN`).

> **Auth gotcha — the key and the token cover different routes.** A hex `x-api-key` authorizes
> `/api/spotify/*` (search, albums, art) but is **rejected by `/api/research/*`** (the per-album
> measurements and the estimator). Those need a **Bearer access token** (`RECOUP_ACCESS_TOKEN`, e.g.
> a Privy session JWT), which **expires in ~1 hour** ("Authentication token expired"). If a catalog
> reads back as **0 streams across every album**, it's almost always this — a hex key or an expired
> token on `/research/*`, not a dormant catalog. Use the Bearer token for measurement work and grab a
> fresh one when it 401s.

## The flow the UI runs

1. **Resolve the artist** — `GET /api/spotify/search?q=<name>&limit=5` → pick the artist id.
2. **List the catalog (with album art)** —
   `GET /api/spotify/artist/albums?id=<artistId>&include_groups=album,single&limit=50&offset=<n>`
   → `items[]` each with `name`, `id`, `release_date`, `total_tracks`, and `images[]`
   (640/300/64px — use the 300px URL for the PDF). **Page it:** the cap is 50, so walk `offset`
   in steps of 50 until a short page — large catalogs run to hundreds of releases and a single
   page silently truncates them. `fetch_catalog.py` does this.
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

## Refined social metrics (followers, bio, avatar, region)

Recoup keeps a `socials` store with **`username`, `profile_url`, `followerCount`, `followingCount`,
`bio`, `avatar`, `region`** — richer than a handle alone. Flow:

- `GET /api/artists/{artist_account_id}/socials` — read stored socials for a platform artist.
- `POST /api/socials/{id}/scrape` (or `POST /api/artist/socials/scrape` with `{artist_account_id}`)
  — trigger an **Apify-backed** scrape; returns `{runId, datasetId}`; poll Apify for results, which
  land back in the `socials` store.

Caveat: this is keyed to a **platform artist account + stored social records**, not arbitrary
handles. A fresh valuation lead (e.g. an artist you only have a Spotify id for) usually has **no
socials rows yet** — you'd onboard the artist (see `recoup-essentials`/`recoup-create-artist`),
attach the profile URLs, then scrape. Worth it for ongoing/refreshable metrics + `region` (audience
geography) and `avatar`; overkill for a one-off report.

**For a one-off report**, get the handles from the artist's official release upload / label page
(cross-checked to the Spotify id) and read live follower/bio counts directly — that's what the
bundled ICEBOX example did when the socials store had no rows yet.

## Spotting a truncated free run (credits)

The free valuation charges credits per measurement, so a **large catalog can exhaust the lead's
credits mid-run** — the tool then reports a value computed on a *partial* catalog, undercounting
badly (Chilled Cat: only ~27% of the catalog measured, ~$290K shown vs ~$1.08M on the full catalog).
Before trusting the tool's figure for a big catalog, check the lead's remaining credits via Supabase
(service key in `mono/api/.env.local`): `account_emails` (email → `account_id`) →
`credits_usage.remaining_credits` (333 free grant). A **near-zero balance timestamped at the
valuation time** means the run was cut short — **re-measure the full catalog** with `fetch_catalog.py`
(it now pages all albums) and reframe the outreach as *"we finished your interrupted run."*

## What the API does NOT give you

Dollar figures (catalog value, per-release value) are a **model output**, not an API field. Take
the band the marketing tool displays, or compute it with the `catalog-value-estimator` skill
(streams → annual NLS → × multiple). `fetch_catalog.py` fills streams + art + counts and leaves
the dollar fields for you to add.

**The estimator's value is trailing-12-month-driven and needs history.** It prices on TTM streams
derived from snapshot deltas (`/research/track/playcount-deltas`, which needs ≥2 captures ≥7 days
apart). A brand-new lead has only a single capture date → **TTM 0 → value $0** — you cannot recompute
a rigorous dollar figure same-day. Two honest workarounds: (a) scale the marketing tool's own
per-stream basis for *that* artist (`tool_value / tool_streams_measured`) to the full live catalog;
or (b) trigger snapshots now and re-run the estimator in ~4 weeks once a trailing window exists.
