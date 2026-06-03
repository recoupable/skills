---
name: recoup-catalog-package
description: Assemble the executive HTML dashboard plus an IC memo, seller cleanup report, financing pack, or post-close administration package — Phases 5–6 only. Use whenever the user types `/recoup-catalog-package`, says "build the IC memo", "package this deal", "draft the seller cleanup report", "assemble the financing pack", or "build the post-close admin plan". For full end-to-end runs prefer /recoup-catalog-deal.
argument-hint: [deal-id] [--package ic-memo|seller-cleanup|financing-pack|post-close-admin]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Catalog Package

Use the `recoup-ic-memo-package` skill.

> **Most users should run `/recoup-catalog-deal` instead** — that command
> chains kickoff → ingest → analysis → dashboard → memo. This command is
> the packaging phase only, for analysts who already have analysis
> workpapers and want to refine the deliverables.

## Steps

1. Confirm package type: IC memo, seller cleanup report, financing pack,
   or post-close admin plan.
2. Run `python3 scripts/run-deal-checks.py deals/{deal-id}` first.
   Validator failures must be cured or explicitly disclosed before
   packaging.
3. Use the relevant template under `templates/deal-workspace/memos/`.
   Pull every material number from the workpapers (
   `valuation-summary.json`, `nps-bridge.json`, `nls-bridge.json`,
   `concentration-analysis.json`), not from prose memory.
4. Run `recoup-catalog-qc` before presenting the output as ready for review.
5. **Always rebuild the dashboard** so it reflects the final memo
   numbers. Use the `recoup-catalog-dashboard` skill to author
   `deals/{deal-id}/DASHBOARD.html`, then validate:
   `python3 scripts/validate-dashboard.py deals/{deal-id}`. If the
   validator returns errors, fix the dashboard and re-run.
6. `python3 scripts/build-deal-readiness.py deals/{deal-id}` for
   the internal readiness check (writes `workpapers/readiness-check.md`
   — analyst-facing only, not for the customer).

## Final landing card

End with the same shape as `/recoup-catalog-deal` so the user has a single,
predictable closing message:

```text
✅ Package ready for review.

Headline:
  Normalized NPS run-rate $X.
  Normalized NLS NPV / run-rate $Y.
  Preliminary value bracket: $LOW – $HIGH.
  N material blockers · K high-severity items.

Open this first:
  deals/{deal-id}/DASHBOARD.html

Then if you want detail:
  deals/{deal-id}/memos/<package-type>.md
  deals/{deal-id}/findings/missing-files.md
```

## Rules

- Do not generate a polished package without disclosing open deal issues.
- Do not mark the package "ready" if `run-deal-checks.py` fails or
  the readiness check shows `blocked`. The Stop hook will block the
  agent from finishing in that state.
- Do not bury critical findings in appendices. They go in the executive
  summary and on the executive dashboard.
