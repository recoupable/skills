---
name: recoup-catalog-ingest
description: Normalize a catalog data room into auditable catalog, royalty, rights, and evidence artifacts. Auto-recovers when seller files use non-canonical headers.
---

> **Note:** This command was migrated to `skills/recoup-catalog-ingest/SKILL.md` in v0.3.0 per Anthropic's official guidance that `commands/*.md` is legacy in favor of `skills/<name>/SKILL.md`. Both layouts are loaded identically by Claude Code; this file is preserved for backwards compatibility. New work should edit the SKILL.md. The legacy command file will be removed in a future release.


# Catalog Ingest

Use the `recoup-catalog-ingest` skill.

> **Most users should run `/recoup-catalog-deal` instead** — that command
> chains kickoff → ingest → analysis → dashboard → memo without stopping.
> This command is the ingest phase only, for analysts who already have a
> workspace and want to re-normalize after dropping new files into
> `source/`.

## Steps

1. Confirm raw files are under `deals/{deal-id}/source/`.
2. Build or update the file manifest (parse_status, likely_provider,
   period, currency, rights-type hint per file):
   `python3 scripts/build-file-manifest.py deals/{deal-id}`.
3. For every manifest entry with a `likely_provider`, normalize:

   ```bash
   python3 scripts/normalize-royalty-statement.py \
     --provider <key> \
     --input <path> \
     --output deals/{deal-id}/normalized/royalty-ledger.csv
   ```

   ### When the normalizer returns `status: "partial"` — auto-recover, do not stop

   The normalizer enforces a 50% population threshold on
   `gross_amount`/`owner_net_amount`/`period_start`. Seller files often
   ship with renamed columns (`Net Royalty`, `Sales Period`, `Track
   Title`) that don't match a provider's stock aliases. **Do not ask the
   user to write a column map.** Run:

   ```bash
   python3 scripts/auto-column-map.py \
     --provider <key> \
     --input <path> \
     --output deals/{deal-id}/workpapers/column-maps/<source-file>.json
   ```

   - Exit `0` (`status: "ok"`) → re-run the normalizer with
     `--column-map workpapers/column-maps/<source-file>.json` and
     continue.
   - Exit `1` (`status: "needs_review"`) → record the file and the
     specific missing critical fields in
     `findings/manual-review-queue.md` and move on. Do not block the
     whole ingest on one file.

4. Build the manual-review queue and ingest-coverage summary:
   `python3 scripts/build-manual-review-queue.py deals/{deal-id}`.
   Surface the resulting `summary_line` in your top-level ingest report —
   for example: "29 of 88 files contributed financial data; 50 require
   manual review."
5. Run the data-room hygiene scan and merge any high-strength matches into
   `findings/findings.json`:
   `python3 scripts/dataroom-hygiene-scan.py deals/{deal-id}`.
6. Compute concentration by catalog asset id; emit a finding when the
   threshold from `assumptions.yaml` is tripped:
   `python3 scripts/calculate-concentration.py deals/{deal-id}/normalized/royalty-ledger.csv \
      --assumptions deals/{deal-id}/assumptions.yaml \
      --output deals/{deal-id}/workpapers/concentration-analysis.json \
      --emit-finding-output deals/{deal-id}/findings/concentration-finding.json`.
   Merge the proposed finding into `findings/findings.json` with a real
   `evidence_ids` reference to the concentration workpaper.
7. Validate the ledger:
   `python3 scripts/validate-normalized-ledger.py deals/{deal-id}/normalized/royalty-ledger.csv`.
8. Run the full readiness check (workspace, ledger, evidence ledger,
   findings-to-evidence traceability, cross-artifact consistency):
   `python3 scripts/run-deal-checks.py deals/{deal-id}`.
9. **Optional**: build a preview dashboard so the user can see what
   ingest produced before analysis runs. Use the `recoup-catalog-dashboard`
   skill to author `deals/{deal-id}/DASHBOARD.html` from the partial
   workpapers (the skill's quality bar still applies — surface what's
   not yet computed honestly). Then validate:
   `python3 scripts/validate-dashboard.py deals/{deal-id}`. Skip this
   if the user is going to run `/recoup-catalog-analyze` immediately after.

## Final report

End with the X-of-Y line from step 4 and a single-line pointer to the
dashboard:

```text
Ingest report:
  29 of 88 files contributed financial data; 50 require manual review.
  4 unparsed files (zero-byte or unsupported format).
  3 high-severity findings auto-merged from concentration + hygiene scans.

Optional preview: deals/{deal-id}/DASHBOARD.html (built only if step 9 ran)
```

## Rules

- Do not edit source files. The PreToolUse hook will deny those writes.
- Do not produce a valuation unless ingest artifacts exist and the user
  explicitly asks to continue. Ingest's job is to make the data
  trustworthy, not value the catalog.
- Do not mark ingest complete while `run-deal-checks.py` still
  reports failures.
- When in doubt, run `/recoup-catalog-deal` to drive end-to-end instead.
