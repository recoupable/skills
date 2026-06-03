---
name: recoup-catalog-analyze
description: Run normalized-catalog analysis (royalties, risk, concentration, valuation scenarios). For full end-to-end runs prefer /recoup-catalog-deal.
---

> **Note:** This command was migrated to `skills/recoup-catalog-analyze/SKILL.md` in v0.3.0 per Anthropic's official guidance that `commands/*.md` is legacy in favor of `skills/<name>/SKILL.md`. Both layouts are loaded identically by Claude Code; this file is preserved for backwards compatibility. New work should edit the SKILL.md. The legacy command file will be removed in a future release.


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
