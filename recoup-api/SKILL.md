---
name: recoup-api
description: Call the Recoupable API from the sandbox to fetch artist data, socials, organizations, reports, and any other platform resource. Use whenever the user asks for Recoup data or any Recoupable platform resource. Triggers on phrases like "look up artist", "fetch from recoup", "artist data", "artist socials", "organizations", "artist report", or whenever the user references a specific artist, org, or campaign that lives in the Recoupable platform. Always load this before writing curl calls against recoup-api.vercel.app or developers.recoupable.com.
---

# Recoupable API

Call the Recoupable production API to fetch artist data, social metrics, org context, and trigger platform operations.

- **Base URL:** `https://recoup-api.vercel.app/api`
- **LLM-readable docs:** `https://developers.recoupable.com` (Mintlify — `/llms.txt` for the index, `/llms-full.txt` for full content)

## Always do this first

Endpoints change. Do **not** guess paths or response shapes from memory. Fetch the docs index before writing the request:

```bash
curl -s https://developers.recoupable.com/llms-full.txt | head -300
```

Skim for the endpoint that matches what the user asked for, then compose the request.

## Authentication

Your sandbox receives a short-lived Privy access token in the env var `RECOUP_ACCESS_TOKEN`. Use it as a `Bearer` token on every request:

```bash
curl -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  https://recoup-api.vercel.app/api/artists/{artistId}/socials
```

**If `RECOUP_ACCESS_TOKEN` is empty or unset**, the calling user is not authenticated — tell the user to sign in rather than retrying.

## Token lifetime — important

`RECOUP_ACCESS_TOKEN` is scoped to the current prompt only. It is injected per-command and dies when the prompt finishes.

- Do **not** persist it to disk, print it in assistant messages, or commit it to files the user can see.
- Do **not** launch detached/background processes that expect it — they will outlive the token.
- Between prompts, the sandbox has no Recoupable credential at all; the next prompt brings a fresh one.

## Typical request pattern

```bash
# 1. Check what endpoints exist
curl -s https://developers.recoupable.com/llms-full.txt | head -300

# 2. Make the call with the Bearer token
curl -sS -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  "https://recoup-api.vercel.app/api/<endpoint>?<params>" | jq
```

Use `jq` (preinstalled in the sandbox) to parse JSON responses.

## Troubleshooting

| Error | Meaning | Fix |
|-------|---------|-----|
| 401 | Token missing, invalid, or expired | Check `RECOUP_ACCESS_TOKEN` is set; if the prompt is long the token may have expired — ask the user to resend |
| 403 | User lacks access to the resource | Confirm the user has permission for the org/artist being queried |
| 404 | Endpoint not found | Re-fetch `/llms-full.txt` — the endpoint may have moved or been renamed |
| 5xx | Server error | Retry once; if persistent, surface the status to the user |

## When NOT to use this skill

- Reading or writing files inside the sandbox — use the filesystem tools.
- Calling Chartmetric, Spotify, or other third-party music APIs — those live in other skills (e.g. `chartmetric`).
- Reading the user's own git repo contents — that's already mounted in the working directory.
