---
name: recoup-content-thumbnail
description: Create a YouTube/video thumbnail optimized for click-through — 16:9 with a clear focal face and a short punchy hook text. Use when the user says "thumbnail", "YouTube thumbnail", "video cover", "make a thumbnail for [video]", or "clickable cover image". Distinct from square DSP cover art (use recoup-content-cover-art). Works with or without artist context.
---

# Thumbnail

Click-through art for a video. The whole job is **maximize CTR**: a 16:9 frame
with a strong focal subject (usually a face with clear emotion) and a few large,
legible hook words. This is the opposite of cover art — here, hooky text and bold
contrast are the point. For square DSP identity art, use `recoup-content-cover-art`.

The job is a loop: **set the focal subject + hook → assemble → verify it wins the
click at phone size → iterate the weakest element.** A thumbnail you haven't
shrink-tested is not done.

Read `references/content-api.md` (image gen, edit/overlay, upscale, async) and
`references/analyze-gate.md` (verify legibility). Both ship alongside this skill.

## Thumbnail requirements (non-negotiable)

- **16:9** (1280×720+), readable as a tiny phone tile.
- **One focal point** — a face with expression, or a single bold object. No clutter.
- **≤ 3–5 words** of hook text, huge and high-contrast, **never covering the face**.
- High saturation/contrast; leave room for the platform's duration stamp
  (bottom-right).

## Inputs

- **Artist** (optional — context mode supplies the face + palette).
- **Video topic** (required) — drives the hook words.
- **Hook text** (optional) — the user's words, or you propose options in Phase 2.

## Procedure

### Phase 1 — Lock the focal subject

Context mode: use `context/images/face-guide.png` as the focal face and
`context/artist.md` for palette. Generic mode: the user's supplied image. A
thumbnail without a clear focal subject won't earn clicks — if none is available,
ask for one rather than generating a faceless tile.

### Phase 2 — Write the hook (3 options, pick the sharpest)

The hook words are the highest-leverage element. Draft **3 short options**
(≤5 words each) framed on the video's actual payoff — curiosity or stakes, not a
title restatement. Pick the strongest, or offer them to the user. Avoid clickbait
that the content doesn't pay off (it tanks retention even if it wins the click).

### Phase 3 — Assemble

Generate/assemble the 16:9 base (use `reference` mode or image gen seeded with the
face), then **overlay** the hook text via the edit endpoint — large, contrasting,
placed off the face (see `references/content-api.md`). Upscale if soft.

### Phase 4 — Verify (the analyze-gate loop; mandatory)

You cannot see pixels — analyze the result at small scale before claiming done
(`references/analyze-gate.md`). Check, and **iterate the weakest element on any
failure**:

- [ ] **Focal point obvious in <1s** at phone-tile size.
- [ ] **Face clear**, expression reads, not muddy or artifacted.
- [ ] **Hook text readable on a phone** and not covering the face.
- [ ] **High contrast** — pops in a crowded feed, not washed out.
- [ ] Duration-stamp corner (bottom-right) left uncluttered.

Weak hook → back to Phase 2; muddy face/contrast → back to Phase 3.

### Phase 5 — Persist

Workspace → `artists/{slug}/content/thumbnails/` (or next to the video in its
release folder); commit `{what}: {why}` (`references/workspace-context.md`).
Otherwise return the URL.

## Guardrails

- **Thumbnail ≠ cover art.** Different aspect (16:9), different reader (a browser
  deciding whether to click), hooky text encouraged.
- **Text never covers the face.** Faces drive clicks.
- **Verify before delivery.** An un-analyzed thumbnail is the failure mode here.
- **Likeness:** seed with the artist's own face reference; models may 422 on
  celebrities.

## References

- `references/content-api.md` — image gen + edit/overlay endpoints.
- `references/analyze-gate.md` — verifying a rendered image before claiming done.
- `references/workspace-context.md` — read-context-first + write-back.
