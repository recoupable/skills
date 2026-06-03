---
name: recoup-catalog-report
description: Export the deal as a single shareable, emailable PDF. Converts the validated DASHBOARD.html (and supporting memos / workpapers) into deals/{deal-id}/REPORT.pdf. Use after the deal review finishes when you want to forward it to an IC, lender, buyer, seller, or counsel.
---

> **Note:** This command was migrated to `skills/recoup-catalog-report/SKILL.md` in v0.3.0 per Anthropic's official guidance that `commands/*.md` is legacy in favor of `skills/<name>/SKILL.md`. Both layouts are loaded identically by Claude Code; this file is preserved for backwards compatibility. New work should edit the SKILL.md. The legacy command file will be removed in a future release.


# Catalog Report (PDF)

Use the `recoup-catalog-report` skill.

> **Run `/recoup-catalog-deal` first.** That command produces the
> validated dashboard, memo, and workpapers this report packages. This
> command is the export step — it turns those artifacts into a single
> PDF you can attach to an email.

## Steps

1. Confirm `deals/{deal-id}/DASHBOARD.html` exists and the workpapers
   it cites (`workpapers/valuation-summary.json`,
   `workpapers/nps-bridge.json`, `workpapers/nls-bridge.json`,
   `workpapers/concentration-analysis.json`,
   `workpapers/recommendations.json`, plus `findings/findings.json`
   and `evidence-ledger.json`) are present. If the dashboard is
   missing or stale, run `/recoup-catalog-dashboard` first.

2. Validate the dashboard before exporting:

   ```bash
   python3 scripts/validate-dashboard.py deals/{deal-id}
   ```

   The report inherits the dashboard's truthfulness. If the validator
   returns errors, stop and fix the dashboard before exporting.

3. Author the PDF with the `recoup-catalog-report` skill. Read the
   skill's instructions carefully — required sections (cover, exec
   summary, findings, recommendations, evidence trail, page footer),
   print-specific quality bar, and the trust contract. Pick the
   conversion path that fits the environment:

   - **Headless Chrome** — fastest, zero Python deps, works on any
     machine with Chrome / Chromium / Edge installed.
   - **Playwright** — most reliable for complex layouts, needs
     `pip3 install playwright && python3 -m playwright install chromium`.
   - **WeasyPrint** — pure-Python print typography; only works when
     charts are pre-rendered as SVG/PNG (no JS execution).
   - **ReportLab / fpdf2** — from-scratch PDF; reach for this only
     when the HTML-based paths give a poor result.

   Write the file to:

   ```text
   deals/{deal-id}/REPORT.pdf
   ```

   For multi-flavor exports (IC, seller, financing, post-close), also
   write each variant to
   `deals/{deal-id}/reports/<package-type>.pdf`.

4. Verify the output (size 100 KB – 15 MB; cover page first; exec
   summary on page 2; first `$`-figure on the executive summary
   matches the dashboard). Quick text-extract sanity check if
   `pdftotext` is available:

   ```bash
   pdftotext -layout deals/{deal-id}/REPORT.pdf - | head -50
   ```

## Final landing card

```text
✅ Report exported.

  File:        deals/{deal-id}/REPORT.pdf
  Pages:       <n>
  Size:        <X.X MB>
  Source:      deals/{deal-id}/DASHBOARD.html (validated)
  Converted:   <Chrome headless | Playwright | WeasyPrint | ReportLab>

Attach this to the email. The dashboard stays in the deal workspace
for the analyst.
```

## Rules

- **The PDF inherits the dashboard's trust contract.** Do not invent
  numbers in the report that aren't already in the workpapers. If a
  number isn't in the truth set, write it into a workpaper first,
  re-validate the dashboard, then export.
- **Do not export a stale dashboard.** If workpapers or findings have
  changed since the dashboard was last built, re-run
  `/recoup-catalog-dashboard` before this command.
- **Do not skip the validator.** The PDF goes to people who can't see
  the source files. Truthfulness has to be verified before, not
  after, distribution.
- **Print quality matters.** Apply the print-specific quality bar in
  `skills/recoup-catalog-report/SKILL.md` — page breaks at section
  boundaries, body text legible on paper, footer with deal ID • date
  • Confidential • page N of M.
- **Do not write into `deals/{deal-id}/source/`.** The PreToolUse
  hook denies it; that's seller evidence.
