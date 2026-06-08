---
name: recoup-quote-cards
description: Turn a lyric or quote into shareable graphic cards — typographic images for Instagram, Stories, or Twitter/X. Use when the user says "quote card", "lyric card", "lyric graphic", "make a shareable quote", "typography post", or "put this lyric on an image". Produces one or more on-brand cards (square + story sizes) from a chosen line. Works with or without artist context.
---

# Quote Cards

A lyric or quote rendered as a designed, shareable image. The job is **typography on a
background** — fast, high-volume social fuel. Distinct from cover art (release identity)
and quote-over-video (that's a lyric video or short clip).

Read `references/content-api.md` (image gen, edit/overlay) and
`references/analyze-gate.md` (verify legibility). Both ship alongside this skill.

## Inputs

- **The line(s)** (required) — a lyric or quote. If the user wants "the best line," pull
  candidates from the song (the `recoup-song-analysis` skills or a transcript) and offer a
  few; don't silently pick.
- **Sizes** (optional) — default to 1:1 (feed) + 9:16 (Story). Add others on request.
- **Look** — context mode: palette/fonts from `context/artist.md`; generic mode: user's
  direction.

## Steps

1. **Pick the line(s)** and confirm wording with the user (especially if pulled from a
   transcript — verify spelling).
2. **Design the card:** generate or select a background on-brand with the aesthetic, then
   overlay the text via the edit endpoint — large, well-kerned, high-contrast, balanced
   composition. Produce each requested size. See `references/content-api.md`.
3. **Verify** with the analyze gate — text legible, no typos, no overflow, on-brand.

## Persist

Workspace → `artists/{slug}/content/quote-cards/`, commit `{what}: {why}`
(`references/workspace-context.md`). Otherwise return the image URLs.

## Guardrails

- **Verify wording** — a typo'd lyric card is embarrassing and gets screenshotted.
- **Don't reproduce third-party copyrighted lyrics** — the artist's own lyrics are fine;
  for covers/samples, confirm rights.
- **Legibility first** — if the text fights the background, change the background.
