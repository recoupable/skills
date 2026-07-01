---
name: recoup-internal-task-email-audit
description: >-
  INTERNAL — Recoup staff tooling. Never use for customer-facing or artist requests.
  Audit the health of scheduled-task emails over a time window: what the
  customer-prompt-task runs actually delivered, how many empty/malformed sends the
  API guard blocked, per-account/per-recipient breakdown, and whether agents used
  the reliable helper vs hand-rolled curl. Use when asked "how did the tasks run
  last night", "what emails went out from tasks", "are we still sending empty
  emails", "task email health", "did the empty-email fix hold". Produces a
  per-run table (one row per Trigger.dev `customer-prompt-task` run: run_id,
  recipient, prompt, email subject, body kb) plus a headline. Reads the Trigger.dev
  run list + `email_send_log` and `chats`/`chat_messages` (Supabase).
---

# Task-email health audit

How Recoup staff check whether scheduled **task emails** are healthy — real
reports delivered, no empty "Message from Recoup" footer-only sends — over any
window. This is the standing audit for the pipeline fixed in
[recoupable/chat#1829](https://github.com/recoupable/chat/issues/1829) (empty-email
bug, resolved 2026-07-01).

## When to use

- "recoup-internal — how did last night's tasks go? What emails went out?"
- "Are we still shipping empty footer-only emails?"
- "Task email health for the last 24h / this week."
- "Did the #729 guard actually block empties in production?"

## Background (what you're measuring)

Scheduled tasks (`customer-prompt-task`, Trigger.dev) each run the
`runAgentWorkflow` agent, which sends its report by calling `POST /api/emails`
from inside the sandbox. Before the 2026-07-01 fix, a malformed/empty body was
silently delivered as a footer-only **"Message from Recoup"** email with
`success:true`. The fix: `POST /api/emails` now **rejects** empty/unparseable
bodies (400) and **logs every attempt** to `email_send_log` (sent / send_failed /
rejected) with the full raw body. That log is the audit's source of truth.

## Data sources

### A. Task runs — Trigger.dev Management REST API (the run list + `run_id`)

Every scheduled task run is a Trigger.dev run of the **`customer-prompt-task`**
task ([`lib/trigger/createSchedule.ts`](https://github.com/recoupable/api/blob/main/lib/trigger/createSchedule.ts)).
Enumerate them via the Management API. **Requires the prod `TRIGGER_SECRET_KEY`**
— a `tr_dev_*` key returns 0 prod runs.

- **List runs** (mirrors [`lib/trigger/fetchTriggerRuns.ts`](https://github.com/recoupable/api/blob/main/lib/trigger/fetchTriggerRuns.ts)):
  ```bash
  curl -s "https://api.trigger.dev/api/v1/runs?page%5Bsize%5D=100" \
    -H "Authorization: Bearer $TRIGGER_SECRET_KEY"
  ```
  Page via `page[after]=<cursor>`. Each run has `id` (**the `run_id`**), `status`,
  `createdAt`/`finishedAt`, `costInCents`, and `tags` (including
  **`account:<accountId>`**). Filter client-side to
  `taskIdentifier == "customer-prompt-task"` and `createdAt` in the window.
  - One account: add `&filter[tag]=account:<accountId>` (this is what
    `GET /api/tasks/runs` uses). **Omit the tag for the whole fleet** (all accounts).
- **Run detail / prompt** (mirrors [`lib/trigger/retrieveTaskRun.ts`](https://github.com/recoupable/api/blob/main/lib/trigger/retrieveTaskRun.ts)):
  `runs.retrieve(runId)` via `@trigger.dev/sdk` → `payload` carries the task
  **prompt** + account/artist ids. (Or resolve the prompt from `scheduled_actions`
  for that account — cheaper, no per-run round-trip.)

### B. Emails + agent activity — Supabase (project `godremdqwajrwazhbrue`)

- **`email_send_log`** — the send-attempt log. One row per `/api/emails` attempt:
  `status` (`sent` | `send_failed` | `rejected`), `account_id`, `chat_id`,
  `resend_id`, `raw_body` (full request body), `created_at`. Exists only from
  **2026-06-30** (when api#731 shipped).
- **`chats` / `chat_messages` / `sessions`** — every run creates a chat; the
  agent's bash/tool activity (how it sent) is in `chat_messages.parts`.
- **`scheduled_actions`** — the scheduled-task **definitions** (title, prompt,
  account_id). Resolve a run's prompt/title without a `runs.retrieve` call.

> ⚠️ **Do NOT use `workflow_runs` or `scheduled_actions.last_run`/`next_run`** —
> stale (not maintained by the current scheduler; `workflow_runs` stopped
> updating 2026-05-27). Run history is Trigger.dev; activity is `chats`/`chat_messages`.

Query Supabase via the MCP (`execute_sql`) or `psql`/`DATABASE_URL`. Read-only.

## The audit (run these, newest-first)

Substitute the window in `interval '24 hours'`. Always **exclude test noise** —
sends to `sweetmantech@gmail.com` and `preview-auth-probe` bodies are staff test
runs, not customer traffic.

### 1. Headline — tasks run, delivered vs. blocked, guard-block rate, forced retries

**`tasks_run`** = the number of `customer-prompt-task` runs in the window — count
them from the Trigger.dev run list (§ A). The remaining columns come from
`email_send_log`:

```sql
with w as (
  select status,
    substring(raw_body from '"to"\s*:\s*\[\s*"([^"]+)"') as rcpt,
    created_at
  from public.email_send_log
  where created_at > now() - interval '24 hours'
    and raw_body not like '%sweetmantech@gmail.com%'
    and raw_body not like '%preview-auth-probe%'
)
select
  count(*) filter (where status='sent')                                   as delivered,
  count(*) filter (where status='rejected')                               as blocked_empty,
  round(100.0*count(*) filter (where status='rejected')/nullif(count(*),0),0) as pct_blocked,
  count(distinct rcpt) filter (where status='sent')                       as recipients_served,
  count(*) filter (where status='rejected'
    and rcpt in (select rcpt from w where status='sent'))                 as blocked_then_delivered;
```

### 2. Per-run table — one row per Trigger.dev run (**the main deliverable**)

Columns: **`run_id`** · **`recipient`** · **`prompt`** (truncated) · **`subject`** ·
**`body (kb)`**. Built by joining the Trigger.dev run list (§ A) to `email_send_log`:

1. **run_id + account + `finishedAt`** — from the Trigger.dev run list (§ A),
   filtered to `taskIdentifier == customer-prompt-task` in the window. The account
   is the run's `account:<id>` tag.
2. **recipient** — the account's own email:
   ```sql
   select account_id, email from public.account_emails where account_id = any($1);
   -- $1 = the run accounts from step 1
   ```
3. **prompt** — `runs.retrieve(run_id).payload.prompt` (or `scheduled_actions.prompt`
   for that account); truncate to ~80 chars.
4. **subject + body(kb)** — the `email_send_log` row for that account nearest the
   run's `finishedAt`:
   ```sql
   select account_id, status,
     substring(raw_body from '"subject"\s*:\s*"([^"]{0,80})') as subject,
     round(length(raw_body)/1024.0, 1) as body_kb, created_at
   from public.email_send_log
   where account_id = any($1) and created_at > now() - interval '24 hours'
   order by created_at;
   ```
   Match each run to the `sent` row with the same `account_id` and the closest
   `created_at ≥ finishedAt`. A run with **no** matching `sent` row delivered
   nothing — surface it (often it has a `rejected` row instead; that's a blocked empty).

Render:

| run_id | recipient | prompt | subject | body (kb) |
|--------|-----------|--------|---------|-----------|
| `run_abc…` | seb.simone@wmg.com | "Daily social trends for PinkPanth…" | Daily Social Trends: PinkPantheress – July 1 | 15.2 |
| `run_def…` | Laszlo.Bihary@gmail.com | "Leonardo daily social trends…" | — (blocked, no send) | — |

> **Join caveat.** `email_send_log.chat_id` is null (agents don't pass it), so the
> run→email link is **account + timing**, not an exact key — reliable when an
> account fires one task per window, ambiguous when several fire together. Threading
> a real `chat_id` into `/api/emails` (the footer-404 follow-up) makes `run_id → email` exact.

### 3. Delivered reports (the real emails that went out)

```sql
select
  substring(raw_body from '"subject"\s*:\s*"([^"]{0,70})') as subject,
  substring(raw_body from '"to"\s*:\s*\[\s*"([^"]+)"')     as recipient,
  account_id, to_char(created_at,'MM-DD HH24:MI') as at
from public.email_send_log
where status='sent' and created_at > now() - interval '24 hours'
  and raw_body not like '%sweetmantech@gmail.com%'
order by created_at desc;
```

### 4. Blocked empties (what the guard caught — footer-only spam pre-fix)

```sql
select
  substring(raw_body from '"subject"\s*:\s*"([^"]{0,70})') as subject,
  substring(raw_body from '"to"\s*:\s*\[\s*"([^"]+)"')     as recipient,
  length(raw_body) as body_len, to_char(created_at,'MM-DD HH24:MI') as at
from public.email_send_log
where status='rejected' and created_at > now() - interval '24 hours'
  and raw_body not like '%sweetmantech@gmail.com%' and raw_body not like '%preview-auth-probe%'
order by created_at desc;
```

### 5. Helper adoption (reliable send-email.mjs vs hand-rolled curl)

For a set of task chats in the window (get `chat_id`s from `chats` created in the
window, or from a fired-run log), check how the agent sent:

```sql
select
  count(*) filter (where parts::text like '%send-email.mjs%') as used_helper,
  count(*) filter (where parts::text like '%/api/emails%' and parts::text not like '%send-email.mjs%') as raw_curl
from public.chat_messages
where chat_id = any($1) ;   -- $1 = array of the window's task chat_ids
```

## How to read it

- **`delivered`** = real reports that reached customers. Spot-check subjects in
  query 2 — they should carry a real title + the correct date (a wrong year, e.g.
  "2024", is a stale/hallucinated-date content bug worth flagging).
- **`blocked_empty`** = empty/malformed sends the **#729 guard** stopped. **Every
  one of these would have been a footer-only "Message from Recoup" email delivered
  to a real customer before 2026-07-01.** This is the guard working, not a failure.
- **`blocked_then_delivered`** = the agent's first attempt was empty (blocked),
  then it retried into a real send to the same recipient — the guard's 400
  *forced a correction*.
- **`pct_blocked`** = the underlying empty-generation rate. It stays high (agents
  still frequently build empty bodies); the guard makes it harmless. A high number
  is the case for driving **helper adoption** (query 4) — the primary
  `recoup-platform-api-access` skill still teaches raw `curl`, so agents rarely
  pick the reliable `recoup-platform-email-helper`.

**Reference point (2026-07-01 overnight batch):** 6 delivered, 10 blocked
(63% pct_blocked), 3 blocked-then-delivered — real customers (WMG, OneRPM, gmail)
got real reports; the 10 empties that would have been spam were blocked.

## Caveats

- **`email_send_log.chat_id` is null on nearly all sends** — agents don't pass it.
  So you can't join sends to a specific run/task by `chat_id`; attribute by
  **recipient** and **account_id** (on `sent` rows) instead. This null also means
  task emails currently render **no footer "continue on Recoup" link** — a known
  follow-up.
- **`account_id` is null on `rejected` rows** — the guard runs *before* auth, so a
  400 has no resolved account. Attribute blocked empties by recipient/subject.
- Always exclude staff test traffic (`sweetmantech@gmail.com`, `preview-auth-probe`).
- No `email_send_log` data before **2026-06-30** — for older windows the log is
  empty and you must fall back to Resend + `chat_messages` scraping (the pre-fix
  method).

## Reference

- Tracking issue: [recoupable/chat#1829](https://github.com/recoupable/chat/issues/1829)
  (resolved 2026-07-01). Baseline (pre-fix): 38% of delivered emails were empty
  footer-only; 30% of runs sent nothing.
- Fix PRs: api#729 (guard), api#731 (`email_send_log` observability),
  skills#67 (`recoup-platform-email-helper`), api#730 (register helper).
