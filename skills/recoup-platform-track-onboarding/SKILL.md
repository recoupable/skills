---
name: recoup-platform-track-onboarding
description: >-
  Check a Recoup user's setup for their intended workflow and identify the next
  applicable step. Use for "where am I in my Recoup setup", "did I finish
  onboarding", "onboarding status", or "activation checklist". Supports artists,
  writers, publishers, labels and file-based catalog work. Reads available account
  evidence and routes the next requested setup task; never requires an artist,
  valuation, claimed catalog, payment or scheduled task for every user.
---

# Recoup — Track onboarding

Read `references/onboarding-checkpoints.md`. Establish the user's actual goal and
workspace before checking readiness. A songwriter organizing files, a label planning
releases and an adviser reviewing an acquisition have different completion conditions.

## Access and scope

Use an already authenticated MCP connection when available. REST helpers may instead
use a supplied `RECOUP_API_KEY` or `RECOUP_ACCESS_TOKEN`; no Claude-specific environment
file is required, and MCP OAuth credentials remain inside the host. Verify the selected
account/workspace through discovered read operations. Never create another identity to
recover access. File-only catalog work can proceed without platform login.

Do not assume staff access or append arbitrary account IDs to endpoints. An authorized
staff operation must explicitly support the selected account and permission scope.
No read or setup request authorizes paid captures, rights filing, scheduling or purchases.

## Procedure

1. State the intended outcome and relevant object: composition, recording/release,
   royalty period, transaction or artist roster. Reuse known context instead of asking
   the user to complete an unrelated funnel.
2. Inspect applicable checkpoints with discovered supported read operations or supplied
   files. Mark each ready, missing, unknown/access_unavailable or not_applicable. Cite
   counts/record IDs/dates privately. An unavailable endpoint is unknown, not a failed user.
3. Report the applicable readiness and exactly one useful next action. Examples:
   import a repertoire file; explain the supplied administration agreement; reconcile
   a royalty statement; add an artist only when a roster is actually needed; connect an
   account only when the requested hosted operation needs it. A public estimate is optional.
4. Keep any commercial adoption indicators separate from task readiness. A recurring
   report is optional and requires a scheduling request; paying is not a prerequisite
   unless the requested operation reaches a real billing gate. Surface the actual gate.
5. Stop after the scorecard and bounded handoff. This skill never creates artists,
   attaches catalogs, schedules jobs, submits registrations or executes the next stage.

An empty roster or organization can be legitimate. Verify identity and workspace before
suggesting setup changes. A complete file review remains complete even if no artist,
valuation, platform catalog claim or subscription exists.
