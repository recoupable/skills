---
name: getting-started
description: Set up Recoupable from scratch — install the CLI, get an API key, and make your first call. Use this skill when the user says "set up Recoupable", "install Recoup", "get an API key", "connect to Recoup", "use Recoupable", "onboard to Recoup", "how do I start", or when an agent needs to configure itself to use the Recoupable platform.
---

# Getting Started with Recoupable

From zero to your first API call in under 2 minutes. Three steps: install, authenticate, use.

## Step 1 — Install the CLI

```bash
npm install -g @recoupable/cli
```

Requires Node.js 18+. The CLI wraps the REST API with convenient commands.

## Step 2 — Get an API key

Two paths depending on who is doing this.

### Path A: Agent (instant, no verification)

POST to the signup endpoint with an `agent+` email. Key comes back immediately.

```bash
export RECOUP_API_KEY=$(curl -s -X POST "https://recoup-api.vercel.app/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "agent+'$(date +%s)-$RANDOM'@recoupable.com"}' | jq -r .api_key)
```

The `agent+{unique}@recoupable.com` pattern always returns a key with no verification step. Combining `$(date +%s)` with `$RANDOM` guarantees unique addresses.

### Path B: Human (email verification)

If the user has an existing account or wants to use their own email:

```bash
curl -X POST "https://recoup-api.vercel.app/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

This sends a verification code to their email. Ask the user for the code, then:

```bash
curl -X POST "https://recoup-api.vercel.app/api/agents/verify" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'
```

The response contains the `api_key`.

### Save the key

Add to shell profile so it persists:

```bash
echo 'export RECOUP_API_KEY="recoup_sk_..."' >> ~/.zshrc
source ~/.zshrc
```

## Step 3 — Verify it works

```bash
recoup whoami
```

Should print your account ID and email. If it does, you're ready.

## First useful command

Research any artist:

```bash
recoup research "Drake"
```

Returns structured data: streaming metrics, audience demographics, social traction, career history — pulled from 14 platforms.

## Connect via MCP

For AI tools that support MCP (Claude, Cursor, etc.):

- **URL:** `https://recoup-api.vercel.app/mcp`
- **Auth:** Bearer token — use your API key as the token

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

This gives your AI tool access to 40+ music intelligence tools.

## Connect via REST API

Base URL: `https://recoup-api.vercel.app/api`

Auth header: `x-api-key: YOUR_RECOUP_API_KEY`

```bash
curl "https://recoup-api.vercel.app/api/research?q=Drake" \
  -H "x-api-key: $RECOUP_API_KEY"
```

Full API reference: https://developers.recoupable.com

## What's next

After setup, use these skills for specific workflows:

| Skill | What it does |
|-------|-------------|
| content-creation | Generate videos, images, captions from artist catalogs |
| industry-research | Deep artist analytics, people search, competitive analysis |
| release-management | Plan and execute release campaigns |
| setup-sandbox | Scaffold workspace for an account's orgs and artists |
| streaming-growth | Grow artists past streaming milestones |
| songwriting | Structured songwriting using the 7 C's method |
