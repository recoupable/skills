---
name: recoup-platform
description: Platform operations for Recoup — get connected, call the API, manage artists and their workspaces, and capture learnings. Modes — setup (first-run connect: email/PIN → API key), sandbox (scaffold your account's org/artist folders), api (raw REST + connector actions like Google Docs/Drive/Gmail/TikTok), create-artist (onboard + enrich a new artist via the 8-call chain), workspace (work inside an artist's folder — context, songs, releases, inventory), and learn (save a solved problem so the next run is cheaper). Use for "set up Recoup", "connect my account", "scaffold my sandbox", "fetch from the recoup api", "edit this Google Doc", "create/onboard an artist", "what artists do I have", "organize this artist's files", or "remember this for next time".
---

# Recoup Platform

The foundation layer: get connected, talk to the platform, manage artists and
their files, and remember what you learn. It **picks a mode from the ask**.

| The user wants… | Mode |
|---|---|
| "set up Recoup", "connect my account", first-run | **setup** |
| "scaffold my sandbox", build the org/artist folder tree | **sandbox** |
| call the API / a connector (Google Docs, Drive, Gmail, TikTok), fetch any platform resource | **api** |
| "create / onboard / add an artist" | **create-artist** |
| "what artists do I have", organize/operate inside an artist's folder | **workspace** |
| "remember this", "that worked", capture a reusable lesson | **learn** |

## Mode: setup (first-run connect — idempotent, once per machine)

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
6. **Org lookup** (via **api** mode): one org → use it; multiple → ask which; none
   → `unspecified`. Sanity-check the roster (`GET /api/artists?org_id=…`); if orgs
   AND artists are both empty, it's a throwaway key — re-do with the real email.
7. **Seed memory:** append a `<!-- recoup-setup:start/end -->` block to
   `~/.claude/CLAUDE.md` (idempotent replace) so music-industry questions route to
   Recoup. 8. Print a smoke-test prompt.

## Mode: sandbox (scaffold the account's folder tree)

**Guard:** if `orgs/` already exists with content, stop → use **workspace** mode.
Auth `Authorization: Bearer $RECOUP_ACCESS_TOKEN`; `RECOUP_ORG_ID` (optional) scopes
to one org. Then: `GET /api/organizations` → for each (or just `RECOUP_ORG_ID`),
`GET /api/artists?org_id=…` → `mkdir -p orgs/{slugify(org)}/artists/{slugify(name)}`
and write a `RECOUP.md` identity file (`artistName`/`artistSlug`/`artistId` from
`account_id`) per artist; skip existing; commit. `slugify` = lowercase-kebab; never
append IDs to folder names. (Note: in an open-agents sandbox artists live at
top-level `artists/` — no `orgs/`; see **workspace**.)

## Mode: api (raw REST + connectors)

Base `https://api.recoupable.com/api`; docs `https://developers.recoupable.com`
(`/llms.txt`, `/llms-full.txt`, OpenAPI JSONs). Auth — prefer key:

```bash
if [ -n "$RECOUP_API_KEY" ]; then AUTH=(-H "x-api-key: $RECOUP_API_KEY")
elif [ -n "$RECOUP_ACCESS_TOKEN" ]; then AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN")
else echo "No credential — ask the user to authenticate; don't retry blindly." >&2; fi
```

**Artist mode first** (guessing here fabricates artists): A=any-artist research
(name, no roster lookup) · B=browse my roster · C=a specific roster artist ·
D=add an artist (→ **create-artist**). **Roster discovery:** `GET /accounts/id`
→ `GET /organizations` → `GET /artists?org_id=…` (capture both `account_id` and
row `id`). **Stop rule:** if the account email is `agent+…@recoupable.com`, or
orgs AND artists are both empty, it's a throwaway key — say so, don't invent a
roster. **Docs map** (pull the section you need, don't guess paths): Account/
Identity · Artists/Content · Research (Songstats+Web) · Social Integrations ·
Chat/Agents · Developer. **Connector actions** (Google Docs/Sheets/Drive, Gmail,
TikTok): `GET /api/connectors/actions` (catalog) → `POST /api/connectors/actions`
`{actionSlug, parameters}`; slugs are `UPPERCASE_SNAKE_CASE`; always pull the
param schema before executing. Never guess paths — `grep` `llms-full.txt` or pull
the OpenAPI JSON first.

## Mode: create-artist (8-call onboarding chain — driven by a checklist)

Long chains run from prose drop steps, so **drive from the `RECOUP.md` checklist**
(scaffold it first; tick + persist captured values after each step — the file is
the workflow state, resumable). Don't run under an `agent+` account. The 8 calls:
1. `POST /api/artists {name, organization_id}` → capture `account_id`.
2. `GET /api/spotify/search` → best match → `id`, `external_urls.spotify`, `images[0]`.
3. `PATCH /api/artists/{id}` with image + `profileUrls:{SPOTIFY}` (UPPERCASE keys).
4. Structured research (retry transient misses): `/research/lookup?spotifyId=` →
   `songstats_artist_id`, then `/research/profile|career|playlists` + `/research/web`.
5. Spotify catalog (`topTracks`, `albums`, `album`) → write `releases/{slug}/RELEASE.md`
   per album + `releases/top-tracks.md`.
6. Web search for socials (ig/tiktok/twitter/youtube).
7. `PATCH /api/artists/{id}` with discovered `profileUrls` (only found platforms).
8. Synthesize a `## Knowledge base` section into `RECOUP.md`.
Run in order; don't continue past a 4xx/5xx without recovery; resume from the
first unchecked box.

## Mode: workspace (operate inside an artist's folder)

Artist dirs live at `artists/{artist-slug}/`; `RECOUP.md` (frontmatter
`artistName`/`artistSlug`/`artistId`) is the identity file. **Inventory** ("what
artists do I have") → walk the filesystem when it's a real sandbox
(`ls -d artists/*/`, `find artists -name RECOUP.md`); if `artists/` is missing/empty,
fall back to **api** roster discovery — never report an empty roster from a missing
filesystem. **Layout:** `context/artist.md` (who they are — static), `context/
audience.md` (static), `context/images/face-guide.png`, `releases/{slug}/RELEASE.md`
(18-section master doc; see `references/release-template.md`), `songs/{slug}/{slug}.mp3`.
Nothing is pre-created — add files when real content arrives; never write
placeholder tokens. **Static vs dynamic context:** update `artist.md`/`audience.md`
deliberately (source of truth); treat research/release docs as time-bound, archive
when stale. Templates: `references/artist-template.md` (+ `artist-example.md`),
`references/audience-template.md`, `references/release-template.md`. Commit
`{what}: {why}`; git log is the per-artist progress log.

## Mode: learn (compounding memory)

Capture a reusable lesson so the next run is cheaper. File by **primary subject**
(`artists/{slug}/learnings/`, `deals/{id}/learnings/`, or root `learnings/`).
**Dedup before create** — score overlap (problem/root-cause/solution/files/
prevention) vs existing; high overlap → update, don't duplicate. Write **one**
file (frontmatter `problem_type`/`component`/`tags`/`date` + Problem/Context/
Root cause/Solution/Prevention), commit `learn: <title>`, then a **discoverability
check** (does a README/RECOUP.md point a fresh agent at `learnings/`? add one line
if not). Reusable only; never fabricate a root cause.

## Guardrails (all modes)

- **Never invent a roster/artist** — an empty roster is a credential problem to
  surface (the throwaway-key stop rule), not a blank canvas.
- **Never echo API keys**; persist to `~/.claude/recoup.env` (`chmod 600`).
- **Ask before editing dotfiles** or writing to the home directory.
- **No placeholder data** in artist files — real content or leave it out.
- **The file is the state** for the create-artist chain — tick + persist each step.

## References

- `references/artist-template.md` · `references/artist-example.md` ·
  `references/audience-template.md` · `references/release-template.md` — the
  workspace context + release scaffolds. Full API surface:
  `https://developers.recoupable.com`.
