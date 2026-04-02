---
name: content-creation
description: Create social videos, TikToks, Reels, and visual content for music artists using AI-generated images, video, on-screen text, and song audio. Use this skill whenever the user asks to create content, make a video, generate an image, produce a TikTok or Reel, create a promotional clip, add on-screen text or captions to a video, do a face swap, make visual content for an artist, post to social media, or create short-form video from a song. Also use when the user wants to iterate on content quality — regenerate images, try different songs, adjust text, or upscale for higher quality.
---

# Content Creation

Create social-ready short-form videos for music artists by composing independent primitives. Each primitive does one thing. You orchestrate them based on the artist's identity and the song's energy.

## How It Works

Six primitives, each callable independently:

| Primitive | Command | Async? |
|-----------|---------|--------|
| Transcribe audio | `recoup content transcribe-audio` | Yes (30-60s) |
| Generate image | `recoup content generate-image` | Yes (10-30s) |
| Generate video | `recoup content generate-video` | Yes (60-180s) |
| Generate caption | `recoup content generate-caption` | No (2-5s) |
| Render final | `recoup content render` | Yes (10-30s) |
| Upscale | `recoup content upscale` | Yes (30-60s) |

Async primitives return a `runId`. Poll with `recoup tasks status --run <runId> --json` until `status` is `COMPLETED`, then read `output`.

There is also `recoup content create` which runs all steps in one shot — use it when the user just wants a video without creative control.

## Creative Decision-Making

The skill's value is not in running commands — it is in making creative decisions at each step. Read the artist's `context/artist.md` before starting. It contains their personality, aesthetic direction, mood, colors, and sacred rules.

### Choosing a template

Templates control the visual scene (lighting, camera, environment). Match the template to the artist's aesthetic and the song's mood:

| Template | Scene | When to use |
|----------|-------|-------------|
| `artist-caption-bedroom` | Moody purple bedroom, deadpan selfie | Introspective songs, vulnerable lyrics, lo-fi vibe |
| `artist-caption-outside` | Night street, phone on ground | Urban feel, cinematic energy, confident tracks |
| `artist-caption-stage` | Small venue, fan cam angle | Performance energy, hype songs, live feel |
| `album-record-store` | Vinyl on display in NYC record store | Album/single promotion, release day content |

If `artist.md` says "dark, moody, introspective" — use bedroom. If it says "cinematic, urban" — use outside. When in doubt, bedroom is the safest default for most emerging artists.

### Choosing a song clip

Start with audio before image because the song's mood should influence your template choice. If the artist has multiple songs, pick one that matches the content goal:
- Promoting a new release? Use `--song <slug>` to target it
- General content? Let the pipeline pick randomly
- Have a specific audio file? Pass the URL: `--song https://...`

After transcription completes, check the lyrics and mood in the output. If the mood doesn't match the template you planned, switch templates before generating the image.

### Evaluating intermediate results

After each step, assess quality before moving on:

- **Image**: Does it match the template's aesthetic? Is the face recognizable? If not, run `recoup content generate-image` again — it picks a different reference composition each time.
- **Video**: Is the motion natural? Lipsync clips should show mouth movement matching the lyrics. If the video is too static or glitchy, regenerate.
- **Text**: Does the text connect to the song's lyrics/theme? Is the length right for the platform? Try a different `--length` if it feels off.
- **Upscale**: Only upscale if you need higher quality (adds 30-60s per step). Skip for quick drafts.

### Handling edge cases

- **Instrumental songs (no lyrics)**: Audio selection still works — Whisper returns empty lyrics. Text generation will have less to work with. Consider writing text manually via `--text "your text here"` on the render command.
- **Artist has no face-guide.png**: Image generation will fail. Ask the user to provide a face image URL with `--face-guide <url>`.
- **Song URL instead of repo slug**: Pass URLs directly in `--song`. The pipeline downloads, transcribes, and analyzes them the same way.

## Workflow

### Step-by-step (creative control)

```bash
# 1. Transcribe a song
recoup content transcribe-audio --artist <id> --json
# Check output: songUrl, fullLyrics, segments

# 2. Generate image
recoup content generate-image --artist <id> --template <name> --json
# Check output: imageUrl — does it match the aesthetic?

# 3. (Optional) Upscale image
recoup content upscale --url <imageUrl> --type image --json

# 4. Generate video
recoup content generate-video --image <imageUrl> --json
# Check output: videoUrl

# 5. Generate on-screen caption
recoup content generate-caption --artist <id> --song "<songTitle>" --length short --json
# Synchronous — returns { content } immediately

# 6. Render final video
recoup content render --video <videoUrl> --audio <songUrl> \
  --start <startSeconds> --duration 15 --text "<content>" --json
# Check output: final videoUrl
```

### Quick (no creative decisions)

```bash
recoup content create --artist <id> --template artist-caption-bedroom --json
```

### Lipsync (mouth moves to lyrics)

```bash
# Audio first, then video with --lipsync
recoup content generate-video --image <imageUrl> --lipsync \
  --song-url <songUrl> --start <seconds> --duration 15

# When rendering, pass --has-audio so ffmpeg doesn't double the audio
recoup content render --video <videoUrl> --audio <songUrl> \
  --start <seconds> --duration 15 --text "<content>" --has-audio
```

## Iteration

The point of primitives is that you can redo any step without rerunning everything:

- Bad image? Run `generate-image` again (different reference each time)
- Wrong song moment? Run `transcribe-audio` again
- Text too long? Run `generate-caption` with `--length short`
- Low quality? Run `upscale` on the image or video
- Everything good but text is wrong? Just rerun `render` with new text

Each retry costs only that step's time, not the full 5-10 minute pipeline.
