---
name: recoup-catalog-kickoff
description: Set up a music catalog deal workspace and first deal-review request list. For full end-to-end runs prefer /recoup-catalog-deal.
---

> **Note:** This command was migrated to `skills/recoup-catalog-kickoff/SKILL.md` in v0.3.0 per Anthropic's official guidance that `commands/*.md` is legacy in favor of `skills/<name>/SKILL.md`. Both layouts are loaded identically by Claude Code; this file is preserved for backwards compatibility. New work should edit the SKILL.md. The legacy command file will be removed in a future release.


# Catalog Kickoff

Use the `recoup-deal-kickoff` skill.

> **Most users should run `/recoup-catalog-deal` instead** — that command
> chains kickoff → ingest → analysis → dashboard → memo without
> stopping. This command is kickoff only, for analysts who want to
> scaffold a workspace and stop before ingest.

## Steps

1. Identify workflow type: buy-side, recoup-seller-prep, or financing.
2. Create or locate `deals/{deal-id}/`.
3. Apply templates from `templates/deal-workspace/`.
4. Build the initial missing-file list in
   `findings/missing-files.md` based on the user's described data room.
5. Run `python3 scripts/validate-deal-workspace.py deals/{deal-id}` to
   confirm the scaffold exists. Validator failures here are expected
   until normalized artifacts are created — use the missing requirements
   as the initial worklist.
6. Recommend the next command. The default recommendation is
   `/recoup-catalog-deal` (it picks up where kickoff stopped). Only
   recommend a single phase command if the user explicitly asked for
   one.

Do not value the catalog during kickoff.

## Final landing card

```text
✅ Workspace scaffolded.

  Deal:        deals/{deal-id}/
  Workflow:    <buy-side | recoup-seller-prep | financing>
  Files in:    <count> seller-supplied files staged in source/

  Initial worklist (from references/deal-workflow.md):
    - <missing item 1>
    - <missing item 2>

Next:
  /recoup-catalog-deal         — drive end-to-end (recommended)
  /recoup-catalog-ingest       — ingest only
```
