---
name: ic-memo-package
description: Use when creating an investment committee memo, buyer diligence package, bid recommendation, seller cleanup report, financing pack, or final catalog deal summary. Triggers include "IC memo", "investment memo", "deal package", "bid recommendation", "catalog memo", "prepare the diligence package", or "package this catalog analysis".
---

# IC Memo Package

Assemble deal outputs from evidence, normalized data, workpapers, and findings.
The memo should be readable, but it must not outrun the evidence.

## Workflow

1. Confirm the intended output: IC memo, seller report, financing pack, or
   post-close plan.
2. Validate that `evidence-ledger.json`, `assumptions.yaml`, and findings exist.
3. Pull normalized NPS/NLS, concentration, red flags, and valuation scenarios
   from workpapers.
4. Separate evidence-backed facts from assumptions and open items.
5. Use the relevant template under `templates/deal-workspace/memos/`.
6. Run or request diligence QC before presenting final recommendations.

## Required sections

- Executive summary.
- Rights analyzed.
- Data confidence.
- Normalized cash-flow bridge.
- Valuation range or readiness score.
- Key risks and valuation treatment.
- Open diligence.
- Recommended next action.
- Evidence references.

## Guardrails

- Do not write polished conclusions without workpapers.
- Do not bury critical findings in appendices.
- Do not cite a source file unless the evidence ledger or workpaper supports it.
- Do not call the memo final if material open items remain unresolved.
