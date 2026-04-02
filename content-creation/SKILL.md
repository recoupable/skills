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

Async primitives return a `runId`. Poll with `recoup tasks status --run {runId} --json` until `status` is `COMPLETED`, then read `output`.

There is also `recoup content create` which runs the full pipeline in one shot — use it when the user just wants a video without creative control.

## Workflow

### Step-by-step (creative control)

```bash
# 1. Transcribe audio
recoup content transcribe-audio --url {audioUrl} --json
# Returns: audioUrl, fullLyrics, segments (timestamped words)

# 2. Generate image
recoup content generate-image --prompt "{scene description}" \
  --reference-image {referenceImageUrl} --json
# Returns: imageUrl

# 3. (Optional) Upscale image
recoup content upscale --url {imageUrl} --type image --json

# 4. Generate video (from image, or prompt-only, or both)
recoup content generate-video --image {imageUrl} --json
# Or without an image:
recoup content generate-video --prompt "{video description}" --json
# Returns: videoUrl

# 5. Generate caption
recoup content generate-caption --topic "{topic}" --length short --json
# Synchronous — returns { content } immediately

# 6. Edit final video (template mode)
recoup content edit --video {videoUrl} --audio {audioUrl} \
  --template artist-caption-bedroom \
  --overlay-text "{caption}" --json

# 6. Edit final video (manual mode)
recoup content edit --video {videoUrl} \
  --trim-start 30 --trim-duration 15 \
  --crop-aspect 9:16 \
  --overlay-text "{caption}" \
  --mux-audio {audioUrl} --json
```

### Quick (no creative decisions)

```bash
recoup content create --artist {artistId} --template artist-caption-bedroom --json
```

### Lipsync (mouth moves to audio)

```bash
# Generate video with audio-driven animation
recoup content generate-video --image {imageUrl} --lipsync \
  --audio {audioUrl} --json

# Edit — no need to mux audio separately (already baked in)
recoup content edit --video {videoUrl} \
  --crop-aspect 9:16 \
  --overlay-text "{caption}" --json
```

## Model Selection

Each generative primitive accepts an optional `--model` flag to override the default:

| Primitive | Default Model | Flag |
|-----------|---------------|------|
| generate-image | `fal-ai/nano-banana-pro/edit` | `--model {modelId}` |
| generate-video | `fal-ai/veo3.1/fast/image-to-video` | `--model {modelId}` |
| generate-video (lipsync) | `fal-ai/ltx-2-19b/audio-to-video` | `--model {modelId}` |
| transcribe-audio | `fal-ai/whisper` | `--model {modelId}` |

## Edit Operations

The `edit` command accepts either a template (deterministic config) or manual flags:

| Operation | Flags | What it does |
|-----------|-------|-------------|
| Trim | `--trim-start {s} --trim-duration {s}` | Cut a time window |
| Crop | `--crop-aspect {ratio}` | Crop to aspect ratio (e.g. 9:16) |
| Overlay text | `--overlay-text {text} --text-color {color} --text-position {pos}` | Add on-screen text |
| Mux audio | `--mux-audio {url}` | Add audio track to video |
| Template | `--template {name}` | Use template's preset operations |

All operations run in a single processing pass.

## Watching Your Work

You can't see pixels — but `analyze-video` can. Use it freely throughout the workflow to evaluate your output. Write your own prompts based on what you need to know.

### What to look for

**QA** — technical quality problems:
- Visual artifacts, glitches, distortion
- Subject consistency and recognizability
- Motion naturalness vs robotic movement
- Broken or repeated frames

**Taste** — creative quality:
- Does the opening hook attention in the first 2 seconds?
- Does it feel intentional and aesthetic, or generic?
- Does the visual energy match the audio energy?
- Would a real person post this?

**Platform readiness** — practical details:
- Text readability and positioning (not blocking the subject, not cut off by UI)
- Vertical crop framing
- Audio-visual sync and pacing

### When to analyze

Use it at every creative checkpoint, not just once at the end:

- **After generating a clip** — catch quality issues before spending time editing
- **After each edit pass** — did the trim land on the right beat? Does the cut feel natural?
- **After combining multiple clips** — do the cuts flow? Does the pacing hold attention?
- **After adding audio** — is the lipsync convincing? Does the music energy match the visuals?
- **After adding text** — is it readable, well-timed, not blocking anything important?
- **When comparing versions** — which of two outputs is better and why?
- **When building a storyline** — does the sequence of shots tell a coherent story?

For longer edits with multiple cuts, analyze after each major assembly — not just the final export. If cut 3 of 5 looks wrong, fix it before adding cuts 4 and 5.

### Acting on feedback

- Artifacts or glitches — regenerate with a different `--model` or `--motion` prompt
- Subject not recognizable — regenerate image with a better `--reference-image` or prompt
- Robotic motion — try a more natural motion prompt or switch to lipsync
- Boring opening — more dramatic image or motion
- Looks like AI slop — different model, better reference image, or more specific prompt
- Bad text placement — adjust position or shorten caption in `edit`

Generate, watch, fix, watch again. Two rounds usually gets you from mediocre to good.

## Iteration

Redo any step without rerunning everything:

- Bad image? Run `generate-image` again with a different prompt
- Wrong audio moment? Transcribe a different file or URL
- Caption too long? Run `generate-caption` with `--length short`
- Low quality? Run `upscale` on the image or video
- Video glitchy? Check `analyze-video` feedback, then regenerate with adjusted params
- Everything good but caption is wrong? Just rerun `edit` with new `--overlay-text`

Each retry costs only that step's time, not the full pipeline.
