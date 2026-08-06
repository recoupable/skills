# Tooling gotchas

Quirks and dead columns across Privy, Stripe, Supabase, Attio and the Recoup API that
have each cost a real misdiagnosis. Consult when a lookup returns something that does not
match what you expect — none of it is needed to run a sweep.

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
