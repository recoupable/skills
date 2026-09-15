---
name: recoup-internal-consulting-higgsfield
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Generate AI media for content by driving the Higgsfield CLI — photoreal or cinematic IMAGES, AI VIDEO / b-roll, branded PRODUCT shots, a face-consistent AI CHARACTER/avatar (\"Soul\"), and AI VOICEOVERS. Use on \"generate an image/photo/video with Higgsfield\", \"make a photorealistic / cinematic / AI-generated visual\", \"AI b-roll\", \"product photoshoot\", \"make an AI avatar / a recurring character\", \"AI voiceover\", or whenever content needs *generated pixels* that can't be drawn in HTML/CSS. NOT for typographic/designed stills (quote cards, frameworks, stat cards, carousels, thumbnails, OG images) → use recoup-internal-consulting-graphics; NOT for HTML-rendered/deterministic video (explainers, captions, motion-type, slideshows) → use recoup-internal-consulting-hyperframes-video. Bills credits (paid) — always preview cost first."
---

# Consulting Higgsfield

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

Generative AI media for the content flywheel. Where `recoup-internal-consulting-graphics` *designs* a still (HTML → PNG,
pixel-perfect text) and `recoup-internal-consulting-hyperframes-video` *renders* video from HTML, Higgsfield **generates
pixels from a prompt** — photoreal scenes, cinematic video, a face-consistent character, product
photography, voiceover — the imagery you can't author by hand.

The Higgsfield CLI is the client (browser auth, bills credits). **Command reference, auth, and cost
mechanics live in `integrations/higgsfield/AGENTS.md` — read it; don't restate it here.**

## Route first — is this even a Higgsfield job?

| The content needs… | Use | Why |
|---|---|---|
| A quote card, framework, stat card, carousel, thumbnail, OG image, banner — anything **typographic / designed** | `recoup-internal-consulting-graphics` | AI models render text unreliably; HTML gives pixel-perfect, on-brand type |
| An explainer, captioned clip, kinetic-type / motion graphic, slideshow — **HTML-rendered video** | `recoup-internal-consulting-hyperframes-video` | Deterministic, brand-driven, text-perfect |
| A **photoreal / cinematic / illustrative** image, **AI video / b-roll**, a **product shot**, a **recurring AI character**, an **AI voiceover** | **this skill** | Only generative AI can make pixels that don't exist yet |

**The power move is the combo:** generate the *imagery* in Higgsfield → add the *text + branding* on top
with `recoup-internal-consulting-graphics` (HTML overlay). Never bake headline copy into an AI generation — the type won't
be on-brand or reliably legible.

## Prerequisite

CLI installed + authed — `higgsfield account status` shows the plan + credits. If it errors with
`Not authenticated`, the user runs `higgsfield auth login` (browser; can't be automated). Full setup and
the command cheat-sheet → `integrations/higgsfield/AGENTS.md`.

## Workflow

1. **Confirm the brief + load the brand.** What's the asset, where does it go, what should it feel like?
   Pull look-and-feel from `recoup-internal-consulting-tasteful-design` (it carries `DESIGN.md` — palette, mood, the
   anti-AI-slop bar) and voice from `recoup-internal-consulting-copy-writer`. Encode brand *mood/palette* into the prompt;
   for anything the brand canon doesn't cover, ask — don't invent.
2. **Pick the model from the live catalog — never invent a name.** `higgsfield model list` (`--video` to
   filter) is the source of truth. Match the model to the job (image vs video vs voice vs product/marketing).
3. **Write the prompt.** Specific subject, composition, lighting, mood, palette (from `DESIGN.md`), and
   aspect ratio. Pass reference images with `--image <path|uuid>` (a local path auto-uploads). Keep text
   *out* of the image.
4. **Preview cost — every time (money).** `higgsfield generate cost <model> --prompt "…"`, and check
   `higgsfield account status` for balance. State the credit cost to the user before any paid run.
5. **Generate.** `higgsfield generate create <model> --prompt "…" [--image <id>] --wait` (blocks, prints
   the result URL). Add `--json` to parse. Image gen can take a couple minutes; video longer.
6. **Land the raw result.** Use the exact dated work folder supplied by the calling workflow.
   Otherwise create `work/YYYY-MM-DD-<task-name>/` in the selected workspace; reuse it for the task.
   Download original provider files there and record their URLs and hashes. Keep raw downloads
   out of Git; promote only selected delivery assets and compact provenance into the bundle.
7. **Finish + brand (usually a handoff).** Needs text/logo/framing → pass the generated image to
   `recoup-internal-consulting-graphics` as a background and overlay branded type. A clip for a post →
   `recoup-internal-consulting-hyperframes-video` can package it with captions/overlays.
8. **Promote keepers → `content/`.** Move only what you'll use into the draft's folder (or `content/_work/`
   while staging; `content/04-published/` once shipped). The repo isn't the archive — Higgsfield's cloud keeps
   job history (`higgsfield generate list`).
9. **Publish.** Hand the final asset + caption to `recoup-internal-consulting-linkedin-publisher` (Postbridge). Never
   auto-send — confirm the final creative + copy first.

## Soul characters (a consistent brand persona)

To reuse the *same* AI person across many posts (a recurring face, a mascot, the owner-as-avatar): train a
**Soul** once with `higgsfield soul-id …`, then reference it in later generations for a consistent look.
Training is an expensive, gated lane — confirm the spend **and** the reference images with the user before
running it. See `integrations/higgsfield/AGENTS.md` and `higgsfield soul-id create --help`.

## Cost discipline (paid — non-negotiable)

- **Preview before every spend** (`generate cost`); after a paid run, **cite the actual credit cost** —
  quote the real number from the CLI, don't estimate (evidence discipline).
- **Gate the expensive lanes — video + Soul training — behind explicit user go-ahead.** Iterate the look on
  a cheap image model first, then commit to the costly render.
- Never loop generations unattended — each `create` bills credits.

## Don't

- Don't bake headline / marketing **text into the AI image** — overlay it with `recoup-internal-consulting-graphics`.
- Don't **invent model names** — `higgsfield model list` is the source of truth.
- Don't **commit raw media to git** — it lives in gitignored `_work/`; promote only keepers to `content/`.
- Don't **auto-publish** — confirm the final creative + caption before `recoup-internal-consulting-linkedin-publisher` sends.
