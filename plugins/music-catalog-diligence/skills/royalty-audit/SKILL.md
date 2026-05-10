---
name: royalty-audit
description: Use when auditing music royalty statements, checking reported revenue, normalizing royalty ledgers, finding missing income, validating NPS/NLS, reviewing PRO/MLC/DSP/distributor statements, or investigating royalty anomalies. Triggers include "royalty audit", "check these statements", "missing royalties", "statement normalization", "income leakage", "MLC mismatch", or "PRO statement issue".
---

# Royalty Audit

Review royalty data for completeness, consistency, and underwritable net cash
flow. The goal is to find statement issues before they become valuation errors.

## Workflow

1. Confirm raw statements are preserved in `source/`.
2. Use `catalog-ingest` if no normalized `royalty-ledger.csv` exists.
3. Validate ledger grain, dates, currencies, sources, rights types, and asset
   matches.
4. Reconcile gross, deductions, participant shares, and owner net.
5. Check period earned versus period paid.
6. Identify duplicate imports, unmatched income, missing sources, and retroactive
   adjustments.
7. Decompose PRO performance income using
   `skills/catalog-analysis/references/pro-performance-income.md`.
8. Write anomalies to `findings/findings.json` and workpapers to `workpapers/`.

## Output

Return:

- Statement sources reviewed.
- LTM/TTM by source and rights type.
- Unmatched or unsupported income.
- Duplicate or suspicious rows.
- Gross-to-net issues.
- PRO/MLC/metadata issues.
- Recommended normalization adjustments.

## Guardrails

- Do not drop unmatched income. Mark it as unmatched.
- Do not treat gross revenue as NPS or NLS.
- Do not classify one-time payments as recurring without evidence.
- Do not hide FX or timing assumptions.
