---
name: getting-started
description: Set up Recoupable from scratch — get an API key, verify it, and make your first call via REST or MCP. Use this skill when the user says "set up Recoupable", "install Recoup", "get an API key", "connect to Recoup", "use Recoupable", "onboard to Recoup", "how do I start", or when an agent needs to configure itself to use the Recoupable platform.
---

# Getting Started with Recoupable

From zero to your first API call in under 2 minutes. Two steps: authenticate, call. No install needed — everything is HTTP.

- **Base URL:** `https://recoup-api.vercel.app/api`
- **MCP URL:** `https://recoup-api.vercel.app/mcp`
- **Auth header (REST):** `x-api-key: YOUR_RECOUP_API_KEY`
- **Auth header (MCP):** `Authorization: Bearer YOUR_RECOUP_API_KEY`
- **Full docs:** <https://developers.recoupable.com>

## Step 1 — Get an API key

Two paths depending on who is doing this.

### Path A: Agent (instant, no verification)

POST to the signup endpoint with an `agent+` email. The key comes back immediately and is exported for the rest of the session.

```bash
export RECOUP_API_KEY=$(curl -s -X POST "https://recoup-api.vercel.app/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "agent+'$(date +%s)-$RANDOM'@recoupable.com"}' | jq -r .api_key)
```

The `agent+{unique}@recoupable.com` pattern always returns a key with no verification step. Combining `$(date +%s)` with `$RANDOM` guarantees a unique address.

### Path B: Human (email verification)

If the user has an existing account or wants to use their own email:

```bash
curl -X POST "https://recoup-api.vercel.app/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

This sends a verification code to the user's email. Ask the user for the code, then:

```bash
curl -X POST "https://recoup-api.vercel.app/api/agents/verify" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'
```

The response contains the `api_key`.

### Path C: Dashboard (humans only, optional)

Prefer clicking over scripting? Create a key at [chat.recoupable.com/keys](https://chat.recoupable.com/keys).

1. Sign in
2. Enter a descriptive name (e.g. "Production Server")
3. Click **Create API Key** and copy it immediately — it's only shown once.

### Save the key

Add it to the shell profile so it survives new sessions:

```bash
echo 'export RECOUP_API_KEY="recoup_sk_..."' >> ~/.zshrc
source ~/.zshrc
```

## Step 2 — Verify it works

Hit the "whoami" endpoint. It echoes the account ID the key belongs to:

```bash
curl -s "https://recoup-api.vercel.app/api/accounts/id" \
  -H "x-api-key: $RECOUP_API_KEY"
```

A `200` with an `accountId` in the body means you're ready. `401` means the key is missing or wrong.

## First useful call — research any artist

Research runs entirely over REST. Everything sits under `/api/research/*`.

```bash
curl -s "https://recoup-api.vercel.app/api/research?q=Drake&type=artists&beta=true" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

That returns ranked matches with Chartmetric IDs. To get a full profile:

```bash
curl -s "https://recoup-api.vercel.app/api/research/profile?artist=Drake" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

For the full research surface — metrics, audience, cities, similar artists, playlists, charts, people search, deep research, URL extraction, structured enrichment — use the `music-industry-research` skill.

## Connect via MCP

For AI tools that speak MCP (Claude, Cursor, etc.), point them at the Recoup MCP server and pass the API key as a Bearer token:

```json
{
  "mcpServers": {
    "recoupable": {
      "url": "https://recoup-api.vercel.app/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_RECOUP_API_KEY"
      }
    }
  }
}
```

This gives the tool access to Recoup's MCP tools — sandbox execution, research, and more. See the [MCP docs](https://developers.recoupable.com/mcp) for the current tool list and schemas.

## Connect via REST API

Every endpoint follows the same pattern: `https://recoup-api.vercel.app/api/<resource>` with `x-api-key` for auth. A minimal REST client in any language:

```bash
curl -s "https://recoup-api.vercel.app/api/tasks" \
  -H "x-api-key: $RECOUP_API_KEY"
```

```python
import os, requests
headers = {"x-api-key": os.environ["RECOUP_API_KEY"]}
r = requests.get("https://recoup-api.vercel.app/api/tasks", headers=headers)
print(r.json())
```

```javascript
const r = await fetch("https://recoup-api.vercel.app/api/tasks", {
  headers: { "x-api-key": process.env.RECOUP_API_KEY },
});
console.log(await r.json());
```

Full reference (all resources, request/response shapes, auth rules): <https://developers.recoupable.com>

## Auth gotchas

- Use `x-api-key` for server-to-server, or `Authorization: Bearer <privy_jwt>` for frontend sessions via Privy. **Never both in the same request** — the API returns `401`.
- API keys are personal by default. If your account is in an organization, you can pass `account_id` on supported endpoints to access other accounts in that org.
- Keys are hashed (HMAC-SHA256) on save — if you lose the key, you rotate it, not recover it. Rotate at [chat.recoupable.com/keys](https://chat.recoupable.com/keys).

## What's next

After setup, use these skills for specific workflows:

| Skill | What it does |
| ----- | ------------ |
| music-industry-research | Deep artist analytics, people search, charts, competitive analysis, web intelligence |
| content-creation | Generate videos, images, captions from artist catalogs |
| release-management | Plan and execute release campaigns |
| setup-sandbox | Scaffold the workspace for an account's orgs and artists |
| streaming-growth | Grow artists past streaming milestones |
| songwriting | Structured songwriting using the 7 C's method |
| artist-workspace | Manage artist directories — context, songs, brand, audience |
