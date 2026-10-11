# Content API (`/api/content/*`) — the building blocks

Every Recoup content skill is built on these endpoints. This is the shared contract:
endpoints, house video frame controls, templates, the async create→poll pattern, and cost
estimation. For auth + artist-ID resolution, use the account-resolver reference when the
skill bundles one; otherwise set the auth header inline (`x-api-key: $RECOUP_API_KEY`, or
`Authorization: Bearer $RECOUP_ACCESS_TOKEN`).

Select one REST credential before using these examples. Prefer a matching
authenticated MCP tool when available; MCP OAuth credentials stay in the host.

```bash
BASE="https://api.recoupable.dev/api"
if [ -n "$RECOUP_API_KEY" ]; then
  AUTH=(-H "x-api-key: $RECOUP_API_KEY")
elif [ -n "$RECOUP_ACCESS_TOKEN" ]; then
  AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN")
else
  echo "REST credentials unavailable; connect through the approved setup flow." >&2
  exit 1
fi
```

## Endpoints

| Capability | Call | Notes |
| --- | --- | --- |
| Generate image | `POST $BASE/content/image` | **sync** (~15–20s) → `{imageUrl, images[]}`. `{prompt, image_urls?, num_images?}` |
| Generate video | `POST $BASE/content/video` | House H3 returns **sync** `{videoUrl}`; integer `duration` 5–15, resolution `480P` or `768P`. May take 60–180s. |
| Generate caption | `POST $BASE/content/caption` | sync. `{topic, template?, length?}` → `{content, font, color, borderColor, maxFontSize}`. `length`=`short\|medium\|long\|none` |
| Transcribe audio | `POST $BASE/content/transcribe` | `{audio_urls:[…]}` (**array** of public audio URLs) → `{audioUrl, fullLyrics, segments:[{start,end,text}], segmentCount}` |
| Edit (trim/crop/overlay/mux) | `PATCH $BASE/content` | **async** → `runId`. Body: `{video_url, operations:[…]}` — see below |
| Upscale | `POST $BASE/content/upscale` | `{url, type}` where `type`=`image\|video` |
| Analyze video | `POST $BASE/content/analyze` | `{video_url, prompt}` → `{text}`. **Video only — rejects still images (400).** The agent's eyes; see the analyze-gate reference |
| List templates | `GET $BASE/content/templates` | id + description only |
| Template detail | `GET $BASE/content/templates/{id}` | full recipe (prompts, motion, caption style, edits) |
| Full pipeline | `POST $BASE/content/create` | async; `{artist_account_id, template?, images?, lipsync?, upscale?}` → `runIds` |
| Cost estimate | `GET $BASE/content/estimate` | **GET** (POST → 405). Returns `{per_video_estimate_usd, total_estimate_usd, batch}` |

> **Sync vs async (source contract; provider latency varies):** `image`, `caption`, and `video` return the
> asset **synchronously** in the response body. `PATCH /content` (edit) and `POST
> /content/create` are **async** → `runId`, polled via `/tasks/runs`. Don't assume everything
> is async — image/caption come straight back.

Full docs: `https://docs.recoupable.dev/content-agent`.

## Direct video, hosted presets and local composition

`POST /content/video` is the fixed MiniMax H3 Max primitive. Pass `prompt`, an optional
`image_url` first frame and `end_image_url` last frame. `duration` is an integer
5–15 (default 5), not a string such as `"8s"`; `resolution` is `480P` or `768P`
(default `768P`). `prompt_expansion_mode` defaults to `balanced`.

There is no `mode`, arbitrary `model`, `audio_url`, `video_url`, extend or reference-only
mode on this primitive. Unsupported fields must not be silently ignored before paid
work. For images, use `image_urls` (up to 10 unique references), not legacy `images` or
`reference_image_url`. The compatibility release translates those image aliases;
new image examples must use the current field. The hosted `/content/create` pipeline
retains its separate `images` input.

Hosted lipsync is retained: use `POST /content/create` with `lipsync: true`, then poll
its run. The coordinated API/worker repair restores selected-clip audio into the fixed
LTX audio-to-video path and checks for an audio stream before composition. Until that
release is deployed and a real output is inspected, do not claim the repaired journey
is verified. The dedicated `/content/lipsync` primitive is release-pending; do not assume
it exists on an older deployment.

Direct provider generation is a separate integration with its own credentials, model
contract and costs. Local ffmpeg trimming, cropping or muxing changes composition;
it cannot prove the hosted generator lip-synced a face. For a loop, use matching first
and last frames and inspect the seam. Crop to 9:16 through composition when necessary.

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

`POST /content/create` and `PATCH /content` (edit) return run ID(s) instead of the asset; poll
`/tasks/runs`. (`image`, `caption`, and video come back synchronously — no poll.)
Polling pattern for the async ones:

```bash
CREATED=$(curl --fail-with-body -sS -X POST "$BASE/content/create" "${AUTH[@]}" -H "Content-Type: application/json" \
  -d "$(jq -n --arg a "$ARTIST_ACCOUNT_ID" --arg t "$TEMPLATE" '{artist_account_id:$a, template:$t}')") || exit 1
RUN_ID=$(printf '%s' "$CREATED" | jq -er '.runIds[0]') || exit 1
printf 'Run ID: %s\n' "$RUN_ID"

for ATTEMPT in $(seq 1 60); do
  RUN=$(curl --fail-with-body -sS "${AUTH[@]}" "$BASE/tasks/runs?runId=$RUN_ID") || exit 1
  STATUS=$(printf '%s' "$RUN" | jq -er '.runs[0].status') || exit 1
  case "$STATUS" in
    COMPLETED) break ;;
    FAILED|CANCELED|CRASHED|SYSTEM_FAILURE|INTERRUPTED)
      printf '%s' "$RUN" | jq '.runs[0].error // {status: .runs[0].status}' >&2
      exit 1 ;;
  esac
  sleep 10
done
[ "$STATUS" = COMPLETED ] || { echo "Still pending: $RUN_ID"; exit 2; }

curl -sS "${AUTH[@]}" "$BASE/tasks/runs?runId=$RUN_ID" | jq '.runs[0].output'
# create → { videoSourceUrl, imageUrl, captionText, template, lipsync, audio: {...} }
```

On a non-`COMPLETED` terminal status, surface `.runs[0].error` and stop — never claim
success. See `https://docs.recoupable.dev/api-reference/tasks/runs`.

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

Generation costs credits (model-specific; the estimate endpoint is advisory and is not a price guarantee). For multi-asset runs (packs,
per-track fan-outs) call `GET $BASE/content/estimate` and confirm with the user before fanning
out. On a 402 / `insufficient_credits`, surface the `billingUrl` — don't silently retry.
