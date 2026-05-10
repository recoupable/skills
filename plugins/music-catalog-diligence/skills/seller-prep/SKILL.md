---
name: seller-prep
description: Use when preparing a music catalog for sale, improving catalog readiness, cleaning metadata before going to market, creating a seller cleanup report, finding missing documentation, or maximizing catalog value before buyer diligence. Triggers include "prepare catalog for sale", "seller prep", "maximize catalog value", "catalog audit checklist", "clean up before sale", or "what should we fix before going to market".
---

# Seller Prep

Help a seller increase buyer confidence before a catalog goes to market. Seller
prep is not about inflating value. It is about reducing avoidable discounts.

## Workflow

1. Run `diligence-kickoff` with workflow type `seller-prep`.
2. Inventory files and build missing-document tracker.
3. Use `catalog-ingest` to normalize metadata and royalty statements.
4. Use `rights-diligence` to find unsupported assets.
5. Use `royalty-audit` to find income leakage and statement gaps.
6. Rank fixes by likely value impact and time to cure.
7. Draft `memos/seller-cleanup-report.md`.

## Fix categories

- Missing split sheets.
- Missing registrations.
- ISRC/ISWC/UPC conflicts.
- Unlinked recordings and compositions.
- Unsupported income.
- Incomplete royalty history.
- Unclaimed or unmatched royalties.
- Non-one-stop sync restrictions.
- Sample and featured artist documentation gaps.

## Output

Return:

- Readiness summary.
- Top value leaks.
- Cleanup priority list.
- Buyer-facing documentation gaps.
- Work that can be fixed quickly.
- Work that needs counsel, administrator, or seller action.

## Guardrails

- Do not promise valuation uplift without evidence.
- Do not hide problems to make the catalog look cleaner.
- Do not overwrite source metadata; create corrected working files.
