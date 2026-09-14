---
name: recoup-internal-consulting-integrations-sync
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. The anti-staleness engine for external integrations. Use on the Friday cadence, on \"sync the integrations\", \"is the CRM in sync\", \"refresh granola/attio/linkedin/gmail/slack\", or whenever the repo might have drifted from Attio/Granola/LinkedIn/Gmail/Slack. Reconciles live sources against the repo and reports what changed and what's stale."
---

# Consulting Integrations Sync

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

Keep `integrations/` (Granola, Attio, LinkedIn, Gmail) and the curated repo from going stale.
Run end-to-end, then report. Use the connected account or explicitly selected workspace environment; never search parent directories for keys.

## Source boundary

Apply the selected workspace's intake policy to every channel before persisting content. A contact,
domain, or channel match is a routing hint, not permission to capture unrelated employment or personal
material embedded in the same thread. Hold mixed or ambiguous records; do not leak their titles or
excerpts into skip reports. Private source capture never grants permission to publish a shared snapshot.

## Steps
1. **Attio (query live — system of record).** Per `integrations/attio/crm-sync.md`, query deals via REST
   (`POST /v2/objects/deals/records/query`). For each deal, compare its **stage** to its
   filesystem location. On mismatch: move the folder (`pipeline/**` ↔ `clients/**`), fix the deal
   `AGENTS.md` status line, and regenerate `pipeline/_board.md`. Attio wins on stage; repo wins on artifacts.
2. **Granola (review before capture).** Use an available connector, or the selected workspace's
   `list_new_notes.py`, with an overlapping window (default: three days before the last successful
   checkpoint). Review the title and content against the workspace's client/deal scope and exclusions.
   Attendees alone never establish scope. Skip unrelated employment, personal material, and excluded
   internal meetings. Hold ambiguous or mixed records; do not save their bodies or identifying details
   in skip logs. For a reviewed in-scope note, a compatible local adapter is:
   `python3 integrations/granola/_work/pull_transcript.py --note <id> --reviewed-scope --out <dest>`.
   Destinations are `clients/<client>/meetings/transcripts/<date>-<slug>.md` or
   `pipeline/<stage>/<deal>/meetings/transcripts/<date>-<slug>.md`. Otherwise use a connector to fetch
   that one reviewed note and preserve the same destination and evidence labels. No bulk fallback.
   Label summaries as non-evidence and keep transcript attribution tied to the actual recording owner.
   Deduplicate by source ID; checkpoint completed work only. Report skipped counts without private
   titles, names, or excerpts. New in-scope prospects route through `recoup-internal-consulting-lead-intake`.
3. **LinkedIn (pull signal).** Refresh follower/engagement snapshots if stale; if new engagement exists,
   chain into `recoup-internal-consulting-linkedin-audience`. Update `integrations/linkedin/_work/LAST_SYNCED`.
4. **Gmail (capture FULL threads for real relationships — Attio-gated).** Scope = people who matter:
   query Attio live for **Customers + Warm Leads + Target Accounts + open-pipeline contacts**, collect their
   email domains/addresses (exclude any segments the workspace marks out of scope). For each
   client/deal, archive the **full thread history** (every message, untruncated):
   `python integrations/gmail/_work/export_thread_bodies.py --query "from:<domain> OR to:<domain>"
   --title "<Name>" --out <clients|pipeline>/<entity>/emails/email-archive-<YYYY-MM-DD>.md`. Then layer the
   triage on top — `pull_threads.py` for **awaiting-my-reply** — as derived signal, not a replacement for
   the archive. A **human, non-automated sender NOT in Attio** → don't archive; flag it in the report as a
   possible new lead. Never archive the whole mailbox (automated/no-reply/newsletters excluded). Stamp
   `integrations/gmail/_work/LAST_SYNCED`. No auth → skip + note.
5. **Slack (if auth configured — log + channel, like Gmail).** Pull deal-tied conversations only
   (never the whole workspace), and pull each one **complete — every top-level message AND every thread
   reply** (`--days 0 --threads`); a bounded window silently drops new replies on older threads, so don't
   use one. Run `integrations/slack/_work/list_access.py` to confirm read access, then for each row of the
   **Deal channel routing** table in `integrations/slack/AGENTS.md` run
   `integrations/slack/_work/pull_conversation.py --channel <id> --token user --days 0 --threads
   --out <dest>/<YYYY-MM-DD>-<channel>.md`. File each keeper next to its client, mine the internal
   product DM into `knowledge/product/`, and flag threads **awaiting my reply**. Mine only the lines new
   since `integrations/slack/_work/LAST_SYNCED` (so insights don't duplicate), then stamp it. No `SLACK_*`
   keys set → skip and note it.
6. **Research wiki (read-only content source).** Mined by `recoup-internal-consulting-research-miner` (delta-guarded
   via `integrations/research/_work/LAST_MINED`) and pulled at draft time by `recoup-internal-consulting-content-drafter`
   — see `integrations/research/AGENTS.md`. The Friday harvest lives in `recoup-internal-consulting-friday-review`;
   trigger the miner here too if the wiki's `log.md` advanced since `LAST_MINED`.
7. **Mine fresh material.** New won deals → `recoup-internal-consulting-case-study-builder`; recurring answers →
   `knowledge/faqs/`; reusable insights/ideas → atomic signals in `signals/`.
8. **Stamp + report.** Update each integration's `LAST_SYNCED`, the crm-sync "Last full reconcile"
   note, and write a short report: **what changed · what drifted · what's stale · what needs me**.

Confirm before inventing client facts. Do the routine filing/reconciling without asking.
