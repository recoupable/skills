---
name: recoup-internal-consulting-integration-scaffolder
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Stand up a new external-tool integration in one move. Use on \"add an integration for X\", \"connect <tool>\", \"I have an API key for X\", or whenever a new data source/channel should flow into the OS. Scaffolds integrations/<tool>/ in the house pattern."
---

# Consulting Integration Scaffolder

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

The repeatable recipe behind `integrations/linkedin/` and `integrations/gmail/`. Given a tool + selected account, build the standard structure so every integration looks and works the same.

## First: classify the ownership type (decides what lives in the repo)
Per `integrations/AGENTS.md`: **Granola you mirror, Attio you query, LinkedIn/Gmail you log, Research you mine.**
- **Read-only source** (can't organize at source) → mirror + index in the repo.
- **System of record** (full API) → store only a thin regenerated snapshot; query live.
- **Channel** (read signal + write actions) → log distilled signal + published artifacts.
- **Read-only content source** (e.g. a local knowledge repo) → mine the delta into `content/` only;
  cite, don't copy. No mirror, and no scripts if it's local files (see `integrations/research/`).

## Steps
1. **Select the account and scope.** Prefer an available connector. If credentials are needed, have
   the user configure them in the selected workspace environment or credential store; show key names
   only. Do not ask for secret values in chat. Ensure local secret files are ignored by Git.
2. **Create the folder:** `integrations/<tool>/` with an ignored `_work/` directory and only the
   signal folders this integration needs. Keep source ownership and privacy rules explicit.
3. **Create the adapter only if a connector cannot do the task.** Start from the bundled
   `assets/http_client.py` read-only template, resolved from this installed skill. It uses standard
   library HTTPS verification, bounded rate-limit retries, and prevents cross-origin credential
   forwarding. Adapt authentication, pagination, response schema, and provider errors using current
   official documentation. It reads the named environment variable, never searches for secret files.
   Use the system trust store or explicitly configured CA bundle; never disable certificate checks.
4. **Write the scripts:** a `pull_*`/read script and (if it's a channel) a `publish_*`/write script.
   Writes default to draft/dry-run and require user authorization for the actual external action. Existing authorization remains valid. Advance `LAST_SYNCED` only after all corresponding scoped items are processed; preserve failed IDs for retry.
5. **Verify live** with a free/read-only call (token check, list accounts) before claiming it works.
6. **Write `integrations/<tool>/AGENTS.md`** (agent-native, not a README) — accounts/IDs,
   in-vs-out-of-repo rules, scripts table, examples, and activation steps. Add a row to the folder
   table in `integrations/AGENTS.md`.
7. **Author companion skills** if there's a recurring task (a publisher, an audience/triage skill).
8. **Gitignore any credential cache** (tokens) and commit. Verify `_work/`, secret files, and `__pycache__/` are actually ignored in this workspace.

Output: a working, documented integration that the `recoup-internal-consulting-integrations-sync` skill can keep fresh.
