---
name: recoup-internal-consulting-system-auditor
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Reconcile and health-check the whole workspace. Use on \"audit the system\", \"is everything up to date\", or periodically."
---

# Consulting System Auditor

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

## Steps
1. Reconcile filesystem ↔ Attio CRM: deals in the right stage, no drift (`integrations/attio/crm-sync.md`).
2. Find stale client `AGENTS.md` dashboards (status/next-action out of date).
3. Find un-processed transcripts in `content/01-raw/` and `*/meetings/` (→ run `recoup-internal-consulting-call-processor`).
4. Find wins missing a case study or testimonial; recurring answers missing an FAQ.
5. Check the dashboard and metrics are current.
6. Report a prioritized punch list (don't auto-change client facts without confirming).

Source: CLAUDE.md auto-manage discipline.
