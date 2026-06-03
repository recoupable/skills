---
name: recoup-catalog-analyze
description: Run normalized-catalog analysis (royalties, risk, concentration, valuation scenarios) — Phases 3 and 4 only. Use whenever the user types `/recoup-catalog-analyze`, says "refresh the analysis", "rerun the valuation analysis", "update the workpapers", or wants to refresh the analysis phase after editing ingest output or assumptions. For full end-to-end runs prefer /recoup-catalog-deal.
argument-hint: [deal-id]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Catalog Analyze

Use the `recoup-catalog-analysis`, `recoup-royalty-audit`, and `recoup-rights-review` skills as
needed.

> **Most users should run `/recoup-catalog-deal` instead** — that command
> chains kickoff → ingest → analysis → dashboard → memo without
> stopping. This command is the analysis phase only, for analysts who
> already have normalized data and want to refresh workpapers.

## Steps

1. Run `python3 scripts/run-deal-checks.py deals/{deal-id}`.
   Validator failures must be cured before analysis.
2. Confirm whether analysis is for buy-side acquisition, seller prep, or
   financing.
3. Compute or review normalized NPS/NLS. Write the bridge JSON files the
   dashboard reads:
   - `workpapers/nps-bridge.json`
   - `workpapers/nls-bridge.json`
   - `workpapers/valuation-summary.json` (with `normalized` and
     `scenarios` keys — see `/recoup-catalog-deal` Phase 4 for the schema).
4. Run `python3 scripts/calculate-concentration.py` and
   `python3 scripts/calculate-nps-nls-bridge.py` when normalized inputs
   are available.
5. Launch specialist sub-agents for rights, royalty, and valuation
   review **in parallel** (single message with three Task calls) when
   the deal is material.
6. Write workpapers and findings before drafting memos.
7. Refresh the customer dashboard so the user can see the updated
   numbers immediately. Use the `recoup-catalog-dashboard` skill to author
   `deals/{deal-id}/DASHBOARD.html`, then validate:
   `python3 scripts/validate-dashboard.py deals/{deal-id}`.

## Final landing card

```text
✅ Analysis layer in place.

Headline:
  Normalized NPS run-rate $X.
  Normalized NLS NPV / run-rate $Y.
  Preliminary value bracket: $LOW – $HIGH.
  N material blockers · K high-severity items.

Open: deals/{deal-id}/DASHBOARD.html

Next:
  /recoup-catalog-dashboard — refresh DASHBOARD.html if workpapers changed
  /recoup-catalog-package   — assemble the IC memo
  /recoup-catalog-qc        — pre-share QC gate
```

Label quick estimates as preliminary. Do not finalize a valuation while
material blockers (split sheets, recoupment schedules, sample clearances,
chain of title gaps) remain open in `findings/findings.json`.
