---
name: recoup-internal-consulting-lead-intake
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Triage a brand-new inbound lead. Use when a new prospect appears — a fresh inquiry email, a first-call transcript, \"new lead\", \"qualify this prospect\", \"should I take this deal\". Verifies the lead against primary sources, creates the pipeline folder, qualifies the buyer, and opens a CRM record."
---

# Consulting Lead Intake

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

## Steps
1. Create `pipeline/01-leads/{deal-name}/AGENTS.md` (dashboard: source, contact, stage, next action) — open it with a `## Reality` block (label it **DRAFT** if agent-reconstructed; see `recoup-internal-consulting-account-reality`).
2. Save any raw inquiry/transcript into that folder, dated.
3. **Verify before you qualify — never trust a single mention.** A lead that surfaced from a summary, a passing mention, or one channel is **[UNVERIFIED]**. Traverse the primary sources for the *real* thread / contact / stakes before triaging:
   - **Gmail:** `python integrations/gmail/_work/pull_threads.py --query "<name or @domain>"` → file the snapshot in the lead folder.
   - **Granola:** the intro-call note — verify any figure against the **verbatim transcript** (`?include=transcript`), not the AI summary.
   - **Attio:** query live (avoid duplicates; get the real stage).
   Quote source + date for every fact; mark what you can't find **[MISSING]**; and **correct overstatements** (e.g. an AI summary's "proposal out" when the thread shows only an intro call). Build/activity ≠ commitment; a summary ≠ the transcript.
4. Run the qualification checklist (Ch.10), grounded in what you verified:
   - Stakes — clear, painful, quantifiable problem?
   - Timeline — urgency?
   - ROI measurability — can success be measured?
   - Decision-maker — is the budget authority engaged? (name the buyer vs. the POC)
5. Flag red flags (vague "nice to have", no authority, wants hourly, **single thin source**) → recommend qualify or pass.
6. **Attio — only once the entity + a real contact are confirmed.** Create/update the record (stage = Lead, source, stakes, next action). Don't open a CRM record off one unverified mention.
7. If qualified, recommend the next move (book discovery, or hold for their committed follow-up) and note it on `pipeline/_board.md`.

Output: a triaged lead folder + a clear qualify/pass recommendation. Don't invent stakes — pull from **verified** primary sources, and say **[MISSING]** when you can't.
