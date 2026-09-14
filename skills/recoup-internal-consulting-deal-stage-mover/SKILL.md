---
name: recoup-internal-consulting-deal-stage-mover
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Advance a deal cleanly when its state changes. Use on \"move X to proposal\", \"we won/lost the deal\", \"X signed\", or any pipeline stage change. Keeps folders, the board, and the CRM in sync."
---

# Consulting Deal Stage Mover

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

## Steps
1. Locate the deal folder under `pipeline/{current-stage}/{deal}/`.
2. Move it to the new stage:
   - Forward through `pipeline/01-leads → 02-qualifying → 03-discovery → 04-proposal → 05-negotiation`.
   - On **win**: run `recoup-internal-consulting-client-onboarding` (move into `clients/{client}/`).
   - On **loss**: move to `pipeline/closed-lost/` and write a short post-mortem (why, what to learn).
3. Update `pipeline/_board.md`.
4. Update the Attio CRM stage to match (`integrations/attio/crm-sync.md` mapping).
5. Update `business/metrics/dashboard.html` funnel counts.

Rule: never let the filesystem and CRM drift. Report the move.
