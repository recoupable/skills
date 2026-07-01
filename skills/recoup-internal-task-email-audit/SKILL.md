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
  recipient, prompt, email subject, body kb) plus a headline, a per-run **tool-call
  trace**, and a **`has_hallucinated_data`** / `expected_data_source` content check.
  Reads the Trigger.dev run list + `email_send_log` and `chats`/`chat_messages` (Supabase).
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
- "Is the data in this task email real, or hallucinated? Why did it fabricate?" (→ §§ 6–7)
- "Show me the exact tool calls a task run made." (→ § 6)

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
task ([`lib/trigger/createSchedule.ts`](https://github.com/recoupable/api/blob/main/lib/trigger/createSchedule.ts)),
tagged **`account:<accountId>`**. Enumerate them with the bundled script — it pages
the Management API, filters to `customer-prompt-task` in the window, and prints the
account array for the correlation SQL:

```bash
node scripts/fetch_task_runs.mjs --hours 24 > runs.json   # add --account <uuid> for one account
```

**Requires the PROD `TRIGGER_SECRET_KEY`** — a `tr_dev_*` key returns **0** prod
runs (the #1 gotcha; the script warns you). Pull it without clobbering your `.env`,
from the `recoupable/api` repo (linked to `recoup/api`):

```bash
vercel env pull /tmp/prod.env --environment=production --yes
export TRIGGER_SECRET_KEY=$(grep '^TRIGGER_SECRET_KEY=' /tmp/prod.env | cut -d= -f2- | tr -d '"')
# … run the script …
rm /tmp/prod.env                                          # scrub the secrets when done
```

`runs.json` rows are `{ run_id, account, status, createdAt, finishedAt }`. For the
exact per-run **prompt**, `runs.retrieve(runId)` (`@trigger.dev/sdk`) has
`payload.prompt`; but `scheduled_actions.prompt` per account (in the SQL below) is
cheaper and usually sufficient.

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

> **`tasks_run` ≠ email tasks — segment the noise.** Many `customer-prompt-task`
> runs are **not** email tasks: profile-sync/maintenance (one account fired **33
> runs in 24h**), health-checks, and misconfigured prompts (literally `"22"`, or
> `"New task — replace with your instructions."`). Report **`tasks_run`** (all runs)
> **and `email_tasks`** (prompt mentions email/send *and* the account resolves a
> recipient) separately, and list the non-email / high-frequency / misconfigured
> ones as a short "ops noise" callout — otherwise the delivery rate is judged
> against a polluted denominator (the first real run read "6 of 90", but ~33 of
> those 90 were one maintenance task).

### 2. Per-run table — one row per Trigger.dev run (**the main deliverable**)

Columns: **`run_id`** · **`recipient`** · **`prompt`** (truncated) · **`subject`** ·
**`body (kb)`**. Paste the `array[...]::uuid[]` that the script printed into this
**one** correlation query (returns recipient + prompt + delivered subject/body per
account — this exact query is validated, mind the inline gotchas):

```sql
with racct as (
  select unnest( /* paste the account array from fetch_task_runs.mjs here */ ) as account_id
)
select substr(ra.account_id::text, 1, 8)                          as acct,
       ae.email                                                   as recipient,
       left(sa.prompt, 60)                                        as prompt,
       es.subject,
       es.body_kb
from racct ra
-- account_emails has NO created_at → limit 1, no order
left join lateral (select email from public.account_emails
                   where account_id = ra.account_id limit 1) ae on true
left join lateral (select prompt from public.scheduled_actions
                   where account_id = ra.account_id order by updated_at desc limit 1) sa on true
-- the delivered email: newest 'sent' row for the account in the window
left join lateral (
  select substring(raw_body from '"subject"\s*:\s*"([^"]{0,60})') as subject,
         round(length(raw_body) / 1024.0, 1)                      as body_kb
  from public.email_send_log
  where account_id = ra.account_id and status = 'sent'
    and created_at > now() - interval '24 hours'
  order by created_at desc limit 1
) es on true
order by (es.subject is not null) desc, ra.account_id;   -- delivered first
```

Then **join `runs.json` to this result by `account`** to fill `run_id`. Notes:
- `subject is null` ⇒ the account delivered **no** email in the window (ran but
  didn't send, or its send was a blocked empty — `rejected` rows carry a **null
  `account_id`**, so they don't show here; count them via § 4).
- An account with **>1 run** in the window (a task firing hourly) maps to one
  account row here — attribute the delivered email to the run whose `finishedAt` is
  nearest the send.

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

### 6. Per-run tool-call trace — *why* an email is empty / rich / hallucinated

To debug a single run (what it actually fetched, whether it fabricated), pull its
tool calls from `chat_messages`.

**First, find the run's chat.** `email_send_log.chat_id` is null, so locate the chat
by recipient (or a subject marker):

```sql
select chat_id, min(created_at) started
from public.chat_messages
where created_at > now() - interval '24 hours'
  and parts::text like '%recipient@domain.com%'
group by chat_id order by started desc;
```

**Then extract the tool calls.** ⚠️ `chat_messages.parts` is an **object**
`{id, role, parts:[…]}`, *not* a bare array — unnest `parts::jsonb->'parts'`. A run
is usually **one** assistant message holding every part:

```sql
select row_number() over (order by ord) as n,
  p->>'type' as tool,
  left(coalesce(p->'input'->>'command', p->'input'->>'skill', p->'input'->>'url',
                p->>'text', (p->'input')::text), 200) as input_or_text,
  left(coalesce(p->'output'->>'stdout', p->'output'->>'content',
                (p->'output')::text, p->>'state'), 200) as result
from public.chat_messages cm,
  lateral jsonb_array_elements(
    case when jsonb_typeof(cm.parts::jsonb)='array' then cm.parts::jsonb
         else cm.parts::jsonb->'parts' end
  ) with ordinality as t(p, ord)
where cm.chat_id = '<chat_id>'
  and p->>'type' in ('text','tool-bash','tool-skill','tool-web_fetch','tool-write')
order by ord;
```

The `text` parts are the agent's **narration** — usually the smoking gun (e.g.
*"the API doesn't have direct CPM metrics, I'll generate … sample data"*).

### 7. Content audit — is the reported data real? (`has_hallucinated_data`)

For each **delivered** email, set `has_hallucinated_data` from the run's tool calls
(§ 6): **a metric is hallucinated if it isn't backed by a successful data-fetch this
run.** Red flags:
- the data call **errored / returned empty** (`/socials` → "Artist not found",
  `organizations: []`) yet the email still reports numbers;
- **no `web_fetch`** in a trends/research task (`used_web_fetch=false`);
- the HTML/narration contains **"sample data" / "estimated" / "industry average" /
  "realistic data" / `chart-placeholder`**;
- the agent used the **wrong id** for a sub-resource (gotchas below) → 404 → no data.

Report two columns alongside the delivered table: **`has_hallucinated_data`** (bool;
mark `✅ verified` vs `⚠️ inferred`) and **`expected_data_source`** (where accurate
data *should* come from — YouTube CPM → YouTube Analytics connector; trends →
`web_fetch` + platform trending; followers/streams → Recoup socials / Research).

**Id gotchas when spot-checking real data** (skip these and you'll log false "no data"):
- `/api/artists/{id}/*` sub-resources key on the **`account_id`**, *not* the list's
  top-level `id`. And socials are **embedded** in `/api/artists` (`account_socials`) —
  check there before calling `/socials` at all.
- `POST /api/socials/{id}/scrape` keys on **`social_id`**, *not* the `id` field.

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

- **Needs the PROD `TRIGGER_SECRET_KEY`** — a `tr_dev_*` key returns 0 runs; the
  script warns you. Pull it to a scratch file and scrub it after (see § A).
- **Not all `customer-prompt-task` runs are email tasks** — filter to email-intent
  before judging delivery (see the § 2 callout).
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
