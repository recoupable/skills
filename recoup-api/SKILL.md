---
name: recoup-api
description: Call the Recoupable API from the sandbox to fetch artist data, socials, organizations, research, documents and any other platform resource — and to invoke external connector actions (Google Docs / Drive / Sheets edits, Gmail, TikTok, Instagram, etc.) via Recoupable's shared connections. Use whenever you're asked for Recoup data, a Recoupable platform resource, or to read/write something outside Recoup like a Google Doc URL or a spreadsheet. Triggers on phrases like "look up artist", "fetch from recoup", "artist data", "artist socials", "organizations", "artist report", "research", "create new artist", "create artist", "onboard artist", "add artist", "edit this Google Doc", "read this doc", "update the spreadsheet", "send an email", "post on TikTok", "save to Drive", or whenever the user pastes a docs.google.com / drive.google.com / sheets.google.com URL. Always load this before writing curl calls against recoup-api.vercel.app.
---

# Recoupable API

Call the Recoupable production API to fetch artist data, social metrics, org context, research, and to trigger platform operations.

- **Base URL:** `https://recoup-api.vercel.app/api`
- **LLM-readable docs:** `https://developers.recoupable.com` — Mintlify site. Use `/llms.txt` for the endpoint index, `/llms-full.txt` for full content, and the OpenAPI JSONs listed below for machine-readable schemas.

## Authentication

Your sandbox receives a short-lived access token in `RECOUP_ACCESS_TOKEN`. Use it as a `Bearer` token on every request:

```bash
curl -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  https://recoup-api.vercel.app/api/artists/{artistId}/socials
```

If `RECOUP_ACCESS_TOKEN` is empty, the user is not authenticated — tell them to sign in rather than retrying.

## Org scoping (`RECOUP_ORG_ID`)

When running inside a sandbox, the environment also exposes `RECOUP_ORG_ID` — the organization the sandbox was opened for. The access token is account-scoped (it covers every org the account belongs to), so when you use it with unscoped list endpoints like `GET /api/artists` you will get results from **all** of that account's orgs, not just the one this sandbox represents. That mismatch surprises accounts.

When `RECOUP_ORG_ID` is set, scope list/query endpoints to it:

```bash
# Artists for this sandbox's org only
curl -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  "https://recoup-api.vercel.app/api/organizations/$RECOUP_ORG_ID/artists"
```

For the Recoup CLI, pass `--org "$RECOUP_ORG_ID"` on commands that accept it. If `RECOUP_ORG_ID` is unset, you are not in an open-agents sandbox — fall back to account-scoped calls as normal.

**Sandbox-inventory shortcut:** for bare "what artists / orgs do I have" questions, prefer reading the local `artists/*/RECOUP.md` tree instead of calling the API at all — the filesystem is authoritative for this sandbox. See the `artist-workspace` skill for the walkthrough.

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

### Research (Chartmetric + Web)

One section covering most music-industry lookup work:

- **Discovery**: search, profile, similar artists, discover by criteria, people search, lookup by URL
- **Catalog**: albums, tracks, track playlists
- **Metrics**: artist rank, platform metrics (14 platforms), audience demographics, career timeline, listener cities, milestones, charts
- **Surface**: playlist, playlist placements, venues, radio stations, festivals, genres, curator
- **Insights**: AI insights, social URLs, instagram posts
- **Web**: enrich, extract URL, deep research, web search

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

Machine-readable schemas for the major sections: `accounts.json`, `social.json`, `releases.json`, `research.json`, `content.json` (served at `https://developers.recoupable.com/<name>.json`).

## Finding an endpoint

Once you know the section, pull just that section's docs instead of the whole index. Example patterns:

```bash
# Find the exact path + params for a specific endpoint
curl -s https://developers.recoupable.com/llms-full.txt | grep -A 30 -i "similar artists"

# Pull the OpenAPI schema for one area
curl -s https://developers.recoupable.com/research.json | jq '.paths | keys'
```

Do **not** guess exact paths, parameter names, or response shapes — fetch the relevant section first.

## Example request

```bash
# Get all socials for an artist
curl -sS -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  "https://recoup-api.vercel.app/api/artists/{artistId}/socials" | jq
```

`jq` is preinstalled in the sandbox.

## Multi-step workflows

For multi-endpoint sequences that need a specific order, follow the published workflow guides instead of inventing the chain yourself. The guide tells you which endpoint to call at each step, what to capture for the next step, and which steps are intentionally skipped from a sandbox context.

| Workflow | Guide | Driver |
|----------|-------|--------|
| Create + research a new artist (full enrichment chain — POST artist, Spotify match, profile/socials/knowledges, structured research via Chartmetric profile/career/playlists + web, KB synthesis) | [https://developers.recoupable.com/workflows/create-artist](https://developers.recoupable.com/workflows/create-artist) | `artist-workspace` skill — scaffolds a `RECOUP.md` checklist file, ticks each step on completion |

Trigger to load a workflow guide: any phrase like "create a new artist", "onboard X", "add this artist", or any request that requires more than one endpoint to complete.

**For the create-artist chain, invoke the `artist-workspace` skill first** — it scaffolds `artists/{slug}/RECOUP.md` with one checkbox per workflow step, and the agent then drives execution from that file (tick + persist outputs to frontmatter after every step). The workflow guide above is the curl-by-curl reference for each step's request shape, but the checklist is the source of truth for what's done. The chain has 8 sequential calls and skipping any leaves the artist partially populated.

## Connector actions (Google Docs/Sheets/Drive, Gmail, TikTok, Instagram)

For reads/writes **outside** Recoup — editing a Google Doc by URL, syncing a sandbox file with Drive, sending an email, posting a TikTok — use the platform's shared third-party connections via two endpoints:

- `GET /api/connectors/actions` — catalog of every available action with its `slug`, `description`, `parameters` JSON Schema, `connectorSlug`, and `isConnected`. See [docs](https://developers.recoupable.com/api-reference/connectors/list-actions).
- `POST /api/connectors/actions` — execute one by `actionSlug` with `parameters` matching its schema. See [docs](https://developers.recoupable.com/api-reference/connectors/execute-action).

Slugs are always **UPPERCASE_SNAKE_CASE** (e.g. `GOOGLEDOCS_INSERT_TEXT_ACTION`, `GMAIL_FETCH_EMAILS`). Auth is the same `RECOUP_ACCESS_TOKEN` Bearer. **Always pull the parameters schema from the catalog before executing** — Composio's shapes vary per action.

### Worked example: Google Doc ↔ sandbox file sync

When the user pastes a `docs.google.com/document/d/{ID}/edit` URL, extract the ID and pick the right Google Docs action — `GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT` to read, `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN` to replace the whole doc, `GOOGLEDOCS_INSERT_TEXT_ACTION` to insert at an index, `GOOGLEDOCS_REPLACE_ALL_TEXT` for find-replace:

```bash
DOC_ID=$(echo "$DOC_URL" | sed -nE 's|.*/document/d/([^/]+).*|\1|p')
EXEC="https://recoup-api.vercel.app/api/connectors/actions"
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
- Calling Chartmetric, Spotify, or other third-party APIs directly — prefer the Recoup **Research** endpoints above (they wrap Chartmetric with our auth), or use the dedicated skill if one exists (e.g. `chartmetric`).
- Reading the user's git repo contents — that's already mounted in the working directory.
