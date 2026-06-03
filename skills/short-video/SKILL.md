---
name: short-video
description: End-to-end playbook for producing a vertical, social-ready short-form music video (image + motion + caption + composed final) from an artist and a song. Use when the user asks to make a video, generate content for an artist, create a TikTok or Reel, produce a music-video clip, or kick off the content pipeline — phrases like "make a video about", "generate content for", "create a TikTok", "kick off a video for X", "short-form video", or "music video for $ARTIST". The skill has two paths: an async pipeline (`POST /api/content/create` + poll `/api/tasks/runs`) for short-shell agents (preferred), and a manual five-step recipe in `references/short-video-manual.md` when you want to swap a single stage.
---

# Short Video

The canonical recipe used internally by Recoup's `create-content` background task. Produces a 9:16 music-video clip from an existing artist + song, ready to post.

## Two paths

| Path | When to use | Where it lives |
|---|---|---|
| **Async pipeline** | Default for agents — fires server-side and polls. Survives short shell timeouts. | This file (below). |
| **Manual walkthrough** | Humans or long-lived shells that want explicit control over a single step (different caption length, different motion, different audio). | `references/short-video-manual.md` |

For sourcing the underlying `song.mp3`, see `references/song-sourcing.md` — it covers the sandbox-repo → YouTube → user-supplied fallback chain. **Do not silently default to a placeholder track.**

## Async pipeline (preferred for agents)

`POST /api/content/video` is synchronous and routinely takes 60–180s. Most agent shells (Claude Cowork, OpenAI tool calls, etc.) cap a single command at 30–60s and kill background processes when the shell exits. The manual walkthrough is effectively un-runnable from those environments. Use the async path instead — same five steps, run server-side.

```bash
# Trigger
RUN_IDS=$(curl -sS -X POST "https://api.recoupable.com/api/content/create" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --arg artist "$ARTIST_ACCOUNT_ID" --arg template "$TEMPLATE" \
        '{artist_account_id: $artist, template: $template}')" \
  | jq -r '.runIds[]')

# Poll (every ~10s) until COMPLETED / FAILED / CANCELED / CRASHED
RUN_ID=$(echo "$RUN_IDS" | head -1)
until STATUS=$(curl -sS "https://api.recoupable.com/api/tasks/runs?runId=$RUN_ID" \
                 -H "x-api-key: $RECOUP_API_KEY" \
               | jq -r '.runs[0].status') && \
      [[ "$STATUS" =~ ^(COMPLETED|FAILED|CANCELED|CRASHED)$ ]]; do
  sleep 10
done

# Read the output
curl -sS "https://api.recoupable.com/api/tasks/runs?runId=$RUN_ID" \
  -H "x-api-key: $RECOUP_API_KEY" \
  | jq '.runs[0].output'
# -> { videoSourceUrl, imageUrl, captionText, template, lipsync, audio: {...} }
```

See [Tasks Runs](https://developers.recoupable.com/api-reference/tasks/runs) for the full status enum and the `CreateContentRunOutput` schema.

### Resolving `$ARTIST_ACCOUNT_ID`

`POST /api/content/create` needs the artist's `account_id`. Three calls:

```bash
ORG_ID=$(curl -sS "https://api.recoupable.com/api/organizations" \
  -H "x-api-key: $RECOUP_API_KEY" | jq -r '.organizations[0].id')

ARTIST_ACCOUNT_ID=$(curl -sS "https://api.recoupable.com/api/artists?org_id=$ORG_ID" \
  -H "x-api-key: $RECOUP_API_KEY" \
  | jq -r --arg name "$ARTIST_NAME" '.artists[] | select(.name == $name) | .account_id')
```

The artist record exposes both `id` and `account_id` (both UUIDs). Use **`account_id`** — `id` is the artist row's primary key, `account_id` is the underlying account that owns it. The two are easy to swap; you'll get a 404 from `/api/content/create` if you pass the wrong one.

## When the agent should reach for the manual walkthrough

The async pipeline produces a finished video with sensible defaults. Switch to `references/short-video-manual.md` when:

- The user wants a **different caption length** than the template default.
- The user supplies their own **reference image** and wants to skip generation.
- The user wants to **swap the audio** with a specific clip rather than the song from the sandbox.
- The user wants to **inspect intermediate outputs** (the raw image, the un-composed 16:9 clip) before composition.

The manual walkthrough is the same five steps, run individually. It is significantly slower in short shells — use it only when the async pipeline's defaults don't fit.
