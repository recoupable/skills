---
name: recoup-internal-consulting-followup-sequencer
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Generate the timed follow-up cadence for a deal, personalized to the client's stated stakes. Use after a call or proposal, on \"draft follow-ups\", \"they went quiet\", \"what do I send next\"."
---

# Consulting Follow-Up Sequencer

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

> Voice + gate: write in `recoup-internal-consulting-copy-writer` voice, then run every draft through `recoup-internal-consulting-outbound-email` (read context, route, reader-POV check) before staging.

## Steps
1. Pull the deal's specifics: the outcome discussed, the stakes in their words, the next-meeting date.
2. Fill the templates in `library/email-templates/`:
   - Same-day thank-you
   - 24h value-add (attach a relevant resource/case study)
   - Proposal delivery (within 48h, suggest a Loom)
3. If silent, generate the Day 5 / 10 / 15 sequence (max 3 touches), each referencing *their* stakes, not your proposal.
4. **Stage in Gmail (optional).** Offer to drop each touch into Gmail as a draft via
   `integrations/gmail/_work/create_draft.py --to <addr> --subject "..." --body-file <file>`
   (creates a draft; only sends with `--send` + a typed confirmation). Save drafts next to the deal
   (e.g. `pipeline/01-leads/<deal>/followups.md`).
5. Offer to set reminders / a scheduled task for the cadence.

Output: ready-to-send emails (optionally staged as Gmail drafts). Source: Ch. 14 (48-Hour Rule + follow-up sequence).
