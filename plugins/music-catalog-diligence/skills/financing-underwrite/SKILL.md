---
name: financing-underwrite
description: Use when underwriting a music catalog for an advance, loan, credit facility, securitization, collateral package, or royalty-backed financing. Triggers include "catalog financing", "underwrite this catalog", "advance rate", "collateral package", "royalty loan", "financing pack", "debt capacity", or "lender diligence".
---

# Financing Underwrite

Build a lender-ready view of catalog cash flow, collateral quality, and downside
risk. Financing work emphasizes coverage, stability, and enforceability.

## Workflow

1. Confirm workflow type is `financing`.
2. Validate normalized royalties, rights map, evidence ledger, and assumptions.
3. Separate eligible collateral from unsupported or restricted assets.
4. Compute normalized NPS/NLS and concentration.
5. Stress cash flows for decay, platform risk, missing docs, recoupment, and
   reserves.
6. Recommend advance-rate adjustments, holdbacks, or conditions precedent.
7. Draft `memos/financing-pack.md`.

## Lender checks

- Is pledged income supported by transferable rights?
- Are royalty sources stable and recurring?
- Are top-song and top-platform concentrations acceptable?
- Are recoupment, reserves, and payables modeled?
- Are there unresolved legal or registration exceptions?
- Is monitoring possible after close?

## Output

Return:

- Eligible collateral summary.
- Normalized cash-flow base.
- Downside stress case.
- Exclusions and haircuts.
- Required conditions before funding.
- Ongoing monitoring plan.

## Guardrails

- Do not use seller gross revenue as debt-service cash flow.
- Do not include unsupported assets in eligible collateral.
- Do not hide missing documents behind a blended advance rate.
