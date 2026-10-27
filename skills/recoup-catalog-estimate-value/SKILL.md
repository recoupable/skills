---
name: recoup-catalog-estimate-value
description: Estimate a catalog, album, or song's value from public streaming data alone — no seller files or data room required. Use for "what's this catalog worth from public data", "ballpark this catalog", or "estimate the value of [album/song]". Wider error bars than a seller-file valuation; states its assumptions. For full diligence on a real data room use recoup-catalog-review-deal.
---

# Recoup Catalog — Estimate Value

Value a catalog/album/recording from **public/streaming data alone** — the clean-room
cousin of a full valuation. Deterministic scripts ship in `scripts/` (invoke
relatively); methodology + API contract in `references/`.

## Procedure

- `python3 scripts/fetch_album_tracks.py` — pull the catalog from public sources.
- `python3 scripts/estimate.py` — estimate streams→revenue→value per
  `references/methodology.md` (uses `references/recoup-api.md`).
- `python3 scripts/build_report.py` — assemble the estimate report (needs
  `pip3 install reportlab`).

Be explicit that this is a **public-data estimate** (wider error bars than a
seller-file valuation), and state the assumptions. For a real data room with seller
files, use recoup-catalog-review-deal instead.

## Guardrails

- **estimate ≠ valuation** — public-data estimates carry wider error bars; say so.
- **State assumptions** — never present an estimate as an audited valuation.

## References & scripts

- `references/methodology.md` · `references/recoup-api.md`
- `scripts/estimate.py` · `scripts/fetch_album_tracks.py` · `scripts/build_report.py`
  — ship alongside this skill; invoke relatively.


## Coverage and reproducible output

Freeze the input population, identities, measurement period, currency and rights scope.
Read `references/methodology.md` before using any numerical default. They are illustrative,
unverified scenarios, not a refreshed market rate card. Preserve dated sources and rationale
in the config. Public metadata never proves the user's controlled interest.

The helper supports master-side scenarios only. Missing annual measurements produce null
money, not zero; partial coverage produces a covered-subset scenario, never an unqualified
catalog-wide value. A complete input subset still does not prove all platforms or rights.
The modeled net factor already includes deductions: do not subtract fees a second time.
Do not convert all-time YouTube views to annual owner income using a Spotify ratio.

For supplied observations, no API/account is needed:

```bash
python3 scripts/estimate.py --observations /private/work/observations.json --config /private/work/assumptions.json --out /private/work/estimate
python3 scripts/build_report.py --estimate /private/work/estimate/estimate.json --out /private/work/estimate
```

The observation JSON has `tracks` (unique `id`, `title`, `sp_ttm`, `ttm_source`, optional
`sp`, `captured_at`, `data_source`) and explicit `population_complete`. Accepted annual
sources are `measured_365d` or `runrate_Nd` from inspected underlying windows; never invent
these labels for missing data. Keep the original evidence with the case. Network mode
uses existing credentials; missing portfolio snapshots are only created with explicit
`--snapshot` authorization. Reads may themselves have a billing gate; honor it.

Return the JSON workpaper and bounded summary/PDF. Preserve prior public scenarios when
new contracts/statements support a deal review or accounting stage. Calibrate only
comparable rights, services, currency, period and measurement coverage; one statement
does not eliminate residual uncertainty. Run `python3 -m unittest discover -s tests`
from this skill to check calculation and missing-coverage behavior.

For the development-only Catalog scenario contract, read `references/scenario-contract.md`.
`scripts/scenario.py` reuses the existing model for one explicit Spotify-rate sensitivity;
it is a local domain reference, not browser integration or a verified rate card.
