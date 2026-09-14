---
name: recoup-internal-consulting-hyperframes-video
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. >\n  The house skill for making any VIDEO — create, edit, animate, or render a video,\n  animation, or motion graphic: a promo, explainer, captioned clip, reel, lyric\n  video, title card, lower-third, logo sting, PR/changelog video, or any moving\n  composition. Built on HeyGen's HyperFrames (renders video from HTML). This one\n  skill folds the whole toolkit: it routes intent to the right workflow MODE\n  (modes/) and leans on the engine knowledge packs (engine/). Defers all\n  look-and-feel to recoup-internal-consulting-tasteful-design and pulls brand tokens from\n  DESIGN.md (via that skill) — so output matches our system and taste by default.\n  Use for anything that MOVES or renders to MP4/WebM. For a STILL image (PNG\n  social post, carousel, thumbnail, OG card) use recoup-internal-consulting-graphics instead."
metadata: { "tags": "video, animation, motion-graphics, hyperframes, router, house-skill" }
---

# Consulting HyperFrames Video — start here

## Current brand

Recoup/Consulting/Business work defaults to **Recoup Sky**. Read `brand/GUIDE.md` and the workspace
`DESIGN.md`; explicit client/artist branding or a fidelity-only migration wins. Stage local resources:
`node <installed-skill>/brand/materialize.mjs <output-directory>`. Use its CSS, actual DM Sans/IBM Plex
Mono fonts, exact outlined SVG logo, and `brand/finals.json` reference IDs. No recurring brand setup
question. Save editable source and `brand.lock.json` with reference IDs/expression beside the output.
Marketing owns the authored identity; the bundled snapshot works without another checkout.


**Portable setup:** read `engine/runtime/SETUP.md` for the pinned runtime. Resolve bundled resources from this
installed skill and write outputs into the selected project. Brand fonts and identity come from that
workspace's `DESIGN.md` or supplied brief; preset fonts and logos are examples, not required defaults.
Keep original asset notices. Use approved workspace fonts for deliverables; optional legacy demo
assets do not grant commercial usage rights. Client stories and figures in templates are illustrative,
never evidence of a real result. Missing provider access remains a reported gap.

HyperFrames **renders video from HTML**: a composition is an HTML file whose DOM declares
timing with `data-*` attributes, whose animation runtime is seekable, and whose media
playback is owned by the framework. This skill is our **single, customized entry point** —
it folds HeyGen's 18-skill HyperFrames toolkit into one house skill we own and tune.

> **Still image, not video?** A PNG social post, carousel, thumbnail, banner, or OG card →
> use **`recoup-internal-consulting-graphics`**. This skill is for anything that **moves** (MP4/WebM/alpha).

## How this skill is organized (the fold)

| Folder | What it is | When you read it |
| --- | --- | --- |
| `modes/<name>/GUIDE.md` | The 11 **workflows** — the *kind* of video (explainer, promo, captions, …) | After routing, read the one matched mode |
| `engine/<name>/GUIDE.md` | The 6 **capability packs** — the HyperFrames "how it works" knowledge | On demand, when a mode points you to one |

**Resolving `/name` references.** The vendored files cross-reference each other with a leading
slash (e.g. `/hyperframes-core`, `/faceless-explainer`). These are routing hints inside this skill, not separately installed commands. Resolve every `/X` like this:

- `/hyperframes` → **this file** (the router).
- `/hyperframes-core`, `/hyperframes-cli`, `/hyperframes-animation`, `/hyperframes-creative`,
  `/hyperframes-media`, `/hyperframes-registry` → `engine/<name>/GUIDE.md`.
- everything else (`/faceless-explainer`, `/motion-graphics`, `/product-launch-video`,
  `/embedded-captions`, `/graphic-overlays`, `/pr-to-video`, `/music-to-video`,
  `/website-to-video`, `/slideshow`, `/general-video`, `/remotion-to-hyperframes`)
  → `modes/<name>/GUIDE.md`.

The upstream "if the workflow isn't installed, run `npx skills add …`" instructions **do not
apply** — every mode is already vendored here. Just open the file.

## Prerequisite — the engine (`npx hyperframes`)

The skills are the know-how; the **rendering engine is the `hyperframes` CLI**, run on demand:

```bash
npx hyperframes lint        # static HTML structure check
npx hyperframes validate    # runtime check (headless Chrome — catches JS errors, missing assets)
npx hyperframes render      # render the composition to video
```

- **Basic usage needs no API keys.** Optional integrations (set in the project, not committed):
  `GEMINI_API_KEY` for AI image captioning during website capture; TTS/voiceover providers
  (HeyGen / ElevenLabs / local Kokoro) and music — see `engine/hyperframes-media/GUIDE.md`.
- **Always `lint` and `validate` before previewing or calling a render done.** Deterministic
  rendering only: no `Date.now()`, no unseeded `Math.random()`, no render-time network fetches.
- Full CLI dev loop (init, inspect, preview, render, publish, lambda, doctor) →
  `engine/hyperframes-cli/GUIDE.md`.

## House taste — make it ours (read before building)

This is where "customize to our system and taste" lives. **Before designing any frame:**

1. **Defer look-and-feel to `recoup-internal-consulting-tasteful-design`.** That skill is the house authority on
   palette, type, spacing, motion restraint, and the anti-AI-slop checklist. Read it and apply it.
2. **Pull brand tokens from the canon — never invent them.** `recoup-internal-consulting-tasteful-design` carries the
   brand source of truth (`DESIGN.md`): palette, type, logo, and
   the footer signature defined by the selected workspace. For anything it doesn't cover (e.g.
   audience), ask — don't invent.
   - *Two `DESIGN.md` scopes — don't confuse them:* the **practice** brand is always
     `DESIGN.md`. Some modes (e.g. `website-to-video`, `general-video`)
     generate a **per-project** design spec at the video's own root (precedence `frame.md` →
     `design.md` → `DESIGN.md`) for that one deliverable — **seed it from the practice brand**, don't
     mistake it for the source.
3. **Voice/copy** (titles, narration, captions) follows `recoup-internal-consulting-copy-writer` —
   `references/voice-principles.md`. No em-dashes-as-crutch, no hype, real specifics.

**Spec defaults — state, don't ask:**

- **Aspect 16:9** by default. Use **9:16** only for a named vertical destination (Reels / Shorts /
  TikTok); **1:1 / 4:5** for in-feed social.
- **Narration / caption language** = the user's.
- **Motion serves meaning.** Ease, stagger, one timeline — never "everything animates at once."
  (The tasteful-design motion rules + `engine/hyperframes-animation` govern this.)

These never change the routing decision below.

## Pick a mode — intent router

Confirm **what the video is about** (its input/subject) first; committing to a mode *is* the
routing decision. Then read that mode's `GUIDE.md`.

| Mode (`modes/<name>/GUIDE.md`) | Use it for |
| --- | --- |
| `product-launch-video` | Marketing / launching / promoting a **product** — from its URL, a brief, or a script |
| `website-to-video` | Turning a **general website** into a video — site tour, portfolio, social clip from the site's visuals |
| `faceless-explainer` | **Explaining a topic / concept** from text — no product, no URL; every visual LLM-invented |
| `pr-to-video` | A **GitHub PR / code change** → changelog / feature-reveal / fix / refactor explainer |
| `embedded-captions` | Adding **captions / subtitles** to an existing talking-head video (footage untouched) |
| `graphic-overlays` | Packaging existing talking-head footage with **designed overlays** — lower-thirds, callouts, kinetic titles, pull-quotes |
| `motion-graphics` | A short, **unnarrated, design-led motion graphic** — kinetic type, a stat hit, a logo sting, a lower-third |
| `music-to-video` | A **music track** → a **beat-synced** video — lyric video, slideshow, or kinetic promo |
| `general-video` | **Anything else** — longer / multi-scene pieces, a static loop / poster, a custom composition |
| `slideshow` | A **slideshow / presentation / pitch deck** — discrete slides, fragments, branching, hotspots |
| `remotion-to-hyperframes` | **Porting an existing Remotion (React) composition** to HyperFrames (migration, not creation) |

**Disambiguation (only where confusable):**

- **Motion-first & unnarrated** (under ~10s, the motion *is* the message) → `motion-graphics`.
- **A URL or script** — markets a specific product → `product-launch-video`; a general non-product
  site → `website-to-video`; a GitHub PR link → `pr-to-video`; explains a concept with no product/site
  → `faceless-explainer`. Genuinely unclear → ask one question.
- **Existing footage** — plain spoken-word subtitles → `embedded-captions`; designed overlay cards →
  `graphic-overlays`. Neither edits the footage itself.
- **A music track is the input** with no narration → `music-to-video`.
- **Length is a guide, not a gate** — go to `general-video` only when clearly > ~3 min, or a static /
  loop / custom format.

## Capability map — the engine packs

Load these **on demand** when a mode points you to one (not full workflows on their own):

| Capability | Engine pack (`engine/<name>/GUIDE.md`) |
| --- | --- |
| Author / edit an HTML composition — `data-*` contract, clips, tracks, sub-comps, variables | `hyperframes-core` |
| Animate — atomic motion, scene blueprints, transitions, runtime adapters (GSAP / Lottie / Three.js / Anime.js / CSS / WAAPI / TypeGPU) | `hyperframes-animation` |
| Creative direction — `frame.md` / `design.md`, palettes, typography, narration, beat planning, audio-reactive | `hyperframes-creative` |
| Media — TTS voiceover, background music, transcription, background removal, captions | `hyperframes-media` |
| CLI dev loop — init, lint, validate, inspect, preview, render, publish, doctor | `hyperframes-cli` |
| Install registry blocks / components (`hyperframes add`) | `hyperframes-registry` |

## Style modes — the look libraries

"Modes for styles" draw from two vendored libraries; **`recoup-internal-consulting-tasteful-design` curates which
ones are on-brand** (don't just grab the flashiest):

- **Frame presets** (palette + type + design system per look): `engine/hyperframes-creative/frame-presets/`
  (e.g. `editorial-forest`, `bold-poster`, `blue-professional`, `cobalt-grid`, `broadside`, …) and
  `engine/hyperframes-creative/palettes/`.
- **Caption identities** (32 visual identities for captioned clips): `modes/embedded-captions/CATALOG.md`.

## Operating loop

1. **Confirm the input/subject** (one question max if unclear).
2. **Route** to a mode (table above) and read `modes/<name>/GUIDE.md`.
3. **Apply house taste** — read `recoup-internal-consulting-tasteful-design` (it carries the brand tokens from
   `DESIGN.md`), voice from `recoup-internal-consulting-copy-writer`. Pick an on-brand style preset.
4. **Build** the composition (HTML) per `engine/hyperframes-core`; **animate** per
   `engine/hyperframes-animation`; add **media** per `engine/hyperframes-media` as needed.
5. **Validate** — `npx hyperframes lint && npx hyperframes validate` (both must pass).
6. **Render** — `npx hyperframes render`; **review** the output against the tasteful-design checklist;
   iterate.

## Output hygiene

Brand tokens come from `recoup-internal-consulting-tasteful-design` → `DESIGN.md` (don't invent them).
Project render output goes in the project's own output dir, **never inside this skill folder**
(the vendored `.gitignore` files already block stray `*.mp4` / `*.webm` / frame dumps).
