---
name: catalog-kickoff
description: Set up a music catalog deal workspace and first diligence request list.
---

# Catalog Kickoff

Use the `diligence-kickoff` skill.

Steps:

1. Identify workflow type: buy-side, seller-prep, or financing.
2. Create or locate `deals/{deal-id}/`.
3. Apply templates from `templates/deal-workspace/`.
4. Build the initial missing-file list.
5. Run `python3 scripts/validate-deal-workspace.py deals/{deal-id}` to confirm
   the scaffold exists. It may fail until normalized artifacts are created; use
   the missing requirements as the initial worklist.
6. Recommend the next command: `catalog-ingest`, `catalog-analyze`,
   `catalog-qc`, or `catalog-package`.

Do not value the catalog during kickoff.
