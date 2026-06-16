---
name: recoup-content-graphic
description: Create a still-image social graphic for an artist — a multi-slide carousel/photo dump, a date/announcement promo (out-now, pre-save, tour poster), or a single static lyric/quote card (one line on one image, no motion). Use when the user says "carousel", "photo dump", "swipe post", "promo graphic", "announcement", "release date graphic", "pre-save graphic", "tour poster", "out now post", "quote card", "lyric card", or "typography post". Produces finished image(s); does not post them. For square DSP cover art use recoup-content-cover-art; for a YouTube thumbnail use recoup-content-thumbnail; for the whole song's words animated on screen use recoup-content-lyric-video. Works with or without artist context.
---

# Content Graphic

Still-image social posts in three shapes. Pick the mode from the ask:

| Ask | Mode | What it is |
|---|---|---|
| "carousel", "photo dump", "swipe post", "5-slide post" | **carousel** | An ordered, cohesive multi-slide set (cover → body → CTA) |
| "promo", "announcement", "release date", "pre-save", "tour poster", "out now" | **promo** | Date-forward announcement art (fact + date + CTA), feed + story sizes |
| "quote card", "lyric card", "typography post" | **quote** | A lyric/quote rendered as typography on a background |

Distinct from `recoup-content-cover-art` (square DSP identity, no dates/CTAs) and
`recoup-content-thumbnail` (16:9 click art). Read `references/content-api.md`
(image gen, edit/overlay) and `references/analyze-gate.md` (verify the result).
Both ship alongside this skill.

## Shared backbone

When an artist is involved, read workspace context first, then layer research
signals (see `references/workspace-context.md` and `references/research-context.md`);
in generic mode, work from the user's direction. Generate, then **verify with the
analyze gate** before claiming done — the agent can't see pixels.

## Mode details

### carousel
Outline the slide-by-slide copy first (hook cover → body → CTA) so the set tells
one story; confirm the outline with the user before generating. Generate a
**consistent** set — same palette/treatment/aspect across slides (reuse a seed or
reference image), overlay each slide's text via the edit endpoint. Default 5 slides
(1 cover + 3 body + 1 CTA), aspect 4:5 or 1:1 kept consistent. Verify the set reads
as one cohesive sequence and the cover earns the swipe.
Persist → `artists/{slug}/content/carousels/{topic}/slide-01.png …`.

### promo
**Lock the facts first** — title, exact **date(s)**, CTA, handle/URL; tour/show:
each date + city + venue. Pull date/title from `releases/{slug}/RELEASE.md` when
available; otherwise have the user confirm. **Never guess a date — wrong dates are
the one unrecoverable error here.** Generate an on-brand background, overlay title /
date(s) / CTA with clear hierarchy (date + CTA dominate). Default sizes 1:1 + 9:16
(tour posters often 4:5). Verify every date/city/CTA is correct and readable.
Persist → `artists/{slug}/releases/{release-slug}/announcement-*.png`.

### quote
Pick the line(s) and **confirm wording** (especially if pulled from a transcript or
the `recoup-song-analyze` skills — verify spelling; a typo'd lyric card gets
screenshotted). Generate/select an on-brand background, overlay large, well-kerned,
high-contrast text; default sizes 1:1 + 9:16. Don't reproduce third-party
copyrighted lyrics — the artist's own are fine; for covers/samples confirm rights.
Persist → `artists/{slug}/content/quote-cards/`.

## Guardrails

- **Legibility first** — if text fights the background, change the background.
- **promo: dates/venues must be exact**; **quote: wording must be verified.**
- Commit `{what}: {why}` on persist (`references/workspace-context.md`); otherwise
  return the image URLs. This skill stops at the asset — it does not post.

## Reference

- `references/content-api.md` — image generation + edit/overlay endpoints.
- `references/analyze-gate.md` — verifying a rendered image before claiming done.
- `references/workspace-context.md`, `references/research-context.md` — artist
  context + live signal layering.
