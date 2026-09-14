---
name: recoup-internal-consulting-nightly-ingestion
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. The autonomous nightly sweep. Runs unattended (cloud routine or local cron) to ingest the day's new meetings, emails, and LinkedIn engagement, run the full auto-manage loop on each new item, update dashboards/board/CRM, commit, and leave a morning digest. Use on \"run the nightly sweep\", \"ingest today\", \"catch the OS up\", or as the scheduled nightly ritual. Full autopilot, inside the three standing safety rails."
---

# Consulting Nightly Ingestion (autopilot)

## Visual handoff

When this workflow creates or requests a rendered artifact, use `recoup-internal-consulting-tasteful-design` and
the selected workspace DESIGN.md. House identity is Recoup Sky; explicit client/artist branding wins.
Pass brand/version, expression, format, reference IDs and output folder to the media skill. Its bundled
package supplies exact fonts/logos. Keep new derivatives in the current identity while preserving
historical evidence. Save editable source and brand.lock.json with the deliverable. Ordinary text
outputs stay text; a script is not a rendered video. Existing data dashboards retain their canonical
Recoup CSS during data updates. Do not publish private client work to the public Brand Studio.


**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

The hands-off version of the CLAUDE.md auto-manage loop. It assumes **no human is watching**, so it
does the safe work fully autonomously and is *stricter*, not looser, on anything it can't verify.

`recoup-internal-consulting-integrations-sync` is the **pull** half (gets new material in + advances watermarks).
This skill wraps it with the **process** half (extract → reconcile → update → commit) and a
**morning digest**. Run end to end, commit as you go, then write the digest. Do not stop to ask —
park anything uncertain in the digest's "Needs you" section instead.

## The three standing rails (never dropped under autopilot)
Autopilot means "no human in the loop," not "skip the rails." These come straight from CLAUDE.md:

1. **Never auto-send.** Every follow-up email / LinkedIn reply is a **draft only**
   (`integrations/gmail/_work/create_draft.py`; revise in place with `--update <id>`, never
   delete-and-recreate). List drafts in the digest for the user to send.
2. **Verify before you write money/dates/stage.** Every `$`, %, date, MRR/fee, or who-pays-whom claim
   that lands in a dashboard, board, dossier, or the CRM must be quoted from a **primary source** —
   the **captured verbatim transcript** (`…/meetings/transcripts/…`, *not* the AI summary), the
   **captured email archive** (`…/emails/…`), the contract, or a **live Attio field**. If you cannot quote it, write **[UNVERIFIED]** and
   route it to the digest's "Needs you" — do **not** assert it. Money is highest-stakes.
3. **Never auto-delete or bulk-sweep.** Add and update only. Never delete or batch-edit a mailbox or
   external record. Act only on an ID you created **this run**, never a pattern/search/list match.

## Steps

0. **Orient (git = memory).** `git log --oneline -20`; `git show`/`git log -p` on paths you expect to
   touch. Read the touched deal/client `AGENTS.md` before changing it. Confirm the env keys are present
   (`GRANOLA_API_KEY`, `GMAIL`/`GWS_*`, `ATTIO_API_KEY`, `APIFY_API_TOKEN`, `POSTBRIDGE_API_KEY`,
   `SLACK_BOT_TOKEN`/`SLACK_USER_TOKEN`/`SLACK_APP_TOKEN`).
   If a key is missing, skip that source and note it in the digest — never guess its data.

1. **Pull (delegate to `recoup-internal-consulting-integrations-sync`).** Run it for the live API sources only:
   **Attio** (query live, reconcile stage ↔ folder), **Granola** (capture **verbatim transcripts** for new
   in-scope notes via `list_new_notes.py` → `pull_transcript.py` — the transcript, never the AI summary;
   **Classify by title and content before capture.** An attendee list can suggest which account to
   inspect, but cannot establish scope. A solo-attendee note may still be a client call. Ambiguous,
   mixed personal/work, or excluded-job notes stay uncaptured and unsummarized; record only a count
   in the digest, not private titles, names, or excerpts. Apply the selected workspace intake policy.
   With the local adapter, use `pull_transcript.py --note <id> --reviewed-scope --out <dest>` only
   after this review. An available connector must enforce the same boundary.),
   **Gmail** (Attio-gated **full-thread archives** via `export_thread_bodies.py`, plus awaiting-reply
   triage), **LinkedIn** (refresh engagement), and **Slack** (deal-tied channels per its Slack step —
   **full pull: every message AND every thread reply**, `--days 0 --threads`; routing table in
   `integrations/slack/AGENTS.md`). Record source IDs and successful checkpoints so reruns can skip already processed items.
   **Use an overlapping Granola window** (default: watermark minus three days) and deduplicate by
   stable note ID. Late-visible notes may have creation times behind the watermark. The overlap is
   a recovery window, not a guarantee for arbitrarily late arrivals: use a specifically scoped
   recovery lookup if a known meeting is still missing. Advance only after successful capture and
   processing; preserve failed IDs for retry without saving excluded note content.
   **Fictional example:** a Cedar Lantern Studio call becomes visible the day after it occurred.
   Re-reading the overlap catches it; deduplication prevents the earlier calls being filed twice.
   Research is optional and uses only the source explicitly configured in
   `integrations/research/AGENTS.md`; skip it if unavailable in this worker.
   Product PRs use the repositories configured in `integrations/github/AGENTS.md` and an available
   GitHub connector or compatible local adapter. Do not assume a public organization or tokenless access.

2. **Process each NEW item through the auto-manage loop** (CLAUDE.md §"Auto-manage"). For every new
   meeting / thread / engagement the pull surfaced, **deal-scoped** (never cross unrelated clients, employers, or personal contexts
   in one item — Granola's don't-cross-jobs rule):
   - **Place** the raw file in its home (`clients/<client>/meetings/` or `…/slack/`,
     `pipeline/<stage>/<deal>/`, `knowledge/product/` for internal product DMs, or `content/01-raw/`),
     dated `YYYY-MM-DD`.
   - **Extract** → `recoup-internal-consulting-content-extraction` — write **atomic signals** to `signals/` (one file per
     item, each with a traversable `source` + `status`; see `signals/AGENTS.md`). This is the owned
     write-step for the reservoir. Discovery call → also `recoup-internal-consulting-discovery-analysis`; qualified →
     chain `recoup-internal-consulting-proposal-drafting`.
   - **Reconcile** the related folder: read its `AGENTS.md`, fix drift against the new info + live Attio.
   - **Update** all affected files: the deal/client `AGENTS.md` dashboard (status, stakes, $, next
     action), `pipeline/_board.md`, `business/metrics/dashboard.html`. New stakeholders, decisions, dates.
   - **Move on stage change:** `recoup-internal-consulting-deal-stage-mover` (folder + board + Attio in lockstep;
     `pipeline/**` ↔ `clients/**` on win) — but only with a primary-source signal for the move
     (rail #2); if the signal is ambiguous, stage the recommendation in the digest instead of moving.
   - **Mine:** new won deal → `recoup-internal-consulting-case-study-builder`; recurring answer → `knowledge/faqs/`;
     reusable win → `proof/` ask.

2b. **Product PRs → `product-update` signals (Engine B's capture half — NOT deal-scoped, a separate pass).**
   From the merged PRs the GitHub pull surfaced (step 1), **filter** to user-facing changes
   (conventional-commit prefix: keep `feat(...)`; drop `chore`/`test`/`ci`/`build`/`refactor`/`docs` + bare
   "Test"), **cluster** related PRs into one feature, and write one `product-update` signal per feature to
   `signals/` — each **cited to its PRs** (PR #/commit sha, never invented; **build activity ≠ adoption** —
   announce shipped capability, not usage you can't prove). Logic: `recoup-internal-consulting-product-engine` (its extract
   half). Then stamp `integrations/github/_work/LAST_SYNCED`. The content phase (phase 3) drafts these like
   any other signal; a **fresh** product-update jumps the queue because feature news is perishable.

3. **Apply the rails** (above) to everything step 2 produced: outbound → drafts; unverifiable figures →
   `[UNVERIFIED]` + digest; no deletes.

4. **Commit (the commit *is* the episodic memory).** Commit each meaningful change with a clear,
   why-first message. Group sensibly (one commit per deal/item is fine). If you changed a skill in the
   `plugin/` submodule, commit there too.

5. **Write the morning digest** → `business/ops/nightly-digests/<YYYY-MM-DD>.md` (create the folder if
   missing). Keep it skimmable for a 30-second morning read:
   - **Ingested** — what came in (N meetings, N threads, N engagements), each one line **with a link to
     its raw artifact** (transcript / email-archive / slack file). The digest is an *index into the raw*,
     never a substitute — every claim below must trace to one of these captured primary sources.
   - **Changed** — dashboards/board/CRM updates made, stage moves, new signals written to `signals/` (incl. `product-update` signals from PRs).
   - **Needs you** — the queue the rails parked: drafts awaiting send, `[UNVERIFIED]` figures to
     confirm, ambiguous stage moves, missing keys/sources. This is the section the user actually acts on.
   - **Commits** — the `git log --oneline` for the run, so the digest ties back to the memory.
   - **Score** — run `python evals/ingestion/score_run.py` and put the **composite + any flags** at the
     top of the digest. A dropped composite or a new flag (orphan, duplicate, missing transcript) is the
     drift signal to act on — see `evals/ingestion/RUBRIC.md`.

6. **Stop.** Do not send, do not delete, do not ask. The digest's "Needs you" is the handoff.

## Notes
- **Idempotent by watermark.** Correctness depends on `LAST_SYNCED`/`LAST_MINED` being honored and
  advanced. If a source has no new items since its marker, that's a clean no-op — say so in one line.
- **Subagents are leads, not facts.** If you dispatch one to read/derive, require source file+line or
  verbatim quote for every quantitative claim, label the rest `[UNVERIFIED]`, and re-verify its numbers
  against the primary source yourself before writing them anywhere.
- **Quiet nights are fine.** No new material → write a one-line digest ("nothing new since <date>") and
  commit nothing. Don't manufacture work.
