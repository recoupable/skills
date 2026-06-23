# Content API (`/api/content/*`) — the building blocks

Every Recoup content skill is built on these endpoints. This is the shared contract:
endpoints, the six video modes, templates, the async create→poll pattern, and cost
estimation. For auth + artist-ID resolution, use the account-resolver reference when the
skill bundles one; otherwise set the auth header inline (`x-api-key: $RECOUP_API_KEY`, or
`Authorization: Bearer $RECOUP_ACCESS_TOKEN`).

> This file ships inside the skill that reads it. It is a byte-identical vendored copy of
> the canonical `plugins/recoup-records/references/content-api.md`; edit the canonical and
> re-sync (see `scripts/vendored.json`).

`BASE="https://api.recoupable.com/api"`. Pass the auth header from `account-resolver.md`
as `"${AUTH[@]}"` on every call.

## Endpoints

| Capability | Call | Notes |
| --- | --- | --- |
| Generate image | `POST $BASE/content/image` | **sync** (~15–20s) → `{imageUrl, images[]}`. `{prompt, reference_image_url?}` |
| Generate video | `POST $BASE/content/video` | 6 modes (below). `animate` returns **sync** `{videoUrl}`; `prompt` mode requires a `duration` enum. May take 60–180s. |
| Generate caption | `POST $BASE/content/caption` | sync. `{topic, template?, length?}` → `{content, font, color, borderColor, maxFontSize}`. `length`=`short\|medium\|long\|none` |
| Transcribe audio | `POST $BASE/content/transcribe` | `{audio_urls:[…]}` (**array** of public audio URLs) → `{audioUrl, fullLyrics, segments:[{start,end,text}], segmentCount}` |
| Edit (trim/crop/overlay/mux) | `PATCH $BASE/content` | **async** → `runId`. Body: `{video_url, operations:[…]}` — see below |
| Upscale | `POST $BASE/content/upscale` | `{url, type}` where `type`=`image\|video` |
| Analyze video | `POST $BASE/content/analyze` | `{video_url, prompt}` → `{text}`. **Video only — rejects still images (400).** The agent's eyes; see the analyze-gate reference |
| List templates | `GET $BASE/content/templates` | id + description only |
| Template detail | `GET $BASE/content/templates/{id}` | full recipe (prompts, motion, caption style, edits) |
| Full pipeline | `POST $BASE/content/create` | async; `{artist_account_id, template?, reference_image_url?, lipsync?, upscale?}` → `runIds` |
| Cost estimate | `GET $BASE/content/estimate` | **GET** (POST → 405). Returns `{per_video_estimate_usd, total_estimate_usd, batch}` |

> **Sync vs async (verified live):** `image`, `caption`, and `video` mode `animate` return the
> asset **synchronously** in the response body. `PATCH /content` (edit) and `POST
> /content/create` are **async** → `runId`, polled via `/tasks/runs`. Don't assume everything
> is async — image/caption come straight back.

Full docs: `https://developers.recoupable.com/content-agent`.

## The six video modes

Set `mode` explicitly (or omit to infer from inputs):

| Mode | What it does | Required inputs |
| --- | --- | --- |
| `prompt` | create from a text description | `prompt` **+ `duration`** |
| `animate` | bring a still image to life | `image_url` + `prompt` (returns sync `{videoUrl}`) |
| `reference` | use an image as style reference (not first frame) | `image_url` + prompt |
| `extend` | continue an existing clip (≤8s input) | video + prompt |
| `first-last` | transition between two images | image + end image + prompt |
| `lipsync` | sync a face to audio | image + audio |

`duration`, when accepted, must be one of the string enums **`"4s"`, `"6s"`, `"7s"`, `"8s"`**
(a bare integer like `8` is a 400). Output aspect ratio is **not guaranteed vertical** —
`animate` returned 16:9 in testing; crop to `9:16` with an edit op (below) for TikTok/Reels.

## Templates (the "looks")

Templates are optional creative presets — image prompts, motion, caption style, edits.
They change the **look**, never the job. Discover them; don't hardcode:

```bash
curl -sS "${AUTH[@]}" "$BASE/content/templates" | jq -r '.templates[] | "\(.id) — \(.description)"'
```

Known video looks include `artist-caption-bedroom`, `artist-caption-stage`,
`artist-caption-outside`, and `album-record-store`. Override priority: **your explicit
params > artist context > template defaults.**

**Auto-select by audio.** When you have the song's audio analysis (see the research-context
reference), let the song pick the look instead of guessing: high `energy` → motion/crowd
looks (`artist-caption-stage`); low `energy` → intimate looks (`artist-caption-bedroom`);
high `bpm` → faster cuts and shorter `trim_duration`. The song should drive the edit, not a
default.

## Async: create → poll (the agent-safe path)

`POST /content/create` and `PATCH /content` (edit) return a `runId` instead of the asset; poll
`/tasks/runs`. (`image`, `caption`, and video `animate` come back synchronously — no poll.)
Polling pattern for the async ones:

```bash
RUN_IDS=$(curl -sS -X POST "$BASE/content/create" "${AUTH[@]}" -H "Content-Type: application/json" \
  -d "$(jq -n --arg a "$ARTIST_ACCOUNT_ID" --arg t "$TEMPLATE" '{artist_account_id:$a, template:$t}')" \
  | jq -r '.runIds[]')
RUN_ID=$(echo "$RUN_IDS" | head -1)

until STATUS=$(curl -sS "${AUTH[@]}" "$BASE/tasks/runs?runId=$RUN_ID" | jq -r '.runs[0].status') && \
      [[ "$STATUS" =~ ^(COMPLETED|FAILED|CANCELED|CRASHED)$ ]]; do sleep 10; done

curl -sS "${AUTH[@]}" "$BASE/tasks/runs?runId=$RUN_ID" | jq '.runs[0].output'
# create → { videoSourceUrl, imageUrl, captionText, template, lipsync, audio: {...} }
```

On a non-`COMPLETED` terminal status, surface `.runs[0].error` and stop — never claim
success. See `https://developers.recoupable.com/api-reference/tasks/runs`.

## Edit operations (`PATCH $BASE/content`)

Body is `{video_url, operations:[…]}` (an **array** — an object 400s) and the response is async
(`{runId}` → poll `/tasks/runs`). Each operation is `{type, …}`:

```bash
curl -sS -X PATCH "$BASE/content" "${AUTH[@]}" -H "Content-Type: application/json" \
  -d '{"video_url":"https://…/clip.mp4","operations":[{"type":"crop","aspect":"9:16"}]}'
# → {"runId":"run_…","status":"triggered"}  then poll /tasks/runs?runId=…
```

| `type` | Fields | Use |
| --- | --- | --- |
| `crop` | `aspect` (e.g. `9:16`, `1:1`, `16:9`) | reframe per platform |
| `trim` | `start`, `duration` | cut a window |
| `overlay` | `text`, `color`, `position` | burn-in captions |
| `mux` | `audio_url` | add the song to a silent clip |

(Field names per op may vary; `crop`/`aspect` is verified. Probe with one op before fanning out.)

## Spend discipline

Generation costs credits (≈$0.82/video at batch 1, live). For multi-asset runs (packs,
per-track fan-outs) call `GET $BASE/content/estimate` and confirm with the user before fanning
out. On a 402 / `insufficient_credits`, surface the `checkoutUrl` — don't silently retry.
