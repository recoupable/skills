---
name: recoup-carousel
description: Create a multi-image Instagram carousel or photo dump — a sequence of cohesive slides. Use when the user says "carousel", "photo dump", "swipe post", "multi-image post", "slideshow post", or "make a 5-slide post about [topic]". Produces an ordered set of on-brand slides (cover slide + body slides + CTA slide). Works with or without artist context.
---

# Carousel

An ordered set of slides meant to be swiped — IG carousel or photo dump. The job is a
**cohesive multi-slide narrative**, not one image: a hook cover slide, body slides that
develop it, and a closing CTA. Output is N images, consistently styled.

Read `references/content-api.md` (image gen, edit/overlay) and
`references/analyze-gate.md` (verify the set). Both ship alongside this skill.

## Inputs

- **Topic/angle** (required) — e.g. behind-the-scenes of the release, a lyric breakdown, a
  "5 things" list, a tour recap.
- **Slide count** (optional) — default 5 (1 cover + 3 body + 1 CTA).
- **Aspect** — default 4:5 (IG feed) or 1:1; keep it consistent across all slides.
- **Look** — context mode: `context/artist.md` aesthetic; generic mode: user's direction.

## Steps

1. **Outline the slides** — write the slide-by-slide copy first (hook → develop → CTA) so
   the set tells one story. Confirm the outline with the user before generating images.
2. **Generate a consistent set** — same palette/treatment across slides (reuse a seed /
   reference image for visual continuity). Overlay each slide's text via the edit endpoint.
   Same aspect for every slide. See `references/content-api.md`.
3. **Verify** with the analyze gate — slides read as a set, text legible, order makes
   sense, cover slide hooks. Regenerate any slide that breaks the visual consistency.

## Persist

Workspace → `artists/{slug}/content/carousels/{topic}/slide-01.png …`, commit
`{what}: {why}` (`references/workspace-context.md`). Otherwise return the ordered URLs.

## Guardrails

- **Cohesion over variety** — slides must look like one set, not five random images.
- **Cover slide earns the swipe** — weak slide 1, dead post.
- **Keep aspect consistent** across all slides or IG crops them unevenly.
