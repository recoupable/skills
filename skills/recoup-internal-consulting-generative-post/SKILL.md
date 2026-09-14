---
name: recoup-internal-consulting-generative-post
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Produce a finished, post-ready branded VISUAL by compositing a Higgsfield-generated background (photoreal / cinematic / illustrative imagery) with an on-brand HTML text overlay. This is \"the power move.\" Use on \"make a post image / hero image / banner / OG card with a real/cinematic/AI background and a headline\", \"put a headline on a generated image\", \"branded visual over a photo/AI background\", or whenever a social asset needs BOTH generative imagery AND clean, on-brand type. Orchestrates recoup-internal-consulting-higgsfield (the background) + recoup-internal-consulting-graphics (the overlay) and defers aesthetics to recoup-internal-consulting-tasteful-design. NOT for a pure typographic graphic on a solid/gradient field (no generated photo) → recoup-internal-consulting-graphics; NOT for raw generation with no text overlay → recoup-internal-consulting-higgsfield."
---

# Consulting Generative Post

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
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

The power move: **generate imagery neither HTML nor a stock library can give you (Higgsfield), then
lay pixel-perfect on-brand type over it (recoup-internal-consulting-graphics).** Each tool does the half it's best at —
AI makes the photoreal/cinematic field; HTML makes legible, on-brand text. Neither alone produces this.

> **This skill locks the WORKFLOW; the DESIGN is a living layer.** The steps below are stable. The
> *visual treatment* — scrim recipe, type placement, which template, composition — is intentionally
> kept malleable: it lives in `references/overlay-shell.html` and defers to `recoup-internal-consulting-tasteful-design`
> (`DESIGN.md`). Iterate the look there without touching the process here.

## Prerequisites
- `recoup-internal-consulting-higgsfield` usable (CLI authed — `higgsfield account status` shows credits).
- `recoup-internal-consulting-graphics` rendering path available (`npx playwright screenshot`).
- Brand canon: `DESIGN.md` (via `recoup-internal-consulting-tasteful-design`); voice via `recoup-internal-consulting-copy-writer`.

## Workflow (stable)

1. **Pick the canvas.** Default LinkedIn feed **1080×1350 (4:5)**; use 1:1, 9:16, or 1.91:1 (OG) per the
   destination. Sizes/safe-zones → `recoup-internal-consulting-graphics` (`references/dimensions.md`).
2. **Generate the background** with `recoup-internal-consulting-higgsfield`. Encode the brand *mood/palette* from
   `DESIGN.md` into the prompt; **reserve negative space** where the headline will sit (e.g. "generous
   empty space, upper-left"); demand **no text/words** in the image. Preview cost, generate, and land the
   raw file in `integrations/higgsfield/_work/`.
3. **Inspect the actual result — don't trust the prompt.** Open the generated image and find the real
   clearest region; AI rarely honors "negative space on the left" exactly. *That* region is
   where the text goes, and the focal element (a streak, a subject) is what the text must not collide with.
4. **Compose the overlay** with `recoup-internal-consulting-graphics`. Start from `references/overlay-shell.html` (or a
   `recoup-internal-consulting-graphics` template like `statement`): swap the template's CSS color field for the generated
   image (`background-size:cover`) and add a **directional legibility scrim** lightening or darkening only the text side
   (keep the focal element visible). Brand tokens from `DESIGN.md`; **never bake text into the AI image** —
   that's the whole point of overlaying it here.
5. **Render + review.** `npx playwright screenshot --viewport-size="W,H" "file:///…/overlay.html" "…/out.png"`.
   Then **look at the PNG**: does the headline read at thumbnail scale, clear of the focal element, exact company mark present where appropriate, readable contrast? Iterate the overlay (not the workflow) until clean.
6. **Promote + hand off.** Move the keeper into `content/` (raw stays gitignored in `_work/`). For LinkedIn,
   pass the final asset + caption to `recoup-internal-consulting-linkedin-publisher` — **drafts only, never auto-send.**

## The overlay technique (what's new vs. recoup-internal-consulting-graphics)

`recoup-internal-consulting-graphics` templates sit on a CSS color field; here the field is a **photo + scrim**:

- **`background-size:cover; background-position:center`** fits a square generation into a 4:5 / 9:16 canvas.
- **Scrim** = a light or forest wash behind the text, selected after inspecting the actual image.
  The shell defaults to ink text on light; its `dark` class switches to white type and the white logo.
- Reuse a `recoup-internal-consulting-graphics` template's *type treatment* (e.g. `statement`: DM Sans headline + limited lime emphasis); only the field changes.

## Cost discipline (inherits recoup-internal-consulting-higgsfield)
Preview every generation (`higgsfield generate cost …`) and **cite the actual credits** after. The overlay
render is free (local Playwright). Gate video/Soul backgrounds behind explicit go-ahead.

## Don't
- Don't bake headline/marketing **text into the AI image** — overlay it.
- Don't **commit raw media** — `_work/` is gitignored; promote only keepers to `content/`.
- Don't **invent Higgsfield model names** — `higgsfield model list` is the source of truth.
- Don't **auto-publish** — confirm the final creative + caption first.
