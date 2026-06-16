---
name: catalog-value-estimator
description: >-
  Estimate the value and performance of a music catalog, album, or individual
  recording from public/streaming data alone — no seller files, no royalty
  statements required. Use this whenever the user wants to value a catalog or
  asset, project annual Net Label Share (NLS) or Net Publisher Share, build a
  catalog/portfolio baseline, measure how an asset is performing over time, run
  a "streams → revenue → value" model, or produce an executive baseline report —
  even if they don't say the words "Catalog Value Estimator". Triggers include
  "what is this catalog worth", "value the K.I.D.S. masters", "estimate NLS",
  "how is this album performing", "build a portfolio baseline", "streams to
  revenue", "annualize streams", "catalog value from public data", or any
  request to size/track a master or publishing asset using Songstats/streaming
  data via the Recoup Research API. Prefer this skill over hand-rolled curl when
  the goal is a defensible, reproducible value or performance number.
---

# Catalog Value Estimator

Turn public streaming data into a defensible, reproducible estimate of a music
asset's **performance** and **value** — assembled with zero seller cooperation,
so it can be produced before a deal, used to verify a counterparty's claims, or
frozen as a baseline to measure impact over time.

The whole method rests on one identity:

> **Catalog value = sustainable annual Net Label Share (NLS) × a market multiple**

NLS is what the owner *keeps* after distribution and artist/producer royalties —
not gross streaming revenue. The job of this skill is to measure real streams,
convert them to annual NLS through a labeled, auditable assumption stack, apply
a multiple, and surface the risks (concentration, rights flags) that move the
multiple — all while being honest about what is *measured* vs *assumed*.

## Scope: a factual baseline, nothing more

This skill produces a **baseline** — a frozen, defensible snapshot of what a
catalog *is and currently earns*, built so the owner can audit every number.
Everything it outputs is either **measured** (streams pulled live) or a
**labeled, auditable assumption** (per-stream rates, the deduction stack, the
multiple). That is the whole deliverable.

**It deliberately does not:**

- project uplift, growth, or "ΔV" from any intervention;
- estimate recoverable or "found" income, or quantify leakage in dollars;
- recommend actions, name opportunities, or describe what Recoup *would do* to
  improve the catalog.

Those are intervention-phase claims. Until they can be measured against a frozen
baseline (and, ideally, calibrated against a real royalty statement), they are
not verifiable — and an unverifiable claim in a baseline costs the trust the
baseline exists to build. Risk factors are reported as **neutral observations**
of what they are, never as a to-do list. Keep forward-looking work out of this
artifact entirely; it belongs in a separate, later deliverable.

## When to use this

Reach for this skill for any of: valuing a catalog/album/track, projecting
annual NLS, building a portfolio baseline, tracking an asset's performance over
time, or producing a streams→revenue→value report. It works on one recording or
thousands. It does **not** need royalty statements — when those exist, use them
to calibrate (see "Verification loop").

## Prerequisites

- **Recoup API access.** All streaming data comes from the Recoup Research API
  (Songstats-backed). Set `RECOUP_API_KEY` (sent as `x-api-key`) **or**
  `RECOUP_ACCESS_TOKEN` (sent as `Authorization: Bearer`). In a Recoup sandbox
  `RECOUP_ACCESS_TOKEN` is already present. To get a key, see
  `references/recoup-api.md`.
- `python3` with `matplotlib` and `reportlab` (only for the PDF report):
  `pip install --break-system-packages matplotlib reportlab`.
- `curl` available on PATH (the scripts shell out to it).

## The loop (five steps)

1. **Assemble the asset + identifiers.** Resolve the recordings you want to
   value into Spotify track IDs or ISRCs, and confirm ownership from public
   metadata (the `℗`/P-line, `labels`, and `distributors` returned by the API).
   - Have ISRCs or Spotify track IDs already → skip to step 2.
   - Have a Spotify album → `scripts/fetch_album_tracks.py --album <id|url>`
     prints the track IDs.
   - Have only an artist/label name → resolve the catalog first (see
     `references/recoup-api.md`: `lookup`, `tracks`),
     then feed the IDs in.
2. **Measure streams.** For every track, pull all-time per-platform counts
   (`/research/track/stats`) and the trailing-12-month delta
   (`/research/track/historic-stats`, diff the cumulative `streams_total` at the
   window endpoints). `scripts/estimate.py` does both. Spotify counts are
   served from Recoup's measurement store (Apify-first; every entry carries
   `data_source` + `captured_at` provenance) — they are platform-displayed
   play counts, quota-free and refreshed within ~24h.
   - **Portfolio scale (hundreds–thousands of tracks):** snapshot first —
     `POST /research/snapshots` captures every track of every album in one
     async job (~$0.003/album, cost estimate returned before spend), then read
     `GET /research/playcounts?spotify_album_id=…` per album. Two snapshots
     ≥7 days apart give per-track run-rates via
     `GET /research/track/playcount-deltas` — a TTM proxy that needs no
     Songstats history. See `references/recoup-api.md`.
   - **Seed deep historical backfill (portfolio mode does this automatically).**
     A real `measured_365d` TTM needs a full year of daily history, which only
     the Songstats backfill worker can supply. That worker drains a queue — and
     **the snapshot/portfolio path never fills it** (only a per-track
     historic-stats read enqueues a track). So `estimate.py` in `--album-ids`
     mode explicitly creates a *historical ingest job* —
     `POST /research/measurement-jobs {scope, source:"historical"}` (ranked by
     all-time streams, deduped server-side, free). The daily cron then drains it
     within quota; re-run the estimate later and run-rate TTMs upgrade to
     `measured_365d`. Disable with `--no-backfill-seed`. Quota is the ceiling
     (~900 hits / 30 days, one per track) — see `references/methodology.md` for
     the head-first prioritization, and `references/recoup-api.md` for the
     `measurement-jobs` + `measurements` resource model (chat#1791) that the
     legacy per-track endpoints consolidate into.
3. **Model gross → NLS → value.** Apply public per-stream rates, the deduction
   stack, and the multiple band from `references/methodology.md`. Keep
   *measured* platforms separate from *approximated* ones and carry a band, not
   a point.
4. **Observe risk (neutrally).** Compute concentration (top-track and top-3
   share of streams) and note the factors that move the multiple —
   single-track dependency, plateauing run-rate, sample-driven hits,
   registration gaps. Report each as a *neutral observation of what it is*
   (e.g. "top track is 70% of TTM streams"), not as an opportunity, a
   remediation step, or a dollar of upside. These observations are as
   important as the dollar figure.
5. **Report.** Emit the structured results, and — if the user wants something
   shareable — a branded executive PDF via `scripts/build_report.py`.

Run steps 2–4 with one command:

```bash
python3 scripts/estimate.py \
  --ids <comma-separated Spotify track IDs>   # or --isrcs / --ids-file
  --asset-name "K.I.D.S." --owner "Rostrum Records" \
  --out ./out
# -> out/estimate.json (full results) + out/summary.md (human-readable)
```

Then, optionally:

```bash
python3 scripts/build_report.py --estimate ./out/estimate.json --out ./out
# -> out/<asset>-baseline-report.pdf  (charts + valuation + methodology)
```

`estimate.py` and `build_report.py` are the workhorses — don't re-derive their
logic inline; call them so every run is identical and auditable.

## Reading the output

`estimate.json` contains, per asset: all-time and trailing-12-month streams per
platform, gross/NLS/value with low–central–high bands, the per-track table, the
concentration metrics, and the exact assumption set used (so any number can be
traced back). `summary.md` is the same thing in prose + a table.

The `provenance` block reports measurement honesty, including
`deep_history_share` (fraction of tracks on a true `measured_365d` TTM) and
`backfill_seed` (what the run enqueued). On a freshly seeded catalog
`deep_history_share` starts low and the value leans on `runrate_*` proxies;
it climbs toward 100% as the backfill worker drains over the following weeks.
State that coverage when sharing a portfolio baseline — it is the difference
between a measured number and a run-rate estimate.

Lead with what's **measured** (streams are real, pulled live) and present the
dollar figures as a **directional model** with assumptions visible. This matters
especially when sharing with a rights owner who knows their real numbers —
overclaiming a value you derived from public rates costs credibility.

## Honest limits (state these in any output)

- **Measured vs approximated platforms.** Songstats exposes per-track streams
  for Spotify, YouTube, and SoundCloud; Apple/Amazon/Deezer/Tidal return
  playlist data but not stream counts, so their revenue is a labeled gross-up.
  The measured-platform figure is a floor; true revenue is higher.
- **Master-side only by default.** This values recordings (NLS). Publishing
  (NPS — mechanical + performance) is separate and additive; only model it if
  the owner controls the compositions.
- **History depth.** Spotify history is a stitched series from Recoup's
  measurement store: snapshot captures (2026-06 onward) plus backfilled
  Songstats points (day-level, typically from ~2021), each point labeled with
  `data_source`. A track only has the deep series once the Songstats backfill
  worker has filled it. **Enqueueing is not automatic for portfolio runs:** a
  per-track `historic-stats` read enqueues lazily, but the snapshot/portfolio
  path does not — that is why portfolio mode seeds the backfill explicitly
  (Step 2). Until a track is drained it returns its snapshot-only series, so
  early portfolio runs lean on `runrate_*` TTMs; re-run after the worker drains
  to pick up `measured_365d`. The all-time cumulative always reflects the full
  life regardless.
- **Every rate, deduction, and multiple is an assumption** (see methodology).
  The multiple is the single biggest swing — concentration and a flat run-rate
  argue for the low end.

## Calibration & the verification loop

When a public comp exists (a reported sale/ask), sanity-check the estimate
against it — but match scope (a single album vs a multi-album, multi-artist
portfolio). When a real royalty statement becomes available, solve for the
counterparty's true blended per-stream rate and deduction stack, replace the
defaults, and the band collapses. Each real statement makes the next
permissionless estimate more accurate — fold corrections back into the config.

## What to read next

- `references/methodology.md` — the full assumption set: per-stream rates, the
  gross→NLS deduction stack, multiple bands, the gross-up, the TTM annualization
  mechanic, calibration, and caveats. **Read this before quoting any number.**
- `references/recoup-api.md` — auth and the exact endpoints used (`track/stats`,
  `track/historic-stats`, `tracks`, `lookup`, `spotify/album`), with examples.
