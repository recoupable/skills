---
name: diligence-kickoff
description: Use when starting a new music catalog deal, setting up a data room review, creating a deal workspace, preparing diligence requests, or triaging a catalog acquisition, seller-prep, or financing opportunity. Triggers include "start catalog diligence", "kick off this deal", "set up the data room", "new catalog acquisition", "prepare diligence request", or "create deal workspace".
---

# Diligence Kickoff

Set up one catalog deal workspace and route the team into the right workflow:
buy-side acquisition, seller preparation, or financing underwriting.

## Workflow

1. Identify the workflow type: `buy-side`, `seller-prep`, or `financing`.
2. Create or locate `deals/{deal-id}/`.
3. Apply the deal workspace convention from
   `references/deal-workspace.md`.
4. Place raw seller files under `source/` and do not edit them.
5. Start `assumptions.yaml` from the template and fill only known facts.
6. Start `evidence-ledger.json` and `findings/findings.json`.
7. Build a first missing-file list from
   `references/diligence-workflow.md` and `references/red-flags.md`.
8. Route next:
   - Raw data room -> use `catalog-ingest`.
   - Legal support -> use `rights-diligence`.
   - Statements -> use `royalty-audit`.
   - Value projection -> use `catalog-analysis`.

## Output

Return:

- Deal workspace path.
- Workflow type.
- Files received.
- Missing documents.
- Immediate red flags.
- Recommended next skill or command.

## Guardrails

- Never call the deal "ready" during kickoff.
- Do not make valuation claims from seller summaries alone.
- Do not assume seller file names are accurate.
- Keep all unknown assumptions visible in `assumptions.yaml`.
