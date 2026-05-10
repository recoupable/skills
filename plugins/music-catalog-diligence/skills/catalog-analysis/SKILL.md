---
name: catalog-analysis
description: Use when analyzing or valuing a music catalog for acquisition, financing, sale, or investment diligence. Triggers include "catalog valuation", "music catalog analysis", "project catalog value", "what is this catalog worth", "NPS multiple", "NLS multiple", "quality of earnings", "royalty cash flows", "catalog acquisition", "recoupment cliff", "PRO bonus", "normalize royalties", or "build an investment memo" for publishing or master rights.
---

# Catalog Analysis

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
  and list missing diligence. Do not present it as a full valuation.

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
    missing diligence, and recommended holdbacks or haircuts.

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
  or reversion data must stay visible as missing diligence.

## Outputs

Use these outputs for a full analysis:

- Executive valuation summary.
- Quality-of-earnings bridge.
- Revenue mix and concentration analysis.
- Rights-support and diligence exceptions.
- Normalized NPS/NLS calculation.
- Downside/base/upside cash-flow scenarios.
- Market-multiple valuation.
- DCF valuation, when enough data exists.
- Sensitivity table.
- Risk register.
- Recommended holdback, escrow, haircut, or follow-up diligence.

Templates and memo structure are in
**[references/output-templates.md](references/output-templates.md)**.

## What to read next

- For valuation mechanics, read
  **[references/valuation-framework.md](references/valuation-framework.md)**.
- For performance royalty traps, read
  **[references/pro-performance-income.md](references/pro-performance-income.md)**.
- For memo and table formats, read
  **[references/output-templates.md](references/output-templates.md)**.
- For workspace-level evidence rules, read
  **[../../references/deal-workspace.md](../../references/deal-workspace.md)**.
