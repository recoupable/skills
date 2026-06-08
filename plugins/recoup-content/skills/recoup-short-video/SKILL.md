---
name: recoup-short-video
description: End-to-end async run that produces a 9:16 social-ready short-form music video (TikTok/Reel/Short) featuring an artist and their song. Use whenever the user types `/recoup-short-video`, says "make a video for [artist]", "create a TikTok for [artist]", "produce a Reel for [artist]", "kick off content for [artist]", or any front-door request to generate a finished short-form clip for an existing artist. Resolves the artist's `account_id`, fires `POST /api/content/create`, polls `/api/tasks/runs` until terminal, and lands the user on the final video URL + caption. The default front door for the recoup-content plugin.
argument-hint: <artist-name> [--template <template-name>]
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# Recoup Short Video

The anchor skill for the recoup-content plugin. Use this on first install to confirm the plugin works end-to-end, and as the default front door for "make a video for [artist]" requests.

This skill is **user-invoked** — the user types `/recoup-short-video <artist-name>` and the harness invokes it with `$ARGUMENTS` populated. It is self-contained: the default async path below runs without any other skill. For granular control (swapping a single stage), it points to the `short-video` skill in the Recoupable skills library.

## Arguments

The user invoked this with: `$ARGUMENTS`

Expected shape: `<artist-name> [--template <template-name>]`

- **`<artist-name>`** — the artist to generate content for. Required. If the user didn't supply one, AskUserQuestion to collect it.
- **`--template <name>`** — optional. Defaults to `artist-caption-bedroom`. Override based on user cue ("with the album cover" → `album-record-store`, etc.).

## Required environment

- `RECOUP_API_KEY` set in the shell environment, OR a Privy access token if running inside chat (pass it as `-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"` instead of `x-api-key`).
- An artist record already exists for the requested artist on the user's first org. If not, run the `recoup-create-artist` skill (Recoupable skills library) first.

## What it does

1. Resolves the artist's `account_id` (from artist name + the user's first org).
2. Picks a template (defaults to `artist-caption-bedroom` if not supplied).
3. Fires `POST /api/content/create` to start the async pipeline server-side.
4. Polls `/api/tasks/runs?runId={runId}` every ~10 seconds until status is `COMPLETED`, `FAILED`, `CANCELED`, or `CRASHED`.
5. Reads the run output: `videoSourceUrl`, `imageUrl`, `captionText`, `template`, `lipsync`, and the audio metadata.
6. Lands the user on the final video URL with the caption text printed below it.

The async pipeline is the agent-safe path — synchronous calls to `/api/content/video` routinely take 60–180 seconds and time out inside most agent shells.

## Template looks (studio / stage / bedroom / …)

The artist's *look* is the **template** — same video job, different aesthetic preset. Don't
make a separate request type per vibe; pick a template. Known looks:

| Look | Template |
| --- | --- |
| Bedroom / intimate | `artist-caption-bedroom` |
| On stage / performance | `artist-caption-stage` |
| Outside / street | `artist-caption-outside` |
| Album in a record store | `album-record-store` |

Templates evolve — list the live set rather than trusting this table:

```bash
curl -sS "${AUTH[@]}" "https://api.recoupable.com/api/content/templates" \
  | jq -r '.templates[] | "\(.id) — \(.description)"'
```

Pick from the user's cue ("on stage" → `artist-caption-stage`, "with the album cover" →
`album-record-store`); default `artist-caption-bedroom`. Full details:
`references/content-api.md`.

## Context vs generic mode

- **Context mode** (artist named, workspace exists): pull the reference image from
  `context/images/face-guide.png` and aesthetic from `context/artist.md`; resolve the song
  from the workspace. See `references/workspace-context.md`.
- **Generic mode** (no artist context wanted): the user supplies the reference image,
  prompt, and audio directly — run the same pipeline without artist context. Don't force a
  workspace.

## Steps the agent must execute

### 1. Resolve the artist's `account_id`

```bash
ORG_ID=$(curl -sS "https://api.recoupable.com/api/organizations" \
  -H "x-api-key: $RECOUP_API_KEY" | jq -r '.organizations[0].id')

ARTIST_ACCOUNT_ID=$(curl -sS "https://api.recoupable.com/api/artists?org_id=$ORG_ID" \
  -H "x-api-key: $RECOUP_API_KEY" \
  | jq -r --arg name "$ARTIST_NAME" '.artists[] | select(.name == $name) | .account_id')
```

Use **`account_id`**, not `id` — `id` is the artist row's primary key, `account_id` is the underlying account that owns it. Passing the wrong one returns a 404 from `/api/content/create`. If no match, the artist record doesn't exist yet — run the `recoup-create-artist` skill first.

### 2. Trigger the async pipeline

```bash
TEMPLATE="${TEMPLATE:-artist-caption-bedroom}"

RUN_IDS=$(curl -sS -X POST "https://api.recoupable.com/api/content/create" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --arg artist "$ARTIST_ACCOUNT_ID" --arg template "$TEMPLATE" \
        '{artist_account_id: $artist, template: $template}')" \
  | jq -r '.runIds[]')
RUN_ID=$(echo "$RUN_IDS" | head -1)
```

### 3. Poll until terminal

```bash
until STATUS=$(curl -sS "https://api.recoupable.com/api/tasks/runs?runId=$RUN_ID" \
                 -H "x-api-key: $RECOUP_API_KEY" \
               | jq -r '.runs[0].status') && \
      [[ "$STATUS" =~ ^(COMPLETED|FAILED|CANCELED|CRASHED)$ ]]; do
  sleep 10
done
```

### 4. Read the output and land the user

```bash
curl -sS "https://api.recoupable.com/api/tasks/runs?runId=$RUN_ID" \
  -H "x-api-key: $RECOUP_API_KEY" \
  | jq '.runs[0].output'
# -> { videoSourceUrl, imageUrl, captionText, template, lipsync, audio: {...} }
```

See [Tasks Runs](https://developers.recoupable.com/api-reference/tasks/runs) for the full status enum and the `CreateContentRunOutput` schema.

## What "complete" looks like

The command finishes when:

- The poll loop has seen a terminal status (`COMPLETED` is the happy path).
- `output.videoSourceUrl` is a fetchable URL.
- `output.captionText` is a non-empty string.

Print both to the user. If status is `FAILED`, `CANCELED`, or `CRASHED`, surface the error from `runs[0].error` and stop — don't claim success.

**Before claiming success, run the analyze gate.** The agent can't see pixels — verify the
render isn't glitchy, empty, or off-brand via `references/analyze-gate.md` rather than
trusting a `COMPLETED` status alone.

For the underlying audio (lipsync templates), see `references/song-sourcing.md` — never
substitute a placeholder track.

## When to reach for the other skills

This async front door is the default. Use the underlying skills directly when:

- The user wants to **swap a single stage** (different caption length, different motion prompt, different reference image), inspect intermediate outputs, or supply their own audio. Use the **`short-video`** skill (Recoupable skills library) — its bundled manual covers the five-step recipe, and it explains resolving the underlying `song.mp3`.
- The user wants to **generate one capability in isolation** (just an image, just a caption). Use the **`content-creation`** skill (Recoupable skills library).
- The artist **doesn't exist yet**. Use the **`recoup-create-artist`** skill (Recoupable skills library) first.

## References

Shared building blocks (ship alongside this skill):

- `references/content-api.md` — endpoints, the 6 video modes, templates, async create→poll.
- `references/account-resolver.md` — auth modes + `account_id` vs row `id`.
- `references/workspace-context.md` — context vs generic mode; read context, write back.
- `references/song-sourcing.md` — sourcing the song audio (no placeholders).
- `references/analyze-gate.md` — verify the render before claiming done.
