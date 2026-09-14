# Planning (Step 3) — pick the brand, fill every frame

At Step 3 **you (the orchestrator)** turn the Step-2 skeleton into a complete, approved
`STORYBOARD.md`. You edit the **same file** in place: pick the brand spine, then for each
frame decide its **groups**, give each group a treatment, bind real beat anchors, and write
the copy.

Your mantra: **music is the spine; a template is a head start, not a cage; typography is the
floor and assets are an optional ingredient on the same beat grid.**

**You own WHAT, not HOW.** You name the template / primitives, the content, the brand, the
anchor seconds, and the intent. The frame-worker (Step 4) decides HOW — micro-timing,
realization, intra-frame cuts. **Never write millisecond tweens into the storyboard.**

## Inputs

- The Step-2 skeleton already in `STORYBOARD.md` — frames with `span_sec` + `pacing` + `mood` + `feel`.
- `audiomap.json` — timing truth; read the real anchor seconds inside each frame's span.
- `template-catalog.md` — the template selection menu.
- `motion-primitive-catalog.md` — the free-compose menu (L0 recipes).
- `montage.md` — asset treatments (only if the user supplied images/videos).
- User brief / supplied copy — topic, mood, exact words to keep.

## Step A — resolve the selected identity

For Recoup/Consulting/Business, generate the packaged Sky frame with the installed video skill's
`modes/faceless-explainer/scripts/build-frame.mjs --brand recoup-sky --hyperframes <project-directory>`.
For explicit artist/client work, use that supplied identity; a generic preset is only an explicit
alternative. Stage fonts and logo assets locally. Templates choose composition and motion, not brand.

Fill storyboard `style.font` and its working palette from frame.md, quoting exact values.
DM Sans is display/body; IBM Plex Mono is for labels/code. Load recoup-brand/brand.css in each frame.

## Step B — per frame, decide its groups

A frame is usually **one group** (one template or one free composition spanning the frame).
Subdivide into 2+ groups **only when a single treatment can't cover the frame** — e.g. a busy
opener plus a closing lockup. When you split, cut at a **real audiomap anchor** inside the
frame's span (a `key_moment` / `phrase` edge / onset-cluster gap), **never inside a `rolls[]`
run**, and keep every group **≥ ~1 bar**. Density does **not** force more groups — a dense
frame is usually ONE group whose template absorbs the density internally (a meta-template like
`poster-tile-mosaic`). **Group count tracks distinct treatments, not beats.**

## Step C — per group, pick a treatment (exactly one of three)

### A. Match a template

Read `template-catalog.md`. Match the group's `feel` + `mood` + `pacing`
to a template's **Reach for it when**; take the closest fit. Then bind it:

- Fill `params` (keys from the catalog entry) — your copy into text slots, palette from the brand spine, `duration` = the group's span length.
- Fill `role_bindings` with this group's **real anchor seconds** read from `audiomap.json` over its span (not example times).
- If the template's natural stop and the group's span end disagree, snap to the nearest anchor.

### B. Free-compose (no template fits)

Write a `free_design` — one visual thesis from `motion-primitive-catalog.md`
(a dominant system + the named L0 primitives + a density topology) + `anchors` (the real
beat / onset seconds the moves ride). Free-compose is a **first-class** choice, written as
carefully as a matched group — never a failure.

### C. Asset treatment (only when the user supplied assets and they fit)

Make it an `asset` group (`montage.md`). **Obey `pacing`:** on a `beat_cut`
frame use `beat_cut` (one clip per anchor) or `bg_under_text`; on a `phrase_flow` frame use
`ken_burns` or a slow crossfade — **never** per-onset hard cuts. Assets are additive: if none
fits a group, fall back to template / free (typography is the floor — a complete video needs
no assets).

## Copy (you own the words)

- Keep exact user words; else invent with taste, on the brief's mood.
- **Message vs texture:** a readable word holds ≥1 beat (headline 3–8, sentence 4–10), stable + focal; a word held <1 beat is texture (strobe / grid / ticks). Never force a message onto a sub-beat — demote it to texture.
- Place copy into the template's text params, onto a free group's anchors, or as an asset group's `overlay_copy`. Declare the anchor + accumulate / stagger intent; leave micro-timing to the worker.
- A closing logo / CTA lands on the final hit / hard stop and holds through trailing silence.

## Transitions (you do not emit them)

Everything is a **0ms hard cut** for now. **frame → frame** is owned by the assembler
(back-to-back files); adjacent `span_sec` already imply the cut. **group → group inside a
frame** is owned by the worker on its frame timeline; you only set each group's `span_sec`.

## Write + validate

Complete `STORYBOARD.md` (`storyboard-format.md`), then run
`node scripts/validate-plan.mjs` and fix every `✗`. Show the user a frame-by-frame summary and
iterate until approved.

## Self-check

- `frame.md` matches the selected identity; frontmatter `style.font` / `style.palette` are drawn from it (exact values).
- Every frame became ≥1 group; groups tile the frame span in order; no group < ~1 bar; no group boundary inside a `rolls[]` run.
- Each group is exactly one of template / free_design / asset.
- Template `params` keys match the catalog entry; `role_bindings` / `anchors` use real audiomap seconds.
- Asset treatments obey `pacing` (no `beat_cut` on a `phrase_flow` frame).
- Every group's palette draws from the one brand palette.
- `duration_s == audiomap.audio.duration_sec`; `validate-plan.mjs` passes.
