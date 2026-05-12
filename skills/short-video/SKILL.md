---
name: short-video
description: End-to-end playbook for producing a vertical, social-ready short-form music video (image + motion + caption + composed final) from an artist and a song. Use when the user asks to make a video, generate content for an artist, create a TikTok or Reel, produce a music-video clip, or kick off the content pipeline — phrases like "make a video about", "generate content for", "create a TikTok", "kick off a video for X", "short-form video", or "music video for $ARTIST". The skill has two paths: an async pipeline (`POST /api/content/create` + poll `/api/tasks/runs`) for short-shell agents, and a manual five-step recipe (template → image → video → caption → ffmpeg compose) when you want to swap a single stage.
---

# Short Video

The canonical recipe used internally by Recoup's `create-content` background task. Follow it to produce a 9:16 music-video clip from an existing artist + song, ready to post.

Two paths are documented below: the **async pipeline** that an LLM agent should use, and the **manual walkthrough** for humans (or for cases where you want to swap a single step).

## Running as an agent? Use the async pipeline

`POST /api/content/video` is synchronous and routinely takes 60–180s. Most agent shells (Claude Cowork, OpenAI tool calls, etc.) cap a single command at 30–60s and kill background processes when the shell exits. The manual walkthrough below is effectively un-runnable from those environments.

Use the async path instead. Same five steps, run server-side:

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

Polling fits inside short shell timeouts and survives session restarts. See [Tasks Runs](https://developers.recoupable.com/api-reference/tasks/runs) for the full status enum (`QUEUED`, `EXECUTING`, `COMPLETED`, `FAILED`, `CANCELED`, `CRASHED`, etc.) and the `CreateContentRunOutput` schema.

### Resolving `$ARTIST_ACCOUNT_ID`

`POST /api/content/create` needs the artist's `account_id`. Three calls:

```bash
ORG_ID=$(curl -sS "https://api.recoupable.com/api/organizations" \
  -H "x-api-key: $RECOUP_API_KEY" | jq -r '.organizations[0].id')

ARTIST_ACCOUNT_ID=$(curl -sS "https://api.recoupable.com/api/artists?org_id=$ORG_ID" \
  -H "x-api-key: $RECOUP_API_KEY" \
  | jq -r --arg name "$ARTIST_NAME" '.artists[] | select(.name == $name) | .account_id')
```

The artist record exposes both `id` and `account_id` (both UUIDs). Use **`account_id`**. `id` is the artist row's primary key, `account_id` is the underlying account that owns it. The two are easy to swap; you'll get a 404 from `/api/content/create` if you pass the wrong one.

## Where the song lives

Step 5 (and the async pipeline's lipsync mode) need a `song.mp3`. **Don't assume one exists, and don't assume the user has one locally.** Walk the agent through this fallback chain:

1. **Check the artist's sandbox repo first.** Each Recoup account has a backing GitHub repo. If the user has imported songs through Recoup, they live at predictable paths:

   ```
   .openclaw/workspace/orgs/{org-slug}/artists/{artist-slug}/songs/{song-slug}/{song-slug}.mp3
                                                                               /lyrics.json
                                                                               /clips.json
   ```

   Discover the repo with `GET /api/sandboxes` (returns `github_repo` and a `filetree`); fetch a file with `GET /api/sandboxes/file?path=…`. **Binary files (`.mp3`, `.png`, `.mp4`) come back base64-encoded in the `content` field. Decode before writing to disk.**

2. **If no song is in the sandbox, ask the user how to proceed.** Two options to offer:
   - *"Want me to fetch the audio from YouTube?"* The agent downloads via `yt-dlp` (or equivalent), saves locally; user is responsible for any rights / DSP-licensing implications.
   - *"Want to supply the song yourself?"* User uploads / drops a path; agent reads from there.

   Don't pick a path silently. The cost of fetching the wrong song from YouTube (or fetching one at all) is enough that the user should make the call.

3. **Don't fall back to "use a placeholder track."** A music video without the song is not a deliverable.

## Manual walkthrough (humans + targeted overrides)

The rest of this skill walks the same steps you can run by hand or call individually if you want to swap a single stage (different prompt for image, different motion, different caption length).

### Prerequisites

- An auth credential for `api.recoupable.com`. Two options. Pick one and use it for every call below:
  - **API key** (`recoup_sk_…`, recommended for sandbox / agent use): pass as `-H "x-api-key: $RECOUP_API_KEY"`.
    - One-shot agent: `POST /api/agents/signup` with an `agent+{unique}@recoupable.com` email returns the key immediately.
    - Real-email signup: same endpoint with a real email mails a 6-digit code; complete with `POST /api/agents/verify`. See [Agents](https://developers.recoupable.com/agents).
  - **Privy access token** (for end-user flows in chat/UI): pass as `-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"`.
  - The examples below use `x-api-key`. Substitute `Authorization: Bearer …` if you're using a Privy token.
- `$ARTIST_NAME`, `$SONG_TITLE`, `$SONG_LYRICS_CLIP` (a 1–2 sentence mood snippet)
- `$REFERENCE_IMAGE_URL` *(optional)*: an artist photo or album cover to seed the image. If your template's purpose is "show this exact image" (e.g. `album-record-store`), set this and skip image generation in step 2.
- A `song.mp3` for step 5. **Don't ask the user for a local file.** Fetch from the artist's repo via `/api/sandboxes/file`.
- `ffmpeg` installed locally for step 5

### Step 0: Scaffold the workspace BEFORE any API call

The `VIDEO.md` checklist *is* the workflow state. Tick boxes and persist values back to the frontmatter as you go. To resume later, find the first unchecked box.

```bash
VIDEO_SLUG=$(echo "$SONG_TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-//; s/-$//')
VIDEO_DIR="videos/$VIDEO_SLUG"
mkdir -p "$VIDEO_DIR"

cat > "$VIDEO_DIR/VIDEO.md" <<EOF
---
artistName: $ARTIST_NAME
songTitle: $SONG_TITLE
template:
imageUrl:
videoUrl:
captionText:
finalVideoPath:
---

# $SONG_TITLE: $ARTIST_NAME

## Pipeline checklist

- [ ] 1. Pick template (\`GET /api/content/templates\` + detail). Capture \`template\`.
- [ ] 2. Generate the base image (\`POST /api/content/image\`). Capture \`imageUrl\`.
  - [ ] 2a. (Optional) Upscale image (\`POST /api/content/upscale\` with \`type: "image"\`).
- [ ] 3. Generate the video (\`POST /api/content/video\`). Capture \`videoUrl\`.
  - [ ] 3a. (Optional) Upscale video (\`POST /api/content/upscale\` with \`type: "video"\`).
- [ ] 4. Generate the caption (\`POST /api/content/caption\`). Capture \`captionText\`.
- [ ] 5. Compose 9:16 final with audio + caption (local \`ffmpeg\`). Capture \`finalVideoPath\`.

## Notes
EOF
```

### Step 1: Pick a template (required: list **and** detail)

Templates carry the prompt, reference images, and styling that drive the rest of the chain. You can't write a good Step 2 prompt without them. List, pick, then fetch detail:

```bash
curl -sS "https://api.recoupable.com/api/content/templates" \
  -H "x-api-key: $RECOUP_API_KEY" \
  | jq -r '.templates[] | "\(.id): \(.description)"'

TEMPLATE="album-record-store"   # or artist-caption-{bedroom,outside,stage}

TEMPLATE_DETAIL=$(curl -sS "https://api.recoupable.com/api/content/templates/$TEMPLATE" \
  -H "x-api-key: $RECOUP_API_KEY")
```

**Templates that list "Requires: face image"** (e.g. `artist-caption-bedroom`) will fall back to their bundled reference images and produce a generic-likeness subject if you don't supply one. They don't 400. Pass `$REFERENCE_IMAGE_URL` if you want the model to preserve a specific artist's likeness, or omit it for a stock-feeling result.

See [List Templates](https://developers.recoupable.com/api-reference/content/templates) and [Template Detail](https://developers.recoupable.com/api-reference/content/template-detail).

**After:** write `template` into frontmatter, tick the box.

### Step 2: Generate the base image

Use the template's own prompt and reference images. Don't write your own from scratch. The template encodes the visual style; freeform prompts almost always drift off-brand.

```bash
PROMPT=$(echo "$TEMPLATE_DETAIL" | jq -r '.image.prompt')
REFS=$(echo "$TEMPLATE_DETAIL" | jq -c '[.image.reference_images[]?]')
# $REFS is 5–15 URLs depending on the template; pass all of them via images[]

IMAGE_URL=$(curl -sS -X POST "https://api.recoupable.com/api/content/image" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --arg prompt "$PROMPT" --argjson refs "$REFS" \
        --arg ref "$REFERENCE_IMAGE_URL" \
        '{prompt: $prompt, images: $refs} + (if $ref == "" then {} else {reference_image_url: $ref} end)')" \
  | jq -r '.imageUrl')
```

**Shortcut:** if `$REFERENCE_IMAGE_URL` is the exact image you want (e.g. an album cover for `album-record-store`, or a final editorial photo), set `IMAGE_URL=$REFERENCE_IMAGE_URL` and skip this call entirely.

**Avoid:** prompts that aim for a real artist's likeness. Veo (used in step 3) rejects celebrity-likeness images with a 422. Use the template's prompt as-is and let the reference images carry the style.

See [Generate Image](https://developers.recoupable.com/api-reference/content/generate-image).

**After:** write `imageUrl`, tick the box.

### Optional: Upscale (image or video)

Same endpoint for both, swap `type`. Skip if you don't need the resolution bump.

```bash
# Image (after step 2)
IMAGE_URL=$(curl -sS -X POST "https://api.recoupable.com/api/content/upscale" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --arg url "$IMAGE_URL" '{url: $url, type: "image"}')" \
  | jq -r '.url')

# Video (after step 3): same call, type: "video", reassign $VIDEO_URL
```

See [Upscale](https://developers.recoupable.com/api-reference/content/upscale).

### Step 3: Generate the video

Pass the image and a short motion prompt. For lipsync, also pass a presigned `audio_url` to a song clip and the model will animate the artist's mouth.

```bash
MOTION=$(echo "$TEMPLATE_DETAIL" | jq -r '.video.movements[0] // "Slow camera drift, subtle subject motion"')

VIDEO_URL=$(curl -sS --max-time 360 -X POST "https://api.recoupable.com/api/content/video" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --arg image "$IMAGE_URL" --arg prompt "$MOTION" \
        '{image_url: $image, prompt: $prompt, aspect_ratio: "9:16"}')" \
  | jq -r '.videoUrl')
```

This call routinely takes 60–180s. **From a short-shell agent, use the async pipeline at the top of this page instead.** From a long-lived shell, output is an 8s clip. Step 5 loops it to song length.

See [Generate Video](https://developers.recoupable.com/api-reference/content/generate-video).

**After:** write `videoUrl`, tick the box.

### Step 4: Generate the caption

```bash
TOPIC="Song: \"$SONG_TITLE\". Lyrics: \"$SONG_LYRICS_CLIP\". Artist: $ARTIST_NAME."

CAPTION_RESPONSE=$(curl -sS -X POST "https://api.recoupable.com/api/content/caption" \
  -H "x-api-key: $RECOUP_API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --arg topic "$TOPIC" --arg template "$TEMPLATE" \
        '{topic: $topic, template: $template, length: "short"}')")

CAPTION_TEXT=$(echo "$CAPTION_RESPONSE"     | jq -r '.content')
CAPTION_FONT=$(echo "$CAPTION_RESPONSE"     | jq -r '.font          // "/System/Library/Fonts/Helvetica.ttc"')
CAPTION_COLOR=$(echo "$CAPTION_RESPONSE"    | jq -r '.color         // "white"')
CAPTION_STROKE=$(echo "$CAPTION_RESPONSE"   | jq -r '.borderColor   // "black"')
CAPTION_FONT_SIZE=$(echo "$CAPTION_RESPONSE" | jq -r '.maxFontSize  // 48')
```

`length` accepts `"short"` (default), `"medium"`, `"long"`, or `"none"` to skip. The four styling fields (`font`, `color`, `borderColor`, `maxFontSize`) are template-driven hints. Step 5 wires them into ffmpeg's `drawtext` so the burned-in caption matches the template's brand.

See [Generate Caption](https://developers.recoupable.com/api-reference/content/generate-caption).

**After:** write `captionText`, tick the box.

### Step 5: Compose the final 9:16 video (local)

The API returns a 16:9 motion clip. Compose locally: crop to 9:16, overlay the song audio for the full duration, and burn in the caption with the styling from step 4.

```bash
curl -sS -o "$VIDEO_DIR/clip.mp4" "$VIDEO_URL"
SONG_PATH="$VIDEO_DIR/song.mp3"           # see "Where the song lives" above
FINAL_PATH="$VIDEO_DIR/final.mp4"

# Write caption to a file. drawtext reads it via textfile=, sidestepping shell-escaping (apostrophes, etc.)
echo -n "$CAPTION_TEXT" > "$VIDEO_DIR/caption.txt"

# Single-line filter graph: newlines inside -filter_complex are literal characters and break the [v] label
ffmpeg -y \
  -stream_loop -1 -i "$VIDEO_DIR/clip.mp4" \
  -i "$SONG_PATH" \
  -filter_complex "[0:v]crop=ih*9/16:ih,scale=1080:1920,drawtext=fontfile=$CAPTION_FONT:textfile=$VIDEO_DIR/caption.txt:fontcolor=$CAPTION_COLOR:fontsize=$CAPTION_FONT_SIZE:x=(w-text_w)/2:y=h-text_h-120:box=1:boxcolor=$CAPTION_STROKE@0.5:boxborderw=20[v]" \
  -map "[v]" -map "1:a" \
  -shortest -c:v libx264 -c:a aac -pix_fmt yuv420p \
  "$FINAL_PATH"
```

**After:** write `finalVideoPath`, tick the box. With every box ticked, the music video is complete.

---

The checklist is the source of truth. If a box isn't ticked, treat the step as not run.
