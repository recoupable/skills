---
name: recoup-promo-graphic
description: Create a promo graphic that announces an event and a date — release date, pre-save, out-now, drop reveal, or a tour/show poster. Use when the user says "promo graphic", "announcement graphic", "release date graphic", "pre-save graphic", "tour poster", "show flyer", "out now post", "coming soon", or "announce [release/tour]". Produces date-forward promo art (feed + story sizes) with the key details. Works with or without artist context.
---

# Promo Graphic

Promo art that communicates a **fact + a date**: "out now," "pre-save," "on tour,"
"coming Friday." The job is information design — the date, title, and call-to-action must
be instantly legible. Distinct from cover art (no dates/CTAs) and quote cards (lyrics).

Read `references/content-api.md` (image gen, edit/overlay) and
`references/analyze-gate.md` (verify the details are right). Both ship alongside this skill.

## Inputs (get the facts straight first)

- **Type** — release / pre-save / tour / show / generic reveal.
- **The details** (required, must be exact): title, **date(s)**, CTA (e.g. "Pre-save now"),
  and any handle/URL. Tour/show: each date + city + venue. Confirm these with the user —
  wrong dates are the one unrecoverable error here.
- **Sizes** — default 1:1 + 9:16; tour posters often 4:5.
- **Look** — context mode: `context/artist.md` aesthetic, `releases/{slug}/RELEASE.md` for
  the canonical title/date; generic mode: user-supplied.

## Steps

1. **Lock the facts.** Pull date/title from `releases/{slug}/RELEASE.md` when available;
   otherwise have the user confirm. Never guess a date.
2. **Design:** generate an on-brand background (optionally seed with cover art / a photo),
   then overlay the title, date(s), and CTA via the edit endpoint — clear hierarchy, date
   prominent. Tour graphics: a clean legible date/city/venue list. See
   `references/content-api.md`.
3. **Verify** with the analyze gate — every date/city/CTA correct and readable; re-check
   spelling of venue and city names.

## Persist

Workspace → `artists/{slug}/releases/{release-slug}/announcement-*.png`, commit
`{what}: {why}` (`references/workspace-context.md`). Otherwise return the URLs.

## Guardrails

- **Dates and venues must be exact.** Confirm against `RELEASE.md` or the user; never
  invent. This is the highest-risk field in the plugin.
- **Hierarchy:** date + CTA dominate; decoration never buries the info.
