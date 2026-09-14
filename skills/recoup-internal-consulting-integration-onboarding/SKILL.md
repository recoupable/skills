---
name: recoup-internal-consulting-integration-onboarding
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Connect a new external data source or channel to the selected business workspace, define ownership and scope, and verify one authorized read through the workflow."
---

# Consulting Integration Onboarding

Use the selected workspace and its `AGENTS.md`. Read `integrations/AGENTS.md` if present, then
follow the installed `recoup-internal-consulting-integration-scaffolder` for account setup, connector selection,
and the bundled HTTP adapter template. Do not search the author's private workspace for helpers.

1. Choose the ownership model: mirror a reviewed primary source, query a live system of record,
   log a channel's distilled signal, or mine a configured read-only content source.
2. Define which clients, folders, channels, and records belong to this workspace. Exclude unrelated
   employers and personal material; mixed or ambiguous records remain held outside the curated tree.
3. Prefer a connected provider tool. If an adapter is necessary, scaffold it with the sibling skill,
   verify provider authentication/pagination, and keep credentials and raw caches out of tracked files.
4. Document the account identity, scope, scripts, data destinations, and checkpoint behavior in
   `integrations/<tool>/AGENTS.md`. Do not put secret values in the document.
5. Run one authorized scoped read, confirm the expected result, and inspect the destination artifact.
   Only claim end-to-end success after both provider response and stored artifact are verified.
6. Connect it to the existing workflow configuration if requested. Creating the integration does not
   create a new scheduler or authorize importing all history. Unattended writes remain drafts, source
   boundaries remain enforced, and checkpoints advance only after successful processing.
7. Commit according to the workspace convention and report what is connected, what was tested, and
   any remaining access or data gaps. Never send, delete, or sweep external records as an auth test.
