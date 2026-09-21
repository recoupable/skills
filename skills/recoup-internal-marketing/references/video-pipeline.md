# Video pipeline — the shared recipe under every format

Format-agnostic build steps for any short video in this workspace: a product update, an explainer,
an announcement, a result. The **look** comes from the account's style catalog, the **hook** from
`references/hooks.md`, the **voice** from `references/voice.md`. This file owns the mechanics;
`SKILL.md` owns the gates and the order they run in.

## What stays constant

- **Default: vertical 9:16, 1080x1920** for Reels / Shorts / TikTok. Some older feed-first pieces
  are 4:5 (1080x1350); match the account's recent output rather than assuming.
- **Voice-forward.** One narration line drives each beat; visuals support the voice.
- **Dark and achromatic.** Chrome stays black and white; colour comes from the content and from
  status indicators, per the shared design system.
- **Runtime target ~40s**, never past it without a stated reason (see `references/hooks.md`).
- **Content fills the frame: cards and imagery occupy ~40% of frame height.** A small floating card
  reads weak on a phone; three of six re-renders on 2026-08-19 were the owner asking for bigger.

What changes per video is **the hero** — what fills the middle. Pick it from the message: a
cover-art wall (a specific artist's catalog), a data or concept diagram (how something works), a
typographic transition (the words are the point: a rename, a number, a claim), real product UI (a
shipped feature, see §4), or generated footage (narrative pieces with a recurring character).

## 0. Prereqs

- Node >= 22 and **ffmpeg** on PATH.
- `npx skills add heygen-com/hyperframes` for the composition skills.
- API keys in a **gitignored `.env`** at the project root. Cloning a reference project's `video/`
  directory gives you a working `.env`; do not scatter new copies of keys.
- **Pin `hyperframes@0.7.5`** in `package.json` scripts. Fresh `hyperframes init` scaffolds pin a
  newer version whose renderer needs a newer Chrome than the cached headless shell, and every
  render fails with `ctx.drawElementImage is not a function`. Lint and inspect work on either.

## 1. Plan doc first, approved before a credit is spent

Write the plan (`SCRIPT.md` or `scene-plan.md`) **before** any code or audio: **the why — theirs,
then ours** as single sentences, then the arc and character, then a beat table
`# · Window · Beat · On screen · VO`. VO copy costs money and carries the message, so lock it first.

**Copy rules:**
- **No em dashes or en dashes** in anything published, including on-screen text.
- **Spell numbers and URLs for TTS**: "ten point one million", "recoupable **dot dev**"; ranges as
  "ten to sixteen times", not `10-16x`.
- **Every claim verified, every derived figure computed** from the saved source file, never typed
  from memory (an invented catalog-plays total reached a render on 2026-08-19 before frame QC caught it).
- Read every line aloud hunting for a **bare number with no unit**.

## 2. Scaffold

Clone the `video/` directory of the reference project for the chosen style rather than running
`hyperframes init`: you inherit the working `.env`, the fonts, the pinned version and the house CSS.
Author `index.html` as a **single composition**: all scenes are divs driven by one paused GSAP
timeline registered as `window.__timelines["main"]`. Do not leave snapshot copies of `index.html`
in the project; a second file carrying `data-composition-id` fails lint ("exactly one root index.html").

## 3. Brand and fonts

Dark background, light foreground, shadow-as-border instead of CSS `border`. Fonts are copied into
the project's `fonts/` directory and referenced by `@font-face`. In CSS use the **literal** family
name (`"Geist Mono"`); the linter does not resolve `var(--mono)`.

## 4. Rebuilding UI: components, not screenshots

**Owner ruling, 2026-08-07.** When a beat shows product UI, rebuild it as HTML components using
production as the reference. Do not composite screenshots: an upscaled capture crop is soft where a
component is vector-crisp; the state you need may be gone (a pre-fix state can mean checking out
and serving the pre-fix commit); and a wide screenshot of a real list publishes customer names,
valuations and identifiers. **Never screenshot a list wide.**

**Label everything.** Each panel carries an on-screen **provenance chip**: `measured on prod`,
`real data, value hidden`, `rebuilt, no ui shipped`. Reconstruct freely, label always.
**Build before/after as one markup block and one class**: a `.broken` modifier that reproduces the
actual defect is stronger evidence than a screenshot.

Rules that hold for any hero:

- **Determinism only.** No `Math.random()`, no `Date.now()`. GSAP `stagger:{grid:[r,c],
  from:"center"}` is fine; `from:"random"` is forbidden.
- Cap display font sizes so text stays inside the canvas. `hyperframes inspect` catches overflow.
- Set all initial hidden states with `gsap.set` at `t=0` so seeking stays correct.
- **Reveals resolve in place, in one continuous scene.** Never cut to a duplicate card to show the
  same content updated; never put filler ("--", "...") in a data cell. A loading state is a skeleton
  bar kept alive by timeline-driven motion (sheen, pulse), resolving into the real value.
- **No dead frames.** The next scene enters as the prior exits; rows land with their panel; a
  counter's initial DOM text equals its tween's start value (it mounts, then moves, never jumps).
- **Stack vertically what would wrap horizontally** (flows, roster rows). Socials show brand
  glyphs, never written platform names.

## 4b. Reference discipline: what a seed image transmits

> **A PLATE image transmits PLACE. A CHARACTER image transmits MEDIUM.**
> Pass both, but **never let two references disagree about the medium.**

- **You cannot edit a photoreal image into another medium** (2026-09-02: four attempts, four
  photoreal results). The source image anchors realism harder than any prompt. Seed on **that
  medium's character** and describe the room in words, holding composition with a shared `ROOM`
  string reused verbatim across media. Once plate and character are both in the medium, passing
  both together locks place and character at once.
- **Declare the medium in the first sentence** ("EVERY element in this image is modelling clay,
  including the moth"): medium is a property of the whole frame, never implied by a reference. A
  plate string ending "a reference photograph of the object" silently forces photorealism on every
  style variant.
- **Say LESS for an empty frame (09-02).** A long prompt gives the model room to populate an empty
  plate, even against an explicit no-people paragraph; two sentences fixed it. Naming the unwanted
  prop only works on populated plates.
- **Test whether you need angle plates before making them.** On `meta/muse-image` an explicit,
  emphatic camera move produced a top-down floor shot straight from an eye-level hall plate; four
  planned angle plates went unused. One image tells you which world you are in. (`recoup-music-video`
  now says the same.)
- **A plate earns its place only when two or more shots share it.** A single-shot plate is two
  generations to do one thing.

## 4c. Keyframed camera moves: `end_image_url`

- **Use `end_image_url` for camera moves** (`minimax/h3-max-turbo`: `image_url` + `end_image_url`,
  `duration` 5 to 15). Cost is per second of output, not per clip, so fewer, longer keyframed shots
  are free precision: start and end are specified instead of hoped for, and near-identical wide
  stills become one travelling shot instead of a repetitive cut.
- **Check consecutive stills as PAIRS before spending motion.** The move interpolates between them;
  any discontinuity in scale, position or the subject's state becomes a visible morph. Fix it at
  the still, not in the clip.
- **Pin geometry in the prompt on long moves (09-02).** Drift grows with duration: a 10s descent
  went through the floor and invented a mirrored warehouse below. State that the floor is solid,
  the camera never goes below it, and exactly one subject is on screen at all times.

## 4d. Lip-synced VO over a still (earned on the first Jenny film, 2026-09-21)

Both endpoints supersede the 08-31 "OmniHuman 1.5 for every mouth-visible shot" split for spoken
pieces, at half the price. The Seedance photoreal-face filter does not apply to MiniMax.

| Endpoint | What it does | What it does to the audio | Billed |
|---|---|---|---|
| `minimax/h3-max/lip-sync/image-to-video` | One still with a visible face (photo, 3D render or illustration; aspect 0.4–2.5) + `audio_url` 5–14.8s. Mouth, eyes and expression move; framing, body and camera stay as the still. | **Keeps our take sample-exact** (cross-correlation 1.00). | $0.08/s at 768P (9s ≈ $0.72) |
| `minimax/h3-max/reference-to-video` | Up to 12 refs (`reference_image_urls`, `reference_video_urls` 2–15s, `reference_audio_urls` 2–15s); prompt refers to "Image 1", "Audio 1"; `duration` 5–15, 9:16 supported, `prompt_expansion_mode: "disabled"`. Holds identity from the sheet and generates real presenter body language and camera moves. | **Re-voices the line**: Audio 1 is a content and timbre reference, not a soundtrack. The words mostly survive, the voice and timing do not, and it can insert a word ("and three" appeared mid-sentence). | $0.08/s at 768P (10s = $0.80) |
| `fal-ai/sync-lipsync/v2/pro` | `video_url` + `audio_url`, `sync_mode: "cut_off"`. Re-syncs an existing clip's mouth to supplied audio; trims the clip to the audio. | Puts the approved take back, sample-exact. | ~$0.75–0.83 per 9–10s clip |

**The production route for a speaking character (owner-approved 09-21):** reference-to-video for the
performance and camera (its audio discarded) → Sync Lipsync with the approved ElevenLabs take. About
$1.55–1.70 per clip at 768P. The locked-still endpoint alone is cheaper but reads too still for a
presenter; reference-to-video alone loses the approved voice. Never ship reference-to-video's own audio.

**Reference-sheet constraints, learned by refusal:** video endpoints reject images over 5760px on a
side or with aspect outside 0.4–2.5. A one-row character sheet fails both; keep a two-row copy of the
same panels for video prompts (`cast/<name>/<name>-sheet-video.png`), the one-row sheet for stills.

**Workflow:** VO lines generated, normalised and approved first per `references/voice.md`, one line
≤14.8s per clip; then the clip; then composite the clip **muted** in HyperFrames with the approved VO
as a separate stem, so the render stays the single source of truth. QC every clip: frames at 1s steps,
cross-correlate the clip's audio against the take (expect 1.00 for lip-sync and Sync, ~0.3 for
reference-to-video), and Scribe-transcribe it to catch inserted words.

## 5. Audio

Generation, voice choice, audio tags, loudness and verification live in `references/voice.md`;
read it before generating anything. Pipeline-level rules: lift the **stems**, not the final mux, so
the voice/bed balance stays yours and the render is the single source of truth; keep raw
un-normalized takes in a sibling directory named after the voice; bed around `0.12` against voice
at `1.0`.

## 6. Wire audio and timing

- Every `<audio>` and `<video>` needs a **unique `id`**. Without one the renderer silently drops it:
  a `<video>` with no `id` renders **frozen**, a still slideshow with perfect audio.
  `media_missing_id` is the most dangerous lint error there is.
- Timed elements need `class="clip"`, `data-start`, `data-duration`, `data-track-index`.
- A `<video>` clip carrying audio needs `data-has-audio`.
- Fades on clips need a hard kill at their end.
- `data-track-index` does not set z-index; DOM order does. Put chrome LAST.
- Chrome over footage needs its own shadow.
- Never animate `innerText` for a text swap; use one timed clip per label.
- Place each VO line at its real start from the generated durations, and align each scene window to
  its line. A ~0.3s pre-roll and ~0.35s to 0.55s gaps between lines read naturally.

### Captions

Burn in captions for every VO line (roughly 12% more watch time, 80% higher completion, most feed
viewers are sound-off). Time them from a transcript of the actual audio, not from the plan.
**A caption's fade-out must complete before the next one starts**: fading out over 0.14s while the
next fades in 0.04s later puts two captions in the same place for 0.1s. Leave a gap larger than the
fade.

## 6b. Build the composition FROM the audio (the pattern that held on 2026-09-21)

Do not hand-time scenes. Write a `build.py` that reads `audio_meta.json` (measured durations, word
timings) and emits `index.html`:

- every scene window derives from its line's start and measured duration, with a fixed gap between
  lines; a card or a clip that must play alone (the raw model voice, an end card) gets its own window;
- captions are chunked from the word timings (split at punctuation, at most ~9 words, the next chunk's
  start minus a fade as the end), one timed clip each;
- the GSAP timeline is emitted as **static** `tl.set` / `tl.to` lines (the linter cannot see inside a
  loop), with cue times taken from specific words ("character", "voice") when a tick must land on a word;
- the build prints its windows and a ready `snapshot --at` list at mid-beat times.

A line change is then a re-record plus a rebuild, never a re-time. Reference: the account workspace's
`content/jenny-ep1-h3-lipsync/video/build.py`.

**Lint gotchas from that build:** a kicker and its scene on the same `data-track-index` fail
`overlapping_clips_same_track`, give kickers their own track; a `.chip` with both `top` and `bottom` set
stretches into a tall pill, set `bottom: auto`; a fade-out on a clip needs `tl.set(..., {opacity: 0})`
at the clip boundary or lint reports `gsap_exit_missing_hard_kill`; a Jenny clip is composited **muted**
with the approved VO as a stem, and the raw model-voice clip plays with its own audio only in a window
where no narration runs.

**Costs on screen come from billing, pulled last.** Query the fal usage API after the final generation
and before the cost line is recorded; the receipt panel, the spoken figure and the log cite the same
JSON, labelled "as billed".

## 7. Lint, snapshot, render, then read frames

**Render is the expensive loop. Do not use it to look at your work.** Render with `--fps 24` to
match 24 fps generated footage, and render heavy compositions in the background.

```bash
npm run check                                     # lint + validate + inspect. 0 errors required
npx hyperframes@0.7.5 snapshot --at 4.2,26,42.5 .       # ~15s, writes PNGs + a contact sheet
npm run render                                    # minutes. Only once the stills look right
```

`snapshot` writes key-frame PNGs **and a contact sheet** in ~15s against minutes for a render; pass
`--at` with the times you care about. Obey the contrast gate, and trust time-aware `inspect` over
the static lint.

**`inspect` samples a fixed number of points across the timeline and will miss collisions between
them** (a caption collision survived two full passes). So **read frames out of the finished MP4,
every time**, at the times **captions are on screen**, not at even intervals; a collision only
exists while both elements are visible, and the tallest scene is the one that collides.

```bash
ffmpeg -ss <t> -i renders/<file>.mp4 -frames:v 1 out.png
```

Verify the render has **both** video and audio streams, the expected duration and dimensions. The
right duration is not evidence it looks right. The mixdown can attenuate voice, so verify levels on
the render, not on the stems.

**Read the plan doc's Screen column back against the composition one row at a time; a row you
cannot point at is a row you did not build (08-12).** No other gate checks the film against the plan.

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

Build gotchas, all caught on the 2026-08-11 run:

- **The linter cannot see inside a loop.** Timing built in a `forEach` produces a phantom
  `gsap_exit_missing_hard_kill` on `__unresolved__`; write the scene table as static `tl.set` /
  `tl.to` calls, one line per scene, generated by a script if you like.
- **A count-up cell must not carry its final value in the markup.** Lint and `inspect` both pass a
  hardcoded `111` that snaps to 0 when its tween starts; only frame QC at the count times catches
  it. Initialise every animated counter at its start value.
- **`0 -> 0` is still not an animation.** A cell whose true value is zero pops in with a scale cue.
- **`data-layout-allow-occlusion` goes on the occluded text**, not on the element doing the occluding.
- **Use the nvm Node, not the system default.** The shell can reset to Node v17 and `hyperframes`
  dies with `SyntaxError: ... does not provide an export named 'styleText'`. Prefix build commands
  with `export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"`.

## 8. Ship

Publishing order, logging and the 48h re-pull are owned by `SKILL.md`; per-platform mechanics live
in `references/publish-verify.md` and `recoup-internal-social-ship-posts`.

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
