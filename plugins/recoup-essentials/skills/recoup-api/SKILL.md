---
name: recoup-api
description: Call the Recoupable API from the sandbox to fetch artist data, socials, organizations, research, documents and any other platform resource — and to invoke external connector actions (Google Docs / Drive / Sheets edits, Gmail, TikTok, Instagram, etc.) via Recoupable's shared connections. Use whenever you're asked for Recoup data, a Recoupable platform resource, or to read/write something outside Recoup like a Google Doc URL or a spreadsheet. Triggers on phrases like "look up artist", "fetch from recoup", "artist data", "artist socials", "organizations", "artist report", "research", "create new artist", "create artist", "onboard artist", "add artist", "edit this Google Doc", "read this doc", "update the spreadsheet", "send an email", "post on TikTok", "save to Drive", or whenever the user pastes a docs.google.com / drive.google.com / sheets.google.com URL. Always load this before writing curl calls against api.recoupable.com.
---

# Recoupable API

Call the Recoupable production API to fetch artist data, social metrics, org context, research, and to trigger platform operations.

- **Base URL:** `https://api.recoupable.com/api`
- **LLM-readable docs:** `https://developers.recoupable.com` — Mintlify site. Use `/llms.txt` for the endpoint index, `/llms-full.txt` for full content, and the OpenAPI JSONs listed below for machine-readable schemas.

## Authentication

Recoup accepts **either** credential — prefer the API key when both are present:

| Credential | Header | Where it comes from |
| --- | --- | --- |
| `RECOUP_API_KEY` (`recoup_sk_…`) | `-H "x-api-key: $RECOUP_API_KEY"` | API-key install (`recoup-setup`) / agent signup |
| `RECOUP_ACCESS_TOKEN` | `-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"` | short-lived open-agents sandbox token |

Build an `AUTH` array once and reuse it on every call:

```bash
if [ -n "$RECOUP_API_KEY" ]; then
  AUTH=(-H "x-api-key: $RECOUP_API_KEY")
elif [ -n "$RECOUP_ACCESS_TOKEN" ]; then
  AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN")
else
  echo "No Recoup credential set — ask the user to authenticate; do not retry blindly." >&2
fi
# Use as:  curl -sS "${AUTH[@]}" "https://api.recoupable.com/api/artists/{id}/socials"
```

If neither is set, the user is not authenticated — tell them to sign in rather than retrying. (Examples further down use `Authorization: Bearer $RECOUP_ACCESS_TOKEN` directly; swap in `"${AUTH[@]}"` when you have an API key instead.)

## Working with an artist — pick the mode first

Before any artist task, decide **which of these the user means.** Guessing here is exactly what makes an agent fabricate an artist that doesn't exist (or invent a persona for one that does).

| Mode | The user means… | Trigger phrases | What to do |
| --- | --- | --- | --- |
| **A · Any artist (research)** | Look up *any* artist — not necessarily one of theirs | "research X", "how's X doing", "compare X and Y" | Use the **Research** endpoints (or the `recoup-artist-research` skill). Works off a name — no roster lookup needed. |
| **B · Browse my roster** | List the artists on *their* account | "my roster", "my artists", "who do I have", "pick one of my artists" | Run **Roster discovery** below, then present the list. |
| **C · A specific roster artist** | Act on one of *their* artists | "make content for `<name>`", "update `<name>`'s brand" | Run **Roster discovery**, match the name, capture `account_id` + row `id`. No match → they're not on the roster yet (offer Mode D). |
| **D · Add an artist** | Onboard a brand-new artist | "add / onboard / create artist X", "set up a new artist" | Use the `recoup-create-artist` skill (8-call chain). |

### Roster discovery (Modes B & C)

In an open-agents **sandbox with a populated `artists/` tree**, that filesystem is authoritative — use the `recoup-artist-workspace` skill instead of the API. Otherwise (an API-key install, or no `artists/` directory), enumerate from the API:

```bash
BASE="https://api.recoupable.com/api"   # AUTH set per the Authentication section above

# 1. Whose account is this credential? Sanity-check BEFORE trusting the roster.
curl -sS "${AUTH[@]}" "$BASE/accounts/id"            # -> {"accountId":"…"}

# 2. Organizations on the account
curl -sS "${AUTH[@]}" "$BASE/organizations" \
  | jq -r '.organizations[] | [.organization_id, .organization_name] | @tsv'

# 3a. Artists for one org (preferred when you know the org)
curl -sS "${AUTH[@]}" "$BASE/artists?org_id=$ORG_ID" \
  | jq -r '.artists[] | [.name, .account_id, .id] | @tsv'

# 3b. …or every artist the account can see (account-wide)
curl -sS "${AUTH[@]}" "$BASE/artists" \
  | jq -r '.artists[] | [.name, .account_id, .id] | @tsv'
```

**Verified field shapes** (live, 2026-06-07): each **org** row has `organization_id`, `organization_name`, and its own row `id` — pass the `organization_id` value as `org_id`. Each **artist** row has `name`, `account_id`, and a row `id`. Capture both artist ids: `account_id` is what content endpoints and `/api/artists/{…}/socials` want; the row `id` is the artist's primary key.

### Stop rule — never invent a roster

If `GET /accounts/id` resolves to an account whose email is `agent+…@recoupable.com` (check `GET /api/accounts/{accountId}`), **or** `organizations` and `artists` both come back empty (`[]`), you are almost certainly on a throwaway / agent-signup key — **not** the user's real account. **Stop and say so:** name the resolved `accountId` and ask the user for a key tied to their real account (or to run `recoup-setup`). Do **not** fabricate an artist, persona, EP, or roster to keep the task moving — an empty roster is a credential problem to surface, not a blank canvas to fill.

## Org scoping (`RECOUP_ORG_ID`)

When running inside a sandbox, the environment also exposes `RECOUP_ORG_ID` — the organization the sandbox was opened for. The access token is account-scoped (it covers every org the account belongs to), so when you use it with unscoped list endpoints like `GET /api/artists` you will get results from **all** of that account's orgs, not just the one this sandbox represents. That mismatch surprises accounts.

When `RECOUP_ORG_ID` is set, scope list/query endpoints to it:

```bash
# Artists for this sandbox's org only
curl -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  "https://api.recoupable.com/api/organizations/$RECOUP_ORG_ID/artists"
```

For the Recoup CLI, pass `--org "$RECOUP_ORG_ID"` on commands that accept it. If `RECOUP_ORG_ID` is unset, you are not in an open-agents sandbox — fall back to account-scoped calls as normal.

**Inventory — filesystem first, API fallback:** inside an open-agents sandbox that has a populated `artists/` tree, prefer reading that local tree instead of calling the API — the filesystem is authoritative for the sandbox (see the `recoup-artist-workspace` skill). **But if there is no `artists/` directory** — e.g. an API-key install outside a sandbox — the filesystem can't answer, so fall back to **Roster discovery** above. Never conclude "the roster is empty" from an empty/missing filesystem; confirm against the API first.

## Docs Map

The full endpoint surface is organized into the sections below. Use this map to pick the right area, then pull the detailed docs for just that area (see [Finding an endpoint](#finding-an-endpoint)) instead of fetching everything.

### Account & Identity

- **Accounts** — create/get/update accounts, add artists to account
- **Organizations** — create/list orgs, add artists to org
- **Workspaces** — create workspaces
- **Subscriptions** — get subscriptions, create Stripe checkout session
- **Agents** — agent signup, email verification
- **Admins** — admin-only: agent sign-ups, coding/content agent Slack tags, Resend emails, Privy logins, sandbox stats, org repo commit stats

### Artists & Content

- **Artists** — create/get/delete, get socials, pin/unpin, get profile (across all platforms), trigger socials scrape
- **Posts** — get artist posts across platforms
- **Comments** — get comments for an artist or a specific post
- **Fans** — get social profiles of an artist's fans
- **Songs** — create/get songs by ISRC, manage catalogs (CRUD + add/remove songs), analyze songs via audio LM, list analyze presets
- **Content Creation** — pipeline trigger, video/image/caption generation, ffmpeg edits, video analysis, upscale, cost estimate, audio transcription, templates

### Research (Songstats + Web)

One section covering most music-industry lookup work. Backed by **Songstats** — entity IDs are short alphanumeric strings (e.g. `wjcgfd9i`), not numeric Chartmetric IDs:

- **Discovery**: search (`type=artists|tracks|labels`), profile, similar artists, people search, lookup by URL
- **Catalog**: albums, tracks, track detail, track playlists
- **Metrics**: platform metrics (16 sources), audience demographics, career timeline, milestones
- **Surface**: playlist placements
- **Insights**: AI insights, social URLs
- **Web**: enrich, extract URL, deep research, web search

> Removed in the Songstats migration (these return 404 — don't call them): `discover`, `rank`, listener `cities`, `charts`, `playlist` (singular), `venues`, `radio`, `festivals`, `genres`, `curator`, `instagram-posts`. Geography now comes from `audience`; discovery from `similar` + `web`.

### Social Integrations

- **Social Media** — get social posts from a profile, trigger scrape
- **Instagram Integration** — comments, profiles (bulk)
- **Spotify Integration** — search, artist, artist albums, artist top tracks, album
- **Twitter/X Integration** — search tweets, get trends
- **Connectors** — list/authorize/disconnect third-party OAuth integrations
- **Connector actions** — execute external operations (Google Docs/Sheets/Drive edits, Gmail, TikTok, Instagram) via shared connections. See the section below.
- **Apify Integration** — scraper run results
- **Transcription** — Whisper audio transcription

### Chat & Agents

- **Chat** — create/get/delete chats, messages, AI generate/stream (Vercel AI SDK compatible), update, copy, compact
- **Content Agent** — Slack webhook + task callback (internal)
- **Pulses** — list/update pulses
- **Notifications** — send notification email to the authenticated account
- **Tasks** — create/get/update/delete scheduled tasks, get task run history
- **Image Generation** — standalone AI image gen (also available scoped under Content Creation)

### Developer & Infrastructure

- **Sandboxes** — create/setup/list/delete sandboxes, get file contents, upload files, update snapshot

### Guides (non-endpoint pages)

Authentication · CLI · MCP · Quickstart.

### OpenAPI specs

Machine-readable schemas for the major sections: `accounts.json`, `social.json`, `releases.json`, `research.json`, `content.json` (served at `https://developers.recoupable.com/api-reference/openapi/<name>.json`).

## Finding an endpoint

Once you know the section, pull just that section's docs instead of the whole index. Example patterns:

```bash
# Find the exact path + params for a specific endpoint
curl -s https://developers.recoupable.com/llms-full.txt | grep -A 30 -i "similar artists"

# Pull the OpenAPI schema for one area
curl -s https://developers.recoupable.com/api-reference/openapi/research.json | jq '.paths | keys'
```

Do **not** guess exact paths, parameter names, or response shapes — fetch the relevant section first.

## Example request

```bash
# Get all socials for an artist
curl -sS -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  "https://api.recoupable.com/api/artists/{artistId}/socials" | jq
```

`jq` is preinstalled in the sandbox.

## Multi-step workflows

For multi-endpoint sequences that need a specific order, follow the published workflow guides instead of inventing the chain yourself. The guide tells you which endpoint to call at each step, what to capture for the next step, and which steps are intentionally skipped from a sandbox context.

| Workflow | Guide | Driver |
|----------|-------|--------|
| Create + research a new artist (full enrichment chain — POST artist, Spotify match, profile/socials/knowledges, structured research via Songstats profile/career/playlists + web, KB synthesis) | [https://developers.recoupable.com/workflows/create-artist](https://developers.recoupable.com/workflows/create-artist) | `recoup-artist-workspace` skill — scaffolds a `RECOUP.md` checklist file, ticks each step on completion |

Trigger to load a workflow guide: any phrase like "create a new artist", "onboard X", "add this artist", or any request that requires more than one endpoint to complete.

**For the create-artist chain, invoke the `recoup-artist-workspace` skill first** — it scaffolds `artists/{slug}/RECOUP.md` with one checkbox per workflow step, and the agent then drives execution from that file (tick + persist outputs to frontmatter after every step). The workflow guide above is the curl-by-curl reference for each step's request shape, but the checklist is the source of truth for what's done. The chain has 8 sequential calls and skipping any leaves the artist partially populated.

## Connector actions (Google Docs/Sheets/Drive, Gmail, TikTok, Instagram)

For reads/writes **outside** Recoup — editing a Google Doc by URL, syncing a sandbox file with Drive, sending an email, posting a TikTok — use the platform's shared third-party connections via two endpoints:

- `GET /api/connectors/actions` — catalog of every available action with its `slug`, `description`, `parameters` JSON Schema, `connectorSlug`, and `isConnected`. See [docs](https://developers.recoupable.com/api-reference/connectors/list-actions).
- `POST /api/connectors/actions` — execute one by `actionSlug` with `parameters` matching its schema. See [docs](https://developers.recoupable.com/api-reference/connectors/execute-action).

Slugs are always **UPPERCASE_SNAKE_CASE** (e.g. `GOOGLEDOCS_INSERT_TEXT_ACTION`, `GMAIL_FETCH_EMAILS`). Auth is the same `RECOUP_ACCESS_TOKEN` Bearer. **Always pull the parameters schema from the catalog before executing** — Composio's shapes vary per action.

### Worked example: Google Doc ↔ sandbox file sync

When the user pastes a `docs.google.com/document/d/{ID}/edit` URL, extract the ID and pick the right Google Docs action — `GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT` to read, `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN` to replace the whole doc, `GOOGLEDOCS_INSERT_TEXT_ACTION` to insert at an index, `GOOGLEDOCS_REPLACE_ALL_TEXT` for find-replace:

```bash
DOC_ID=$(echo "$DOC_URL" | sed -nE 's|.*/document/d/([^/]+).*|\1|p')
EXEC="https://api.recoupable.com/api/connectors/actions"
AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" -H "Content-Type: application/json")

# Read the doc into a local file.
curl -sS -X POST "${AUTH[@]}" "$EXEC" \
  -d "$(jq -n --arg id "$DOC_ID" '{actionSlug:"GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT", parameters:{document_id:$id}}')" \
  | jq -r '.result.data.text' > artists/$ARTIST_SLUG/notes.md

# (edit notes.md locally — agent edits, git diff, etc.)

# Push it back, replacing the doc's content.
curl -sS -X POST "${AUTH[@]}" "$EXEC" \
  -d "$(jq -n --arg id "$DOC_ID" --rawfile md artists/$ARTIST_SLUG/notes.md \
        '{actionSlug:"GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN", parameters:{document_id:$id, markdown_content:$md}}')"
```

The Google Doc and the local file are two views of the same content — commit the local copy with the artist's other workspace files.

**Trigger heuristic:** external URLs (`docs.google.com`, `drive.google.com`, `sheets.google.com`), or phrases like "edit this doc", "send an email", "post on TikTok". Internal Recoup resources (artists, socials, research) use the dedicated endpoints in the Docs Map above.

## Troubleshooting

| Error | Meaning | Fix |
|-------|---------|-----|
| 401 | Token missing, invalid, or expired | Check `RECOUP_ACCESS_TOKEN` is set; if the prompt has been running a long time, ask the user to resend |
| 403 | User lacks access to the resource | Confirm the user has permission for the org/artist being queried |
| 404 | Endpoint not found | Re-check the Docs Map above; the endpoint may have moved or been renamed |
| 5xx | Server error | Retry once; if persistent, surface the status to the user |

## When NOT to use this skill

- Reading/writing files inside the sandbox — use the filesystem tools.
- Calling Songstats, Chartmetric, Spotify, or other third-party APIs directly — prefer the Recoup **Research** endpoints above (they wrap the configured research provider, currently Songstats, with our auth), or use a dedicated skill if one exists.
- Reading the user's git repo contents — that's already mounted in the working directory.
