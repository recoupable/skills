---
name: recoup-platform-track-onboarding
description: >-
  Check how far a Recoup account has gotten in onboarding and drive it to the
  next step. Measures the account against the eight activation checkpoints
  (artist added, socials connected, first chat, valuation run, catalog claimed,
  first scheduled task, paying) using the caller's own API key, then routes to
  the skill that completes the next step. Use for "where am I in my Recoup
  setup", "what should I do next", "did I finish onboarding", "onboarding
  status", "activation checklist", "how set up is my account", or after
  recoup-platform-connect-account finishes first-run setup. Read-only; never
  performs the steps itself — it routes.
---

# Recoup — Track Onboarding

Score an account against the Recoup activation funnel and say exactly what to
do next. The checkpoint definitions, API calls, and scoring rules live in
`references/onboarding-checkpoints.md` — read that first.

## Prerequisites

- A connected account: `RECOUP_API_KEY` from `~/.claude/recoup.env` (if absent,
  run recoup-platform-connect-account first — that IS step 1).
- Base URL `https://api.recoupable.dev/api`, auth header `x-api-key`. Load
  recoup-platform-api-access for endpoint plumbing.
- Recoup staff with an admin token may score **any** account by appending
  `?account_id=<uuid>` to the list endpoints (reads only).

## Procedure

1. Run the owner-token check for each checkpoint in
   `references/onboarding-checkpoints.md`, in order. Every call is a GET.
2. Present the scorecard: one row per checkpoint, ✓/—, with the evidence
   (counts, names, dates). State the furthest contiguous step and any skipped
   steps explicitly.
3. Name the single next action and hand off to the skill that does it:

   | Missing step | Route to |
   |---|---|
   | 2 — no artist | recoup-roster-add-artist (bulk roster: recoup-roster-onboard) |
   | 3 — no socials | recoup-roster-manage-artist |
   | 4 — never chatted | suggest one concrete first prompt using their artist's name |
   | 5–6 — no valuation / unclaimed catalog | recoup-catalog-estimate-value |
   | 7 — no scheduled task | propose one recurring report tied to what they did in steps 4–6 (e.g. weekly streams + socials digest for their claimed catalog) |
   | 8 — not paying | mention Pro only if they hit a limit; never lead with it |

4. One goal per session: recommend exactly one next step, not the whole list.
   If the account is fully activated (through step 7), say so and stop.

## Guardrails

- Read-only: this skill never creates artists, tasks, or catalogs — it routes
  to the skill that does, and that skill asks its own confirmations.
- Don't shame gaps ("you haven't done X") — frame as the next win.
- An empty roster on a fresh key can be a throwaway-credential problem, not a
  new account: if orgs AND artists are empty but the account is weeks old,
  surface that (see recoup-platform-connect-account guardrails) instead of
  restarting onboarding.
