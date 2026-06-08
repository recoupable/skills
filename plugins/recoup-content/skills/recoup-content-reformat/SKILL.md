---
name: recoup-content-reformat
description: Adapt one master video into platform-specific cuts, or polish the artist's own footage (BTS, live clips) into postable assets. Use when the user says "reformat this for TikTok/Reels/Shorts", "make platform versions", "resize this video", "cut this down", "add captions to my clip", "crop this to 9:16", or "clean up this BTS footage". Produces distinct per-platform versions (never identical re-uploads) and captions/crops user-supplied footage. Audio/visual editing, no generation required.
---

# Content Reformat

Two jobs that share an engine (edit, not generate):

1. **Master → per-platform cuts** — take one finished video and produce genuinely
   different versions for TikTok / Reels / Shorts / X (aspect, length, caption placement).
2. **Polish raw footage** — the artist shoots BTS / live / studio video; you crop, trim,
   caption, and hook it into a postable clip.

Read `references/content-api.md` (edit ops, async) and `references/analyze-gate.md`
(verify each cut). Both ship alongside this skill.

## Why distinct cuts (not copy-paste)

Platforms penalize identical re-uploads — IG suppresses >~70% reused audio/visual and
watermarked cross-posts. **Never hand the user the same file renamed for three platforms.**
Each version should differ in at least crop, opening hook framing, or caption treatment.

## Steps

1. **Take the source** — a master video URL or the user's uploaded footage. (For raw BTS,
   no generation is needed; this is pure edit.)
2. **Per target platform**, apply edits via the edit endpoint (`references/content-api.md`):
   - **TikTok / Reels / Shorts** → 9:16, lead with the hook (use `recoup-song-hook` from
     `recoup-song-analysis` to pick the in-point), captions high enough to clear the UI chrome.
   - **X / feed** → 1:1 or 16:9, shorter, front-load the payoff.
   - Vary the opening framing / caption so the cuts aren't near-duplicates.
3. **Caption/clean** raw footage — trim dead air, crop to vertical, burn in a hook caption,
   mux/clean audio.
4. **Verify** each cut with the analyze gate — correct aspect, captions clear of UI safe
   zones, hook lands in the first seconds.

## Persist

Workspace → `artists/{slug}/content/{source-slug}/{platform}.mp4`, commit `{what}: {why}`
(`references/workspace-context.md`). Otherwise return the per-platform URLs.

## Guardrails

- **No identical re-uploads** — each platform gets a meaningfully distinct cut.
- **Respect safe zones** — captions/text must clear each platform's on-screen UI.
- **It's their footage** — enhance, don't restyle beyond what the user wants; confirm
  before heavy creative changes.
