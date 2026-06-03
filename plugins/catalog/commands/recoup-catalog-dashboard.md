---
name: recoup-catalog-dashboard
description: Author or refresh the customer-facing DASHBOARD.html for a deal workspace. Standalone shortcut to the recoup-catalog-dashboard skill — useful after editing workpapers, findings, or recommendations.
---

> **Note:** This command was migrated to `skills/recoup-catalog-dashboard/SKILL.md` in v0.3.0 per Anthropic's official guidance that `commands/*.md` is legacy in favor of `skills/<name>/SKILL.md`. Both layouts are loaded identically by Claude Code; this file is preserved for backwards compatibility. New work should edit the SKILL.md. The legacy command file will be removed in a future release.


# Catalog Dashboard

Use the `recoup-catalog-dashboard` skill.

> **Most users should run `/recoup-catalog-deal` instead** — that
> command runs end-to-end and includes the dashboard as Phase 5. This
> command is the dashboard phase only, for analysts who already have
> workpapers and want to refresh `DASHBOARD.html` after editing
> findings, the valuation summary, recommendations, or any other
> workpaper.

## Steps

1. Confirm `deals/{deal-id}/` exists and has the workpapers the
   dashboard reads (`workpapers/valuation-summary.json`,
   `workpapers/nps-bridge.json`, `workpapers/nls-bridge.json`,
   `workpapers/concentration-analysis.json`,
   `workpapers/recommendations.json`, plus
   `findings/findings.json` and `evidence-ledger.json`). If a
   workpaper is missing, the dashboard skill will degrade that
   section gracefully — but warn the user about which sections will
   read as "data not yet computed."

2. Run `python3 scripts/run-deal-checks.py deals/{deal-id}`
   first. The dashboard reflects whatever the workpapers say, so the
   validators must pass before the dashboard is trustworthy.

3. Author the dashboard with the `recoup-catalog-dashboard` skill.
   Read the skill's instructions carefully — required sections, brand
   rules, the trust contract (every `$`-claim either matches a
   workpaper value or carries `data-evidence` / `data-source` /
   `data-derived`), and the CDN allowlist. Write a single
   self-contained file at `deals/{deal-id}/DASHBOARD.html`.

   You have full creative freedom on layout, chart types, tabs,
   scenario toggles, narrative structure, and depth. The skill
   teaches taste; the validator enforces truthfulness.

4. Run the validator:

   ```bash
   python3 scripts/validate-dashboard.py deals/{deal-id}
   ```

   If it returns `status: errors_found`, **read the errors, fix the
   dashboard, re-run.** Common fixes:

   - Missing required section → add a marker for status / KPIs /
     findings / recommendations / evidence trail.
   - Unverified `$`-claim → either correct the number, add
     `data-evidence="EV-NNN"`, or wrap in `data-derived="<reason>"`.
   - External script not allowed → swap to a CDN in the allowlist
     (`cdn.jsdelivr.net`, `cdnjs.cloudflare.com`, `unpkg.com`).

## Final landing card

```text
✅ Dashboard refreshed.

Headline:
  Normalized NPS run-rate $X.
  Normalized NLS run-rate $Y.
  Preliminary value bracket: $LOW – $HIGH.
  N material blockers · K high-severity items.

Open: deals/{deal-id}/DASHBOARD.html

Validator: <ok | errors_found>
  $-claims seen:        <n>
  $-claims unverified:  <n>
  External scripts:     <list>
```

## Rules

- The dashboard is the customer-facing artifact. Apply the quality
  bar in `skills/recoup-catalog-dashboard/SKILL.md` — hierarchy,
  restraint, accessibility, responsiveness.
- Do not skip the validator. The Stop hook (Gate B) blocks the agent
  from finishing an end-to-end run if `DASHBOARD.html` does not pass
  validation; this scoped command stops cleanly after a single phase
  but the validator still has to pass for the dashboard to be
  trustworthy.
- Do not mutate `source/` files (the PreToolUse hook denies this
  anyway).
- If you discover that workpapers are stale (e.g., findings have
  changed since the bridge was computed), say so in the recap and
  recommend `/recoup-catalog-analyze` before regenerating the
  dashboard.
