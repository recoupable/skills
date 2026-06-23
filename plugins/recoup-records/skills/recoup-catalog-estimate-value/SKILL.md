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
- `python3 scripts/build_report.py` — assemble the estimate report.

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
