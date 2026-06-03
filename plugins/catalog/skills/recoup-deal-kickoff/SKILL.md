---
name: recoup-deal-kickoff
description: Use when starting a new music catalog deal, setting up a data room review, creating a deal workspace, preparing deal-review requests, or triaging a catalog acquisition, recoup-seller-prep, or financing opportunity. Triggers include "start a catalog deal", "kick off this deal", "set up the data room", "new catalog acquisition", "prepare deal request", or "create deal workspace".
---

# Deal Kickoff

Set up one catalog deal workspace and route the team into the right workflow:
buy-side acquisition, seller preparation, or financing underwriting.

## Workflow

1. Identify the workflow type: `buy-side`, `recoup-seller-prep`, or `financing`.
2. Create or locate `deals/{deal-id}/`.
3. Apply the deal workspace convention from
   `references/deal-workspace.md`.
4. Place raw seller files under `source/` and do not edit them.
5. Start `assumptions.yaml` from the template and fill only known facts.
6. Start `evidence-ledger.json` and `findings/findings.json`.
7. Build a first missing-file list from
   `references/deal-workflow.md` and `references/red-flags.md`.
8. Route next:
   - Raw data room -> use `recoup-catalog-ingest`.
   - Legal support -> use `recoup-rights-review`.
   - Statements -> use `recoup-royalty-audit`.
   - Value projection -> use `recoup-catalog-analysis`.

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
