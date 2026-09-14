---
name: recoup-internal-consulting-proposal-designer
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Render approved proposal copy and commercial terms as a branded two-page HTML/PDF document. Use after proposal drafting and pricing, when the user needs the final visual artifact."
---

# Consulting Proposal Designer

## Current brand

Recoup/Consulting/Business work defaults to **Recoup Sky**. Read `brand/GUIDE.md` and the workspace
`DESIGN.md`; explicit client/artist branding or a fidelity-only migration wins. Stage local resources:
`node <installed-skill>/brand/materialize.mjs <output-directory>`. Use its CSS, actual DM Sans/IBM Plex
Mono fonts, exact outlined SVG logo, and `brand/finals.json` reference IDs. No recurring brand setup
question. Save editable source and `brand.lock.json` with reference IDs/expression beside the output.
Marketing owns the authored identity; the bundled snapshot works without another checkout.


Use the selected workspace and its `DESIGN.md`. Read the deal's approved copy, actual pricing,
scope, and agreement before rendering. `recoup-internal-consulting-proposal-drafting` and
`recoup-internal-consulting-pricing-builder` can prepare those inputs; this skill owns layout and rendering.

1. Read `assets/copy-and-design-frameworks.md` relative to this installed skill.
2. Copy `assets/proposal-template.html` into the deal's existing `02-proposals/` folder. Preserve the
   installed template; generated files and environments belong in the selected workspace.
3. Fill every slot, including `DOC_TITLE`, all `TIER_1_*` through `TIER_3_*` fields, steps, commercial
   terms, and brand fields. Escape text values. Use only reviewed markup in rich-content slots.
   All prices, service promises, and ownership claims require actual approval/source evidence.
4. Fill `BRAND_CSS` with `node <installed-skill>/brand/materialize.mjs --inline-css` output for Recoup.
   Fill `BRAND_LOCKUP_HTML` with the supplied outlined ink SVG (or a data-URI image); this makes the
   document independent of the plugin path and network. For another selected brand supply its own
   full CSS tokens and exact logo. Omit personal attribution unless requested. Font changes affect pagination.
5. Prepare a Python environment outside the plugin. Install Playwright and its Chromium browser,
   or an available WeasyPrint environment. These are alternative renderers, not hidden dependencies:
   `python3 -m venv <workspace-env>`; use that environment's Python for `-m pip install playwright`
   and `-m playwright install chromium`. WeasyPrint is optional and needs its platform libraries.
6. Run the installed helper with absolute paths:
   `"<workspace-env>/bin/python" "<installed-skill>/assets/render.py" "<workspace>/.../proposal.html"`.
   `--check` validates slots without rendering. `--engine chromium|weasyprint|auto` selects the engine.
   `CHROMIUM_PATH` optionally names an existing browser executable.
7. Inspect both pages, verify prices/terms and text overflow, and retain the editable HTML alongside
   the PDF. Target two pages; the renderer does not certify page count or visual fit.
8. Prepare delivery according to the agreed process. Do not invent a deadline, require a video,
   or send the proposal without authorization.
