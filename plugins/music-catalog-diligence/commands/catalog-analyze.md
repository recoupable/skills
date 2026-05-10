---
name: catalog-analyze
description: Analyze normalized music catalog royalties, risk, concentration, and valuation scenarios.
---

# Catalog Analyze

Use the `catalog-analysis`, `royalty-audit`, and `rights-diligence` skills as
needed.

Steps:

1. Run `python3 scripts/run-diligence-checks.py deals/{deal-id}`.
2. Confirm whether analysis is for buy-side acquisition, seller prep, or
   financing.
3. Compute or review normalized NPS/NLS.
4. Run `python3 scripts/calculate-concentration.py` and
   `python3 scripts/calculate-nps-nls-bridge.py` when normalized inputs are
   available.
5. Launch specialist agents for rights, royalty, and valuation review when the
   deal is material.
6. Write workpapers and findings before drafting memos.

Label quick estimates as preliminary.
