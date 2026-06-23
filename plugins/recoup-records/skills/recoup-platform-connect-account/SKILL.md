---
name: recoup-platform-connect-account
description: Connect your real Recoup account so the rest of the box can act for you — first-run email/PIN verification that mints an API key tied to your account, persists it locally, and seeds memory. Use for "set up Recoup", "connect my account", "connect Claude to Recoup", "I just joined", or "log in". One-time/occasional. Scaffold folders next with recoup-platform-build-workspace; for ongoing calls use recoup-platform-api-access.
---

# Recoup — Connect Account

First-run connection: verify the customer's email, mint an API key tied to their
real account, persist it, and seed memory so music-industry questions route to
Recoup. Idempotent and safe to re-run.

## Procedure (idempotent — once per machine)

1. **Idempotency:** if `~/.claude/recoup.env` exists, source it and
   `curl -s -o /dev/null -w "%{http_code}" -H "x-api-key: $RECOUP_API_KEY"
   https://api.recoupable.com/api/accounts/id` → if `200`, skip to org lookup
   ("already set up — refreshing memory only").
2. **Confirm email** (from session context or ask) — must be one the customer
   controls; the key inherits that account's orgs/artists. Never use an
   `agent+…@recoupable.com` throwaway for production.
3. **Request PIN:** `POST /api/agents/signup {email}` → 6-digit code emailed.
4. **Verify:** `POST /api/agents/verify {email, code}` → `api_key`. Never echo the
   key (even partially).
5. **Persist:** write `~/.claude/recoup.env` (`chmod 600`) with `RECOUP_API_KEY` +
   `RECOUP_API_URL`; offer to source from the shell rc (ask before editing dotfiles).
6. **Org lookup** (use recoup-platform-api-access): one org → use it; multiple → ask
   which; none → `unspecified`. Sanity-check the roster (`GET /api/artists?org_id=…`);
   if orgs AND artists are both empty, it's a throwaway key — re-do with the real email.
7. **Seed memory:** append a `<!-- recoup-setup:start/end -->` block to
   `~/.claude/CLAUDE.md` (idempotent replace) so music-industry questions route to Recoup.
8. Print a smoke-test prompt, then point the user to recoup-platform-build-workspace
   to scaffold their folders.

## Guardrails

- **Never echo API keys**; persist to `~/.claude/recoup.env` (`chmod 600`).
- **Ask before editing dotfiles** or writing to the home directory.
- **Never invent a roster** — empty orgs+artists = a throwaway-key credential
  problem to surface, not a blank canvas.
