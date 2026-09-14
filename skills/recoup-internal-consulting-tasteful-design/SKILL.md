---
name: recoup-internal-consulting-tasteful-design
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Apply the current Recoup identity across graphics, video, slides, proposals and interfaces. Resolves brand selection, packaged fonts and exact logos, cross-media composition, and visual checks; explicit client brands can override house identity."
metadata: { "tags": "design, taste, brand, visual, motion, look-and-feel, anti-slop, house-authority" }
---

# Consulting Tasteful Design

The shared visual authority for Recoup, Consulting and Business. Keep current workspace folders;
resolve skills by installed name. Brand inputs never require access to another private checkout.

## Resolve the identity first

Read the workspace DESIGN.md and explicit brief. House work defaults to **Recoup Sky** from
brand/GUIDE.md (`brand/GUIDE.md`) and brand/brand.json (`brand/brand.json`). Marketing owns the authored
identity; this versioned package distributes its reviewed fonts, exact logo SVGs and approved
reference manifest. Use the bundled package when marketing is unavailable. Do not ask the user to
reselect Recoup on each run. An explicit client/artist identity or fidelity-only migration wins.

Stage with `node <installed-skill>/brand/materialize.mjs <output-directory>`. Each primary media skill
carries a checked copy of this package, so its installation is self-contained. Exact CSS/font data
for standalone HTML is available with `--inline-css`. Do not use a local computer path or Google
Fonts network import. Wait for document.fonts.ready before capture.

## Apply the identity

- **Functional:** clear white reports, proposals, decks and dashboards; ink text, fine borders,
  forest anchors, sky links, restrained lime emphasis.
- **Editorial:** papers, notes, concepts and diagrams; DM Sans with exact editable labels. Choose
  from the eleven approved carousel directions in brand/finals.json. Warm paper and Night shift
  forest are valid approved expressions.
- **Expressive:** daylight, sky atmosphere, Blue sweep, considered physical materials; let the
  content supply the focal point. Soft depth is useful; decoration is optional.

DM Sans headlines 450–500, body 400. IBM Plex Mono 400 for short labels/code/metadata only.
Use supplied outlined logo geometry; no regenerated marks. Company media need no personal-name
footer. Author attribution is an explicit content choice. Direct, concrete copy follows
recoup-internal-consulting-copy-writer; figures and customer claims still need primary evidence.

For generated imagery, create environments first and composite exact editable type and logos.
For video, resolve brand before frame.md: frames own composition, pacing and placement, while
brand.json owns identity. Generic vendor presets never override selected Recoup colors or fonts.
Use one focal action per beat, calm fades/small reveals and static grain. No automatic glow loops,
heavy serif headings, robot/mascot, or unapproved sonic identity. Existing Studio motion remains
experimental; approved stills are references, not approval of a new animation.

## Check the artifact

Verify loaded font faces, exact logo, visible contrast, safe areas, mobile-scale reading, overflow,
and actual PDF pagination. For motion check multiple timeline seeks and footage occlusion. Preserve
client source appearance when explicitly selected. Save editable source and brand.lock.json with
expression, selected reference IDs and output paths alongside the deliverable. Keep existing private
output ownership; /brand is public and new intended Studio assets start in Experiments.

## Maintaining the package

Update from marketing's root DESIGN.md / brand-studio/DESIGN-SYSTEM.md and committed Finals only.
Keep source revision and hashes in brand.json, bump version, then run scripts/sync_brand.py from the
plugin root. scripts/sync_brand.py --check rejects differing consumer copies. Do not edit those copies
independently. Preserve original vendor-font notices and alternatives for explicit other brands.
