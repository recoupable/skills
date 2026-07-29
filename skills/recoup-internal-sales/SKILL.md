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

- `RECOUP_API_KEY` / `RECOUP_ACCESS_TOKEN` — **the primary source.** A `recoup_sk_`
  key, or an admin Privy JWT for cross-account work (see Source order). Load
  `recoup-platform-api-access` for the endpoint map.
- `ATTIO_API_KEY` — read + write (this sweep *writes* follow-ups back).
- Supabase read access to production (MCP `execute_sql` or psql) — **augmentation
  only**, for the fleet-wide aggregates the API has no endpoint for.
- Stripe: authenticated CLI **or** a live restricted key (pass `--api-key` — the
  keychain is often unreadable in sandboxed shells).
- `PRIVY_APP_ID` + `PRIVY_PROJECT_SECRET` — Privy Management API.

Everything is a GET or SELECT **except** the two sanctioned writes named in
Guardrails (Attio follow-ups; disabling a confirmed-dead task). Outreach is
**always drafted for a human to send**, never sent from this skill.

## Source order — dogfood the API first

**1. Recoup API → 2. Supabase.** Reach for `api.recoupable.dev` first and drop to
SQL only for what it cannot answer. This is not a style preference: the sweep is
run by the people who own the product, and every pull is a free QA pass. The
2026-07-26 run found two product bugs purely by looking at API responses that no
SQL query would have surfaced.

**Use the API for anything scoped to one account, artist, or task:**

| Need | Call | Why not SQL |
| --- | --- | --- |
| A customer's tasks | `GET /api/tasks?account_id=` | Returns `owner_email`, `model`, `next_run`, `upcoming`, `recent_runs`, `trigger_schedule_id` — **none of which exist as columns** on `scheduled_actions`. A schedule that will never fire is only visible here. |
| An artist's socials | `GET /api/artists?account_id=` | Socials are **embedded** as `account_socials`; the hand-rolled `accounts → account_socials → socials` join is where mistakes happen. |
| Remove an artist | `DELETE /api/artists/{id}` | Encodes the last-owner check and the fail-closed song-dependency guard. Raw SQL skips both. |
| Email → account | `POST /api/accounts` | One call vs. a `account_emails` lookup. |
| Refresh a profile | `POST /api/socials/{id}/scrape` | Real scrape; SQL only shows you stale rows. |

**Admin cross-account access.** An admin Privy JWT plus an `account_id` override
lets you read/write in a customer's context without their key — `account_id` as a
**query param** on GETs, in the **JSON body** on `PATCH`/`DELETE`. Authorized by
`validateAuthContext` / `checkIsAdmin`. Confirm with `GET /api/admins` →
`{"isAdmin":true}`. These JWTs expire in **~1 hour** — re-request rather than
debugging a sudden 401.

**Drop to SQL only for the fleet-wide sweep** — the cross-account aggregates that
have no endpoint: per-account credit burn, negative balances, went-silent accounts,
zombie tasks, valuation runs in a window, chat-title themes. That is most of the
seven pulls, and SQL is genuinely the right tool there. The rule is about
*account-scoped* reads, not about banning SQL.

**When the two disagree, the API is the customer's truth** — it is what the product
actually serves them. A DB row the API doesn't surface is not something the customer
can see.

## The seven pulls

Each pull is: **what to read → the sales signal → the action**. Always drop test
rows (`sweetmantech*`, `sidney@`, `@example.com`, `[TEST]`, `preview-auth-probe`).

These seven are the *fleet-wide* layer, so most of them are legitimately SQL (or
Stripe/Privy/Attio). The API-first rule bites at the **next** step: the moment the
ranked list names a person, every drill-down on that account — their tasks, artists,
socials, scrape freshness — goes through `api.recoupable.dev`, not another SELECT.
Ranking is a SQL job; qualifying a named lead is an API job.

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
- ⚠️ **Burn reads wrong in BOTH directions.** High burn is not engagement — a daily
  scheduled task produces usage events and looks like an active account. And **near-zero
  burn is not disengagement**: it is just as often an account we never funded. Confirm
  against step 7 before calling anyone active *or* dead.
- **Read the balance and the plan together** (see *Credits mechanics* below). An account
  that has been at the same balance for months is not frugal, it is unrefilled.
- **Action:** log the follow-up; for a billing-risk account, pair the outreach with
  the plan-fit conversation from step 1.

#### Credits mechanics — read this before you quote anyone's balance

`checkAndResetCredits` refills a stale row to the plan total (`DEFAULT_CREDITS` 333 /
`PRO_CREDITS` 9999). Three things follow, and all three have bitten:

1. **Refill is lazy, and reading a balance MUTATES it.** It is reachable from exactly one
   place — the `GET /api/accounts/{id}/credits` handler. The spend path never calls it
   (`autoRechargeOrFail` reads `remaining_credits` directly and mints a Checkout session on
   a shortfall). So an account nobody opens never refills, and *your* GET is what finally
   tops it up. That is the sanctioned one-call comp for a stale account.
2. **It SETS, it does not add** — and only fires when the row is **> 1 month old**. On a
   free-tier account sitting above 333 the same read silently **reduces** the balance.
   Check `timestamp` and `is_pro` *before* you call it on anyone.
3. **There is no staff-facing way to grant credits.** Every route under
   `/api/admins/credits` is a GET; only the Stripe webhook and auto-recharge increment. If
   the row is too fresh to refill, the only options are a deliberate raw DB write (breaks
   the SQL guardrail — get sign-off and log it) or putting them on a plan.

**`isPro` is derived from Stripe by account id**, so a customer whose Stripe record is
missing `metadata.accountId` resolves to **free tier while paying** — seen live on a
$5,000/mo account sitting on 333 credits. Check that linkage before diagnosing anything
credit-related.

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

- **Read:** chats created in the window with titles (weekly-usage-review SQL queries
  5a/5b). Titles are admin-readable; **bodies are owner-scoped** (see account-health
  caveat).
- ⚠️ **Do not split on the `'Scheduled generation'` topic — it no longer identifies
  autopilot.** Scheduled rooms now commonly carry a **NULL topic**, and titled rooms
  include cron output (a real one: `"Weekly Performance Dashboard 2026-07-20 to
  2026-07-26"`). Two tests that do work:
  - **Clock alignment.** A cron fires at the same minute every day; a human is off-clock.
    Group an account's rooms by `extract(minute from updated_at)` — one dominant minute is
    the schedule, everything else is a person.
  - **User messages per room** (the sharper one). A scheduled run writes **exactly one
    user-role message per room**, at the cron minute. A human session is multi-turn and
    off-clock. `count(user_msgs) == count(rooms)` for a month means nobody typed anything
    that month.
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
   operator to send. Before drafting for any selected contact, build their
   four-source dossier (next section).

## The contact dossier — before any outreach is drafted

The moment the operator selects a specific contact (from the ranked list or on
their own), research that person into one concise four-row table and present it
alongside the draft. It is the pre-flight that catches "already paying",
"payment-blocked, not disinterested", "this IS the artist", and "we emailed
them yesterday". Build it fresh even if a sweep pull already touched the
account — the fleet aggregates hide the per-person timeline.

| Source | What goes in the row | The lookup that works |
| --- | --- | --- |
| **Privy** | first + last login events | `POST https://auth.privy.io/api/v1/users/email/address` with `{"address": "<email>"}` (basic auth `PRIVY_APP_ID:PRIVY_PROJECT_SECRET` + `privy-app-id` header) → `created_at` and each linked account's `first_verified_at` / `latest_verified_at`. One call — no need to re-run the pagination script for one person. |
| **Stripe** | customer / card / subscription status | Find the customer by `metadata.accountId` (email search misses — see Tooling gotchas), then `GET /v1/customers/{id}/payment_methods` and `GET /v1/subscriptions?customer=…&status=all`. A customer with 0 payment methods and 0 subscriptions = they reached checkout and never paid — blocked, not disinterested. |
| **Supabase** | credits_usage, sessions, chats | All by `account_id` — except `chats`, which has **no `account_id` column**: join `sessions.account_id → chats.session_id`, then count `chat_messages` rows with `role='user'` per chat. Report typed chats separately from empty `"New chat"` rows — an untyped open is still a signal (they visited and bounced). Balance via SQL only, never the credits GET (see Credits mechanics). |
| **Resend** | outbound emails we've sent them | `email_send_log` by `account_id` (there are no `to_email`/`subject` columns; the subject is inside `raw_body`) → cross-ref each `resend_id` against the Resend API for subject + delivery status. Zero rows = we have never emailed this person from the product. |

Read the table before writing a word of outreach: the first/last-login pair
sets the "returning vs. new" frame, the Stripe row sets the ask (rescue vs.
upgrade vs. retention), the chats row tells you what they actually tried to do
in their own words (titles are admin-readable), and the Resend row is what
"we" have already said to them.

Then extend the dossier with four product-side tables — what the contact has
actually *done* with Recoup, in their own timeline:

| Table | What goes in it | The lookup that works |
| --- | --- | --- |
| **Lifetime activity** | Key dated events from signup to now, weighted to recent: first login, each typed chat (title verbatim), tasks created, valuation runs, checkout attempts, emails delivered or missed, last event. | Merge the four source rows chronologically. A 10–15 row timeline reads faster than any aggregate and is where the story ("built the report Thursday, hit the paywall Monday") becomes visible. |
| **Tasks** | Every task: title, artist, cadence, model, enabled, last run + status, next runs, does it email — and does the sent email match the intention the customer typed when they created it? | `GET /api/tasks?account_id=` only (model / `upcoming` / `recent_runs` / `owner_email` don't exist on `scheduled_actions`). For intention-vs-output: compare the `email_send_log.raw_body` headline against the chat/task title that spawned it. A run that says COMPLETED with **no matching `email_send_log` row** delivered nothing — the customer thinks the task ran; it silently didn't reach them. |
| **Artists** | Roster: each artist + every connected social (platform, handle/URL, followers, scrape freshness). | `GET /api/artists?account_id=` — socials embedded as `account_socials`; the social's `updated_at` is the scrape date. A one-platform roster (e.g. Spotify only) is itself an outreach hook: nothing else is connected. |
| **Valuation / catalog** | Run count + dates, claimed vs unclaimed, the value on file, what's in the catalog (songs / albums / total streams), and the crown jewels (top songs by plays). | `playcount_snapshots` by `account` (the column is `account`, not `account_id`) → `song_measurements.snapshot = ps.id`, join `songs ON songs.isrc = song_measurements.song`; `value` is the play count. The dollar value is **not** in the DB (never persisted) — read it off the Attio auto-note or the valuation email. Repeat runs of the same catalog in one sitting = they're trying to answer a question; find out which one. |

## Guardrails

- **Read-only except two sanctioned writes:** enriching/advancing Attio, and
  disabling a **confirmed-dead** task. Both are reversible; still **confirm before
  moving a lead to Lost or disabling a task**.
- **Never mutate customer data with raw SQL — go through the API.** An `UPDATE` on
  `scheduled_actions` writes the row but skips everything the endpoint does around
  it: `updateTask` re-syncs the Trigger.dev schedule, and `deleteArtist` runs a
  last-owner check plus a fail-closed song-dependency guard before hard-deleting.
  A direct write leaves the row and the scheduler disagreeing, and the drift is
  invisible in the table you just edited. Use `PATCH`/`DELETE` with an `account_id`
  override. This applies to *every* customer-facing table, not just tasks.
- **Draft, never send.** Every message touching a real customer is handed to the
  operator to send. No auto-send from this skill.
- **PII stays in the CRM.** Names, emails, account IDs live in Attio/Supabase —
  never paste them into shared docs or external services.
- **Exclude test rows** everywhere (`sweetmantech*`, `sidney@`, `@example.com`,
  `[TEST]`, `preview-auth-probe`).
- **Trust Stripe over the DB for paying status** — the Supabase `subscriptions`
  mirror can be empty/stale.

## Lessons from the first live run (2026-07-23)

Four leads worked end to end: an inbound valuation lead, a distributor/broker, a
major-label exec, and a dormant power user. What actually mattered.

### Qualification

- **Credit burn is not engagement.** Two accounts looked "active today" and were
  pure autopilot — the usage was a scheduled task firing. One had been dark **4 months**
  while its daily task quietly burned the balance negative. Check the last *interactive*
  chat date, always (step 7 has the two tests that survive a NULL topic).
- **And a quiet account is not a disengaged one.** A subscriber of **19 months** read as
  dormant — 1 active day, 0 chats — because he had **456 credits against a 9,999
  entitlement** the whole time and nobody had ever read his balance to trigger the refill.
  He had paid $405.46 for roughly 2% of one month's allowance. Fleet-wide, **1,499 of
  1,646** accounts were carrying an unapplied refill and **133 were blocked at or below
  zero**. Before writing anyone off, check whether we ever funded them.
- **Qualify the catalog before spending human time.** A lead who ran a valuation
  and asked "what can I sell for" held a 10-track **public-domain classical**
  catalog worth ~$700 — no publishing to sell, since Bach and Chopin are public
  domain. Capture works fine; qualification is the gap. Check repertoire type and
  streams before drafting anything.

### Valuation you can put in front of a buyer

- **Say "asset value, not a bid."** A catalog buyer asked "is this for the buy?"
  The number models a 10-16x multiple on sustainable annual net label share. It is
  not an offer price and must never anchor an LOI.
- **It mis-prices older catalogs in BOTH directions.** Against four independent
  market comps (independent catalog buyers and distributors) it was accurate on a 2-year
  catalog, **undervalued an 8-year/90-release catalog ~2x**, and **overvalued**
  8-10 year catalogs. Cause: annual run rate is estimated as *lifetime streams ÷
  catalog age*, which averages an old catalog flat — understating one weighted to
  recent output, overstating a decaying one. The market prices trailing-12-month
  performance. **Older than ~3 years: get statements before quoting.**
- **It is Spotify only.** One artist's self-reported ~700k/month **Amazon** track
  was worth roughly 10-20x his entire Spotify catalog *per year* at Amazon's public
  ~$0.00402/stream rate. Ask about other DSPs before calling a catalog small.
- **Pull real release dates.** Catalog age is floored at 1 year and falls back to 5
  when unknown, so identical streams can value ~5x apart.

### Delivering

- The sequence that converted: verify the roster → measure → render the PDF →
  deliver by email **and** the channel they replied on → advise honestly on the
  number → ask for statements. Being the one who says *"you may be overpaying"* is
  what turned a valuation into a partnership conversation.
- Keep outreach short and lead with the concrete thing you did for them. Attach a
  report only when their job makes it relevant — a label exec has no use for a
  catalog valuation of an artist their employer already owns.

### Keeping a lead warm — do all three

Set `owner`, log a note saying what you sent and what you're waiting for, and
create a **dated follow-up task**. A Qualified enterprise lead had sat **21 days**
untouched because none of the three existed.

### Tooling gotchas

- Privy / Spotify / Apify credentials come from the **`api`** submodule
  (`vercel env pull`); `chat` is not Vercel-linked.
- **Stripe lookup by login email mostly misses, and the roster alone is not enough.**
  Pull the active-subscription roster — but **`expand[]=data.customer`** or Stripe returns
  customer *ids*, not emails, and a paying customer reads as unpaid. That cost a real
  misdiagnosis: a $20/mo subscriber of 19 months was reported as a cold lead. The reliable
  join is **`customer.metadata.accountId`**, not the email; a customer's Stripe address is
  routinely different from their Recoup login (`derekgtaylor@me.com` vs `hello@dddvvv.xyz`).
- **`usage_events.source` is NOT an auth discriminator.** `source='api'` covers ~28k events
  across 164 accounts — effectively all traffic since `source='web'` stopped being written
  on 2026-06-05. It is a transport label. It tells you nothing about whether a call came
  from a customer's API key, our task runner, or the app, so never infer "they built an
  integration" from it. To rule the task runner in or out, check `scheduled_actions` and
  whether a room was created per run.
- **`account_api_keys.last_used` is never written** (production code never sets it; it
  appears only in test fixtures). There is no way to tell when a customer last used an API
  key. Same dead-column class as `scheduled_actions.last_run` / `next_run`.
- **Privy `latest_verified_at` undercounts actives** (long sessions never re-verify);
  cross-check with interactive chats. It is trustworthy at *long* range though — a
  320-day-old value plus zero off-clock user messages is a safe "they have been gone a year".
- **Attio:** the people query caps at **500** (page it), `stage.active_from` gives
  days-in-stage for non-responder detection, location writes require *every*
  sub-field, task `content` is immutable (close and recreate), and creating an
  attribute needs a `config` key.
  - **Enrichment fields are guesses, not facts.** On auto-captured records the
    `name`, `description`, and `linkedin` values are often Attio *system enrichment*
    (data-broker match on the email, `created_by_actor.type = "system"`, stamped seconds
    after creation) — seen internally inconsistent on a real lead (name "Benita" with a
    LinkedIn slug `ben-hanchett` and an unrelated bio). Check provenance before using a
    name in outreach; prefer an identity the person chose (artist name, chat sign-off).
  - **Judge prior contact by `last_interaction` / `first_interaction`, never by note
    count.** A record with zero notes can still have years of email history; email sync
    populates the interaction fields, not notes. Calling such a lead "never contacted" in
    front of the rep who emailed them is the fastest way to lose the room.
  - **`owner` lives on the list entry, not the person** — a contact on no list has nowhere
    to hang accountability. Add the entry first, then set `owner`.
  - **No binary file upload.** `/v2/files` accepts only `folder | connected-folder |
    connected-file` (pointers to externally hosted files). A valuation PDF has to be
    dragged onto the record by hand, or the file hosted elsewhere first — which the PII
    guardrail means you ask before doing.
- **`socials.profile_url` is lowercased by a DB trigger** — never store a YouTube
  `/channel/UC…` URL (case-sensitive id, silently corrupted). Resolve and store the
  `@handle` form instead.
