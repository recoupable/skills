---
name: recoup-internal-consulting-inbox-triage
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Turn the inbox into a prioritized \"what you owe people\" digest across active deals. Use on \"what emails need a reply\", \"triage my inbox\", \"what am I behind on\", or as a daily/weekly ritual. Reads Gmail, classifies by who owes the next step, and ties each thread to its deal."
---

# Consulting Inbox Triage

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

Surface only the threads where the ball is actually on you — no bot noise, no threads you already
answered, no "they'll follow up" closes.

## Steps
1. **Gather active relationships.** From `clients/` + `pipeline/` (and Attio if needed), collect the
   key email addresses/domains for each open deal/client.
2. **Pull threads.** Run `integrations/gmail/_work/pull_threads.py --query "<addr/domain>"` per deal
   (or a combined query). It classifies each thread's **full last-message body** into:
   `needs_your_reply` · `waiting_on_them` · `courtesy_close` · `automated` · `you_replied_last`.
3. **Build the digest** — list only `needs_your_reply`, grouped by deal/client, newest first. For
   each: subject, who's waiting, and a one-line "what they want." Note `waiting_on_them` separately
   (so you know who *you're* waiting on, e.g. the contact's availability).
4. **Reconcile.** If a thread reveals a deal moved (signed, scheduled, went cold), update the deal
   `AGENTS.md` dashboard + `pipeline/_board.md`, and check Attio (`recoup-internal-consulting-integrations-sync`).
5. **Offer to draft.** For each `needs_your_reply`, offer a draft via
   `integrations/gmail/_work/create_draft.py` (creates a Gmail draft; never sends without `--send`
   and confirmation). Ground replies in the deal context + the thread.

Note: classification reads only the latest message body; verify before sending. Never auto-send.
Output: a prioritized reply digest + optional ready-to-review drafts.
