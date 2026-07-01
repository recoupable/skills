---
name: recoup-internal-task-email-audit
description: >-
  INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke
  ONLY when the request explicitly includes "recoup-internal" (e.g.
  "recoup-internal audit last night's task emails"). Never use for customer-facing
  or artist requests.
  Audit the health of scheduled-task emails over a time window: what the
  customer-prompt-task runs actually delivered, how many empty/malformed sends the
  API guard blocked, per-account/per-recipient breakdown, and whether agents used
  the reliable helper vs hand-rolled curl. Use when asked "how did the tasks run
  last night", "what emails went out from tasks", "are we still sending empty
  emails", "task email health", "did the empty-email fix hold". Reads
  `email_send_log` (the send-attempt log) + `chats`/`chat_messages` via Supabase.
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

## Data sources (Supabase project `godremdqwajrwazhbrue`)

- **`email_send_log`** — the canonical source. One row per `/api/emails` attempt:
  `status` (`sent` | `send_failed` | `rejected`), `account_id`, `chat_id`,
  `resend_id`, `raw_body` (full request body), `created_at`. Exists only from
  **2026-06-30** (when api#731 shipped) — no data before that.
- **`chats` / `chat_messages` / `sessions`** — every run creates a chat; the
  agent's bash/tool activity (including how it sent) is in `chat_messages.parts`.
- **`scheduled_actions`** — the 549 scheduled-task **definitions** (title, prompt,
  schedule, account_id). Use for "which tasks exist / whose task is this".

> ⚠️ **Do NOT use `workflow_runs` or `scheduled_actions.last_run`/`next_run` for
> run history — they are stale** (not maintained by the current Trigger.dev
> scheduler; `workflow_runs` stopped updating 2026-05-27). Run activity lives in
> `chats`/`chat_messages`.

Query via the Supabase MCP (`execute_sql`) or any `psql`/`DATABASE_URL` connection
to the prod project. Prefer read-only `select`s.

## The audit (run these, newest-first)

Substitute the window in `interval '24 hours'`. Always **exclude test noise** —
sends to `sweetmantech@gmail.com` and `preview-auth-probe` bodies are staff test
runs, not customer traffic.

### 1. Headline — delivered vs. blocked, guard-block rate, forced retries

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

### 2. Delivered reports (the real emails that went out)

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

### 3. Blocked empties (what the guard caught — footer-only spam pre-fix)

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

### 4. Helper adoption (reliable send-email.mjs vs hand-rolled curl)

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
