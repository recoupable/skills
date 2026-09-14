# Recoup Sky / media package 1.0.0

This is a reviewed distribution snapshot of marketing's root DESIGN.md and Brand Studio
DESIGN-SYSTEM.md, not a second independently authored identity. Provenance and exact file hashes
are in brand.json. Update from that source, bump this version, and run the plugin's
scripts/sync_brand.py; --check detects drift across self-contained consumer skills.

## Select and stage

Recoup, Consulting and Business house work defaults to this package. Read a project's DESIGN.md
and the brief first. An explicit client/artist brand or a fidelity-only migration wins; record that
selection and supply its actual assets. Never infer a new identity from a captured site's first font.
Run `node <installed-skill>/brand/materialize.mjs <output-directory>` before authoring HTML.
This writes recoup-brand/ (CSS, fonts, exact SVGs, manifests) and brand.lock.json beside the output.
Use `<link rel="stylesheet" href="recoup-brand/brand.css">`. For self-contained HTML/PDF use
`--inline-css` to print equivalent CSS with embedded font data; insert it into BRAND_CSS.
No network or other checkout is required for brand assets. Wait for document.fonts.ready before capture.
For nested HyperFrames sub-compositions, embed the --inline-css result and exact SVG inside the
<template> (or use a logo data URI). The player clones template contents, so relative file links
can resolve against the host instead of the frame directory. Inline assets avoid that ambiguity.

## Compose

DM Sans serves headlines (450–500) and body (400); IBM Plex Mono 400 is only for short labels,
code and metadata. Scale type to the canvas. The outlined SVG lockup is the Recoup name: do not
redraw, stretch, or typeset a replacement logo. Use ink on light, white on forest/sky; maintain clear
space. Company work has no compulsory personal name footer. Attribution is an explicit content field.

Functional: proposals, reports, dashboards, decks. White surfaces, ink copy, fine borders,
forest anchors, restrained lime highlights. Editorial: concepts, carousels, articles; working
papers and diagrams with exact editable labels. Expressive: campaigns, podcast, promos;
daylight, blue atmosphere and soft physical depth. Texture is optional, not a required overlay.

Choose a relevant approved reference from finals.json. All eleven carousel directions are valid;
Paper trail and Night shift deliberately have warm-paper/forest palettes. Preserve the artwork's
own approved values; do not flatten them to the website palette. The bundled templates are new
applications of this identity, not exact replicas or newly approved Studio Finals.
Generate image environments separately from exact text/logo overlays. Keep charts, labels and
logo geometry editable. Avoid a generic robot, new mascot, pixel/serif identity, neon orb,
heavy dark navy default or automatic floating dashboard. Use concrete, direct copy; no invented
performance claims. Client examples are fictional unless supported by supplied evidence.

Motion: one focal action per beat; calm fades, small movement, purposeful wipes. Guidance ranges
are 180–240 ms for controls and 450–700 ms for editorial reveals. These are implementation guidance,
not approval of a video. All six existing Studio motion files remain experiments. No default sonic
identity or synthetic presenter. Preserve camera transparency and keep captions away from faces.

## Save and check

Keep editable source and output in the existing client/deal/content folder. Add expression,
reference IDs and artifact paths to brand.lock.json. Keep private work private; /brand is public.
New intended Studio work starts in Experiments, through the existing promotion process.
Check actual fonts, exact logo, contrast, phone-scale reading, overflow, safe areas, PDF pagination
and timeline seeks. White on sky is for large type; small links use link blue on white. Lime needs
ink/forest text, never white. Caption text uses a solid forest plate on variable footage.
