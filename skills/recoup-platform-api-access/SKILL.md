---
name: recoup-platform-api-access
description: Call the Recoup API and external connectors directly — fetch any platform resource (artists, socials, organizations, research, documents) and run connector actions (Google Docs/Sheets/Drive edits, Gmail, TikTok, Instagram). Use whenever you need raw Recoup data, a platform resource, to write curl against api.recoupable.com, or to read/write something outside Recoup like a Google Doc URL or a spreadsheet. The plumbing every other skill rides on. To onboard or operate on an artist use the recoup-roster-* skills; for first-run connection use recoup-platform-connect-account.
---

# Recoup — API Access

The platform access layer: authenticate, talk to the Recoup REST API, and
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

Geography comes from `audience`; discovery from `similar` + `web`.

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

## Send an email (from Recoup)

`POST /api/emails` sends an email from `Agent by Recoup <agent@recoupable.com>` via
Recoup — works headless with your API key, no Gmail connector needed. Use it for
reports, alerts, and scheduled-task output.

**Send it by running this exact `curl` with the `bash` tool. Do NOT use `web_fetch`,
`fetch`, or any HTTP-request tool** — those omit the `$AUTH` header (→ 401) and
truncate the response so you can't confirm what was sent. Resolve auth **inline, in
the same command** (each shell is fresh, so an `AUTH` from an earlier step is gone):

```bash
AUTH=$([ -n "$RECOUP_API_KEY" ] && echo "x-api-key: $RECOUP_API_KEY" || echo "Authorization: Bearer $RECOUP_ACCESS_TOKEN")
curl -sS -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"to":["someone@example.com"],"subject":"Weekly report","text":"# Summary\n…"}' \
  "https://api.recoupable.com/api/emails"
# → {"success":true,"message":"Email sent successfully … to someone@example.com.","id":"<resend-id>"}
```

**Payload — follow exactly (weak models get these wrong):**
- `to` is a **JSON array of email strings**: `["a@b.com"]`. Never a bare string
  (`"a@b.com"` → 400), never objects (`[{"email": …}]`).
- The **only** valid keys are `to`, `cc`, `subject`, `text`, `html`, `chat_id`,
  `account_id`. **Do not invent keys** like `recipients` or `email` — unknown keys
  are silently dropped, and `to` then defaults to *your own* account email, so the
  message goes to the wrong person and still returns `200` (a silent misroute).
- `subject` is optional (defaults from the body); `text` (Markdown) or `html` is the
  body; `cc` is an array; `chat_id` adds a footer chat link.
- **After sending, read the JSON response:** confirm `"success": true` and that the
  `message` names the recipient *you intended* before reporting success.

The same `recoup_sk_` key authenticates over **either** `x-api-key` or
`Authorization: Bearer`, so the inline `AUTH` above works in any context (sandbox sets
`RECOUP_ACCESS_TOKEN`; a local user sets `RECOUP_API_KEY`). **Without a payment method
on file, `to`/`cc` are limited to the account's own email (403 otherwise).** To send
**as the user** from their own Gmail instead, use the `GMAIL_SEND_EMAIL` connector action.

## Troubleshooting

401 = token missing/expired (check the credential). 403 = no access to the
org/artist. 404 = re-check the Docs map (endpoint moved/renamed). 5xx = retry once,
then surface the status.

## When NOT to use

- Files inside the sandbox → filesystem tools.
- Onboarding/operating an artist's workspace → the recoup-roster-* skills.
- A domain task (research/content/release/deal/song) → that domain skill, which
  makes its own calls.
