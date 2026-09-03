# Video pipeline — the shared recipe under every format

Format-agnostic build steps for any short video in this workspace: a product update, an explainer,
an announcement, a result. The **look** is chosen from the account's style catalog; the **hook** is
governed by `references/hooks.md`; the **voice** by `references/voice.md`. This file is the
plumbing they all sit on.

## What stays constant

- **Vertical 9:16, 1080x1920** for Reels / Shorts / TikTok. Some older feed-first pieces are 4:5
  (1080x1350). Match the account's recent output rather than assuming.
- **Voice-forward.** One narration line drives each beat; visuals support the voice.
- **Dark and achromatic.** Chrome stays black and white; colour comes from the content and from
  status indicators, per the shared design system.
- **Runtime target ~40s**, and never past it without a stated reason (see `references/hooks.md`).
- **Content fills the frame: cards and imagery occupy ~40% of frame height.** A small floating card
  reads weak on a phone. Three of six re-renders on 2026-08-19 were the owner asking for bigger.

What changes per video is **the hero** — what fills the middle. Pick it from the message:

| Hero | When |
|---|---|
| Cover-art wall | A specific artist's catalog is the subject |
| Data or concept diagram | Explaining how something works |
| Typographic transition | The words themselves are the point: a rename, a number, a claim |
| Real product UI | A shipped feature. See "Rebuilding UI" below |
| Generated footage | Narrative pieces with a recurring character |

## 0. Prereqs

- Node >= 22 and **ffmpeg** on PATH.
- `npx skills add heygen-com/hyperframes` for the composition skills.
- API keys in a **gitignored `.env`** at the project root. Cloning a reference project's `video/`
  directory gives you a working `.env`; do not scatter new copies of keys.
- **Pin `hyperframes@0.7.5`** in `package.json` scripts. Fresh `hyperframes init` scaffolds pin a
  newer version whose renderer needs a newer Chrome than the cached headless shell, and every render
  fails with `ctx.drawElementImage is not a function`. Lint and inspect work on either.

## 1. Plan doc first, approved before a credit is spent

Write the plan (`SCRIPT.md` or `scene-plan.md`) **before** any code or audio. It opens with **the
why — theirs, then ours** as single sentences, then the arc and character, then a beat table:
`# · Window · Beat · On screen · VO`.

This is the artifact to review. VO copy is what costs money to generate and what carries the
message, so lock it first.

**Copy rules:**
- **No em dashes or en dashes** in anything published, including on-screen text.
- **Spell numbers and URLs for TTS**: "ten point one million", "recoupable **dot dev**".
- Ranges as "ten to sixteen times", not `10-16x`.
- **Every claim verified, every derived figure computed.** Sums and totals are computed from the
  saved source file, never typed from memory (an invented catalog-plays total shipped to a render
  on 2026-08-19 before the frame-pull caught it).
- Read every line aloud hunting for a **bare number with no unit**.

## 2. Scaffold

Clone the `video/` directory of the reference project for the chosen style rather than running
`hyperframes init`. You inherit the working `.env`, the fonts, the pinned version and the house CSS.

Author `index.html` as a **single composition**: all scenes are divs driven by one paused GSAP
timeline registered as `window.__timelines["main"]`.

Do not leave snapshot copies of `index.html` anywhere in the project. A second file carrying
`data-composition-id` fails lint with "exactly one root index.html".

## 3. Brand and fonts

Dark background, light foreground, shadow-as-border instead of CSS `border`. Fonts are copied into
the project's `fonts/` directory and referenced by `@font-face`.

In CSS use the **literal** family name (`"Geist Mono"`). The linter does not resolve
`var(--mono)`.

## 4. Rebuilding UI: components, not screenshots

**Owner ruling, 2026-08-07.** When a beat shows product UI, rebuild it as HTML components in the
composition using production as the reference. Do not composite screenshots.

1. **Quality.** A crop from a browser capture is upscaled to fill a 1080x1920 frame. A component is
   vector-crisp at any size.
2. **Control.** The state you need may not exist any more. A pre-fix state can require checking out
   the commit before the fix and serving it locally, and some states are simply gone.
3. **Safety.** A wide screenshot of a real list publishes everything else in it. Customer names,
   valuations and identifiers end up on camera. **Never screenshot a list wide.**

**Label everything.** Each panel carries an on-screen **provenance chip** saying what it is:
`measured on prod`, `real data, value hidden`, `rebuilt, no ui shipped`. Reconstruct freely, label
always.

**Build before/after as one markup block and one class.** A single component with a `.broken`
modifier that reproduces the actual defect is stronger evidence than a screenshot: on one build the
composition linter independently flagged exactly the elements the original bug report named, which
is the bug reproducing itself from the markup.

Rules that hold for any hero:

- **Determinism only.** No `Math.random()`, no `Date.now()`. GSAP `stagger:{grid:[r,c],
  from:"center"}` is fine; `from:"random"` is forbidden.
- Cap display font sizes so text stays inside the canvas. `hyperframes inspect` catches overflow.
- Set all initial hidden states with `gsap.set` at `t=0` so seeking stays correct.
- **Reveals resolve in place, in one continuous scene.** Never cut to a duplicate card to show the
  same content updated, and never put filler ("--", "...") in a data cell: a loading state is a
  skeleton bar kept alive by timeline-driven motion (sheen, pulse), resolving into the real value.
- **No dead frames.** The next scene enters as the prior exits; rows land with their panel; a
  counter's initial DOM text equals its tween's start value (it mounts, then moves, never jumps).
- **Stack vertically what would wrap horizontally** (flows, roster rows). Socials show brand
  glyphs, never written platform names.

## 4b. Reference discipline: what a seed image actually transmits

Learned the expensive way on 2026-09-02, across four separate failures in one build. Every one of
them was the same misunderstanding, so it is worth stating as a law:

> **A PLATE image transmits PLACE. A CHARACTER image transmits MEDIUM.**
> Pass both, but **never let two references disagree about the medium.**

What that predicts, and what actually happened:

| Attempt | Result |
|---|---|
| photoreal plate + clay character, plate first | photoreal moth in a photoreal room |
| photoreal plate + clay character, character first | same, reordering changed almost nothing |
| "rebuild this photoreal image in claymation" | photoreal with faint thumbprint texture |
| "redraw this photoreal image as 8-bit" | only the light beam pixelated |
| **styled character alone + the room described in words** | **correct medium, correct composition** |

**So you cannot edit a photoreal image into another medium.** The source image anchors realism
harder than any instruction in the prompt. To build the same location in another medium, seed on
**that medium's character** and describe the room in words, holding the composition constant with a
shared `ROOM` string reused verbatim across all media. Once the plate and the character are both
already in the medium, passing both together is safe and is what locks place and character at once.

**Corollary — declare the medium globally.** Medium is a property of the whole frame, so put it in
the first sentence of the prompt ("EVERY element in this image is modelling clay, including the
moth"), not implied by a reference. Do the same for the character's own style variants: a shared
plate string ending "a reference photograph of the object" silently forced photorealism and defeated
the felt, watercolour and clay variants until it was removed from the edit path.

**Corollary — say LESS for an empty frame.** A long prompt gives the model room to populate an empty
plate. An empty-field-under-stars shot came back twice with an invented woman walking through it,
the second time *after* the prompt was hardened with an explicit no-people paragraph. What fixed it
was cutting the prompt to two sentences. This is the opposite of the fix for populated plates, where
naming the unwanted prop does work.

**Test whether you need angle plates; do not assume.** `music-video.md` says plate-seeding locks the
camera and you must generate angle plates. On `meta/muse-image` that is **not true** if the camera
move is stated explicitly and emphatically: a top-down floor shot came straight out of a wide
eye-level hall plate on the first try, and four planned angle plates turned out to be unnecessary.
One image tells you which world you are in. Spend it before spending four.

**A plate earns its place only when two or more shots share it.** A plate for a single shot is
ceremony: it is a scene generation with the character left out, then re-edited to put it back. Two
generations to do one thing.

## 4c. Keyframed camera moves: `end_image_url`

The image-to-video models take a **first frame and a last frame** and fly the camera between them
(`minimax/h3-max-turbo`: `image_url` + `end_image_url`, `duration` 5 to 15). This is the single
biggest precision lever in the pipeline and it is free.

**Cost is per second of video, not per clip.** Ninety seconds costs the same as twenty clips or as
thirteen. So fewer, longer, keyframed shots cost nothing extra and buy:

- **Precision.** You are specifying where the shot starts *and* ends instead of hoping a prompt
  lands. Two near-identical wide stills stop being a repetitive cut and become the endpoints of one
  travelling shot.
- **Fewer seams.** Fewer cut-headroom bugs, fewer joins to get wrong.
- **Movement instead of repetition.** On the 2026-09-02 build, eight near-interchangeable wide shots
  collapsed into three continuous moves and the middle of the film stopped being static.

**Check consecutive stills as PAIRS before you spend motion on them.** A keyframed move interpolates
between them, so any discontinuity becomes a visible morph, which is the failure mode these models
are worst at. On the same build, a moth was a crumpled wreck in the start frame and pristine and
serene in the end frame, so a 10s move had to visibly repair it. Check scale, position and the
subject's state across every pair, and fix it at the still, not in the clip.

**Budget re-rolls on long moves.** Drift grows with duration. A 10s descent read "the camera falls
with it" literally, went *through* the floor and invented a mirrored upside-down warehouse below,
with two subjects on screen. The fix was pinning the geometry in the prompt: the floor is solid,
the camera never goes below it, there is no space beneath it, exactly one subject at all times.

## 5. Audio

Generation, voice choice, audio tags, loudness and verification all live in `references/voice.md`.
Read it before generating anything.

The pipeline-level rules:

- Lift the **stems**, not the final mux. It keeps the voice/bed balance under your control and
  leaves the render as the single source of truth.
- Keep raw un-normalized takes in a sibling directory named after the voice.
- Bed volume around `0.12` against voice at `1.0`.

## 6. Wire audio and timing

- Every `<audio>` and `<video>` needs a **unique `id`**. Without one the renderer silently drops it:
  a `<video>` with no `id` renders **frozen**, which looks like a still slideshow with perfect
  audio. `media_missing_id` is the most dangerous lint error there is.
- Timed elements need `class="clip"`, `data-start`, `data-duration`, `data-track-index`.
- Place each VO line at its real start from the generated durations, and align each scene window to
  its line. A ~0.3s pre-roll and ~0.35s to 0.55s gaps between lines read naturally.

### Captions

Burn in captions for every VO line. They are worth roughly 12% more watch time and 80% higher
completion, and most feed viewers are sound-off.

**A caption's fade-out must complete before the next one starts.** Fading out over 0.14s while the
next fades in 0.04s later puts two captions in the same place for 0.1s. Leave a gap larger than the
fade.

## 7. Lint, snapshot, render, then read frames

**Render is the expensive loop. Do not use it to look at your work.**

```bash
npm run check                                     # lint + validate + inspect. 0 errors required
npx hyperframes@0.7.5 snapshot --at 4.2,26,42.5 .       # ~15s, writes PNGs + a contact sheet
npm run render                                    # minutes. Only once the stills look right
```

`hyperframes snapshot` writes key-frame PNGs **and a contact sheet** in ~15s against minutes for a
render; pass `--at` with the times you care about. (Why this is law: SKILL.md's QC ladder — one run
burned seven renders on findings all visible in a still.)

Then, and only when the stills are right:

**`inspect` samples a fixed number of points across the timeline and will miss collisions between
them.** A caption collision survived two full passes because the sampler never landed while both
elements were visible.

So **read frames out of the finished MP4, every time**:

```bash
ffmpeg -ss <t> -i renders/<file>.mp4 -frames:v 1 out.png
```

Sample at the times **captions are on screen**, not at even intervals. A collision only exists while
both elements are visible, and the tallest scene is the one that collides.

Verify the render has **both** video and audio streams, the expected duration, and the expected
dimensions. A render returning the right duration is not evidence it looks right.

### Measure layout complaints, do not eyeball them

"Feels low / feels off" gets answered by extracting frames and computing the content's bounding box
across several beats. One run: "empty space at the top" measured as every card's top edge at exactly
y=960 of 1920 (the 50% line), which named the lost `translateY(-50%)` (the GSAP trap below).

### ⚠️ GSAP overwrites CSS `transform`, so never centre with one

**Centring must live in GSAP (`xPercent: -50, yPercent: -50`), never in a CSS
`transform: translate(-50%,-50%)` on an element GSAP animates.**

```css
/* WRONG — GSAP rewrites `transform` the moment it animates y/z/rotation */
.scene { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%); }
```
```js
/* RIGHT */
gsap.set(".scene", { xPercent: -50, yPercent: -50 });
```

Cost three renders on 2026-08-07: tweens animating `y`/`z`/`rotationY` rebuilt the transform matrix
and the CSS `translateY(-50%)` silently vanished. **A hand-tuned offset that corrects a layout you
cannot explain is a symptom — find the cause before shipping the nudge.**

Lint gotcha: CSS `transform: scaleX(0)` plus a GSAP `scaleX` tween conflict. Use `gsap.fromTo(...)`
and drop the CSS transform.

## 8. Ship

Publishing mechanics and per-platform traps live in `references/publish-verify.md` and in
`recoup-internal-social-ship-posts`. Log the post, declare the attribution state **at publish time**,
and re-pull engagement at ~48h.

## Project file map

```
<project>/
  SCRIPT.md            the plan doc, reviewed first
  post.config.mjs      per-platform copy + asset paths
  li-card/             purpose-built LinkedIn image, not a video-frame crop
  video/
    index.html         single composition, one timeline
    gen-voice.py       VO generation, voice + model recorded in the docstring
    audio_meta.json    durations per line
    assets/voice/      generated lines, plus raw originals in a named sibling
    fonts/
    renders/           MP4s
    thumbs/            cover frame
    .env               gitignored
```


## Build gotchas from the 2026-08-11 run

Four defects, all caught, each cheap to avoid next time.

**The linter cannot see inside a loop.** Scene and caption timing built in a `forEach` produced a
phantom `gsap_exit_missing_hard_kill` on a selector reported as `__unresolved__`, because the linter
resolves selectors and times statically. **Write the scene table out as static `tl.set` / `tl.to`
calls**, one line per scene, generated by a script if you like. It clears the error and makes the
timeline readable in a diff.

**A count-up cell must not carry its final value in the markup.** A strip hardcoded as `111` in the
HTML displayed 111 from frame one, then snapped to 0 and counted up when its tween began four
seconds later. Lint passed, `inspect` passed, and **frame QC at the exact count times caught it.**
Initialise every animated counter at its start value.

**`0 -> 0` is still not an animation.** A cell whose true value is zero should pop in with a scale
cue, not tween from zero to zero. Third time this has been written down.

**`data-layout-allow-occlusion` goes on the occluded text, not on the element doing the occluding.**
A strike-through bar over its own text trips `text_occluded`; marking the bar changes nothing.

**Use the nvm Node, not the system default.** The shell can reset to Node v17 between commands, and
`hyperframes` then dies with `SyntaxError: The requested module 'util' does not provide an export
named 'styleText'`. Prefix long-running build commands with
`export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"`.


## The QC gap: nothing checks the render against the script (2026-08-11)

Every gate in this pipeline checks the film **against itself**. `lint` checks the timeline, `validate`
checks the console, `inspect` checks layout, `ebur128` checks loudness, and frame QC checks that what
rendered is what the composition describes. **None of them check that the composition is what the
plan doc described.**

So a scene element can be specified, approved by the owner, and silently never built. It happened on
2026-08-12: the B1 Screen column read "over a dim map", the composition had no map in it, and the
film passed every gate and was handed over as finished. The owner caught it on playback.

**Add this to the pre-render checks, and it costs about a minute:**

> **Read the plan doc's Screen column back against the composition, one row at a time.** For each
> beat, name the element in the script and point at the markup that implements it. A row you cannot
> point at is a row you did not build.

It is the same discipline as reading frames out of the render rather than trusting the duration: the
artifact has to be checked against the intent, not only against itself. Cheapest at the moment the
composition is written, and cheap at pre-render. Expensive once it has been sent to the owner as done.
