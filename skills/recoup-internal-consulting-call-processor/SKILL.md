---
name: recoup-internal-consulting-call-processor
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. The auto-manage orchestrator. Use whenever new client/deal material lands — a transcript, meeting note, email, or result — or when the user says \"process this call\", \"ingest this\", \"handle this transcript\". Runs the full keep-the-system-current loop end to end."
---

# Consulting Call Processor

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

The CLAUDE.md auto-manage loop as one skill. Don't stop after a single step — run the whole loop, then report what changed.

## Steps
1. **Place the raw file.** Save to the right home (`content/01-raw/`, `clients/{client}/meetings/`, or `pipeline/{stage}/{deal}/`), dated `YYYY-MM-DD`.
2. **Read it.**
3. **Extract.** Run `recoup-internal-consulting-content-extraction`. If it's a discovery/sales call, also run `recoup-internal-consulting-discovery-analysis`; if the deal is qualified, chain into `recoup-internal-consulting-proposal-drafting`.
4. **Scan the related folder.** Open the client/deal folder, read its `AGENTS.md` dashboard, reconcile against the new info.
5. **Update affected files.** Refresh the client `AGENTS.md` dashboard (status, stakes, $, next action), `pipeline/_board.md`, and `business/metrics/dashboard.html`. Capture new stakeholders, decisions, dates.
6. **Move files to match reality.** If the deal changed stage, run `recoup-internal-consulting-deal-stage-mover`.
7. **Mine for content + proof.** Recurring answers → `knowledge/faqs/`; wins → trigger `recoup-internal-consulting-case-study-builder` / `recoup-internal-consulting-testimonial-capture`.
8. **Report** a short summary of everything changed.

Confirm before inventing client facts; otherwise do the routine filing without asking.
