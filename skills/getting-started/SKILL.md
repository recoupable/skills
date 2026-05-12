---
name: getting-started
description: Onboard to Recoup — detect the user's auth + roster state, install the CLI and create an API key only when needed, then route the agent to the right next skill (`setup-sandbox`, `create-artist`, or `artist-workspace`). Use when the user says "set up Recoup", "install Recoup", "get an API key", "connect to Recoup", "onboard to Recoup", "use Recoup", "how do I start", "I'm new here", or any time the agent needs to bootstrap itself before doing Recoup work. Also use as the first skill in any conversation that starts from `developers.recoupable.com` or `chat.recoupable.com` and asks the agent to install plugins and skills.
---

# Getting Started with Recoup

This skill is the **onboarding orchestrator**. It detects where the user is in their Recoup journey, fills in the missing pieces (CLI install, API key, sandbox setup), and routes the agent to the right next skill for the user's actual work.

## How this skill flows

```text
Step 0  Detect environment + auth state (shell)
   │
   ├── auth missing  ──►  Step 1  Install CLI         (BYOA only)
   │                  ──►  Step 2  Get an API key
   │
   └── auth present  ──►  Step 3  Verify auth + identify the account
                       ──►  Step 4  Detect roster + filesystem state
                       ──►  Step 5  Route to the next skill
```

You can re-run this skill at any time — Steps 1-2 are skipped if the user is already authenticated.

---

## Step 0 — Detect environment and auth state

Run this in the shell first. The output decides which path you take.

```bash
echo "=== Environment ==="
[ -n "$RECOUP_ACCESS_TOKEN" ] && echo "RECOUP_ACCESS_TOKEN: set (sandbox)"  || echo "RECOUP_ACCESS_TOKEN: unset"
[ -n "$RECOUP_API_KEY" ]      && echo "RECOUP_API_KEY: set (BYOA)"          || echo "RECOUP_API_KEY: unset"
[ -n "$RECOUP_ACCOUNT_ID" ]   && echo "RECOUP_ACCOUNT_ID: $RECOUP_ACCOUNT_ID" || echo "RECOUP_ACCOUNT_ID: unset"
[ -n "$RECOUP_ORG_ID" ]       && echo "RECOUP_ORG_ID: $RECOUP_ORG_ID"       || echo "RECOUP_ORG_ID: unset"
echo
echo "=== Cached identity ==="
if [ -f ~/.config/recoup/account.json ]; then
  echo "~/.config/recoup/account.json: present ($(jq -r '.email // "unknown email"' ~/.config/recoup/account.json))"
else
  echo "~/.config/recoup/account.json: not present"
fi
echo
echo "=== CLI ==="
command -v recoup >/dev/null 2>&1 && recoup --version || echo "recoup CLI: not installed"
echo
echo "=== Workspace ==="
[ -d "artists" ] && echo "artists/ dir: exists ($(ls -d artists/*/ 2>/dev/null | wc -l | tr -d ' ') folders)" || echo "artists/ dir: not present"
[ -d "orgs" ]    && echo "orgs/ dir: exists ($(ls -d orgs/*/   2>/dev/null | wc -l | tr -d ' ') folders)"    || echo "orgs/ dir: not present"
```

Read the output:

- **`RECOUP_ACCESS_TOKEN` is set** → the user is in a Recoup-hosted sandbox. Skip Steps 1-2. Go to Step 3.
- **`RECOUP_API_KEY` is set** → the user is BYOA with a saved key. Skip Steps 1-2. Go to Step 3.
- **Neither set** → BYOA, first run. Continue to Step 1.

---

## Step 1 — Install the CLI (BYOA only)

```bash
npm install -g @recoupable/cli
```

Requires Node.js 18+. The CLI wraps the REST API.

If `command -v recoup` from Step 0 already showed a version, skip this step.

---

## Step 2 — Get an API key (BYOA only)

Two paths depending on who is doing this.

### Path A — Agent (instant, no email verification)

For agents bootstrapping their own throwaway account. Use this for demos, exploration, and testing — **never for creating real artist data** (see warning below).

```bash
RECOUP_EMAIL="agent+$(date +%s)-$RANDOM@recoupable.com"
SIGNUP_RESPONSE=$(curl -s -X POST "https://recoup-api.vercel.app/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg email "$RECOUP_EMAIL" '{email: $email}')")
export RECOUP_API_KEY=$(echo "$SIGNUP_RESPONSE" | jq -r .api_key)
RECOUP_ACCOUNT_ID=$(echo "$SIGNUP_RESPONSE" | jq -r .account_id)
```

The `agent+{unique}@recoupable.com` pattern returns a key immediately. The `$(date +%s)-$RANDOM` combination guarantees a unique email. The signup response also returns `account_id`, which we save to disk in the "Persist the key" step below.

> ⚠️ **`agent+` accounts are throwaway.** Any artists, releases, or notes created against them are permanently isolated to that account and unrecoverable if the API key is lost. Use Path B for any work you want to keep.

### Path B — Human (real account, email verification)

```bash
read -p "Email: " RECOUP_EMAIL
curl -X POST "https://recoup-api.vercel.app/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg email "$RECOUP_EMAIL" '{email: $email}')"
```

Ask the user for the verification code that was emailed:

```bash
read -p "Verification code: " RECOUP_CODE
VERIFY_RESPONSE=$(curl -s -X POST "https://recoup-api.vercel.app/api/agents/verify" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg email "$RECOUP_EMAIL" --arg code "$RECOUP_CODE" \
        '{email: $email, code: $code}')")
export RECOUP_API_KEY=$(echo "$VERIFY_RESPONSE" | jq -r .api_key)
RECOUP_ACCOUNT_ID=$(echo "$VERIFY_RESPONSE" | jq -r .account_id)
```

### Persist the key + account identity

So future shell sessions inherit `RECOUP_API_KEY`, and future runs of this skill can look up the account_id + email without re-signing-up:

```bash
# Persist API key into the user's shell init
echo 'export RECOUP_API_KEY="'$RECOUP_API_KEY'"' >> ~/.zshrc

# Persist account identity for future skill runs
mkdir -p ~/.config/recoup
jq -n --arg account_id "$RECOUP_ACCOUNT_ID" --arg email "$RECOUP_EMAIL" \
   '{account_id: $account_id, email: $email}' > ~/.config/recoup/account.json
```

(Use `~/.bashrc` instead of `~/.zshrc` on bash. On Windows / WSL, follow the platform's shell-init convention.)

---

## Step 3 — Verify auth + identify the account

This works whether the user is sandbox or BYOA. Use whichever auth header is set, then verify by hitting `/api/organizations` (any 200 response means the key is valid; the response body becomes our first piece of state for Step 4).

```bash
AUTH_HEADER=""
if [ -n "$RECOUP_ACCESS_TOKEN" ]; then
  AUTH_HEADER="Authorization: Bearer $RECOUP_ACCESS_TOKEN"
elif [ -n "$RECOUP_API_KEY" ]; then
  AUTH_HEADER="x-api-key: $RECOUP_API_KEY"
else
  echo "No Recoup auth found. Re-run Step 2."; exit 1
fi

# Verify auth by calling /organizations — succeeds (200) if the key works.
# We reuse the response body in Step 4 instead of fetching again.
HTTP=$(curl -sS -o /tmp/recoup-orgs.json -w "%{http_code}" \
  "https://recoup-api.vercel.app/api/organizations" -H "$AUTH_HEADER")

if [ "$HTTP" != "200" ]; then
  echo "Authentication failed (HTTP $HTTP). The API key/token is invalid or expired."
  echo "BYOA: re-run Step 2. Sandbox: refresh your sandbox session."
  exit 1
fi
echo "Authenticated."

# Recover account identity from local cache (saved in Step 2 for fresh signups,
# pre-injected by the sandbox for Recoup-hosted, or missing for returning agents).
RECOUP_ACCOUNT_ID="${RECOUP_ACCOUNT_ID:-}"   # sandbox-injected wins
RECOUP_EMAIL=""
if [ -z "$RECOUP_ACCOUNT_ID" ] && [ -f ~/.config/recoup/account.json ]; then
  RECOUP_ACCOUNT_ID=$(jq -r '.account_id // empty' ~/.config/recoup/account.json)
  RECOUP_EMAIL=$(jq -r '.email // empty' ~/.config/recoup/account.json)
fi

if [ -n "$RECOUP_EMAIL" ]; then
  echo "Account: $RECOUP_EMAIL (id: $RECOUP_ACCOUNT_ID)"
elif [ -n "$RECOUP_ACCOUNT_ID" ]; then
  echo "Account id: $RECOUP_ACCOUNT_ID (email unknown — returning agent)"
else
  echo "Account identity unknown — returning agent with no cached identity."
  echo "Proceeding with auth-only checks. /api/whoami would close this gap in the future."
fi
```

**Throwaway check.** If we have an email AND it matches `^agent\+.*@recoupable\.com$`, the user is on an agent throwaway account. Warn them once before doing anything that creates real data. **Skips silently when email is unknown** (returning agent without cached identity).

```bash
if [ -n "$RECOUP_EMAIL" ]; then
  case "$RECOUP_EMAIL" in
    agent+*@recoupable.com)
      echo "⚠️  You're on a throwaway agent account ($RECOUP_EMAIL)."
      echo "    Artist data created here is isolated and unrecoverable if the key is lost."
      echo "    Run Step 2 Path B with your real email if you want to keep this work."
      ;;
  esac
fi
```

---

## Step 4 — Detect roster + filesystem state

Use the orgs response already fetched in Step 3. Enumerate artists per org. Inspect the workspace filesystem.

```bash
# Platform side: orgs and artists (reusing the orgs payload from Step 3)
ORG_COUNT=$(jq '.organizations | length // 0' /tmp/recoup-orgs.json)
echo "Orgs on platform: $ORG_COUNT"

ARTIST_COUNT=0
if [ "$ORG_COUNT" -gt 0 ]; then
  for ORG_ID in $(jq -r '.organizations[].id' /tmp/recoup-orgs.json); do
    THIS_ORG_ARTISTS=$(curl -sS "https://recoup-api.vercel.app/api/organizations/$ORG_ID/artists" -H "$AUTH_HEADER" | jq '.artists | length // 0')
    ARTIST_COUNT=$((ARTIST_COUNT + THIS_ORG_ARTISTS))
  done
fi
echo "Artists on platform: $ARTIST_COUNT"

# Filesystem side: is the workspace scaffolded?
FS_STATE="empty"
if   [ -d "artists" ] && [ "$(ls -A artists 2>/dev/null)" ]; then FS_STATE="single-org-scaffolded"
elif [ -d "orgs"    ] && [ "$(ls -A orgs    2>/dev/null)" ]; then FS_STATE="multi-org-scaffolded"
fi
echo "Workspace filesystem: $FS_STATE"
```

You now know the state dimensions Step 5 routes from:

| Variable | Meaning |
| --- | --- |
| `$RECOUP_EMAIL` | Real user vs `agent+` throwaway vs unknown (returning agent) |
| `$ORG_COUNT` | How many organizations the account belongs to |
| `$ARTIST_COUNT` | Artists across all orgs the account can access |
| `$FS_STATE` | Whether the local/sandbox filesystem is scaffolded yet |

---

## Step 5 — Route to the next skill

Decide which skill the agent should load next. Match the **first** rule that applies, from top to bottom:

| If… | Then load skill | Why |
| --- | --- | --- |
| `$ORG_COUNT = 0` AND `$RECOUP_EMAIL` is a throwaway `agent+` | **`create-artist`** | Brand-new agent demo — create the first artist in the throwaway account. The chain will auto-create a default org. |
| `$ORG_COUNT = 0` AND `$RECOUP_EMAIL` is a real user | (ask the user) | A real user with no org is unusual. Ask: (a) Create an org at `https://chat.recoupable.com`, (b) Be invited to one — paste invite link, (c) Use a throwaway `agent+` account for this session. Don't auto-create. |
| `$ORG_COUNT = 0` AND `$RECOUP_EMAIL` is unknown (returning agent) | (ask the user) | Email isn't cached. Ask: (a) "Are you a real user? Go to `https://chat.recoupable.com` to create or join an org," (b) "Are you a throwaway agent? Let me create a default artist for you," (c) "Try Step 2 again with your real email to fix this." |
| `$ORG_COUNT > 0` AND `$ARTIST_COUNT = 0` | **`create-artist`** | They have an org but no artists yet. Walk them through onboarding their first artist. |
| `$ORG_COUNT > 0` AND `$ARTIST_COUNT > 0` AND `$FS_STATE = empty` AND the cwd looks like a sandbox (`RECOUP_ACCESS_TOKEN` was set, or `$HOME` is `/home/sandbox` or similar) | **`setup-sandbox`** | They have artists on the platform, but the sandbox filesystem isn't scaffolded yet. Build the folder tree from their roster. |
| `$ORG_COUNT > 0` AND `$ARTIST_COUNT > 0` AND `$FS_STATE = empty` AND BYOA (no sandbox markers) | **`artist-workspace`** | They have artists; the BYOA agent doesn't need a sandbox tree. Tell the user where the agent will read/write artist context. |
| `$FS_STATE = single-org-scaffolded` OR `$FS_STATE = multi-org-scaffolded` | **`artist-workspace`** | Everything is wired. Read the existing tree, list the artists the user has, and ask what they want to do. |

End your turn with a single-line summary the user can read:

```text
Onboarding complete: authenticated (<email-or-"identity unknown">), found <N> orgs and <M> artists, workspace state <FS_STATE>. Next: <skill-name>.
```

Then load the chosen skill from `recoup-skills` and continue the conversation. Do NOT silently begin doing work — confirm the goal first.

---

## What's next (after onboarding)

Once the user is set up, these skills handle specific workflows:

| Skill | What it does |
| --- | --- |
| `artist-workspace` | Manage artist directories, RECOUP.md files, brand/audience/songs |
| `create-artist` | End-to-end 8-step playbook for adding and enriching a new artist |
| `setup-sandbox` | Scaffold an empty sandbox from the account's orgs and artists |
| `release-management` | Plan and execute release campaigns |
| `chartmetric` | Music analytics — streaming, audience, playlists, charts |
| `content-creation` | Generate social videos, images, captions, lipsync clips |
| `music-industry-research` | Artist + people + competitive research via Recoup `/research/*` |
| `recoup-api` | Reference for calling the Recoup API directly |

For the catalog-diligence vertical (royalty audits, rights diligence, valuation), install the catalog plugin separately:

```bash
/plugin install music-catalog-diligence@recoup
```

## Connect via MCP (BYOA only)

If the agent supports MCP (Claude Code, Cursor, Codex), configure the Recoup MCP server so the agent can call Recoup tools natively:

```json
{
  "mcpServers": {
    "recoup": {
      "url": "https://recoup-api.vercel.app/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_RECOUP_API_KEY"
      }
    }
  }
}
```

Once connected, the agent has access to 40+ music intelligence tools without extra setup.

## API reference

Base URL: `https://recoup-api.vercel.app/api`
Docs: <https://developers.recoupable.com>
