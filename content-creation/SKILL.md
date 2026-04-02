---
name: content-creation
description: Compose content creation primitives to produce social videos for artists. Use when asked to create content, make a video, generate an image, or produce social media posts for an artist.
---

# Content Creation Skill

Create social-ready videos by composing independent primitives via CLI. Each primitive does one thing and can be run alone or chained together.

## Primitives

| Command | What it does | Returns |
|---------|-------------|---------|
| `recoup content audio --artist <id>` | Pick a song, transcribe, find the best 15s clip | `runId` → poll for `{ songTitle, songUrl, startSeconds, clipLyrics, clipMood }` |
| `recoup content image --artist <id> --template <name>` | Generate an AI image from face guide + template scene | `runId` → poll for `{ imageUrl }` |
| `recoup content video --image <url>` | Animate the image into a video | `runId` → poll for `{ videoUrl }` |
| `recoup content text --artist <id> --song <name>` | Generate on-screen text based on the song | `{ content, font, color }` (synchronous) |
| `recoup content render --video <url> --audio <url> --text <text>` | Combine video + audio + text into final mp4 | `runId` → poll for `{ videoUrl, sizeBytes }` |
| `recoup content upscale --url <url> --type image` | Upscale an image or video | `runId` → poll for `{ url }` |
| `recoup content create --artist <id>` | Run the full pipeline (all steps in one shot) | `runId` → poll for final video |

## Workflow: Step-by-Step Content Creation

Use this when you want creative control over each step.

```
1. Select audio
   recoup content audio --artist <id> --song <slug> --json
   → Wait for completion, get songTitle, songUrl, startSeconds, clipLyrics

2. Generate image
   recoup content image --artist <id> --template artist-caption-bedroom --json
   → Wait for completion, get imageUrl

3. (Optional) Upscale image
   recoup content upscale --url <imageUrl> --type image --json
   → Wait for completion, get upscaled URL

4. Generate video
   recoup content video --image <imageUrl> --json
   → Wait for completion, get videoUrl

5. Generate text
   recoup content text --artist <id> --song "<songTitle>" --length short --json
   → Synchronous, get { content }

6. Render final video
   recoup content render --video <videoUrl> --audio <songUrl> --start <startSeconds> --duration 15 --text "<content>" --json
   → Wait for completion, get final videoUrl
```

## Workflow: Quick Full Pipeline

Use this when you just need a video without creative decisions.

```
recoup content create --artist <id> --template artist-caption-bedroom --json
```

## Templates

| Template | Scene | Best for |
|----------|-------|----------|
| `artist-caption-bedroom` | Moody purple bedroom selfie | Introspective, lo-fi vibe |
| `artist-caption-outside` | Night street scene | Urban, cinematic feel |
| `artist-caption-stage` | Small venue concert | Performance, energy |
| `album-record-store` | Vinyl on display in record store | Album/single promotion |

## How to Choose a Template

- Look at the artist's `context/artist.md` for their aesthetic direction
- Match the template to the song's mood (use `clipMood` from the audio step)
- Bedroom = introspective/emotional, Outside = cinematic/urban, Stage = energetic

## Iteration

The power of primitives is iteration. If a step produces bad results:

- **Bad image?** Run `recoup content image` again — it picks a different reference image each time
- **Wrong song clip?** Run `recoup content audio` again — the LLM may pick a different moment
- **Text doesn't fit?** Run `recoup content text` with a different `--length`
- **Want higher quality?** Run `recoup content upscale` on the image or video before rendering

## Lipsync Mode

For lip-synced videos where the artist's mouth moves to the song:

```
recoup content video --image <imageUrl> --lipsync --song-url <songUrl> --start <seconds> --duration 15
```

The video will have audio baked in. When rendering, pass `--has-audio` so ffmpeg doesn't overlay a second audio track.

## Polling for Results

Async primitives return a `runId`. Check progress with:

```
recoup tasks status --run <runId> --json
```

Poll until `status` is `COMPLETED`, then read the `output` field.
