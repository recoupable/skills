---
name: recoup-internal-sales
description: >-
  INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke
  ONLY when the request explicitly includes "recoup-internal" (e.g.
  "recoup-internal run the sales sweep"). Never use for customer-facing or
  artist requests.
  Run Recoup's daily sales sweep — walk the whole activity surface (Stripe
  payments, Privy logins, new catalog valuations, the Attio pipeline, Supabase
  credits, scheduled tasks, and chats), turn each signal into a prioritized
  follow-up, then act on it: log the follow-up in Attio and draft (never send)
  outreach. Use when asked to "run the sales sweep", "who should we follow up
  with", "work the sales pipeline", "any new customers to reach out to", "who
  signed in / paid / ran a valuation", "who's about to churn", or "find zombie
  tasks we can turn off". Requires Stripe, Privy, Supabase, Attio, and Recoup
  API access.
---

# Recoup Sales Sweep

The repeatable **prospecting + follow-up** motion for Recoup staff. Seven data
pulls plus one synthesis: read every place a sales signal shows up, collapse it
into one ranked list of people to follow up with, then act — enrich/advance the
Attio pipeline and draft the outreach. First drafted 2026-07-23; refine the
steps below against each real run.

Define the window up front as UTC `[FROM, TO)` — usually **since the last sweep**
(default last 24h). Run the seven pulls in parallel (subagents work well; each is
self-contained), then synthesize.

## What this is (and what it is not)

This skill is **forward-looking**: it produces *actions* (who to contact, why,
how). It deliberately reuses the data plumbing of two sibling skills instead of
re-implementing it — load them for the ready-made queries/scripts:

- **`recoup-internal-weekly-usage-review`** — the retrospective *numbers* (Stripe,
  Privy logins, the credits/chats/tasks/valuations SQL pack). This sweep turns those
  same pulls into follow-ups; that skill reports the totals.
- **`recoup-internal-funnel-valuation-pipeline`** — the *deep* motion for one
  valuation lead: Attio funnel recipes, qualification rubric, the valuation PDF,
  and the outreach template. Step 3 hands qualified new valuations to it.

Also useful: **`recoup-internal-account-health-report`** (deep dive on one account
you're about to contact), **`recoup-internal-task-email-audit`** (task-run health
for step 6), **`recoup-platform-api-access`** (raw Recoup API).

## Prerequisites

- Stripe: authenticated CLI **or** a live restricted key (pass `--api-key` — the
  keychain is often unreadable in sandboxed shells).
- `PRIVY_APP_ID` + `PRIVY_PROJECT_SECRET` — Privy Management API.
- Supabase read access to production (MCP `execute_sql` or psql).
- `ATTIO_API_KEY` — read + write (this sweep *writes* follow-ups back).
- `RECOUP_API_KEY` / `RECOUP_ACCESS_TOKEN` — Recoup API for account/artist detail.

Everything is a GET or SELECT **except** the two sanctioned writes named in
Guardrails (Attio follow-ups; disabling a confirmed-dead task). Outreach is
**always drafted for a human to send**, never sent from this skill.

## The seven pulls

Each pull is: **what to read → the sales signal → the action**. Always drop test
rows (`sweetmantech*`, `sidney@`, `@example.com`, `[TEST]`, `preview-auth-probe`).

### 1. Stripe — new money to protect

- **Read:** subscriptions created / trials converted / first invoices in the
  window; failed payments + disputes; `credits_topup` sessions (weekly-usage-review
  §3 has the exact calls).
- **Signal:** a **new paid customer or trial-converter** → welcome + make-sure-they-
  activate follow-up (the highest-value moment to reach out). A **failed payment /
  dispute** → save-the-account follow-up, today. A **top-up loop** (many identical
  small sessions) → a "let's right-size your plan" conversation.
- **Action:** log the person in Attio; draft the welcome / recovery note.

### 2. Privy — who is signing in

- **Read:** the Privy-logins script from `recoup-internal-weekly-usage-review` — it
  paginates the Privy Management API into new signups vs returning for the window.
- **Signal:** a **new signup with no chats yet** → onboarding-stall follow-up. A
  **returning power user** → expansion. An **enterprise/label domain** email → high-
  value human outreach. Cross-check session-riders (long sessions never bump
  `latest_verified_at`) against the interactive-chats query in step 7.
- **Action:** route new signups through the activation-funnel lens; flag warm
  enterprise leads for a personal note.

### 3. Valuations — new catalog leads

- **Read:** `playcount_snapshots` created in the window (weekly-usage-review SQL
  query 13). A row with a **NULL `catalog`** is a *measured-but-unclaimed* run — a
  brand-new warm lead nobody is working yet.
- **Signal:** every new valuation is a lead; unclaimed ones are the freshest.
- **Action:** hand each qualified lead to
  **`recoup-internal-funnel-valuation-pipeline`** (research → qualify → enrich Attio
  → valuation PDF → outreach). Don't re-implement that motion here.

### 4. Attio — the follow-up backlog (the heart of this sweep)

The one pull that is *only* about follow-through. Load
**`recoup-internal-funnel-valuation-pipeline`** for its Attio funnel recipes (list
entries, stages, field slugs, enrich/advance calls), then surface:

- **Owed a nudge:** entries at **Report Delivered** or **Pro Offer Sent** whose
  last activity is older than the follow-up SLA (default **3 business days**) with
  no reply/advance — someone we reached out to who went quiet.
- **Flagged for follow-up:** any entry whose note / next-step says to circle back.
- **Signal → action:**
  - Non-responder, < 3 touches → draft the next nudge (new angle, not a resend).
  - Non-responder, ≥ 3 touches over ~2 weeks → move to **Lost** with
    `lost_reason = No response` so the board stays honest.
  - Replied / booked → advance the stage and set the next step.
- Always set the `owner` so every live lead is accountable to a person.

### 5. Credits — engagement and billing risk

- **Read:** per-account burn, current balances, and prior-week-active-now-silent
  (weekly-usage-review SQL queries 2, 4, 8).
- **Signal:** **heavy burners** → healthy; candidate for expansion / a testimonial.
  **Negative balance still burning** → billing risk *and* a top-up conversation
  (nothing stops them at zero). **Went silent** (active last week, zero this week) →
  churn-save follow-up while it's still warm.
- **Action:** log the follow-up; for a billing-risk account, pair the outreach with
  the plan-fit conversation from step 1.

### 6. Tasks — zombie schedules on inactive accounts

Scheduled tasks keep firing (and burning AI tokens) long after an account goes
cold. Find enabled schedules whose owner has **no recent usage and no recent
login** — reach out to confirm the task still adds value, else turn it off to save
spend. `scheduled_actions.last_run` is dead (not written by the Workflows runner),
so judge activity by `usage_events`, not that column.

```sql
-- Zombie tasks: enabled schedules whose account had NO usage in the last 30 days.
-- (Cross-check task-run health with recoup-internal-task-email-audit.)
SELECT sa.account_id, ae.email, sa.title, sa.schedule, a2.name AS artist,
       (SELECT MAX(created_at) FROM usage_events ue
          WHERE ue.account_id = sa.account_id) AS last_usage
FROM scheduled_actions sa
LEFT JOIN LATERAL (SELECT email FROM account_emails
  WHERE account_id = sa.account_id LIMIT 1) ae ON true
LEFT JOIN accounts a2 ON a2.id = sa.artist_account_id
WHERE sa.enabled = true
  AND NOT EXISTS (SELECT 1 FROM usage_events ue
    WHERE ue.account_id = sa.account_id
      AND ue.created_at >= now() - interval '30 days')
ORDER BY ae.email NULLS LAST, sa.title;
```

- **Signal:** a still-firing task for a dormant / non-paying account = wasted
  tokens **and** a re-engagement opening ("this report still runs — still useful?").
- **Action:** draft the check-in. Disable the schedule **only** after no-response or
  an explicit "turn it off" — see Guardrails; disabling is a mutation.

### 7. Chats — what customers actually use Recoup for

- **Read:** chats created in the window with titles, split interactive vs
  `'Scheduled generation'` (weekly-usage-review SQL queries 5a/5b). Titles are
  admin-readable; **bodies are owner-scoped** (see account-health caveat).
- **Signal:** theme the titles (strategy / analytics / content / release) to see
  *what* the product is used for — that shapes both the follow-up hook and product
  feedback. A **new interactive user** is engaged and worth a check-in; a
  **recurring pain theme** is a feature request plus a helpful-outreach opening.
- **Action:** note the usage themes; follow up with high-intent interactive users;
  feed recurring friction back to product.

## Synthesis — one ranked follow-up list

1. **Collapse to people.** Key every signal by account/email and merge across the
   seven pulls — one person, all their signals, deduped.
2. **Rank by opportunity × urgency.** Roughly: failed payment / churn-in-progress
   (save today) > new paid customer (welcome now) > warm valuation or enterprise
   lead (work this week) > expansion / testimonial > zombie-task cleanup.
3. **Correlate across sources** — the cross-checks are where the real finds are:
   - paid in Stripe **but** no Privy login → onboarding never landed; reach out now.
   - valuation run **with no Attio entry** → an unworked lead; create it (step 3).
   - negative credits **and** an enterprise domain → expansion priced as risk.
   - zombie task **on** a went-silent account → one message does double duty
     (re-engage + stop the token drain).
4. **Act:** write the follow-ups into Attio (create/advance entries, set `owner` +
   next step) and draft each outreach. Present the ranked list + drafts to the
   operator to send.

## Guardrails

- **Read-only except two sanctioned writes:** enriching/advancing Attio, and
  disabling a **confirmed-dead** task. Both are reversible; still **confirm before
  moving a lead to Lost or disabling a task**.
- **Draft, never send.** Every message touching a real customer is handed to the
  operator to send. No auto-send from this skill.
- **PII stays in the CRM.** Names, emails, account IDs live in Attio/Supabase —
  never paste them into shared docs or external services.
- **Exclude test rows** everywhere (`sweetmantech*`, `sidney@`, `@example.com`,
  `[TEST]`, `preview-auth-probe`).
- **Trust Stripe over the DB for paying status** — the Supabase `subscriptions`
  mirror can be empty/stale.
