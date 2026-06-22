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

## Refined social metrics — exact followers + real bios via the API (no scraping, no Supabase)

Recoup keeps a `socials` store with **`username`, `profile_url`, `follower_count`, `following_count`,
`bio`, `avatar`, `region`** — richer and **exact** vs. the rounded "1M" a public Instagram
`og:description` shows. Onboard the valued artist and pull this entirely over the API. Full flow, all
on `https://api.recoupable.com` (confirmed working with a Bearer Privy JWT, **including writes** — the
old "Privy tokens don't verify on prod" note was wrong). This is **part of working the lead**, not
overkill: it also lands the artist in the lead's own Recoup workspace so the metrics stay refreshable.

1. **Resolve the lead's account** — `POST /api/accounts {"email": "<lead email>"}`. Idempotent: if the
   account already exists it is returned (with `account_id`). This is the email→`account_id` lookup —
   **use this, not Supabase**.
2. **Create the artist under the lead's account** —
   `POST /api/artists {"name": "<artist>", "account_id": "<lead account_id>"}` → returns the new
   **artist account id** as `artist.account_id`. Pass `account_id` only when your token's account has
   org access to the lead's account; otherwise the artist is created under your own account.
3. **Attach the verified profile URLs** —
   `PATCH /api/artists/{artistAccountId} {"profileUrls": {"INSTAGRAM": "...", "SPOTIFY": "...",
   "YOUTUBE": "...", "FACEBOOK": "..."}}`. **Keys must be UPPERCASE** (`SPOTIFY`, `INSTAGRAM`,
   `TIKTOK`, `TWITTER`, `YOUTUBE`, `APPLE`, `FACEBOOK`, `THREADS`) — lowercase silently creates
   duplicate socials instead of replacing.
4. **Trigger the scrape** — one platform: `POST /api/socials/{social_id}/scrape` (get `social_id` from
   `GET /api/artists/{artistAccountId}/socials`); all platforms at once:
   `POST /api/artist/socials/scrape {"artist_account_id": "<artistAccountId>"}`. Each returns
   `{runId, datasetId}` (Apify).
5. **Poll, then read back** — `GET /api/apify/runs/{runId}` until `status` is `SUCCEEDED`, then
   `GET /api/artists/{artistAccountId}/socials` for the real `follower_count` + `bio` per platform.
   `GET /api/artists?account_id=<id>` lists artists under an account to confirm the setup.

Live-run caveat (Ulices Chaidez, 2026-06-22): the **Instagram** actor returned an exact 1,276,417
(vs the rounded "1M" public meta) plus the real bio, but the Spotify/YouTube/Facebook actors returned
empty `bio`/`follower_count` on that pass. For those, fall back to the platform page — read it via the
**authenticated browser (chrome-devtools MCP)**, since LinkedIn/Instagram block `WebFetch` (HTTP 999).
Put **only real platform bios** in the lead JSON `socials[].bio` (no editorial filler; leave blank if
unverified).

## The tool's number is often a partial run — always re-measure the full catalog

The free valuation charges credits per measurement, so a large catalog can exhaust the lead's credits
mid-run and report a value built on only **part** of the catalog (Chilled Cat: ~27% measured, ~$290K
shown vs ~$1.08M full; Ulices Chaidez: 115.5M streams shown vs ~1.25B measured, ~11x). You don't need
to check credits to catch this — `fetch_catalog.py` already pages the **whole** catalog, so just
re-measure and compare to the tool's figure. A big gap means the run was cut short — reframe the
outreach as *"we finished your interrupted run."*

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
