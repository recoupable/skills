---
name: recoup-internal-consulting-graphics
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Generate on-brand social media graphics for any platform and format — feed posts, carousels, stories/reels covers, banners and headers, profile pictures, YouTube thumbnails, Pinterest pins, Open Graph link cards, and ad creative. Renders HTML to PNG via Playwright at correct platform dimensions with safe zones. Use when asked to create a social post, carousel, slide deck for social, story/reel, cover/banner, profile picture, thumbnail, pin, OG image, or to resize/adapt one design across multiple platforms and aspect ratios (1:1, 4:5, 9:16, 16:9, 1.91:1, 2:3, banners, pfps). Visual styles live as templates in references/; output-craft playbooks (thumbnail, carousel, …) live in references/recipes/; dimensions and safe zones in references/dimensions.md. Static images only — for video, motion graphics, or anything animated, use recoup-internal-consulting-hyperframes-video."
---

# Consulting Graphics

## Required public-content gate

Read `references/public-content-quality.md` before drafting, reviewing, illustrating or publishing.
It governs competitor/source restrictions, plain-language explanations, cover comprehension and
revision evidence. Apply it to every public format; older style examples do not override this gate.

## Current brand

Recoup/Consulting/Business work defaults to **Recoup Sky**. Read `brand/GUIDE.md` and the workspace
`DESIGN.md`; explicit client/artist branding or a fidelity-only migration wins. Stage local resources:
`node <installed-skill>/brand/materialize.mjs <output-directory>`. Use its CSS, actual DM Sans/IBM Plex
Mono fonts, exact outlined SVG logo, and `brand/finals.json` reference IDs. No recurring brand setup
question. Save editable source and `brand.lock.json` with reference IDs/expression beside the output.
Marketing owns the authored identity; the bundled snapshot works without another checkout.


**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

Generate on-brand social media graphics from content, at the right dimensions for any platform and placement. HTML → Playwright screenshot → PNG. **Static images only — for video, motion graphics, or anything animated, use `recoup-internal-consulting-hyperframes-video`.**

**Three choices** drive every graphic:
- **Format** = the dimensions/aspect ratio (square, 4:5, story, banner, pfp, thumbnail, pin…). See `references/dimensions.md`.
- **Template** = the *style* (layout + which color field + the dominant element). See `references/<template>.md`.
- **Recipe** = the *output craft* — what makes a great thumbnail vs carousel vs OG card. See `references/recipes/<output>.md`.

Any output is a **Format × Template × Recipe** composition — e.g. a thumbnail = `recipes/thumbnail` × the `statement` style × 1280×720.

All templates share **one brand DNA** — palette, type, logo, footer — defined in
**`DESIGN.md`**. That's the trick: a bold infographic and a dark quote card look like
the *same brand* without looking *the same*. Pick the template by what the content needs, and **vary it
across a series** — making everything look identical is the failure mode this kit exists to fix.

You can render the *same* template at *many* formats — that's how you create one design for every platform and size.

## Setup

**Step 0: Load the brand + the kit**

1. Read the project's top-level **`DESIGN.md`** — the brand source of truth: the CSS palette, fonts, the
   selected Recoup package, optional author attribution, and composition
   principles every template builds on. **Always read this before composing.** Never hardcode a value
   that disagrees with it; for anything it doesn't cover (e.g. audience), ask — don't invent.
2. Use the brief’s format; otherwise default to a 1080×1350 feed graphic. Choose a relevant approved
   reference from `brand/finals.json`; no local setup file or brand questionnaire is required.

## Workflow

1. **Identify the format(s).** What is being made and for where? Look up the exact dimensions, aspect ratio, file specs, and safe zone in `references/dimensions.md`. If the user names a platform but not a placement, default to the highest-engagement feed format: **1080×1350 (4:5)**.
2. **Choose the template** (the composition) by what the *content* is, not a default look: `framework-blocks` for teaching/lists/how-tos, `statement` for hooks/POVs/quotes/announcements, `stat` for a number or proof, `editorial` for the occasional restrained piece. Read `DESIGN.md`, then `references/<template>.md`. Across a batch, deliberately mix them. **Then read the recipe** for the output (`references/recipes/<output>.md` — e.g. thumbnail, carousel) for its craft bar.
3. **Apply brand from `DESIGN.md`.** Use the brand name, logo SVG, and handle for footers/close slides/profile marks.
4. **Compose for the format.** Match the layout to the canvas — a 4:5 feed post, a 9:16 story, a 4:1 banner, and a circular pfp are different compositions, not the same art stretched. Respect the safe zone for the format (see dimensions.md). For multi-slide carousels, one idea per slide.
5. **Stage `brand/materialize.mjs` in the output directory and load `recoup-brand/brand.css`. Generate HTML** sized to the target canvas. Set `body { width: Wpx; height: Hpx; }`. Replace `BRAND_NAME` with the brand from `DESIGN.md`; use its logo SVG.
6. **Render a PNG intermediate** at the matching viewport in the task's dated work folder.
   Use the workspace's supported browser/rendering tool; when Playwright CLI is available:

   ```bash
   npx playwright screenshot --viewport-size="WIDTH,HEIGHT" "file:///abs/path/graphic.html" "/abs/path/graphic.png"
   ```

7. **Wait for `document.fonts.ready` before capture; verify DM Sans actually loaded. Review each render visually** against the safe zone and the template's quality checklist. If cluttered, split or simplify. If text is hard to read at phone scale, increase size/contrast.
8. **Iterate** until clean.

## Create once, adapt everywhere

To ship the same design across platforms and sizes:

- **Within the vertical/square family** (1:1, 4:5, 3:4, 9:16 — all 1080px wide), one HTML can serve all sizes if type and spacing use **width-relative units** (`vw`) instead of fixed `px`. Then only the canvas height changes between sizes and the composition holds. Re-render the same file at each viewport:

  ```bash
  HTML="file:///abs/path/graphic.html"
  for size in 1080,1080 1080,1350 1080,1920; do
    npx playwright screenshot --viewport-size="$size" "$HTML" "out/graphic-${size/,/x}.png"
  done
  ```

- **Landscape, banners, profile pictures, thumbnails** (16:9, 1.91:1, 3:1, 4:1, circle) have very different proportions — give them a **bespoke composition** rather than cramming the portrait layout in. Keep the same colors, type family, and logo so the set stays cohesive.
- **Keep critical content centered.** For 9:16, the *center-square method* (all key elements inside a centered 1080×1080) lets one asset survive Feed/Story/Reel crops. See dimensions.md.

## Available templates (the kit — all share `DESIGN.md`)

| Template | Field | Dominant element | Best for | Reference |
|----------|-------|------------------|----------|-----------|
| `framework-blocks` | light + dark header band | a named, color-coded framework (numbered or acronym variant) | teaching / "save this" infographics, lists, how-tos — the reach + lead-magnet engine | references/framework-blocks.md (`references/framework-blocks.md`) |
| `statement` | sky or forest | one huge line | hooks, contrarian POVs, manifestos, quote cards, announcements | references/statement.md (`references/statement.md`) |
| `stat` | dark or light | one giant number | data drops, proof, milestones, before/after | references/stat.md (`references/stat.md`) |
| `editorial` | crisp light, minimal | a clear DM Sans headline | the occasional restrained, premium piece — **one option, not the default** | references/editorial.md (`references/editorial.md`) |

> **Taste authority:** `recoup-internal-consulting-tasteful-design` is the house north star for look-and-feel across
> every medium; this kit is its still-graphics implementation. Brand tokens (color/type/logo/footer)
> live in **`DESIGN.md`** — read it first. Choose by the content; a
> single minimal template is what made everything samey, so `editorial` is one choice, not the floor.

To add a template: create `references/<name>.md` (visual identity, layout rules, a complete HTML shell
using the tokens, quality checklist).

## Recipes — output craft (what makes each output *good*)

Templates give you the *style*; **recipes give you the craft bar for a specific output**. Read the recipe
for what you're making, then compose it with a template + format.

| Output | Recipe | Typical format × template |
|---|---|---|
| **Thumbnail** (YouTube, blog hero, link/OG preview) | references/recipes/thumbnail.md (`references/recipes/thumbnail.md`) | 1280×720 / 1200×630 × `statement`·`stat` |
| **Carousel** (LinkedIn / IG swipe-through) | references/recipes/carousel.md (`references/recipes/carousel.md`) | 1080×1350 ×N × `framework-blocks`·`statement` |

To add a recipe: create `references/recipes/<output>.md` (when to use, the craft bar, layout pattern,
render notes, quality checklist). **Separation of concerns:** recipes own *output craft* · templates own
*style* · `dimensions.md` owns *size* · `DESIGN.md` owns *brand*.

## Dimensions & safe zones

All platform sizes, aspect ratios, file specs, profile/banner safe zones, 9:16 story safe zones, and design best practices live in **references/dimensions.md (`references/dimensions.md`)**. Read it whenever choosing or adapting a format. The six canvases that cover ~90% of placements: `1080×1080` (1:1), `1080×1350` (4:5), `1080×1920` (9:16), `1920×1080` (16:9), `1200×630` (1.91:1), `1000×1500` (2:3).

## Slide/format count guidelines

- **LinkedIn carousel:** 5–10 slides (5 min for narrative, 8–10 for deep dives). Export to PDF for upload.
- **Instagram carousel:** 5–7 slides; up to 20 supported. Square or 4:5; first slide sets the ratio.
- **X thread companion:** 3–5 punchy slides.
- **Single graphics** (hero post, quote card, announcement): one strong composition beats a thin carousel.

## Content principles

The full "bold, not boring" stance + the anti-AI-slop checklist live in **`recoup-internal-consulting-tasteful-design`**
(`DESIGN.md`). The essentials:

- Every graphic/slide earns its place — if it adds no new idea, cut it.
- **Choose the expression**: white/paper editorial, functional white, or expressive sky/forest. Calm sky gradients are part of the current identity.
- **One thing is huge** — a hook, a number, or a framework, legible as a thumbnail.
- **Color carries meaning:** `--accent` for structure, one `--signal` pop for the eye-hit. Never rainbow.
- **Make it saveable:** real numbers, named frameworks, worked examples (specificity is the design).
- The hook (slide 1 / the headline) decides whether anyone engages — spend disproportionate effort there.
- **Vary the template across a series.** Sameness is the failure mode this kit exists to fix.
- Mobile-first: if it doesn't read at phone-thumbnail scale, it fails.

## Output

Preserve the workspace or bundle's delivery format. For existing WebP bundles, convert the rendered
PNG intermediate to WebP, verify dimensions, text and visual quality, and save to the existing
WebP path. Keep PNG intermediates in `work/YYYY-MM-DD-<task-name>/`, not as duplicate bundle
assets. PNG remains valid when it is the requested delivery format. If a distribution surface
explicitly requires a separate PNG OG card, export that named derivative for that surface; it does
not replace the article's WebP image. Keep editable HTML alongside final delivery assets.
