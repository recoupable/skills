# Methodology & Assumptions

This file is the auditable assumption set behind every number the estimator
produces. The defaults live in `scripts/estimate.py` (the `DEFAULTS` block) and
can be overridden with `--config config.json`. Read this before quoting any
figure, and cite the relevant lines when you present results.

## 1. Streams → gross receipts (master side)

Gross master receipts ≈ Σ (streams on platform × public per-stream rate). 2025
public rates (USD per stream/view), used as defaults:

| Platform | Rate | Measured by API? |
|---|---|---|
| Spotify | $0.0035 (range 0.003–0.005) | ✅ `streams_total` |
| YouTube | $0.00069 (video views) | ✅ `video_views_total` (+ `short_views_total`) |
| SoundCloud | $0.0030 (range 0.0025–0.004) | ✅ `streams_total` |
| Apple Music | ~$0.01 | ❌ not exposed → gross-up |
| Amazon | ~$0.004 | ❌ not exposed → gross-up |
| Tidal | ~$0.0128 | ❌ not exposed → gross-up |
| Deezer | ~$0.004 | ❌ not exposed → gross-up |
| TikTok / Instagram | n/a (UGC / lump-sum license) | excluded from per-stream gross |

**Measured gross** = Spotify + YouTube + SoundCloud (the platforms the API
returns stream counts for). Treat this as a **floor**.

**Other-DSP gross-up.** Apple/Amazon/Deezer/Tidal stream counts are not exposed,
so approximate their revenue as a labeled percentage *of Spotify gross*. Apple
alone often rivals Spotify revenue (it pays ~3× the per-stream rate on a smaller
stream base). Default band: **+25% / +40% / +60%** of Spotify gross
(low/central/high). This is the largest source of measurement uncertainty —
always show it as a band.

## 2. Gross → Net Label Share (NLS)

NLS is what the label keeps. `NLS = gross × (1 − distribution%) × (1 − royalty%)`.

- **Distribution fee** — the distributor's cut. Default **15%**. (Check the
  `distributors` field on the track; e.g. WMG/Warner-distributed catalogs carry
  a real Warner fee.)
- **Artist + producer royalties** — the performer's and producers' share of net
  receipts. Default **25%** blended. For catalogs old enough to be recouped,
  royalties are paid through, so this is a real reduction to the owner's keep.
- Resulting **NLS ≈ 55%–70% of gross** (central ~64%). Carry the band.

If valuing **publishing** instead, compute **NPS (Net Publisher Share)** on the
composition side with its own splits — do not merge NPS and NLS into one "net".

## 3. Annualization (the run-rate that gets the multiple)

Value is built on **sustainable annual** NLS, not lifetime totals. Get the
annual run-rate from `track/historic-stats`: `streams_total` is cumulative as of
each date, so

> **trailing-12-month streams = streams_total(end_date) − streams_total(end_date − 365d)**

Use the cumulative values at the two window endpoints (robust to flat/duplicate
snapshot days); don't sum daily deltas. Spotify TTM is measured precisely;
approximate YouTube/SoundCloud TTM at their all-time share of Spotify gross to
avoid extra calls (small contributors). Day-level history generally begins
~2021, so trajectories may be ~5 years even for older catalogs.

**TTM derivation labels.** Every track's TTM carries a `ttm_source`:

- `measured_365d` — true 365-day diff from the stitched historic series. The
  gold standard; use whenever backfilled history spans the window.
- `runrate_<N>d` — annualized from snapshot deltas over an N-day capture
  window (`track/playcount-deltas`). A **proxy**, accepted only when
  N ≥ `min_delta_days` (default 28): short windows embed release spikes,
  viral noise, display-count update lag, and uncorrected seasonality (Q4
  typically runs +20–30% vs January). Expect ±misstatement vs measured TTM
  that shrinks as windows lengthen; do not mix derivations silently — the
  estimate reports the mix and TTM coverage in `provenance`.
- `insufficient_window` / `none` — no accepted TTM; the track contributes
  all-time presence but $0 to the TTM-based value (state the coverage %).

When a material share of value rides on `runrate_*`, say so next to the
headline and prefer re-running after a longer capture window or backfill.

**Seeding the backfill (how `runrate_*` becomes `measured_365d`).** A
`measured_365d` TTM requires a full year of daily history, which only the
Songstats backfill worker supplies. That worker drains a queue, and **the
snapshot/portfolio read path never fills it** — so `estimate.py` in portfolio
mode seeds the catalog explicitly via `POST /research/backfill`. Two rules:

- **Prioritize head-first.** The queue is ranked by all-time streams, and so is
  the seed. The value-bearing head dominates — for a multi-thousand-track
  catalog the top several hundred tracks carry essentially all the NLS — so seed
  (and judge "enough coverage") by value, not by raw track count.
- **Respect the quota ceiling.** One Songstats hit backfills one track's entire
  history, permanently (it is never re-fetched). The plan allows ~1,000 hits per
  rolling 30 days, ~100 reserved, so ≈900 tracks/30d. Backfilling the
  value-bearing head (hundreds of tracks) is ~1 month; a full several-thousand
  track catalog is several months and consumes nearly the whole research quota
  for the duration. Seed the head, report `deep_history_share`, and let coverage
  climb across cron runs rather than claiming full measured coverage on day one.

## 4. NLS → value (the multiple)

`value = annual NLS × multiple`. Master catalogs have traded broadly **8×–16×**
NLS in recent years (publishing higher). Default band **10× / 13× / 16×**
(low/central/high). The multiple is the biggest swing in the whole model:

- **Down** the band: single-track concentration, flat/declining run-rate,
  unsupported rights, sample-dependent income.
- **Up** the band: diversified, durable/evergreen, *growing* run-rate, clean and
  documented rights.

Choose the band deliberately and say *why* — a defensible value names the
multiple's drivers.

## 5. Risk metrics that move the multiple

- **Concentration.** Top-track and top-3 share of trailing-12-month streams. A
  catalog where one track is the majority of streams is underwritten at a
  discount and sits lower in the multiple band. Report the share as a neutral
  observation; do not turn it into a growth recommendation in the baseline.
- **Trajectory.** YoY change in annual streams: growing vs plateaued vs
  declining. Plateau/decline ⇒ mid/low multiple.
- **Rights flags.** Sample-driven hits (a share of income may flow to the
  sampled rights holders; clearance affects transferability), missing
  registrations (use SoundExchange ISRC Search / MLC to detect leakage),
  reversions, territory limits. Flag, don't assume.

## 6. Calibration

If a public comp exists (reported sale or ask), compare — but **match scope**: a
single album is a fraction of a multi-album, multi-artist portfolio. A central
estimate landing at a sensible fraction of the comp is a passing sanity check;
a wild divergence means revisit assumptions (usually the multiple or the
gross-up).

## 7. The verification loop (turning assumptions into actuals)

Every default above is an industry estimate. When one real royalty statement
from the owner becomes available:

1. Solve for their **true blended per-stream rate** (their reported receipts ÷
   their streams for the period).
2. Solve for their **real deduction stack** (reported NLS ÷ gross).
3. Replace the defaults in `--config` and re-run; the band collapses toward a
   point.
4. Report the accuracy of the prior permissionless estimate, and fold the
   correction forward so the next catalog is estimated better with no statement.

## 8. Scope caveats to print in every output

- Master-side only unless publishing is explicitly modeled.
- Measured = Spotify/YouTube/SoundCloud; other DSPs approximated.
- TikTok/Instagram excluded from per-stream gross (UGC/lump-sum).
- Figures are estimates derived from public rates, **not reported royalties**.
