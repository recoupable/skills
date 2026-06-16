---
name: recoup-deal-value
description: Use when analyzing or valuing a music catalog for acquisition, financing, sale, or investment deal review, or when refreshing the analysis after editing ingest output or assumptions. Triggers include "catalog valuation", "music catalog analysis", "project catalog value", "NPS multiple", "NLS multiple", "quality of earnings", "royalty cash flows", "catalog acquisition", "recoupment cliff", "PRO bonus", "normalize royalties", "refresh the analysis", "rerun the valuation", "update the workpapers", or "build an investment memo" for publishing or master rights. Works from an INGESTED data room (seller royalty statements + rights files); for a quick estimate from public/streaming data alone with no seller files, use recoup-catalog-value.
---

# Deal Valuation Analysis

Analyze normalized music catalog cash flows and project value. Do not apply a
multiple to headline royalties until you understand what income is sustainable,
what rights are supported, and what risks change the buyer's actual cash flow.

## Decision tree

Start here based on the user request:

- **Clean ingest package exists** -> validate the canonical catalog, royalty
  ledger, rights map, and source lineage, then analyze.
- **Only raw data-room files exist** -> ingest first. Valuation before ingest is
  unreliable.
- **Publishing catalog** -> analyze Net Publisher Share (`NPS`).
- **Master catalog** -> analyze Net Label Share (`NLS`), recoupment, reserves,
  artist royalties, producer points, and distribution fees.
- **Mixed rights catalog** -> segment publishing and master income separately,
  then reconcile to a blended view.
- **Quick value estimate requested** -> give a clearly labeled diagnostic range
  and list open deal-review items. Do not present it as a full valuation.

If inputs are too incomplete, say what cannot be valued yet and list the minimum
files needed.

## Core workflow

1. **Validate inputs.** Confirm the catalog table, royalty ledger, rights map,
   and source lineage are present or explain what is missing.
2. **Define the asset.** Separate publishing, masters, neighboring rights, sync,
   or mixed rights. State whether you are calculating NPS or NLS.
3. **Compute raw earnings.** Calculate LTM/TTM, three-year average, and trend by
   source, song, artist, platform, territory, and period.
4. **Analyze concentration.** Show dependence on top songs, artists, platforms,
   territories, rights types, and income sources.
5. **Normalize run-rate.** Bridge raw LTM to sustainable NPS/NLS by removing or
   haircutting non-recurring or fragile income.
6. **Check rights and cash-flow support.** Tie meaningful income to ownership,
   contracts, registrations, recoupment, reserves, restrictions, and
   transferability.
7. **Segment risk.** Separate evergreen, recent, sync-heavy, bonus-driven,
   one-stop, fragmented, supported, and unsupported assets.
8. **Project scenarios.** Build downside, base, and upside cash flows using
   explicit growth/decay, recoupment, reserve, and rights assumptions.
9. **Value the catalog.** Use market multiples and/or DCF, then reconcile to a
   supportable range.
10. **Write the memo.** Lead with value range, normalized cash flow, key risks,
    open deal-review items, and recommended holdbacks or haircuts.

Run deterministic scripts from `scripts/` when the required files exist:

- `calculate-concentration.py` for song, platform, territory, and source risk.
- `calculate-nps-nls-bridge.py` for reported-to-normalized cash-flow bridges.
- `validate-evidence-ledger.py` before relying on memo citations.

## Required bridge

Always show a bridge from reported royalties to underwritable earnings:

```text
Reported LTM NPS/NLS
  - one-time sync and direct-license spikes
  - viral, playlist, death-bump, or campaign spikes
  - settlement, audit recovery, and accounting catch-up income
  - non-repeat PRO bonus or premium income
  +/- current run-rate trend adjustment
  +/- admin, collection, reserve, recoupment, or contract adjustment
  +/- undercollection or missing-registration adjustment
= Normalized run-rate NPS/NLS
```

Use real source amounts when available. If you must illustrate, label the number
as illustrative and do not mix it into the final valuation.

## Critical gotchas

- **Headline `NPS x multiple` can be wrong.** Multiples apply to sustainable
  underwritable earnings, not whatever happened in the last twelve months.
- **PRO income is not one number.** Decompose by PRO/society, use type, format,
  territory, credits, bonus/premium participation, and cue-sheet support when
  available.
- **Bonus/premium royalties can be fragile.** A song that earned from a
  threshold-driven radio or TV bonus may not repeat that income.
- **Sync is usually upside, not baseline.** One-time sync fees should be
  excluded, averaged, or heavily haircut unless a repeatable library pattern is
  proven.
- **Master gross is not NLS.** Artist royalties, producer points, distributor
  fees, reserves, and recoupment determine the owner's actual cash flow.
- **Unrecouped accounts can flip.** A catalog may look more profitable before
  artists recoup. Model the post-recoupment margin.
- **Track count is not diversification.** A 500-track catalog with one income
  driver is concentrated.
- **Unsupported income is risky.** If the rights map cannot support meaningful
  income, separate financial performance from transferable value.
- **Do not fabricate assumptions.** Unknown decay, split, recoupment, reserve,
  or reversion data must stay visible as open deal-review items.

## Outputs

Use these outputs for a full analysis:

- Executive valuation summary.
- Quality-of-earnings bridge.
- Revenue mix and concentration analysis.
- Rights-support and deal-review exceptions.
- Normalized NPS/NLS calculation.
- Downside/base/upside cash-flow scenarios.
- Market-multiple valuation.
- DCF valuation, when enough data exists.
- Sensitivity table.
- Risk register.
- Recommended holdback, escrow, haircut, or follow-up deal-review items.

Templates and memo structure are in
**`references/output-templates.md`**.

## Operational pipeline (deal workspace)

When working inside a deal workspace (not a one-off valuation question):

1. Run `python3 scripts/run-deal-checks.py deals/{deal-id}` first. Cure
   validator failures before analysis.
2. Compute or review normalized NPS/NLS, then write the bridge JSON files the
   dashboard reads: `workpapers/nps-bridge.json`, `workpapers/nls-bridge.json`,
   and `workpapers/valuation-summary.json` (with `normalized` and `scenarios`
   keys — see recoup-deal-start Phase 4 for the schema).
3. Run `python3 scripts/calculate-concentration.py` and
   `python3 scripts/calculate-nps-nls-bridge.py` when normalized inputs exist.
4. For material deals, launch specialist sub-agents for rights, royalty, and
   valuation review **in parallel** (a single message with three Task calls).
5. Write workpapers and findings before drafting any memo.
6. Refresh the customer dashboard with recoup-deal-dashboard, then validate:
   `python3 scripts/validate-dashboard.py deals/{deal-id}`.

Label quick estimates as preliminary. Do not finalize a valuation while material
blockers (split sheets, recoupment schedules, sample clearances, chain-of-title
gaps) remain open in `findings/findings.json`.

```text
✅ Analysis layer in place.

Headline:
  Normalized NPS run-rate $X.
  Normalized NLS NPV / run-rate $Y.
  Preliminary value bracket: $LOW – $HIGH.
  N material blockers · K high-severity items.

Open: deals/{deal-id}/DASHBOARD.html

Next:
  recoup-deal-dashboard — refresh DASHBOARD.html + run the pre-share QC gate
  recoup-deal-report    — assemble the IC memo and export a shareable PDF
```

## Diligence deep-dives (read the one the deal needs)

This skill is the single diligence surface for the plugin. The valuation
workflow above is the spine; pull in the matching deep-dive when a deal's
shape calls for it. Each reference is a self-contained playbook.

| When the deal involves… | Read |
| --- | --- |
| Splits, assignments, samples, reversions, chain of title | **`references/rights-review.md`** |
| Gross-to-net, duplicate imports, retro adjustments, suspicious spikes | **`references/royalty-audit.md`** |
| A lender / advance / debt sizing against catalog cash flow | **`references/financing-underwrite.md`** |
| Prepping a seller's catalog before going to market | **`references/seller-prep.md`** |
| Administering a catalog after the deal closes | **`references/post-close-admin.md`** |

For the buy-side material deal, run the rights review and royalty audit
deep-dives together with the valuation spine — those are the three
specialist lenses dispatched in parallel by `recoup-deal-start` Phase 3.

## What to read next

- For valuation mechanics, read
  **`references/valuation-framework.md`**.
- For performance royalty traps, read
  **`references/pro-performance-income.md`**.
- For deal red flags to watch, read
  **`references/red-flags.md`**.
- For memo and table formats, read
  **`references/output-templates.md`**.
- For workspace-level evidence rules, read
  **`references/deal-workspace.md`**.
