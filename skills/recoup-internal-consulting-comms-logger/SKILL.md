---
name: recoup-internal-consulting-comms-logger
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Log a single comms event on a deal/client (you sent, they replied, it was opened, you got a message) and reconcile state. Use on \"I sent that\", \"he replied\", \"they opened it\", \"got a reply from {name}\", \"just emailed {name}\", or a screenshot of a sent/received message. Faithfully records the as-sent/as-received text + the engagement signal (open != reply), then updates the deal AGENTS.md, _board.md, any active followups sequence, and whose ball it is. NOT recoup-internal-consulting-call-processor (the heavy \"new material -> extract + mine\" loop for transcripts/notes/results) and NOT recoup-internal-consulting-inbox-triage (the radar for what needs a reply across deals) -- this is the light \"log one touch and reconcile\" move."
---

# Consulting Comms Logger

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

The fast path for **after** a touch happens. Email skills (`recoup-internal-consulting-outbound-email`,
`recoup-internal-consulting-followup-sequencer`) own *drafting*; this skill owns *recording the event and
reconciling the deal* once a message has actually gone out or come in. Git is the episodic
memory, so a logged touch must leave the dashboards true.

> Scope one deal. Load only that entity's folder + its live Attio/Gmail (deal-scoped loading).
> **Logging only — never auto-send, never fabricate.**

## Steps

1. **Identify the deal/client.** Locate `pipeline/<stage>/<deal>/` or `clients/<client>/`. If you
   can't tell which deal, ask.

2. **Capture the event faithfully (evidence discipline).**
   - **As-sent / as-received text, verbatim** — what *actually* went out, not the draft you think
     was sent. From a screenshot, transcribe exactly. Note the provenance ("logged from the owner's word"
     vs. "screenshot" vs. "live Gmail"), since a screenshot is stronger than a paraphrase.
   - **Channel + timestamp** (thread subject, LinkedIn, etc.), in the user's timezone.
   - **Engagement signal, read literally:** an **open / read-receipt is engagement, not a reply**;
     a reply is not a commitment. Quote the source (Superhuman receipt, screenshot, live Gmail).
     **Never upgrade a signal into momentum** ("opened in 2 min" = watching the thread, still no
     reply/booking/decision).
   - **Missing detail?** Get it from the **live** source, not a stale snapshot (e.g. a cc email: the
     synced `integrations/gmail/threads/<deal>.json` predates today's reply, so query Gmail live).
     Never guess an address or name.

3. **Decide the ball + posture.** Who owes the next move now (mirror `pull_threads.py` logic): a
   question/ask to you = **needs you**; a forward commitment ("I'll get back to you") = **on them**;
   an open with no reply = **still on them**. When the ball is on them, the posture is **don't
   chase** (let `recoup-internal-consulting-lead-temperature` set the objective if a touch is warranted).

4. **Reconcile every state surface** (the actual job):
   - **Deal `AGENTS.md`:** the `## Reality` "where it stands" line, the **📧 Email signal** log
     (append dated), the **Next action**, and the ball. Keep the [MISSING] list honest (resolve what
     this event answered: a timeline, a stakeholder, who-signs).
   - **`pipeline/_board.md`** row (or the client board).
   - **Active `followups.md`:** **STOP the sequence the moment they reply** (mark queued touches
     `VOID`); otherwise advance it. A reply kills the nudge cadence.
   - **New stakeholder surfaced?** Capture them: live email lookup + a **dedup-safe** Attio add
     (check by email before creating; dry-run then apply) and add to the dashboard roster.

5. **Reconcile-on-touch (Attio).** A comms touch usually does **not** change the deal stage, but
   verify live and fix any drift (Attio wins on stage, the repo on artifacts). Don't copy the CRM in.

6. **Report + commit.** Summarize what changed in one or two lines; the commit is the memory. Offer
   to commit (don't auto-commit unless asked).

## Worked example — fictional touch sequence

All names, companies, and events here are invented.
- A proposal email to Morgan at Cedar Lantern Studio is opened. Record an open; the ball remains
  with Morgan because no reply has arrived.
- Morgan replies and introduces Jordan. Stop the queued nudge sequence, verify Jordan's address
  from that reply, and check for an existing CRM record before adding one.
- The consultant answers Jordan's question. Log the actual sent text and receipt, then update who
  owes the next action. None of these touches proves a purchase commitment.

## Related
- Heavy intake (transcript / note / result) -> `recoup-internal-consulting-call-processor`.
- "What across all deals needs a reply?" -> `recoup-internal-consulting-inbox-triage`.
- Drafting the next touch -> `recoup-internal-consulting-followup-sequencer` + `recoup-internal-consulting-outbound-email`.
- Posture/score -> `recoup-internal-consulting-lead-temperature`. CRM mechanics -> `integrations/attio/crm-sync.md`.
