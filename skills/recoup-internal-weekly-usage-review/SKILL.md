---
name: recoup-internal-weekly-usage-review
description: >-
  INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke
  ONLY when the request explicitly includes "recoup-internal" (e.g.
  "recoup-internal run the weekly usage review"). Never use for customer-facing
  or artist requests.
  Produce a fleet-wide, period-scoped business review of the Recoup platform:
  who logged in and visited the web UI, what changed in Stripe (signups, trials,
  billings, cancellations, paid roster), who consumed credits and on what,
  AI Gateway spend reconciled against the credits ledger, and which customers
  hold the most valuable catalogs. Use when asked for a "weekly usage review",
  "week in review", "what happened while I was gone", "who used the product
  this week", "business pulse", or a vacation catch-up. For a single account's
  deep dive use recoup-internal-account-health-report instead.
---

# Recoup Weekly Usage Review

Five independent data pulls plus one synthesis. Run the pulls in parallel
(subagents work well — each section is self-contained), then write the
week-in-review. First validated end-to-end 2026-07-20.

Define the window up front as UTC `[FROM, TO)` — normally the last 7 days —
and compute every section against the same window plus the prior 7 days for
comparison.

## Prerequisites

- `PRIVY_APP_ID` + `PRIVY_PROJECT_SECRET` — Privy Management API (Basic auth).
- Stripe: an authenticated Stripe CLI **or** a live restricted key. Caveat: the
  CLI stores its key in the macOS keychain, which sandboxed shells often cannot
  read — the CLI then falls back to an interactive `stripe login` pairing flow.
  Prefer passing the key explicitly (`stripe ... --api-key "$STRIPE_RESTRICTED_KEY"`).
- Supabase access to the production project (MCP `execute_sql` or psql),
  read-only.
- `AI_GATEWAY_API_KEY` (`vck_...`) — AI Gateway reporting.
- A **fresh** Vercel session token for Web Analytics: run `vercel login`, then
  read the token from `~/Library/Application Support/com.vercel.cli/auth.json`.
- The Vercel team id and the chat project name/id.

Never mutate anything: every call in this skill is a GET or a SELECT.

## 1. Logins & signups (Privy)

`node scripts/privy_logins.mjs --from 2026-07-13 --to 2026-07-20` (script ships
alongside this skill; needs only `PRIVY_APP_ID`/`PRIVY_PROJECT_SECRET` in the
environment). It paginates `GET https://api.privy.io/v1/users` and reports every
user whose max `latest_verified_at` across linked accounts falls in the window,
split into new signups vs returning.

Gotchas learned the hard way:

- `GET /api/admins/privy` on the Recoup API needs an **admin** token; a normal
  `recoup_sk_` API key authenticates but returns `isAdmin: false` → 403. The
  direct Privy route needs no Recoup admin and returns identical data.
- `latest_verified_at` moves only on a fresh auth verification. A returning
  user riding a long-lived session never bumps it, so this **undercounts**
  actives. Always cross-check with the interactive-chats SQL (query 5b in
  `references/sql.md`) — users with chats but no login event are session-riders.
- Sanity-check a quiet week by widening to 14 days; if the wider window shows
  returning users, the field is working and the quiet week is real.

**Signup-cohort scorecard:** grade every new signup in the window against the
activation funnel in `references/onboarding-checkpoints.md` (one column per
account, one row per checkpoint, using the internal checks). The story is
where the cohort stalls — historically nobody reaches step 7 (first scheduled
task), which is the step that predicts retention — and which warm leads
(measured-but-unclaimed valuations, enterprise domains) need human outreach.

## 2. Web UI traffic (Vercel Web Analytics)

There is no documented query API, but the dashboard's internal one accepts a
plain bearer token (the fresh CLI token) — the `v2` prefix is mandatory:

```
GET https://vercel.com/api/web-analytics/v2/{overview|timeseries|stats}
  ?environment=production&filter=%7B%7D&projectId=<project>&teamId=<team>
  &tz=UTC&from=<ISO>&to=<ISO>
  # stats also: &type={path|referrer|country|event_name}&limit=250
```

`devices` = unique visitors. Interpret paths before quoting the visitor count:
visitors whose only path is `/` bounced at the login screen (marketing
clickthrough), so report "reached the app" and "got past the homepage"
separately. If `type=event_name` is empty, no custom events are instrumented
and analytics cannot attribute identity — say so.

## 3. Stripe billing changes

Read-only pulls, live mode, window-scoped by `--created` / `created[gte]`:

1. Subscriptions created, canceled, or plan-changed in the window; trials
   started/converted (`stripe subscriptions list --limit 100`, inspect
   `created`, `canceled_at`, `trial_start`, `trial_end`).
2. Invoices and charges in the window; failed payments and disputes
   (`stripe events list --created ...` for `invoice.payment_failed`,
   `charge.dispute.created`).
3. The full current roster, split into **actually collecting** vs
   **`pause_collection` set** (`keep_as_draft` / `void` subs read as "active"
   but collect $0 — report their nominal MRR separately, with resume dates).
4. Expired Checkout Sessions with `metadata.purpose = credits_topup`. A pile of
   identical small sessions from one account is a programmatic loop, not
   abandoned carts — report per-account counts and the daily spike shape.

A restricted key may be denied on `/v1/account`, `/v1/prices`, `/v1/payouts`;
product names and `pause_collection` detail may need a full secret key.
Report which calls were denied rather than guessing.

## 4. Credits consumption (Supabase)

Run the SQL pack in `references/sql.md` (queries 1–10). Schema facts that make
or break it:

- The ledger is `usage_events`; `credits_deducted_cents` is the amount and
  **1 credit = 1 cent** (`UNIT_AMOUNT_CENTS_PER_CREDIT = 1` in
  `api/lib/stripe/createCreditsStripeSession.ts`).
- `credits_usage` is one balance-snapshot row per account (`remaining_credits`);
  its `timestamp` is last-update, often stale.
- Account email lives in `account_emails` (1-to-many — LATERAL LIMIT 1).
- Chats join accounts only via `sessions` (`chats.session_id → sessions.id →
  sessions.account_id`).
- Scheduled-task runs are the chats titled `'Scheduled generation'`; report the
  scheduled-vs-interactive split — it is the character of the business.
- `scheduled_actions.last_run` is **not written** by the Vercel Workflows
  runner; infer task activity from chats + `email_send_log` + usage events.

Always report: per-account burn with emails, what the top burners ran,
**accounts with negative balances that kept burning** (nothing stops them at
zero — a standing risk), prior-week actives that went silent (churn signal),
and the daily curve (Mondays spike from weekly crons).

## 5. AI Gateway spend vs credits (reconciliation)

Gateway side — the beta Custom Reporting API (account-scoped, uses
`AI_GATEWAY_API_KEY`; **billed ~$5 per 1,000 queries, so batch — a full weekly
pull needs ≤ 10 queries**):

```
GET https://ai-gateway.vercel.sh/v1/report   # group by day, model, apiKey, user
GET https://ai-gateway.vercel.sh/v1/credits  # current balance — flag if < ~3 days of runway
```

(The `api.vercel.com/v1/ai-gateway/*` paths do not exist.)

Reconcile: gateway `total_cost` for the window vs `SUM(credits_deducted_cents)`
(query 2), remembering that flat-fee charges (5¢ research, scrapes) are credits
without gateway cost — subtract them (query 3 splits by model attribution)
before naming the leakage number. Decompose any gap by API key first (a
non-app key = spend that bypasses billing entirely), then by day. Known leakage
mechanisms in the app code: `handleChatCredits` skips silently when `accountId`
is absent and swallows billing errors, and errored turns that produce no
`responseMessage` are never charged. If most gateway rows carry an empty `user`
tag, per-account attribution is impossible — recommend setting
`providerOptions.gateway.user = accountId` in the app.

## 6. Catalog value ranking

Recoup stores **no dollar values** — only Spotify lifetime play counts in
`song_measurements`; the /valuation tool computes dollars client-side. Rank
with queries 11–14 in `references/sql.md`, then convert streams to a central
value with the marketing formula (canonical implementation:
`marketing/lib/valuation/computeCatalogValuation.ts` in the monorepo —
re-derive from there if precision matters):

```
annual_streams ≈ lifetime_streams / catalog_age_years   (age from earliest release)
central_value ≈ annual_streams × $0.0035 × 1.4 × 0.6375 × 13
```

Report the top catalogs with owner emails and paying status, valuations run in
the window, and measured-but-unclaimed runs (warm leads). Caveats to carry:
exclude internal/test rows (sweetmantech*, sidney@, `[TEST]`); a catalog with
no earliest-release link falls back to a default age and over-values; the
Supabase `subscriptions` mirror may be empty — verify paying status against
Stripe, not the DB.

## 7. Synthesis

Write the week-in-review in this shape, leading with the single most
consequential finding (not necessarily revenue):

1. **One-paragraph TLDR** — what changed, what's at risk, the one urgent item.
2. **Dimension table** — logins/visitors, paid roster delta, credit burn +
   scheduled/interactive split, gateway spend vs credits recorded, top
   catalogs/leads, broken plumbing found along the way.
3. **Prioritized actions** — stop-the-bleeding today, revenue this week,
   product/integrity next. Name owners where obvious.

Cross-reference the pulls against each other before publishing: signups with no
chats = bounced onboarding; credit-active accounts with no login = scheduled
autopilot; gateway spend with no credits = billing leakage; a valuation run
with no claim = an unworked lead.
