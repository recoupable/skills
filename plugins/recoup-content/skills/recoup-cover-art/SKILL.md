---
name: recoup-cover-art
description: Create square cover art for a release — single, EP, or album artwork sized for DSPs (Spotify, Apple Music). Use when the user says "cover art", "album art", "single artwork", "artwork for [release]", "make a cover for [song]", or "DSP artwork". Produces brand-defining 1:1 art with no clickbait text. Distinct from a YouTube thumbnail (use recoup-thumbnail). Works with or without artist context.
---

# Cover Art

Square release artwork for DSPs. This is **brand-defining, durable** art — the image that
represents the release everywhere it streams. It is NOT a clickbait thumbnail: cover art
carries at most the artist/title set cleanly, never hooky overlay text or arrows. For
YouTube/video CTR art, use `recoup-thumbnail`.

Read `references/content-api.md` (image gen, upscale, async) and
`references/analyze-gate.md` (verify before delivery). Both ship alongside this skill.

## DSP requirements

- **Square 1:1**, high resolution (aim ≥ 3000×3000 for store acceptance) — generate then
  `upscale` (`type: image`) if needed.
- **Legible at thumbnail size** — it'll appear tiny in a queue; test the concept small.
- Keep text minimal and on-brand; no streaming logos, no URLs, no "explicit"-style badges.

## Steps

1. **Gather direction.** Context mode: aesthetic + any palette/motifs from
   `context/artist.md`, release theme from `releases/{slug}/RELEASE.md`. Generic mode: the
   user's concept/prompt. Optionally seed with a supplied photo as `reference_image_url`.
2. **Generate** the 1:1 image (`POST $BASE/content/image`, poll). Offer 2–3 directions.
3. **Upscale** the chosen one to DSP resolution.
4. **Verify** with the analyze gate — composition reads at small size, no garbled text, no
   artifacts, title/name legible if included.

## Persist

Workspace → `artists/{slug}/releases/{release-slug}/cover.png` and record the URL in that
release's `RELEASE.md` (Section 18, visuals). Commit `{what}: {why}`. See
`references/workspace-context.md`. No workspace → return the image URL.

## Guardrails

- **Cover art ≠ thumbnail.** No hooky overlay text, arrows, or shocked faces.
- **Square + high-res**, or DSPs reject it.
- **Likeness:** if seeding with a real face, use the artist's own reference; image models
  may 422 on celebrity likeness.
