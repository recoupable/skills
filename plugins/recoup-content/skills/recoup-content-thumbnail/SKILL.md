---
name: recoup-content-thumbnail
description: Create a YouTube/video thumbnail optimized for click-through — 16:9 with a clear focal face and a short punchy hook text. Use when the user says "thumbnail", "YouTube thumbnail", "video cover", "make a thumbnail for [video]", or "clickable cover image". Distinct from square DSP cover art (use recoup-content-cover-art). Works with or without artist context.
---

# Thumbnail

Click-through art for a video. The job is **maximize CTR**: a 16:9 frame with a strong
focal subject (usually a face with clear emotion) and a few large, legible hook words.
This is the opposite of cover art — here, hooky text and bold contrast are the point.

Read `references/content-api.md` (image gen, edit/overlay, upscale, async) and
`references/analyze-gate.md` (verify legibility). Both ship alongside this skill.

## Thumbnail requirements

- **16:9** (1280×720+), readable as a tiny phone tile.
- **One focal point** — a face with expression, or a single bold object. No clutter.
- **≤ 3–5 words** of hook text, huge and high-contrast, never covering the face.
- High saturation/contrast; leave room for the platform's duration stamp (bottom-right).

## Steps

1. **Gather direction.** Context mode: use `context/images/face-guide.png` as the focal
   subject and `context/artist.md` for palette; the video's topic for the hook words.
   Generic mode: the user's image + hook text.
2. **Generate / assemble** the 16:9 base image (`reference` mode or image gen seeded with
   the face), then **overlay** the hook text via the edit endpoint (large, contrasting,
   off the face). See `references/content-api.md`.
3. **Upscale** if soft.
4. **Verify** with the analyze gate at small scale — is the face clear, the text readable
   on a phone, the focal point obvious in <1s? Iterate the hook words if weak.

## Persist

Workspace → `artists/{slug}/content/thumbnails/` (or next to the video in its release
folder), commit `{what}: {why}` (`references/workspace-context.md`). Otherwise return the URL.

## Guardrails

- **Thumbnail ≠ cover art.** Different aspect (16:9), different reader (a browser deciding
  whether to click), hooky text encouraged.
- **Text never covers the face.** Faces drive clicks.
- **Likeness:** seed with the artist's own face reference; models may 422 on celebrities.
