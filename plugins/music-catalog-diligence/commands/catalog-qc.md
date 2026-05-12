---
name: catalog-qc
description: Run diligence quality control before a catalog package is shared.
---

# Catalog QC

Use the `diligence-qc-reviewer` agent when available.

Steps:

1. Run `python3 scripts/run-diligence-checks.py deals/{deal-id}`.
2. Check that material memo claims cite evidence or are labeled assumptions.
3. Check that open findings are not hidden.
4. Check that source files were not modified.
5. Run `python3 scripts/build-diligence-dashboard.py deals/{deal-id}`.
6. Report blockers before any memo is treated as shareable.

Do not mark a package complete if validation fails.
