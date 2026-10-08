---
name: recoup-internal-content-design-motion
description: Create and refine Recoup feature-announcement films, product demos, and marketing motion graphics with art direction, generated media, precise typography, and editable choreography. Internal only; use when the request explicitly contains recoup-internal and asks for motion design or a feature-launch video. Does not generate a customer release pack or publish content.
metadata:
  version: 1.1.0
---

# Internal motion design

Use only for explicitly requested `recoup-internal` work. This namespace is a routing convention, not access control. Work in the selected authorized private project; keep artist media, prompts, customer evidence and generation receipts there. This public skill contains only reusable instructions and original motion helpers.

## Establish the direction

Read the project's current brief, approved/rejected decisions, owning product implementation, brand assets and design instructions. Resolve the exact product name, destination and supported workflow from those sources. Do not inherit stale colors, URLs or claims from earlier films. Choose audience, one concrete promise, output dimensions, duration and audio source. Infer routine choices and begin; do not introduce extra approval rounds when the user has already authorized the work.

Read `references/gauntlet-loop.md` and run its build–critique–revision loop for full films; do not stop at the first render. Read `references/generated-assets.md` and execute image/video generation for the planned original media. Read `references/higgsfield-references.md` to select and inspect actual comparison films. Read `references/film-direction.md` for story, source variety, feature identity and pacing. Read `references/engine.md` before implementing mixed-media choreography. Scripts and assets ship alongside this skill; resolve their paths from this skill directory, not the project's working directory.

1. Write a compact direction: idea, visual rule, defining behavior, delivery and proof.
2. Inspect two or three relevant reference passages when available. Record what was actually seen and which decision it changes; do not infer official brand rules from a film.
3. Build the hardest handoff with real copy and actual source media before expanding the timeline.
4. Create the planned original image and video assets using available authorized generation tools. Inspect candidates, reject weak takes, and integrate selected outputs into the final render. Reuse approved assets when appropriate; do not silently replace required video generation with animated stills or stop at prompts. Follow `references/generated-assets.md` for tool discovery, generation, polling, selection and receipts. Keep exact lettering, UI and logos in controlled graphic layers.
5. Compose one focal read per beat. Carry an input or result identity through the action. Preserve footage playback through camera/layout changes.
6. Run fresh-context independent critics against the actual export and inspected reference. Convert their findings and user notes into concrete repairs; regenerate weak sources, rerender and repeat the comparison. Maintain a live progress document and preserve earlier versions. Follow `references/gauntlet-loop.md` for stopping conditions and honest blocked states.

## User notes are part of the production loop

Show each meaningful revision as a playable export. Record user notes against its exact version and time range. Translate “too slow,” “boring,” or “does not look like chat” into a testable change in source action, timing, hierarchy, typography or control semantics. Preserve what the user liked. Separate concept approval from asset, identity, pacing and final-film approval. Do not defend a failed direction because an earlier critic passed it.

Continue authorized revisions without asking permission each round. If the user says the result still misses the brief, reopen the relevant comparison. Finish the autonomous loop before asking for final taste approval; only request missing inputs or additional spending authorization when actually needed. A narrow edit may use targeted re-review, but any full-film completion claim requires a fresh complete-export review.

## Recoup music announcement default

Unless the brief overrides it, begin with an audio file dropped into a recognizable chat composer, one plain-language request, and send; the agent does the subsequent work. Use neutral application chrome, normal input typography, a compact attachment and send control. Put expressive design into the results. Do not replace chat with an oversized brand-colored advertising panel or invent extra manual forms.

This is a storytelling default, not proof that a depicted workflow is live. Verify product behavior separately and label illustrative UI/generated concepts honestly. A song upload does not itself prove streaming availability, email collection, consent or a business result.

For an abundance brief, keep setup brief and show overlapping creation with a clear dominant result. Different crops of one image are variations, not independent creative concepts. Choose the soundtrack passage before timing the edit; preserve natural speed unless explicitly directing a speed change.

## Build and deliver

Use the existing renderer when appropriate: DOM/SVG, Canvas, 3D or a motion editor. The bundled kernels are optional deterministic helpers, not a renderer, generative-media service or deployed Recoup API. Keep source media clocks, inner shot edits, outer layout/camera and soundtrack timing distinct. Save editable cues, trims, crop decisions and asset hashes beside the final export.

Read `references/review-and-delivery.md` before calling the work finished. Deliver the actual playable export, editable source, asset provenance and a concise statement of what was reviewed. Distinguish technical checks, frame inspection, playback, listening, human approval and publication. An approved concept is not approval of every asset. Do not post, schedule or publish unless authorized.

For helper changes, run the bundled tests with Node.js (standard library only):

```sh
node scripts/test-motion.mjs
node scripts/test-scene.mjs
node scripts/test-choreography.mjs
node scripts/test-experience.mjs
```

Source lineage and hashes are in `references/upstream.json`. These tests check mechanics, not taste or final rendered quality.
