---
name: recoup-internal-account-health-report
description: >-
  INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke
  ONLY when the request explicitly includes "recoup-internal" (e.g.
  "recoup-internal account health for this account"). Never use for
  customer-facing or artist requests.
  Produce an account-status / account-health snapshot for a Recoup account from
  an email, account ID, or artist name. Resolves the account, pulls its artists,
  socials, chats, scheduled tasks, sandboxes, credits and subscription, then
  generates an ACCOUNT.md, a per-artist ARTIST.md tree, and a polished status
  PDF. Use when asked to "check this account", "account status", "account
  health", "how are they using the product", "what artists / chats does this
  account have", "evaluate this user/profile", or to find the sign-in email
  behind an artist. Requires a Recoup API token (an admin token can inspect any
  account; an owner token only its own).
---

# Recoup Account Health

Builds a complete picture of how a Recoup account uses the product and packages
it as Markdown + a PDF. This is the workflow that produced the Sound of Fractures
account status report.

## When to use

- "Summarize / evaluate the status of this account or profile."
- "Do they have artists? Are they opening chats? How are they using the product?"
- "Find the email an artist used to sign in" (admin token).
- "Build an account-status PDF / ACCOUNT.md / per-artist folders."

## Prerequisites

- A Recoup API bearer token in `RECOUP_ACCESS_TOKEN` (or pass `--token`).
  - An **admin** token can read any account via the `account_id` override on
    list endpoints. Confirm admin with `GET /api/admins` → `{"isAdmin": true}`.
  - An **owner** token only sees its own account.
- `reportlab` for the PDF: `pip install reportlab --break-system-packages`.
- Base URL: `https://api.recoupable.dev/api` (override with `RECOUP_API_BASE`).
  Load the `recoup-platform-api-access` skill for endpoint details.

## Quick run

```bash
export RECOUP_ACCESS_TOKEN="<token>"
python3 scripts/generate_account_status.py \
  --email soundoffractures@gmail.com \
  --out-dir <workspace>/<artist-folder>
# or: --account-id <uuid>
```

Outputs into `--out-dir`:

- `ACCOUNT.md` — identity, plan & usage, verdict, artist roster table.
- `artists/INDEX.md` — one-line roster across all records.
- `artists/<slug>-<shortid>/ARTIST.md` — per artist: socials (handle, followers,
  last-scraped date), chats, and tasks. The short ID suffix keeps duplicate
  same-name records distinct.
- `<name>-Account-Status.pdf` — executive snapshot. Page 1 is the identity /
  usage / verdict / roster; page 2 is the **Most relevant chats** table.

Both `ACCOUNT.md` and the PDF include a **Most relevant chats** table — the top 10
chats across all of the account's artists, ranked to show what the account is
actually working on in Recoup (see step 4 below).

## Workflow (what the script automates)

1. **Resolve the account.**
   - By email: `POST /api/accounts {"email": "..."}` returns the existing account
     (UUID, name, emails, wallets) — it does not create one if it already exists.
   - By id: `GET /api/accounts/{id}`.
   - To find an account behind an artist name from an admin token, search Privy
     logins: `GET /api/admins/privy?period=all` and grep the linked email.
2. **Pull account-level data** (pass `?account_id=<uuid>` as admin):
   - `GET /api/accounts/{id}/subscription` — isPro, plan, status.
   - `GET /api/accounts/{id}/credits` — used vs. total.
   - `GET /api/organizations?account_id=<uuid>`.
   - `GET /api/sandboxes?account_id=<uuid>`.
   - `GET /api/artists?account_id=<uuid>` — the roster.
3. **Per artist:**
   - `GET /api/artists/{artistId}/socials` — connected platforms + followers.
   - `GET /api/chats?artist_account_id={artistId}&account_id=<uuid>`.
   - `GET /api/tasks?artist_account_id={artistId}&account_id=<uuid>`.
4. **Synthesize a verdict.** If chats, tasks, sandboxes and credits-used are all
   zero, the account is **dormant**; otherwise it shows real engagement. Flag
   data hygiene issues (duplicate artist records, mismatched social auto-matches,
   missing platforms). Also grade the account against the activation funnel in
   `references/onboarding-checkpoints.md` (furthest contiguous step + skipped
   steps) — the data pulled in steps 2–3 already answers every checkpoint.
5. **Rank the chats** (`rank_chats`). Collect every chat across all artists and
   score each by a topic signal (regex keyword buckets over the chat **title** —
   `CHAT_THEMES`) plus a recency bonus, then take the top 10. Each row shows the
   title, last-active date, and inferred theme (e.g. *Strategy & frameworks*,
   *Analysis & metrics*, *Content production*). For multi-artist accounts an
   **Artist** column is added automatically. Titles only: see the chat-bodies
   caveat below.
6. **Render** `ACCOUNT.md`, the `artists/` tree, and the PDF, then present the PDF
   to the user.

## PDF styling notes (don't regress these)

- **White header text on dark rows.** A reportlab `Paragraph` carries its own
  `textColor`, so a `TableStyle` `TEXTCOLOR` on the header row is **not** enough —
  the text renders black on navy and is unreadable. Every navy header row must use
  the dedicated `CELLBW` (white bold) paragraph style for its cells. This applies
  to the Product-engagement, Artists, and Most-relevant-chats tables. The identity
  table and the left "Metric" label column sit on a light background and correctly
  use the dark `CELLB` style.
- The chats table lives on its own page (`PageBreak`) and repeats its header row
  (`repeatRows=1`) if it ever spills.

## Notes & caveats

- Pre-migration chat sessions may not surface in current endpoints — cross-check
  multiple usage signals before declaring an account dead.
- The `account_id` override is honored for **reads** with an admin token but
  **not** for `DELETE /api/artists/{id}` (that route only unlinks the caller's
  own artist link). Deleting another account's records needs an owner-scoped
  token or an in-app/admin action.
- Social auto-matches can be wrong (e.g. a Spotify match returning an unrelated
  major artist). Treat large follower counts on a small artist as suspect.
- **Chat bodies are owner-scoped.** The admin `account_id` override works for the
  chat **list** (`GET /api/chats`), so titles, dates and counts are available. But
  per-chat message bodies are not: `GET /api/chats/{id}/messages` returns
  `Chat room not found` and `GET /api/sessions/{sessionId}/chats/{chatId}` returns
  `Forbidden` for another account's chats. The Most-relevant-chats ranking and
  themes are therefore derived from the **auto-generated title** (which Recoup
  builds from the chat's opening prompt), not the transcript. To produce
  transcript-level summaries, run with an **owner-scoped** token for that account.
- Chat titles can be long; the script truncates display titles (~70–78 chars).
