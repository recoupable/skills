---
name: content-creation
description: Create content for artists and record labels — short-form videos, images, captions, lipsync clips, and more. Use when the user asks to create content, make a video, generate an image, produce a TikTok or Reel, create a promotional clip, add captions, or create visual content for an artist. Also use when iterating on content quality — regenerating images, trying different audio, adjusting text, or upscaling for higher quality.
---

# Content Creation

Create visual content for artists and record labels using the Recoup API. You can access every capability through either the CLI (`recoup content`) or the REST API (`/api/content/*`).

## What You Can Do

| Capability | CLI | API |
|------------|-----|-----|
| Generate image | `recoup content image` | `POST /api/content/image` |
| Generate video | `recoup content video` | `POST /api/content/video` |
| Generate caption | `recoup content caption` | `POST /api/content/caption` |
| Transcribe audio | `recoup content transcribe` | `POST /api/content/transcribe` |
| Edit (trim, crop, overlay, mux audio) | `recoup content edit` | `PATCH /api/content` |
| Upscale image or video | `recoup content upscale` | `POST /api/content/upscale` |
| Analyze video | `recoup content analyze` | `POST /api/content/analyze` |
| Full pipeline (one shot) | `recoup content create` | `POST /api/content/create` |

Image and video generation are async — they return a `runId`. Poll with `recoup tasks status --run {runId} --json` (or `GET /api/tasks/runs?runId={runId}`) until `status` is `COMPLETED`, then read `output`.

Full API docs: https://developers.recoupable.com/content-agent

## Video Modes

`generate-video` supports 6 modes. Set `--mode` (CLI) or `mode` (API) explicitly, or omit it and the mode is inferred from inputs.

| Mode | What it does | Required inputs |
|------|-------------|-----------------|
| `prompt` | Create from text description | prompt |
| `animate` | Animate a still image | image + prompt |
| `reference` | Use image as style reference (not first frame) | image + prompt |
| `extend` | Continue an existing video (max 8s input) | video + prompt |
| `first-last` | Transition between two images | image + end image + prompt |
| `lipsync` | Sync face movement to audio | image + audio |

### When to use which mode

- "I need a cinematic establishing shot" → `prompt`
- "I have a photo of the artist, make it come alive" → `animate`
- "I have a photo of the artist, put them in a new scene" → `reference`
- "This clip is great but too short" → `extend`
- "I want a smooth transition from the studio to the stage" → `first-last`
- "I need the face to sing along to this audio" → `lipsync`

## Templates

Templates are optional shortcuts — curated creative recipes that pre-fill prompts, reference images, style rules, and edit operations. Every capability works without a template.

List available templates:

```bash
recoup content templates --json
```

Or via API: `GET /api/content/templates`

### Override priority

When using a template, your explicit parameters always win:

1. **Your parameters** — highest priority
2. **Artist context** — if the artist has a style guide, it personalizes the template
3. **Template defaults** — lowest priority

## Workflow

### Step by step (full creative control)

```bash
# 1. Transcribe audio
recoup content transcribe --url {audioUrl} --json

# 2. Generate image
recoup content image --prompt "{scene description}" \
  --reference-image {referenceImageUrl} --json

# 3. (Optional) Upscale image
recoup content upscale --url {imageUrl} --type image --json

# 4. Generate video
recoup content video --mode animate --image {imageUrl} \
  --prompt "{how to animate}" --json

# 5. Generate caption
recoup content caption --topic "{topic}" --length short --json

# 6. Edit final video
recoup content edit --url {videoUrl} --audio {audioUrl} \
  --overlay-text "{caption}" --json

# 7. (Optional) Analyze the result
recoup content analyze --video {videoUrl} \
  --prompt "Rate this 1-10 for social media engagement" --json
```

### One-shot pipeline

When you just want a finished video without controlling each step:

```bash
recoup content create --artist {artistAccountId} --json
recoup content create --artist {artistAccountId} --template artist-caption-bedroom --lipsync --json
```

Or via API: `POST /api/content/create` with `{ "artist_account_id": "..." }`

### Lipsync

```bash
recoup content video --mode lipsync \
  --image {faceUrl} --audio {audioUrl} --json

recoup content edit --url {videoUrl} \
  --crop-aspect 9:16 --overlay-text "{caption}" --json
```

## Edit Operations

The edit command applies operations in a single processing pass:

| Operation | CLI flags | What it does |
|-----------|-----------|-------------|
| Trim | `--trim-start {s} --trim-duration {s}` | Cut a time window |
| Crop | `--crop-aspect {ratio}` | Crop to aspect ratio (e.g. 9:16) |
| Overlay text | `--overlay-text {text} --text-color {color} --text-position {pos}` | Add on-screen text |
| Mux audio | `--mux-audio {url}` | Add audio track to video |
| Template | `--template {name}` | Use template's preset operations |

## Evaluating Output

You can't see pixels — but `analyze` can. Use it throughout the workflow to evaluate output.

**What to look for:**
- **QA** — artifacts, glitches, subject consistency, motion naturalness
- **Taste** — does the opening hook attention? Does visual energy match audio?
- **Platform readiness** — text readability, vertical crop framing, audio-visual sync

Analyze after each creative checkpoint, not just at the end.

## Iteration

Each step is independent. Redo any step without rerunning the whole pipeline:

- Bad image? Regenerate with a different prompt or reference
- Caption too long? Regenerate with `--length short`
- Video glitchy? Analyze it, then regenerate with adjusted params
- Clip too short? Use `extend` mode to continue it
- Low quality? Upscale the image or video
- Everything good but wrong caption? Just re-run the edit step
