
# HyperFrames Creative

## Selected brand

For Recoup/Consulting/Business, read `../../brand/GUIDE.md` and stage
`node <video-skill>/brand/materialize.mjs <project-directory>`. Use the packaged CSS/fonts/exact SVGs.
Identity is selected before frame.md; a frame can change layout/timing but cannot replace the brand.
Generic style catalogues below are alternatives for an explicit other brand, not Recoup defaults.
An explicitly selected client/artist identity or fidelity-only migration preserves that identity.
Record brand/version, expression and reference IDs with editable sources in the existing output folder.


**Portable setup:** read `../runtime/SETUP.md` for the pinned runtime. Resolve bundled resources from this
installed skill and write outputs into the selected project. Brand fonts and identity come from that
workspace's `DESIGN.md` or supplied brief; preset fonts and logos are examples, not required defaults.
Keep original asset notices. Use approved workspace fonts for deliverables; optional legacy demo
assets do not grant commercial usage rights. Client stories and figures in templates are illustrative,
never evidence of a real result. Missing provider access remains a reported gap.

Brand, pacing, style, narration, and composition direction. Use after the technical contract from `hyperframes-core` is in place.

For motion patterns, scene blueprints, transitions, and CSS marker effects, use `hyperframes-animation` — this skill is intentionally non-animation.

> **Read these two FIRST for any non-trivial composition — they override web instincts:**
>
> - `references/house-style.md` — "interpret the prompt, generate real content," the lazy-default list, and the background/foreground layer recipe. This is what turns a literal restyle into a _concept_.
> - `references/video-composition.md` — video-medium density, scale, foreground metadata (the "produced, not generated" detailing: data bars, registration marks, monospace readouts, 8-10 elements/scene).
>
> Skipping these is the single biggest cause of generic, web-page-looking output. They are not optional rows in the routing table below — for anything beyond a one-line edit, open both before you choose colors or write HTML.

## Workflow

1. If a project has a design spec, **read it first** and treat its frontmatter tokens as brand truth (colors, fonts, spacing, tone, constraints). Which file to read (precedence `frame.md` → `design.md` → `DESIGN.md`) and how to parse it (frontmatter = normative, prose = context) are defined once in `references/design-spec.md` — resolve and load per that doc.
2. If no design spec exists and the user asks for visual direction, choose a route:
   - Ready-made frame-preset (optional) → `frame-presets/` (adopt a `FRAME.md` as `frame.md`; see `references/design-spec.md`)
   - Named style or mood → `references/visual-styles.md`
   - Fast defaults → `references/house-style.md`
   - Interactive selection → `references/design-picker.md`
3. For multi-scene work, plan beats and rhythm before writing HTML → `references/beat-direction.md`. For scene transitions, jump to `hyperframes-animation/transitions/`.
4. For motion-heavy work, read `references/motion-principles.md` (high-level guardrails), then go to `hyperframes-animation` for atomic rules.

## Routing

| Topic                                                                    | Read                                           |
| ------------------------------------------------------------------------ | ---------------------------------------------- |
| Adopt a ready-made frame-preset as `frame.md` (optional)                 | `frame-presets/` · `references/design-spec.md` |
| Default palettes, motion, typography, lazy defaults to question          | `references/house-style.md`                    |
| Named style presets, mood-to-style routing                               | `references/visual-styles.md`                  |
| Palette-specific color tokens                                            | `palettes/*.md`                                |
| Composition patterns — PiP, text-behind-subject, title card, slide show  | `references/composition-patterns.md`           |
| Stats / infographic presentation                                         | `references/data-in-motion.md`                 |
| Structured expansion for open-ended prompts                              | `references/prompt-expansion.md`               |
| Video-medium density, scale, color, frame composition                    | `references/video-composition.md`              |
| Per-beat direction, rhythm planning, transition timing                   | `references/beat-direction.md`                 |
| Post-authoring spec verification (colors, type, corners, spacing, depth) | `references/design-adherence.md`               |
| High-level motion guardrails and GSAP-quality rules                      | `references/motion-principles.md`              |
| Font selection, pairings, rendered-video type guardrails                 | `references/typography.md`                     |
| Script pacing, tone, openings, number pronunciation                      | `references/narration.md`                      |
| Precomputed audio bands mapped to motion                                 | `references/audio-reactive.md`                 |

## Scripts

- `scripts/contrast-report.mjs` — inspect contrast warnings from rendered frames.
- `scripts/extract-audio-data.py` — pre-extract audio bands for audio-reactive compositions.
- `scripts/package-loader.mjs` — support script for bundled creative tooling.

Run from the repo root with explicit paths, for example:

```bash
python skills/hyperframes-creative/scripts/extract-audio-data.py <audio-file>
```

Animation analysis (`animation-map.mjs`) lives in `hyperframes-animation/scripts/`.

## Boundaries

- Do not override `hyperframes-core` technical rules.
- Do not require a design system for a minimal technical composition.
- Do not add extra scenes, narration, music, captions, or transitions unless the request calls for them or you first propose the expansion.
- Keep recipe references task-specific; do not read every reference for simple edits.
