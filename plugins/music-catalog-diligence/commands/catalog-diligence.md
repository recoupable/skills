---
name: catalog-diligence
description: Run the end-to-end music catalog diligence workflow from workspace setup through package readiness.
---

# Catalog Diligence

Run the end-to-end workflow for a music catalog transaction.

Steps:

1. Identify the workflow mode: buy-side, seller-prep, financing, or post-close.
2. Create or locate `deals/{deal-id}/` and apply `templates/deal-workspace/`.
3. Run `python3 scripts/validate-deal-workspace.py deals/{deal-id}`.
4. Use `catalog-ingest` to normalize royalty, metadata, and rights support files.
5. Run `python3 scripts/run-diligence-checks.py deals/{deal-id}`.
6. Use `catalog-analyze`, `royalty-audit`, and `rights-diligence` to create
   workpapers and findings.
7. Run `catalog-qc` before drafting or sharing memos.
8. Run `python3 scripts/build-diligence-dashboard.py deals/{deal-id}` and use
   the dashboard to report blockers, readiness, and next actions.
9. Use `catalog-package` only after validation and QC blockers are disclosed or
   resolved.

Do not mark a package ready if `run-diligence-checks.py` fails or the dashboard
shows `blocked`.
