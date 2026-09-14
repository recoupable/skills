---
name: recoup-internal-consulting-outbound-email
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. The process every personalized outbound email runs through before it is staged — gather full context on the person, decide who it is really for and what the objective is (set by temperature), simulate the reader, and pass the pre-send gate. Use when drafting or reviewing any 1:1 nudge, follow-up, broadcast, or stakeholder note. Voice and craft live in recoup-internal-consulting-copy-writer; the context gather lives in recoup-internal-consulting-lead-context."
---

# Consulting Outbound Email

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

The shared gate for outbound email. `recoup-internal-consulting-email-atomizer`, `recoup-internal-consulting-followup-sequencer`,
`recoup-internal-consulting-stakeholder-update`, and the newsletter compile (`recoup-internal-consulting-friday-review`) all run their
drafts through this before staging.

This skill owns the **process**: who the email is for, what its objective is, the reader-POV check, and
the pre-send gate. It does not own the writing rules.

- **Voice and craft → `recoup-internal-consulting-copy-writer`.** Zero em-dashes, short and direct, plain words a human
  would say out loud, evidence over vague authority, confident-not-needy outreach posture. Every rule
  there applies to every email; this skill does not restate them.
- **Context gather → `recoup-internal-consulting-lead-context`.** The full dossier on the person before you write.

## 1. Read all context first

Never draft from a snippet or a single source. Before writing to a named person, gather everything
knowable by running `recoup-internal-consulting-lead-context`: the post or thread they actually engaged (read the FULL
thing, not their one-line comment), Gmail history for them *and their colleagues*, Granola notes, the
deal file (`pipeline/<stage>/<deal>/AGENTS.md` or `clients/<client>/`), the live Attio record, and the
`recoup-internal-consulting-lead-temperature` record on the dashboard (recompute it if it is missing or stale).

Resolve it yourself. Escalating "confirm X before I send" to the human is the last resort, only after
those sources are exhausted. If the answer sits in a post, a profile, a thread, or a company's homepage,
go get it.

## 2. Decide who it is for, and the objective

- **Who:** the exec sponsor (keep it light, route the work to the team) vs. the hands-on POC (go deep on
  their actual pain). Target the message and the ask to that person, not the company in general. Get
  every name, title, and role right.
- **Objective (set by temperature, not just tone):** let the `recoup-internal-consulting-lead-temperature` score set
  what this one touch is *for*.
  - **Hot (8-10):** advance or close. A direct ask, book the next step.
  - **Cooling (5-7):** regain attention and curiosity. Lead with something genuinely interesting, ask
    for little or nothing. Do not try to close — that is what reads as a pushy vendor.
  - **Cold (2-4):** pure value, no ask.
  The ask scales with temperature; rising vs. falling shifts the tone even at the same score.

## 3. Reader-POV loop (any important email)

Spawn a subagent to read the draft as the actual recipient — a busy human with limited attention: line
by line in their voice, where they skim, what feels salesy / needy / presumptuous, and reply odds
(1-10). Revise and loop until it lands. Keep those simulated reactions ephemeral; never file them into
the CRM or a deal folder.

## Pre-send checklist

- [ ] Voice pass done against `recoup-internal-consulting-copy-writer` (zero em-dashes; plain words; nothing a human
      wouldn't say out loud; no vague authority — every claim backed by a real, named example or dropped).
- [ ] First line states the point; reads cool, calm, and confident, not needy.
- [ ] Every name, title, and fact verified against real context, not assumed.
- [ ] Right person, right ask (sponsor vs. POC); one low-effort default, work taken off their plate.
- [ ] Ran the reader-POV subagent loop.

Apply the selected workspace voice preferences to the template.
