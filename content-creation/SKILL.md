---
name: content-creation
description: Create social videos, TikToks, Reels, and visual content using AI-generated images, video, captions, and audio. Use this skill whenever the user asks to create content, make a video, generate an image, produce a TikTok or Reel, create a promotional clip, add captions to a video, make visual content, or create short-form video. Also use when the user wants to iterate on content quality — regenerate images, try different audio, adjust text, or upscale for higher quality.
---

# Content Creation

Create social-ready short-form videos by composing independent primitives. Each primitive does one thing. You orchestrate them.

## Primitives

Seven primitives, each callable independently:

| Primitive | Command | Async? |
|-----------|---------|--------|
| Transcribe audio | `recoup content transcribe-audio` | Yes (30-60s) |
| Generate image | `recoup content generate-image` | Yes (10-30s) |
| Generate video | `recoup content generate-video` | Yes (60-180s) |
| Generate caption | `recoup content generate-caption` | No (2-5s) |
| Edit media | `recoup content edit` | Yes (10-30s) |
| Upscale | `recoup content upscale` | Yes (30-60s) |
| Analyze video | `recoup content analyze-video` | No (10-30s) |

Async primitives return a `runId`. Poll with `recoup tasks status --run <runId> --json` until `status` is `COMPLETED`, then read `output`.

There is also `recoup content create` which runs the full pipeline in one shot — use it when the user just wants a video without creative control.

## Workflow

### Step-by-step (creative control)

```bash
# 1. Transcribe audio
recoup content transcribe-audio --url <audioUrl> --json
# Returns: audioUrl, fullLyrics, segments (timestamped words)

# 2. Generate image
recoup content generate-image --prompt "<scene description>" \
  --reference-image <faceUrl> --json
# Returns: imageUrl

# 3. (Optional) Upscale image
recoup content upscale --url <imageUrl> --type image --json

# 4. Generate video
recoup content generate-video --image <imageUrl> --json
# Returns: videoUrl

# 5. Generate caption
recoup content generate-caption --topic "<song or theme>" --length short --json
# Synchronous — returns { content } immediately

# 6. Edit final video (template mode)
recoup content edit --video <videoUrl> --audio <audioUrl> \
  --template artist-caption-bedroom \
  --overlay-text "<caption>" --json

# 6. Edit final video (manual mode)
recoup content edit --video <videoUrl> \
  --trim-start 30 --trim-duration 15 \
  --crop-aspect 9:16 \
  --overlay-text "<caption>" \
  --mux-audio <audioUrl> --json
```

### Quick (no creative decisions)

```bash
recoup content create --artist <id> --template artist-caption-bedroom --json
```

### Lipsync (mouth moves to audio)

```bash
# Generate video with audio-driven animation
recoup content generate-video --image <imageUrl> --lipsync \
  --audio <audioUrl> --json

# Edit — no need to mux audio separately (already baked in)
recoup content edit --video <videoUrl> \
  --crop-aspect 9:16 \
  --overlay-text "<caption>" --json
```

## Model Selection

Each generative primitive accepts an optional `--model` flag to override the default:

| Primitive | Default Model | Flag |
|-----------|---------------|------|
| generate-image | `fal-ai/nano-banana-pro/edit` | `--model <id>` |
| generate-video | `fal-ai/veo3.1/fast/image-to-video` | `--model <id>` |
| generate-video (lipsync) | `fal-ai/ltx-2-19b/audio-to-video` | `--model <id>` |
| transcribe-audio | `fal-ai/whisper` | `--model <id>` |

## Edit Operations

The `edit` command accepts either a template (deterministic config) or manual flags:

| Operation | Flags | What it does |
|-----------|-------|-------------|
| Trim | `--trim-start <s> --trim-duration <s>` | Cut a time window |
| Crop | `--crop-aspect <ratio>` | Crop to aspect ratio (e.g. 9:16) |
| Overlay text | `--overlay-text <text> --text-color <color> --text-position <pos>` | Add on-screen text |
| Mux audio | `--mux-audio <url>` | Add audio track to video |
| Template | `--template <name>` | Use template's preset operations |

All operations run in a single processing pass.

## Watching Your Work

After generating a video, use `analyze-video` to watch it before moving on. This is how you evaluate your own creative output and decide what to improve.

```bash
# After generate-video returns a videoUrl:
recoup content analyze-video --url <videoUrl> \
  --prompt "Evaluate this video for social media. Is the motion natural? Is the subject recognizable? Does it feel polished or glitchy? Rate 1-10 and explain what could improve." \
  --json
```

Read the analysis. If it flags problems, fix them:
- **Glitchy motion or artifacts** → regenerate video with a different `--model` or `--motion` prompt
- **Subject not recognizable** → regenerate image with a better `--reference-image` or more specific `--prompt`
- **Too static / boring** → try a more dynamic `--motion` prompt or switch to lipsync mode
- **Good quality but wrong mood** → the video is fine, adjust the caption or audio choice instead

Do this after every video generation, not just when something looks wrong. The analysis catches things you might miss and builds a feedback loop that improves each iteration.

For final edited videos, analyze again after the edit pass:

```bash
recoup content analyze-video --url <finalVideoUrl> \
  --prompt "This is the final social video with caption and audio. Is the text readable? Does the crop look right? Is the audio synced? Any issues that would hurt engagement?" \
  --json
```

## Iteration

Redo any step without rerunning everything:

- Bad image? Run `generate-image` again with a different prompt
- Wrong audio moment? Transcribe a different file or URL
- Caption too long? Run `generate-caption` with `--length short`
- Low quality? Run `upscale` on the image or video
- Video glitchy? Check `analyze-video` feedback, then regenerate with adjusted params
- Everything good but caption is wrong? Just rerun `edit` with new `--overlay-text`

Each retry costs only that step's time, not the full pipeline.
