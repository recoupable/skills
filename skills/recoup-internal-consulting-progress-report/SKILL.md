---
name: recoup-internal-consulting-progress-report
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Draft a recurring client progress report from primary evidence, review it for the sponsor, and prepare the authorized delivery format. Use for biweekly or monthly engagement reports; use recoup-internal-consulting-stakeholder-update for a short session recap."
---

# Consulting Progress Report

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

Write the recurring client update from verified work and observed outcomes. Match the agreed
reporting cadence and the sponsor's needs; keep it short enough to read on a phone.

## Inputs

Use the selected workspace and one client only. Read its `AGENTS.md`, executed agreement,
`04-delivery/account-activity-log.md`, recent reports, client-facing running lists, and primary
sources in `meetings/transcripts/` and `emails/`. Preserve any existing Reality heading, including
an owner-specific title. Confirmed owner statements outrank inferred account state.

Read the installed `recoup-internal-consulting-copy-writer` skill and its relevant references, including the full
anti-slop reference. Use the workspace's voice preferences. A remembered summary of a writing guide
is not a substitute for the rules it contains.

For a complete format example, read `references/fictional-progress-report.md` relative to this skill.
Every company, person, figure, and event in that example is invented. Never use it as client evidence.

## Evidence and client boundaries

- Verify every number, attribution, date, state claim, and commercial term against a primary source.
  AI meeting summaries are leads; use the verbatim transcript, email, executed agreement, or live field.
- Separate shipped code, live availability, observed usage, and measured impact. One does not prove another.
- Qualitative estimates must be attributed and labeled as estimates. Missing outcome measurements stay
  missing; record who can provide them in the internal notes rather than inventing a savings figure.
- Reconcile corrections and conflicting counts before publishing. Log user-confirmed facts back to the
  account record with their provenance. Do not hide an unresolved disagreement behind a precise number.
- Only include actual account spending and approved controls when relevant. This skill supplies no
  budget, spending cap, fee, default allowance, or promise of a future measurement.
- Keep internal expansion notes, private collaborator assessments, and other clients' records out.
- Ownership, support terms, exclusivity, and scope must match the executed agreement. A new opportunity
  belongs in a separate proposal, not an implied commitment in a progress update.

## Report shape

Adapt this shape to the client; omit unchanged sections and use the account's template when it exists.

1. Greeting and one sentence identifying the reporting period.
2. **What changed:** a few concrete before → after bullets. Lead with the strongest observed result.
3. **Quick notes:** useful context such as rollout status, measured usage, or an agreed spending policy.
4. **Next period:** actual commitments with owners; distinguish proposed work from committed work.
5. **Where this is heading:** a brief, client-relevant explanation of deferred work. Label it unstarted
   and uncommitted. Do not turn a vendor meeting into a story about winning more scope for yourself.
6. **Needs:** only actionable requests, routed to the person who can resolve each one.

Use stakeholder goals when they help explain a change. Repeating the same goal every report becomes
noise. Report the delta. Keep the main body near one page; supporting evidence stays in internal notes.
Use plain text system names in email output: Markdown backticks often paste as literal characters.

## Process

1. Backfill missing activity from primary evidence, then assemble a cited claim list.
2. Draft in `clients/<client>/04-delivery/progress-reports/<date>-report-<number>.md`, marked DRAFT.
3. Apply the copywriter's full anti-slop pass, including patterns requiring reading rather than search.
4. Review through the actual sponsor's needs using `recoup-internal-consulting-copy-reviewer`. Any simulated reader
   feedback is an editing aid, never a quote from the sponsor or evidence of their opinion.
5. Make a fresh-context condense pass: remove repetition, combine related bullets, and catch conflicting
   states. Use a separate reviewer when available; otherwise perform and label a second editing pass.
6. Incorporate the user's corrections and record newly supplied facts with provenance. Commit meaningful
   changes according to the workspace's existing convention.
7. Prepare the requested delivery format. A clean HTML paste source, short video script, or Slack variant
   is optional. Default to a draft; send only when the user has authorized that recipient and content.
8. After a confirmed send, retain the as-sent text and receipt, update the activity log, due date,
   commitments, and next actions. Never mark SENT from a prepared draft alone.
9. Improve the client template for client-specific preferences and this skill for reusable lessons.
