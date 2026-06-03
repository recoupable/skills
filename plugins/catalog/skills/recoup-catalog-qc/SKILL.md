---
name: recoup-catalog-qc
description: Run deal-review quality control before a catalog package is shared — Phase 6 QC only. Refreshes the executive dashboard with the latest findings. Use whenever the user types `/recoup-catalog-qc`, says "QC the deal", "run quality control on this deal", "check before sharing", "is this ready to send", or wants a pre-share QC gate after editing findings or memos. For full end-to-end runs prefer /recoup-catalog-deal.
argument-hint: [deal-id]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Catalog QC

Use the `deal-qc-reviewer` agent when available.

> **Most users should run `/recoup-catalog-deal` instead** — that command
> includes QC as Phase 6. This command is the QC phase only, for
> analysts who edited findings or memos and want to re-check before
> sharing.

## Steps

1. Run `python3 scripts/run-deal-checks.py deals/{deal-id}`.
2. Check that material memo claims cite evidence or are labeled
   assumptions.
3. Check that open findings are not hidden.
4. Check that source files were not modified (the PreToolUse hook
   prevents this, but verify the hook actually loaded).
5. Run `python3 scripts/build-deal-readiness.py deals/{deal-id}`
   for the internal readiness check
   (`workpapers/readiness-check.md`).
6. **Refresh the customer dashboard** so what the user sees matches the
   QC verdict. Use the `recoup-catalog-dashboard` skill to update
   `deals/{deal-id}/DASHBOARD.html`, then validate:
   `python3 scripts/validate-dashboard.py deals/{deal-id}`.
7. Dispatch the `deal-qc-reviewer` agent with the IC memo and the
   findings as input. Surface its `overall_status`, `blockers`, and
   `unsupported_claims` verbatim.

## Final landing card

```text
QC verdict: <ready | ready_with_caveats | blocked>

  Open blockers (must cure before sharing):
    <one bullet per critical finding>

  Unsupported claims:
    <one bullet per memo claim that lacks evidence>

  Required caveats to add:
    <one bullet per risk that needs disclosure>

Open: deals/{deal-id}/DASHBOARD.html
```

## Rules

- Do not mark a package complete if validation fails. The Stop hook will
  block the agent from finishing if the package is claimed ready while
  any open critical finding exists.
- Do not silently fix issues the QC reviewer found — surface them so the
  user can decide.
