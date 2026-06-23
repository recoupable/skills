---
name: recoup-platform-api-access
description: Call the Recoupable API and external connectors directly — fetch any platform resource (artists, socials, organizations, research, documents) and run connector actions (Google Docs/Sheets/Drive edits, Gmail, TikTok, Instagram). Use whenever you need raw Recoup data, a platform resource, to write curl against api.recoupable.com, or to read/write something outside Recoup like a Google Doc URL or a spreadsheet. The plumbing every other skill rides on. To onboard or operate on an artist use the recoup-roster-* skills; for first-run connection use recoup-platform-connect-account.
---

# Recoup — API Access

The platform access layer: authenticate, talk to the Recoupable REST API, and
invoke external connectors. Base `https://api.recoupable.com/api`; docs
`https://developers.recoupable.com` (`/llms.txt`, `/llms-full.txt`, OpenAPI JSONs).

## Auth — prefer the API key

```bash
if [ -n "$RECOUP_API_KEY" ]; then AUTH=(-H "x-api-key: $RECOUP_API_KEY")
elif [ -n "$RECOUP_ACCESS_TOKEN" ]; then AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN")
else echo "No credential — ask the user to authenticate; don't retry blindly." >&2; fi
# curl -sS "${AUTH[@]}" "https://api.recoupable.com/api/artists/{id}/socials"
```

## Pick the artist mode first (guessing here fabricates artists)

- **A — any-artist research** (a name; no roster lookup) → Research endpoints.
- **B — browse my roster** → Roster discovery (below).
- **C — a specific roster artist** → Roster discovery, match the name, capture
  `account_id` + row `id`.
- **D — add an artist** → use recoup-roster-add-artist.

**Roster discovery:** `GET /accounts/id` → `GET /organizations` →
`GET /artists?org_id=…` (each artist row has `name`, `account_id`, and a row `id`
— capture both ids).

**Stop rule — never invent a roster:** if `GET /accounts/id` resolves to an
`agent+…@recoupable.com` email, or `organizations` and `artists` both return `[]`,
it's a throwaway key — say so and ask for a real-account key (or
recoup-platform-connect-account). Don't fabricate an artist/roster to keep moving.

## Docs map (pull the section you need; don't guess paths)

Account & Identity · Artists & Content · Research (Songstats + Web) · Social
Integrations · Chat & Agents · Developer/Infra. Find the exact path/params by
grepping `llms-full.txt` or pulling the OpenAPI JSON for the area, e.g.:

```bash
curl -s https://developers.recoupable.com/llms-full.txt | grep -A 30 -i "similar artists"
curl -s https://developers.recoupable.com/api-reference/openapi/research.json | jq '.paths | keys'
```

Removed in the Songstats migration (return 404 — don't call): `discover`, `rank`,
listener `cities`, `charts`, `playlist` (singular), `venues`, `radio`,
`festivals`, `genres`, `curator`. Geography comes from `audience`; discovery from
`similar` + `web`.

## Connector actions (Google Docs/Sheets/Drive, Gmail, TikTok, Instagram)

For reads/writes **outside** Recoup:
- `GET /connectors/actions` — catalog (each action's `slug`, `parameters`
  schema, `connectorSlug`, `isConnected`).
- `POST /connectors/actions` `{actionSlug, parameters}` — execute one.

Slugs are `UPPERCASE_SNAKE_CASE` (e.g. `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN`,
`GMAIL_FETCH_EMAILS`). **Always pull the parameters schema from the catalog before
executing** — shapes vary per action. Trigger heuristic: a pasted
`docs.google.com`/`drive.google.com`/`sheets.google.com` URL, or "edit this doc",
"send an email", "post on TikTok".

## Troubleshooting

401 = token missing/expired (check the credential). 403 = no access to the
org/artist. 404 = re-check the Docs map (endpoint moved/renamed). 5xx = retry once,
then surface the status.

## When NOT to use

- Files inside the sandbox → filesystem tools.
- Onboarding/operating an artist's workspace → the recoup-roster-* skills.
- A domain task (research/content/release/deal/song) → that domain skill, which
  makes its own calls.
