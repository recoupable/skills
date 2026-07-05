---
name: recoup-content-clip-video
description: 'Clip long-form video (podcast, interview, livestream, live set, music video) into ready-to-post short clips using the OpusClip API. Use for "clip this video", "turn this podcast/stream into shorts", "make clips from this YouTube video", or "cut this into TikToks/Reels/Shorts". Input is an existing long video URL; output is a set of generated clips. To generate new video from scratch, use recoup-content-make-video; to find the single best moment in a song, use recoup-song-find-hook.'
---

# Recoup Content — Clip Video

Turn one long-form video into a set of short, social-ready clips via the
[OpusClip API](https://help.opus.pro/api-reference/quickstart).

## Setup

- Auth: `Authorization: Bearer $OPUS_PRO_API_KEY` (never hardcode the key; get
  one at https://clip.opus.pro/dashboard).
- Base URL: `https://api.opus.pro/api`

## Flow

1. **Submit** the long-form video: `POST /clip-projects` with `{ "videoUrl": "<source url>" }`.
   The response includes a project `id`.
2. **Wait** for clipping to finish — configure a webhook via `conclusionActions`
   (type `WEBHOOK`) when possible; otherwise poll step 3 until clips appear.
3. **Fetch clips**: `GET /exportable-clips?q=findByProjectId&projectId=<id>`.
4. **Deliver** the clip URLs to the user with each clip's title/duration.

## Docs

- Quickstart: https://help.opus.pro/api-reference/quickstart
- Full endpoint index (LLM-readable): https://help.opus.pro/llms.txt
- Every doc page has a `.md` version — append `.md` to the URL and fetch it
  before using any endpoint not covered here (curation preferences, brand
  templates, social posting, collections, transcripts).
