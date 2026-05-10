---
name: catalog-package
description: Assemble an IC memo, seller cleanup report, financing pack, or post-close administration package.
---

# Catalog Package

Use the `ic-memo-package` skill.

Steps:

1. Confirm package type: IC memo, seller cleanup report, financing pack, or
   post-close admin plan.
2. Run `python3 scripts/run-diligence-checks.py deals/{deal-id}`.
3. Use the relevant template under `templates/deal-workspace/memos/`.
4. Run `catalog-qc` before presenting the output as ready for review.
5. Attach or summarize `deals/{deal-id}/diligence-dashboard.md` with the
   package.

Do not generate a polished package without disclosing missing diligence.
