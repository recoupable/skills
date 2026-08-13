# Seedance 2.5 — house reference

ByteDance's video model. Announced **2026-07-31**, API live on BytePlus ModelArk and fal from
**~2026-08-07**. This doc is the durable place we accumulate what we learn about it; the **Run log**
at the bottom is the part that grows. First written 2026-08-13, before our first generation — so
everything above the run log is *sourced*, not *earned*. Mark earned findings as such.

## Sources, ranked by trust

| Trust | Source | What it's good for |
|---|---|---|
| Canonical | [ByteDance Seed launch post](https://seed.bytedance.com/seedance2_5) (07-31) | What the model is for, capability claims |
| Canonical | [BytePlus ModelArk prompt guide](https://docs.byteplus.com/en/docs/ModelArk/2607689) | Locked/unlocked task rules, reference budgets, `content.role`, official prompt doctrine |
| High | [fal prompting guide](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) (08-07) | Exact fal endpoints and params, 10 worked techniques, the prompt template |
| Ours | **`seedance-examples.md`** — every worked example prompt verbatim, with source links | Steal structure from a prompt that already works. Read it before writing one. |
| **Ignore** | `skillsllm.com/skill/seedance-2-5-skill` | Affiliate listing (0 stars, `?ref=` links). **Its specs are wrong** — claims 1080p and only three aspect ratios. Both refuted below. |

There is an **official ByteDance prompt-engineering skill**. Prefer it over any third-party one:

```bash
npx --yes skills@latest add \
  "https://arkdocs-en.tos-ap-southeast-1.volces.com/skills/" --skill sd25-pe --yes
# then: /sd25-pe <your prompt>
```

## The face restriction — read it precisely, it is narrower than it sounds

> **"Seedance 2.5 does not support directly uploading reference images/videos containing real human
> faces."** — [BytePlus docs](https://docs.byteplus.com/en/docs/ModelArk/2607688)

**This restricts what you may UPLOAD as a reference. It does not restrict what the model may
GENERATE.** Every ByteDance demo is full of faces — the singer walking from dressing room to stage,
the Peking Opera trio, the grandmother and the robot — and so is every worked example in the fal
guide (the bodega messenger, the diner customer, the UGC presenter). Text-to-video with an invented
character is completely unaffected. **Do not read this rule as "make faceless videos."** An early
draft of this doc did, and it nearly cost us a good idea.

What it actually blocks: uploading a **photograph of a real person** as a reference. That is the
2026 Disney / Netflix / WBD / Paramount cease-and-desist fallout — ByteDance added C2PA watermarking
and real-face filters on 2026-03-30.

| You want to | Status |
|---|---|
| Generate an invented character with a face, via t2v | ✅ Unaffected. This is what the demos do. |
| Generate a character and keep them consistent across a 30s take | ✅ Native (imperfect — see failure modes) |
| Upload a real artist's photo as a subject reference | ❌ Rejected at input |
| Upload our Nano Banana 2 face guide of a real person (brauxelion, Gatsby Grace) | ❌ Rejected — it is a real face |

So the **cast pipeline** is the part that is blocked, not the medium. Three sanctioned routes exist
([doc 2608626](https://docs.byteplus.com/en/docs/ModelArk/2608626)), none tested by us:

1. **Reuse trusted model outputs** — face-containing frames *your own account generated* can be fed
   back in without tripping input moderation. Most promising; test this first.
2. **The preset digital-characters library** — free compliant portrait assets, but off-canon faces.
3. **Authorized real-person assets** — a formal licensing path we have not explored.

**Practical rule:** an original character invented in the prompt is fully available today. A
recurring cast member whose likeness is a real person is not, until route 1 is proven.

## The constraints that will bite us

Read these before planning a shot. Every one changes what we can promise.

| Constraint | Value | Why it matters to us |
|---|---|---|
| **Real faces as INPUT** | Rejected. Generating faces is fine. | Blocks the face-guide → i2v *cast* route until route 1 is proven. Invented characters are unaffected. |
| **Max resolution** | **480p or 720p. No 1080p, no 4K.** | **Our slate renders 1080x1920.** At 9:16 that's **720x1280** — needs a 1.5x upscale or an accepted softer master. The "native 4K" headlines belong to Seedance **2.0** (which does do 1080p/4K); 2.5 traded resolution for length and reference control. |
| **No draft mode** | `draft` is unsupported on 2.5 | **This breaks our cheap-QC-ladder doctrine.** There is no preview pass — every attempt is full price. Budget for iterations up front and get the prompt reviewed before spending. |
| Duration | 4–30s, every integer; `-1`/`auto` lets the model choose | A 30s single take can carry a whole canon post (ours run 30–46s). |
| Aspect ratio | `16:9 · 4:3 · 1:1 · 3:4 · 9:16 · 21:9 · adaptive` | 9:16 supported. **But see the `adaptive` trap below** — for i2v, first/last frame, edit and extend you *cannot* set a ratio. |
| Native audio | `generate_audio`, **default `true`** | Jointly generated, not dubbed. Voice casting is reported **unpredictable** (a character got an unprompted British accent). Collides with our cast voice canon — see house rules. |
| Reference budget | ≤30 images + ≤10 videos + ≤10 audio, **≤50 total** | Videos 2–30s each, **combined ≤30s**; audio the same. Images 300–6000px/side, <30MB, request body ≤64MB. 2.5 is the first to accept **audio-only** references. |
| **Output URLs expire** | **24 hours, max 100 downloads** | **Download immediately** and register the local file. Never store the returned URL as the asset reference. Task records are kept 7 days. |
| No negative prompt | No `negative_prompt` field on any provider | Exclusions go in the prompt text ("No subtitles, no cuts, no duplicated people"). |
| Output fps | 24 (inferred from fal's billing formula, not documented) | Match the HyperFrames timeline accordingly; verify on the first run. |
| Prompt length | Replicate truncates at **2000 chars** | ByteDance's own sample prompts exceed that. Another reason to prefer fal or ModelArk for timestamped multi-shot prompts. |

**The `adaptive` trap.** For **video edit, extend, first-frame and first-and-last-frame** tasks,
`ratio` *must* be `adaptive` — the output inherits the input's aspect ratio, and setting anything
else returns `InvalidParameter.TaskTypeConstraint`. **To get a 9:16 output from an image, feed it a
9:16 image.** Editing also forces `duration: -1`.

Set `omni_reference_task_type` explicitly (`auto` | `edit` | `extend`) to get **synchronous**
validation. Leave it on `auto` and errors arrive asynchronously after the task has already started.

## What it costs

Per second of output, 720p, no video references — the shape we would actually use:

| Provider | 480p | 720p | 30s clip @720p |
|---|---|---|---|
| **Replicate** | $0.1028/s | **$0.2312/s** | **~$6.94** |
| EvoLink | $0.136/s | $0.293/s | ~$8.79 |
| **fal** (our existing path) | $0.2205/s | **$0.4730/s** | **~$14.19** |
| PiAPI | $0.30/s | $0.60/s | ~$18.00 |

fal bills tokens: `(h × w × duration × 24) / 1024` at `$0.0214/1k`. **The two flip on video
references**: fal *discounts* them 0.6x (720p → $0.2838/s) while Replicate charges ~4x more
(720p → $0.9676/s). So **fal is the cheaper home for reference-heavy work, Replicate for plain
text-to-video** — and with no draft mode, that gap is the main cost lever. BytePlus sells prepaid
resource packs and its USD rate could not be verified; Together AI still shows "launching soon"
despite publishing a model string.

## The mental model: locked vs unlocked

This is the concept most likely to cause a confusing failure, and it has no equivalent in our other
tools. **Some tasks let the input asset dictate the output's geometry, and silently ignore the
parameters you set.**

**Locked** — the input is placed on the output timeline, so aspect ratio (and sometimes duration) is
inherited. You must set `ratio: adaptive`, and for editing `duration: -1`.

- *Editing* — locks ratio **and** duration to the source video. Output may differ by up to ~0.3s
  (transition frames only) unless the source was itself Seedance 2.5 output, in which case it matches.
- *First frame / first-and-last frame* — locks ratio to the **first-frame image**. Duration stays yours.
  A last frame with a different ratio gets **stretched**, so match them.
- *Extension* — locks ratio to the source video. Duration stays yours.

**Unlocked** — the input is only a semantic reference, so you choose ratio and duration: subject /
motion / style / audio references, storyboards, and keyframes.

Editing and extension are triggered by **keywords in the prompt**, not only by parameters:
`edit video, add, insert, remove, delete, modify, replace, change to` for edits;
`extend forward, extend backward, continue, continue from, extend the story` for extension.
Use `output_format: mov` for edit and extend — it preserves colour, brightness and audio continuity.

**Storyboards vs keyframes are not the same thing.** A multi-panel storyboard is a *loose* plot
reference (≤15 panels, line art, no text on the image). Independent keyframe images align
*strictly*. If you need the shot to hit exact frames, use keyframes and open the prompt with
"Use Images 1 to N in order as keyframes."

## Calling it

fal is our existing path (we already use fal for Nano Banana 2), and its two endpoints are:

```ts
import { fal } from "@fal-ai/client";

// Prompt only
const r = await fal.subscribe("bytedance/seedance-2.5/text-to-video", {
  input: { prompt, duration: "30", aspect_ratio: "9:16", resolution: "720p", generate_audio: true },
});

// With references — numbered by UPLOAD ORDER as @Image1, @Video1, @Audio1
const r2 = await fal.subscribe("bytedance/seedance-2.5/reference-to-video", {
  input: {
    prompt,
    image_urls: [faceGuideUrl, environmentUrl],
    video_urls: [cameraMotionUrl],
    duration: "16", aspect_ratio: "9:16", resolution: "720p", generate_audio: true,
  },
});
console.log(r.data.video.url);
```

**Verify upload order before sending the prompt.** The right description bound to the wrong reference
number is still wrong, and it fails in a way that looks like a model problem.

Credentials: `FAL_KEY` lives in `mono/api/.env.local` (also in `api-wt-decompose/.env.local`), and
`@fal-ai/client` is imported from an api worktree — same path the Nano Banana 2 face-guide work uses
(`machine-env-gotchas` and `faceguide-model-workflow` memories). Values in those files are quoted;
strip with `tr -d '"'`. Node must be v24 via nvm — the default v17 on this machine breaks fetch.

fal exposes exactly **three** endpoints — `text-to-video`, `image-to-video`, `reference-to-video`.
There is no dedicated edit or extend endpoint; both are folded into `reference-to-video` and
selected by prompt intent.

**BytePlus ModelArk** is the canonical API: model `dreamina-seedance-2-5-260628`, base
`https://ark.ap-southeast.bytepluses.com/api/v3`, async create-task → poll or `callback_url`.
It exposes fields the wrappers do not: `content[].role`
(`first_frame` · `last_frame` · `reference_image` · `reference_video` · `reference_audio`),
`camera_fixed`, `watermark`, `return_last_frame`, `omni_reference_task_type`, `service_tier`.
It requires a **prepaid resource pack** before the model activates. **Replicate**
(`bytedance/seedance-2.5`) is one endpoint for all modes and the cheapest for plain t2v, but
truncates prompts at 2000 characters.

Audio is steered from inside the prompt on ModelArk: `()` music · `<>` sound effects · `{}` dialogue
· `【】` subtitles. Replicate instead documents double quotes for lip-synced dialogue. `seed` exists
everywhere, but Replicate is candid that **reproducibility is not guaranteed**.

## Known failure modes

From hands-on reviews, worth believing before we spend money rediscovering them:

- **Text rendering is broken.** Signs, screens and titles come out garbled. Confirms the house rule:
  composite every word and number in HyperFrames.
- **Morphing and decoherence in fast action**, not fixable by upscaling. Prefer scenes that breathe.
- **Character consistency is imperfect** even within one 30s pass — reviewers report body
  proportions drifting between shots.
- **Hair flicker** and **background warping on fast wide pans**.
- **Voice casting is unpredictable** and inferred from reference images, not a fixed profile.
- **Seedance 2.0 prompts do not transfer to 2.5.** 2.5 resists rapid-cut prompting and wants longer,
  more explicit prompts. Run everything through `/sd25-pe` first.
- **Generation time is unverified.** ByteDance's own quickstart polls every 30s, implying minutes.
  Treat "near real-time" marketing as unsubstantiated.

**Legal context worth knowing as a company that publishes.** Seedance 2.0 drew cease-and-desist
letters from Disney, Netflix, Warner Bros. Discovery and Paramount, plus MPA allegations about
training data. 2.5 ships with C2PA watermarking, face filters and a licensed-IP revenue-share
program. Disputes are not settled. Our exposure is low when we generate original characters and
non-IP scenes, which is what an invented-character prompt does by construction.

## How to write the prompt

Seedance rewards a **production note**, not a mood description. The fal guide's template, which
matches the ByteDance doctrine — keep only the sections a given shot actually needs:

```
FORMAT           duration, aspect ratio, single take or cuts, real-time or specified speed
REFERENCE ROLES  @Image1 controls only [invariant]. Do not copy [pose/background/lighting] from @Image1.
                 @Video1 controls only [camera path/timing]. Do not copy [subject/setting] from @Video1.
STARTING STATE   character positions, held objects, camera position, environment state
TIMELINE         0-X s: first action / X-Y s: second action, beginning from the first one's result
CAMERA           path, position within the frame, when movement starts and stops
CONTINUITY       identity, object, direction, clothing, geometry invariants
AUDIO            dialogue, room tone, contact sounds, music or silence
ENDING STATE     exact position of character, objects and camera in the final frame
CONSTRAINTS      no cuts, no slow motion, no repetition, no extra objects, no text, no logos
```

The techniques that carry the most weight, each earned from a worked example in the fal guide:

1. **A 30s shot needs a timeline.** Extra duration does not add events — without blocks it becomes
   waiting, repetition or slow motion. Use integer-second blocks; each picks up the physical state
   the previous one left. (Seedance 2.0 ignored timestamps and only understood shot numbers; 2.5
   honours integer seconds. Don't use them for high-frequency actions like "shakes head 3x/sec".)
2. **Write the cause before the reaction.** "Looks surprised" lets the reaction land before its
   cause. Write contact → resulting movement → sound → reaction, as separate beats.
3. **Occluded objects still need continuity.** State how long a subject is hidden and repeat the few
   details that must survive re-emergence. "The same woman emerges" is too weak.
4. **Give the camera a position inside the frame**, not just a movement. Say which third the subject
   occupies and which event triggers a pan.
5. **Give each reference exactly one job**, and say what must *not* transfer from it. Never let an
   image and a video reference do the same job — video for camera path and timing, image for
   identity and design.
6. **Break physical movement into contacts**: approach, contact, transfer of force, recovery, and
   how it settles. Don't stop at the most dramatic frame.
7. **Block dialogue like performance.** Line in straight quotes with start and end times, plus who
   is silent. "Her mouth moves only during her own lines."
8. **Say where fluid motion ends** — direction of force and the state left behind. "Realistic
   physics" carries no information.
9. **Continue a shot via its final frame.** Extract the last frame, pass it as the image reference,
   and describe only what has already finished plus the first new action. Do not retell the clip.
10. **When a generation misses, change one thing.** Rewrite the physical state where the bad action
    begins and where it should end. Leave a correct camera line alone.

**Negative control** works for subtitles and audio specifically: "No subtitles." · "No BGM; generate
only environmental sounds and action sounds." · "No audio." Prefer positive description everywhere else.

Camera vocabulary is understood directly — shot sizes, push in / pull out / pan / track / orbit /
dive, low angle / overhead / FPV, one-take, dolly zoom, bullet time, speed ramp. For niche terms,
write `[term + plain explanation]`.

## House rules (ours, not ByteDance's)

- **720p is a downgrade from our current master.** Our slate is 1080x1920 from HyperFrames. Say in
  the plan doc whether a Seedance piece ships at 720p or gets upscaled, and never quietly mix a
  720p Seedance shot into a 1080p timeline without deciding it on purpose.
- **Native audio conflicts with cast voice canon.** A recurring character keeps a canonical voice
  recorded in `cast/<character>/`, and `references/voice.md` owns the bake-off. Seedance will invent
  a voice if you let it. Default for any cast character: **`generate_audio: false`, keep the
  ElevenLabs VO**. Seedance *does* accept an audio reference for timbre, which is worth a controlled
  test before trusting it — log the result below. Ambient SFX from Seedance is lower risk than
  dialogue.
- **Every existing gate still applies.** Named artists need real, auditable numbers and consent;
  external likenesses need explicit permission (`cast/<character>/`); the why-for-them sentence
  comes before the build; no AI disclosure in body copy (use the platform's upload toggle). A new
  generator changes the craft, not the ethics.
- **Never let a generated frame carry a factual claim.** The Studio arc's rule. Numbers live in the
  panels we build — composite them with `motion-graphics` over the plate, never prompt them into the
  model, which can hallucinate a digit and will do it in a frame that looks finished.
- **Text in frame is a known weak point across video models.** Assume on-screen numbers and UI get
  composited in HyperFrames over the Seedance plate until a run proves otherwise. This also keeps
  the `HOOKS.md` on-screen-numbers audit meaningful, since audited figures stay in layers we control.
- **Do not build bespoke generation scripts inside a `content/<project>/` folder.** That is how the
  per-project `post-*.mjs` sprawl happened before the shared runner. Seedance calls belong in
  `media-use` as a provider, with the plate registered in the project manifest.

## How it plugs into the skills we already have

**Seedance is a plate source, not a pipeline.** It produces footage we could not shoot. Everything
that happens to that footage afterwards is already owned by a skill — do not rebuild any of it here,
and do not let this doc grow into a parallel video workflow.

```
sd25-pe (prompt)  →  Seedance on fal (the plate)  →  media-use (register + cache)
                                                          ↓
   motion-graphics / embedded-captions overlays  ←  hyperframes (composite, time, render)
                                                          ↓
                                   hyperframes-cli snapshot → render → frame QC
```

| Step | Skill that owns it | What to lean on it for |
|---|---|---|
| Writing the prompt | **`sd25-pe`** (ByteDance official, install above) | Run the prompt through `/sd25-pe` before spending a generation. It is the model author's own optimizer — cheaper than a bad render. |
| Calling fal | **`recoup-internal-video-grok-1.5-imagine-facetime`** | Our existing precedent for a fal generative-video call: client import from an api worktree, polling, verbatim scripted dialogue, native voice. Copy its plumbing rather than writing new. |
| Holding the asset | **`media-use`** | The media OS: `resolve --from` registers a generated file into the project manifest, and the content-addressed cache at `~/.media` makes plates reusable across projects. It already lists "no video generation" as a HyperFrames gap it owns (local LTX today) — **Seedance belongs here as a provider**, not as bespoke scripts in a content folder. |
| Voiceover + loudness | **`media-use` audio engine** | Why `generate_audio: false` stays coherent: ElevenLabs TTS, loudnorm/linear-gain and ducking already live there, and `references/voice.md` owns the bake-off. Keep VO in the engine that can measure it. |
| Compositing | **`hyperframes`** (+ `-core`, `-animation`) | The plate becomes a media layer in a composition. Typography, UI panels and timing stay deterministic HTML over the top. |
| Numbers and stat hits | **`motion-graphics`** | Count-ups, lower-thirds, callouts, data-viz hits as an overlay. **This is how we honour "never let a generated frame carry a factual claim"** — the number is composited, never prompted. |
| Captions over a face | **`embedded-captions`** | Built for exactly this shape: transcription → `hyperframes remove-background` matting → HTML render → ffmpeg overlay. A Seedance talking-head plate is a valid input; `anchor` is the verbatim default. |
| Multi-scene assembly | **`general-video`** | The fallback orchestrator when a piece is several Seedance plates plus built scenes rather than one take. |
| QC and render | **`hyperframes-cli`** | `npx hyperframes@0.7.5 snapshot --at <times> .` stays the cheap rung. The QC ladder does not change because the source is generated. |

Two skills that look adjacent and are not: **`recoup-content-make-video`** is customer-facing and
credit-metered, so it never runs for our own accounts; **`hyperframes-media`** was retired into
`media-use`, so prefer `media-use` when both appear.

### Where it beats what we already do

- **HyperFrames** stays the default for anything fundamentally typography, UI, data panels or exact
  on-screen numbers — most of our canon slate, and it is deterministic.
- **Seedance 2.5** earns its place where we need *filmed reality we cannot shoot*: a performance, a
  location, a physical action, a 30s one-take narrative. **The Studio arc** (storyline #5, lead
  Gatsby Grace) is the natural home; its premise is literally making the thing the artist could
  never afford to shoot.
- **Grok Imagine** currently handles cast scene stills and i2v off the Nano Banana 2 face guide
  (`faceguide-model-workflow` memory). Seedance's subject-reference path may replace part of that —
  test before assuming, since likeness drift is the failure mode that has cost us most. Note
  Seedance accepts the **same face guide** as a subject reference, so the Nano Banana 2 step is
  reusable either way.

## Run log

One row per generation. This is the section that makes the doc worth keeping — record the cost, the
parameters and the honest verdict, including the failures.

| Date | Piece / arc | Endpoint | Duration · ratio · res · audio | Refs | Time | Verdict |
|---|---|---|---|---|---|---|
| 2026-08-13 | back-office v1 `[Builder Diary]` | fal t2v | 10s · 9:16 · 720p · audio on | none | 142s | ❌ **Generated, then REJECTED by output moderation.** `content_policy_violation`, "potential copyright violation", `partner_validation_failed`. Prompt was film-noir styled: night, rain on the window, loosened tie, desk lamp. |
| 2026-08-13 | back-office v2 (same beat, restyled) | fal t2v | 10s · 9:16 · 720p · audio on | none | 162s | ✅ **Passed.** 720x1280, 24fps, 10.08s, 1.55MB, AAC stereo 32kHz, seed `1632188029`. Character consistency across the full take was excellent. One constraint violation — see below. |

### 🔴 New failure mode: output moderation, after the generation completes

**The filter judges the generated FRAMES, not just the prompt.** The first run ran to `COMPLETED`
and was then rejected — you pay the wall-clock, and possibly the credits, for a video you never see.
There is no way to preview this, because there is no draft mode.

What flipped it from rejected to passed, changing only styling and keeping every story beat:

| v1 (rejected) | v2 (passed) |
|---|---|
| Night, rain running down the window, desk lamp, overhead fluorescent | Ordinary weekday afternoon, flat daylight through half-open venetian blinds |
| Rolled shirtsleeves, collar open, tie pulled loose | Plain grey crew-neck t-shirt |
| "cinematic" framing language | "Plain documentary realism, no cinematic stylisation, no film-noir look" |
| No statement about the character's identity | "a fictional, unremarkable person… **must not resemble any real, famous or public figure, and this is not a scene from any film or television programme**" |

**⚠️ This experiment is CONFOUNDED — do not read a cause out of it.** Five things changed between
v1 and v2 at once, so we do not know which one mattered. FAL's guide says plainly *"change one thing
when a generation misses"*, and we did not. An earlier version of this section asserted that the
identity disclaimer "got our run past the filter"; **that claim was unfounded and has been removed.**

**What is actually reasonable to believe.** The rejection fired on the *generated output*
(`partner_validation_failed`, "the generated output was rejected"), which means a classifier looked
at frames. A sentence in the prompt cannot change pixels the way lighting can. So the **styling
change is the plausible lever** — night, rain, desk lamp and a loosened tie produce a recognisably
noir image; flat daylight does not. **The identity disclaimer is probably inert**, and possibly
counterproductive, since it injects the words "famous", "public figure" and "film or television
programme" into a prompt for no mechanical benefit.

**Working rules, held loosely until someone runs the ablation.** Prefer plain, documentary, daylit
description over noir and prestige-TV styling. Budget for a rejection on any stylised first attempt.
When one happens, **change styling first, and change ONE thing** so the next result is readable.
Calling a subject "fictional" is cheap and has real precedent (FAL uses it for the car), so keep the
adjective; drop the disclaimer sentence, which has precedent nowhere.

**The ablation worth running** when we next have budget: re-send the v1 prompt with *only* the
lighting changed to daylight. If it passes, styling is confirmed and every other change was noise.

### ⚠️ Negative constraints are not reliably honoured for brand marks

The prompt said **"no logos"** and the render still put a clearly readable **Apple logo** on the
laptop lid, on screen for roughly half the take. Do not trust a negative instruction to keep brands
out of frame. Either compose so the object is turned away, or plan to patch it in post. This matters
beyond tidiness: an unlicensed brand mark in a published piece is a real problem, and it is exactly
the class of defect that survives review because the frame otherwise looks finished.

### What the first runs settled

- **Generation time: ~142–162s for a 10s 720p clip.** Not "near real-time"; budget ~3 minutes per
  attempt, and remember a rejection costs the same wait.
- **Output is 24 fps** — confirmed from the file, so the inference from fal's billing formula was
  right. Duration came out **10.08s** for a requested 10, so do not assume frame-exact length.
- **Native audio works and is quiet.** AAC stereo, 32 kHz, measured **-21.8 LUFS integrated /
  -1.4 dBTP**, against our ~-15.9 LUFS publish target. It needs gain, so measure before normalising
  per the house rule rather than reaching for dynamic normalization.
- **Character consistency over 10s was genuinely good** — same face, build and wardrobe in every
  sampled frame, with the physical beats (the arm sweep, the paper falling, the hand down the face)
  all landing where the timeline asked.
- **The no-text instruction held.** No readable screen, signage or caption anywhere. Only the logo
  leaked.

### Open questions to answer with the first runs

Priced and specced questions are answered above. These are the ones only a generation can settle:

1. ~~How long does a generation take?~~ **Answered:** ~142–162s for 10s at 720p. Still unmeasured
   for a full 30s take.
2. **Does 9:16 at 720p hold up on a phone** next to our 1080p HyperFrames masters, or is the
   softness obvious in-feed? This decides whether Seedance can ever carry a full canon post.
3. **Does the "trusted model output" route actually clear the real-face filter?** If yes, the
   recurring-cast pipeline is alive and this is the single highest-value thing to test. If no,
   Seedance stays limited to invented characters — still most of what we would want it for.
4. ~~Is output really 24fps?~~ **Answered: yes**, confirmed from the file.
5. **Does an audio reference carry a cast voice's timbre**, or does it drift like the reported
   accent failures?
6. **Can it render any legible text**, or is compositing mandatory? (Assume mandatory.)
7. ~~What does it refuse?~~ **Partly answered:** an output-side copyright filter rejects finished
   generations; noir styling tripped it, plain daylight did not. Still unknown whether music-industry
   specifics (artist names, venue names, label imagery) trip it.
8. **Does a rejected generation still cost credits?** Unverified — check the fal usage page against
   the two runs on 2026-08-13.

### Where the numbers came from

Specs and pricing above were pulled 2026-08-13 from ByteDance Seed, BytePlus ModelArk docs, the fal
guide, fal/Replicate/EvoLink/PiAPI model pages, and hands-on reviews. Unverified and flagged as such:
the mainland Volcengine model ID, an official BytePlus USD rate, a rumoured 180s beta long-video
mode, output fps, generation time, and Together AI's live availability.
