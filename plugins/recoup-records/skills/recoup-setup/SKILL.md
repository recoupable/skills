---
name: recoup-setup
description: Get the Recoup box connected and your workspace scaffolded — the first thing you run. Modes — connect (first-run: email/PIN verification → an API key tied to your real account, persisted locally, memory seeded) and scaffold (build the org/artist folder tree for your account). Use for "set up Recoup", "connect my account", "connect Claude to Recoup", "I just joined", "scaffold my sandbox", or "build my workspace folders". One-time/occasional config — for ongoing API calls use recoup-api; to operate inside an artist's folder use recoup-artists.
---

# Recoup Setup

The operating-layer skill that makes the box usable: connect your account, then
scaffold your folders. Idempotent and safe to re-run.

| The user wants… | Mode |
|---|---|
| "set up Recoup", "connect my account", first-run | **connect** |
| "scaffold my sandbox", build the org/artist folder tree | **scaffold** |

## Mode: connect (first-run — idempotent, once per machine)

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
6. **Org lookup** (use `recoup-api`): one org → use it; multiple → ask which; none
   → `unspecified`. Sanity-check the roster (`GET /api/artists?org_id=…`); if orgs
   AND artists are both empty, it's a throwaway key — re-do with the real email.
7. **Seed memory:** append a `<!-- recoup-setup:start/end -->` block to
   `~/.claude/CLAUDE.md` (idempotent replace) so music-industry questions route to
   Recoup. 8. Print a smoke-test prompt.

## Mode: scaffold (build the account's folder tree)

**Guard:** if `orgs/` already exists with content, stop → use `recoup-artists`
(workspace) instead. Auth `Authorization: Bearer $RECOUP_ACCESS_TOKEN`;
`RECOUP_ORG_ID` (optional) scopes to one org. Then: `GET /api/organizations` → for
each (or just `RECOUP_ORG_ID`), `GET /api/artists?org_id=…` →
`mkdir -p orgs/{slugify(org)}/artists/{slugify(name)}` and write a `RECOUP.md`
identity file (`artistName`/`artistSlug`/`artistId` from `account_id`) per artist;
skip existing; commit. `slugify` = lowercase-kebab; never append IDs to folder
names. (Note: in an open-agents sandbox artists live at top-level `artists/` — no
`orgs/`; that's `recoup-artists` territory.)

## Guardrails

- **Never echo API keys**; persist to `~/.claude/recoup.env` (`chmod 600`).
- **Ask before editing dotfiles** or writing to the home directory.
- **Never invent a roster** — empty orgs+artists = a throwaway-key credential
  problem to surface, not a blank canvas.
