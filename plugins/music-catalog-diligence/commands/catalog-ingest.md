---
name: catalog-ingest
description: Normalize a catalog data room into auditable catalog, royalty, rights, and evidence artifacts.
---

# Catalog Ingest

Use the `catalog-ingest` skill.

Steps:

1. Confirm raw files are under `deals/{deal-id}/source/`.
2. Build or update the file manifest (now classifies parse_status, likely
   provider, period, currency, rights-type hint per file):
   `python3 scripts/build-file-manifest.py deals/{deal-id}`.
3. Normalize catalog, royalty, rights, and source-lineage artifacts into
   `normalized/`. For each provider statement, run
   `python3 scripts/normalize-royalty-statement.py --provider <name> --input <path> --output <ledger.csv>`
   and treat any `status: partial` or non-zero exit as a hard signal that the
   provider profile needs a `--column-map` extension before continuing.
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
   `python3 scripts/run-diligence-checks.py deals/{deal-id}`.

Do not edit source files. Do not produce a valuation unless ingest artifacts
exist and the user explicitly asks to continue. Do not mark ingest complete
while `run-diligence-checks.py` still reports failures.
