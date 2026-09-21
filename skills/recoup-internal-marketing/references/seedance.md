# Seedance 2.5 — house reference

ByteDance's video model. Announced **2026-07-31**, API live on BytePlus ModelArk and fal from
**~2026-08-07**. First written 2026-08-13, before our first generation. The decision gate, the cost
anchors, the house rules, the dated one-liners and the **Run log** are *earned*; the spec section is
*sourced* and collapsed to what still matters. Mark new findings with their date.

## The decision gate (earned 2026-09-14, NOBODY OFF THE STAGE) — read before any other section

**Through fal, Seedance's input filter rejects every photoreal human face, whatever made it** — a Muse sheet,
a Nano Banana sheet, a frame extracted from Seedance's own output, that output's untouched mp4, and a
face-bearing clip sent as an extension source (six rejections, run log). **A stylized face passes and holds
identity across shots.** So the *medium* decides the model:

| Cast | Model | Why |
|---|---|---|
| Photoreal characters | **H3 Max i2v from Muse start stills** (SMALL ROOM pipeline) | Seedance cannot take the face; H3 takes the still |
| Stylized / animated characters | **Seedance 2.5 `reference-to-video`** with the sheets as references | The sheets get in, identity is held by reference, whole song sections become one take |
| Face-free plates and beats (empty streets, cranes, crowds from behind) | Seedance | Its strongest work either way |

What still passes with a photoreal cast, for a hybrid: **headless wardrobe crops** (build, clothes, props
transfer; the face is redrawn), location plates, props. What never passes: any face, by any route. Route 1
("reuse trusted model outputs") is dead through fal: the trust check is account/task provenance on ModelArk,
and a reseller cannot pass it (run log, 09-14). Identity across takes with a photoreal cast = wardrobe by
image + face by descriptor, redrawn every take.

### The stylized pipeline, in order (what worked first time and what did not)

1. **Cast photoreal first, from the owner's references** (Muse, bake-off, approved sheets). Identity decisions
   are made on real faces, where they are easiest to judge.
2. **Re-render every asset with ONE style string via Muse edit** — sheets, plates, props, the two-shot size
   reference — so the character survives the medium change. Keep the string in its own module and paste it
   verbatim into every Seedance prompt too (`content/off-the-stage/style3d.mjs`).
3. **Bisect-test every face panel alone before a take**: one panel + one plate, 4s, 480p (free if rejected).
   The phone-lit close-up in our set stayed near-photoreal after the first pass, tripped the filter, and cost a
   full 8-reference take before the bisect found it. A harder push ("larger eyes, smooth skin, no freckles,
   unmistakably an animated character") fixed it in one edit.
4. **Proof take = the hardest two-lead beat first** (ours: the reversal two-shot, 15s). If identity holds
   there it holds everywhere; if it fails, nothing downstream is worth spending on.
5. **One take per song-map section, ≤30s, cuts written as `Shot N` inside the take.** No per-shot start
   stills. Seven takes covered a 121.6s film.
6. **Upscale per take, not the master**: Topaz on fal, 720→1080 at $0.02/s. It trims ~0.5s off some takes
   (twice on the same two); pad by cloning the last frame to the window length.
7. **HyperFrames `--fps 24`**, and its render lands as `renders/video_<timestamp>.mp4`, so the mux script
   must glob, not assume `main.mp4`.

### The prompt architecture that held (el.cine's "The Last Dish" template + the Higgsfield 2.5 dialect)

```
[GLOBAL]  medium + palette + "every shot is a LOCKED camera" + acting register + PHYSICS LAWS + no text + NO BGM
[Characters]  one line per lead: @ImageN roles with exclusions and a fidelity grade; count header
[Scenes and props]  plates and props by role, "do not use as a starting frame"
[GEO SPATIAL LAYOUT]  per location, pasted unchanged into every shot of that location
[Shots — N seconds continuous]  Shot k (a–b s): size, locked camera, initial state, primary event, End state
[Maintain Consistency]
AUDIO: diegetic only. NO BGM.
```

**PHYSICS LAWS is the block that stopped the re-rolls.** Both physics failures we shipped past were prompt
omissions, not model faults: thumbs passed through a handshake, and a phone teleported between hands with its
earbud cable detached. The fixes, now standing in every `[GLOBAL]`: *hands that touch stay solid and never pass
through each other; every prop belongs to ONE named hand and changes hands only when a shot says so; the cable
runs from the phone to her ear whenever she holds it; the crowd is one mass, backs to camera, never a face.*
Then per shot, write ownership explicitly ("phone in her LEFT hand", "hat in her RIGHT hand") and restate it in
every End state. A climb floated until it was written as weight transfer ("plants her right foot on the
crossbar, the crossbar takes her weight, pushes up, left foot lands flat on the planks; each foot always in
contact"). Age-blind names throughout (THE PASSENGER, THE DIRECTOR; never "kid", "young").

### Cost anchors (fal, 2026-09-14)

720p `reference-to-video` ≈ $0.47/s (a 15s take ≈ $7); rejected inputs are not billed. A 121.6s film: ~$78
across six tests, three proof takes, six slate takes and one re-roll, + ~$4 Muse + ~$3.30 Topaz. The same
15s beat on H3 Max cost $0.60 and followed one action per clip; Seedance followed the staged direction and
kept the world continuous across its internal cut. Choose Seedance for multi-beat, two-lead takes; H3 for
single-action solo clips if the cast is photoreal.

## Sources, ranked by trust

| Trust | Source | What it's good for |
|---|---|---|
| Canonical | [ByteDance Seed launch post](https://seed.bytedance.com/seedance2_5) (07-31) | What the model is for, capability claims |
| Canonical | [BytePlus ModelArk prompt guide](https://docs.byteplus.com/en/docs/ModelArk/2607689) | Locked/unlocked task rules, reference budgets, `content.role`, official prompt doctrine |
| High | [fal prompting guide](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) (08-07) | Exact fal endpoints and params, 10 worked techniques, the prompt template |
| Ours | **`seedance-examples.md`** — worked example prompts verbatim, with source links, plus our own | Steal structure from a prompt that already works. Read it before writing one. |
| **Ignore** | `skillsllm.com/skill/seedance-2-5-skill` | Affiliate listing (0 stars, `?ref=` links). **Its specs are wrong** — claims 1080p and only three aspect ratios. |

There is an **official ByteDance prompt-engineering skill**. Prefer it over any third-party one:

```bash
npx --yes skills@latest add \
  "https://arkdocs-en.tos-ap-southeast-1.volces.com/skills/" --skill sd25-pe --yes
# then: /sd25-pe <your prompt>
```

## The spec, collapsed (sourced 2026-08-13; re-verify before an expensive decision)

fal exposes three endpoints — `text-to-video`, `image-to-video`, `reference-to-video`; edit and extend are
folded into `reference-to-video` and triggered by prompt keywords (`edit video, add, remove, replace` /
`extend forward, continue from`). 720p max (our 1080x1920 master needs a 1.5x upscale), 24 fps, 4–30s, no
draft mode, no `seed` input (output only; both 08-13 runs confirmed), ~3 minutes per attempt whatever the
outcome (142–162s for 10s, 292s for 30s), native audio ≈ -22 LUFS so it needs gain, output URLs expire in
24h. **Output moderation judges the generated frames after the run**, so you pay the wait for a video you
never see; rejected inputs are not billed (09-14). The `adaptive` ratio trap: i2v, first/last-frame, edit and
extend inherit the input's ratio (fal spells it `aspect_ratio: "auto"`), so to get 9:16 feed a 9:16 image.
References are numbered by upload order as `@Image1` / `@Video1` / `@Audio1`; bind each explicitly, give it
exactly one job and say what must not transfer, put the important ones first, and use 4–5 assets, not the
50-slot cap. A 30s shot needs an integer-second timeline or it becomes waiting; write cause before reaction;
break movement into contacts; continue a shot via its last frame and describe only the first new action;
when a generation misses, change one thing. Text rendering is broken, so composite every word. There is no
negative-prompt field: prescribe the staging instead of banning the outcome ("all laptops closed or turned
away from camera" held where "no logos" leaked an Apple logo, 08-13); "No subtitles" and "No BGM" are the
negatives that work. Prices: fal 720p $0.473/s, 480p $0.2205/s, video references discounted 0.6x, audio off
saves nothing; Replicate is cheaper for plain t2v ($0.2312/s at 720p) but truncates prompts at 2000 chars.
BytePlus ModelArk (`dreamina-seedance-2-5-260628`, `https://ark.ap-southeast.bytepluses.com/api/v3`,
async create-task → poll) is the canonical API and the only place `content[].role`
(`first_frame` / `last_frame`), `camera_fixed` and task provenance exist; fal has no `role` field.

## Calling it

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
    image_urls: [stylizedSheetUrl, environmentUrl],
    video_urls: [cameraMotionUrl],
    duration: "16", aspect_ratio: "9:16", resolution: "720p", generate_audio: true,
  },
});
console.log(r.data.video.url);
```

**Verify upload order before sending the prompt.** The right description bound to the wrong reference
number fails in a way that looks like a model problem. Credentials: `FAL_KEY` lives in `mono/api/.env.local`
(values are quoted; strip with `tr -d '"'`), `@fal-ai/client` is imported from an api worktree, and Node
must be v24 via nvm (`machine-env-gotchas`, `faceguide-model-workflow` memories).

**`reference-to-video` input schema, verified from fal's API page 2026-08-13:**

| Field | Type | Notes |
|---|---|---|
| `image_urls` | string[] | addressed in the prompt as `@Image1`, `@Image2`… |
| `video_urls` | string[] | `@Video1`… |
| `audio_urls` | string[] | `@Audio1`… |
| `duration` | string | `auto`, or `"4"`–`"30"` |
| `resolution` | string | `480p` \| `720p` |
| `aspect_ratio` | string | `auto` \| `21:9` \| `16:9` \| `4:3` \| `1:1` \| `3:4` \| `9:16` |
| `generate_audio` | boolean | |

Files may be supplied as **public URLs, base64 data URIs, or via `fal.storage.upload()`**.

**🔴 fal has NO `role` / `reference_type` field.** Assets are bound *only* by index in the prompt
text. So `first_frame` / `last_frame` roles are **not reachable through fal's reference-to-video** —
use the separate `image-to-video` endpoint, or go direct to ModelArk, if you need strict
first/last-frame locking. Note also fal spells the adaptive value **`aspect_ratio: "auto"`** where
ModelArk uses **`ratio: "adaptive"`**.

**`image-to-video` input schema, verified from fal's API page 2026-08-13:**

| Field | Type | Notes |
|---|---|---|
| `image_url` | string | **single**, not a list — the first frame |
| `end_image_url` | string | **the last frame.** "the generated video will transition from the starting image to this ending image" |
| `duration` | string | `auto`, `"4"`–`"30"` |
| `resolution` | string | `480p` \| `720p` |
| `aspect_ratio` | string | **fixed at `auto`** — the lock, confirmed |
| `generate_audio` | boolean | default `true` |

**Turning audio off saves nothing:** fal states *"The cost of video generation is the same regardless
of whether audio is generated or not."* So `generate_audio: false` is a creative choice, never a
cost one.

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

Seedance is a plate source, not a pipeline: `sd25-pe` writes the prompt → Seedance on fal makes the plate →
`media-use` registers it and owns VO + loudness → `hyperframes` composites (`motion-graphics` carries every
number, `embedded-captions` handles captions over a face, `general-video` assembles several plates) →
`hyperframes-cli snapshot` is the cheap QC rung. `recoup-internal-video-grok-1.5-imagine-facetime` is the
precedent for a fal video call; `recoup-content-make-video` is customer-facing and credit-metered, so it never
runs for our own accounts. HyperFrames stays the default for typography, UI and data panels; Seedance earns
its place where we need filmed reality we cannot shoot; the house i2v for a photoreal cast is MiniMax H3 Max.

## Run log

One row per generation. This is the section that makes the doc worth keeping — record the cost, the
parameters and the honest verdict, including the failures.

| Date | Piece / arc | Endpoint | Duration · ratio · res · audio | Refs | Time | Verdict |
|---|---|---|---|---|---|---|
| 2026-09-14 | NOBODY OFF THE STAGE — **cast acceptance test** | fal ref2v | 4s · 9:16 · 480p · audio off | Muse-generated director face close-up + hill plate | 122s | ❌ **REJECTED AT INPUT** (`content_policy_violation`, "likenesses of real people"). A Muse face is not trusted either; it is the face, not the generator. Unbilled. |
| 2026-09-14 | route 1 test A — character on grey | fal **t2v** | 4s · 9:16 · 480p · audio off | none | 142s | ✅ Generated. Seed `988227973`. Used only as the source for tests B and C. |
| 2026-09-14 | route 1 test B — **Seedance's own frame** as face ref | fal ref2v | 4s · 480p | PNG frame extracted from test A + hill plate | 100s | ❌ **REJECTED AT INPUT**, same error. An extracted frame is "secondary editing". Unbilled. |
| 2026-09-14 | route 1 test C — **Seedance's own untouched mp4** as identity ref | fal ref2v | 4s · 480p | test A's original mp4 as `@Video1` + hill plate | 161s | ❌ **REJECTED AT INPUT**, same error. **Route 1 is dead through fal**: the trust check is account/task provenance on ModelArk, and a reseller cannot pass it. Unbilled. |
| 2026-09-14 | **extension test** — extend a face-bearing Seedance clip forward | fal ref2v (extension order) | 4s · auto · 480p | test A's mp4 as `@Video 1`, extension phrasing | 105s | ❌ **REJECTED AT INPUT** on `video_urls`. The filter runs on the upload, not the prompt intent: **chains cannot carry a face through fal.** Unbilled. |
| 2026-09-14 | **headless wardrobe test** — director body crop, no face | fal ref2v | 4s · 9:16 · 480p · audio off | `cast/director-body-headless.png` (crop from the collar down) + hill plate | 468s (queued) | ✅ **ACCEPTED, and the wardrobe transferred**: shell open over tank, walkie on chest strap, headset, cargos, shot list, sleeve faint on the raised arm; hill plate and the crane signal landed. **The face is the model's own** (different from the t2v plate). Seed `143886878`. |
| 2026-09-14 | **stylized-face test** — dir5 re-rendered as 3D feature-animation (Muse edit) as the face ref | fal ref2v | 4s · 9:16 · 480p · audio off | `cast/director-stylized.png` + hill plate | 415s (queued) | ✅ **ACCEPTED, identity HELD**: same face, hair, hoops, sleeve, headset, wardrobe on the hill, crane signal landed. **The filter is a photoreal-likeness classifier; a stylized face is not a likeness.** This is how el.cine's Filmera "The Last Dish" template holds two characters across a 27s take (stylized 3D, two sheets + storyboard + set). Seed `715878081`. |
| 2026-08-13 | back-office v1 `[Builder Diary]` | fal t2v | 10s · 9:16 · 720p · audio on | none | 142s | ❌ **Generated, then REJECTED by output moderation.** `content_policy_violation`, "potential copyright violation", `partner_validation_failed`. Prompt was film-noir styled: night, rain on the window, loosened tie, desk lamp. |
| 2026-08-13 | **THE OPERATOR ep1, full 30s** | fal **ref2v** | **30s** · 9:16 · 720p · audio on | 1 face-free scene plate | **292s** | ✅ **All three acts, one cut, identity held across a hard location change.** Seed `39363830`, 7.68MB, -22.3 LUFS. |
| 2026-08-13 | PoC: collision `[The Operator]` | fal **ref2v** | 10s · 9:16 · 720p · audio on | **1 face-free scene plate** | 208s | ✅ **Best result yet.** Scene plate transferred completely; the collision read as an accident; the crouch + phone-to-ear + line all landed. Seed `927418445`. |
| 2026-08-13 | corridor v2 — **first reference call** | fal **ref2v** | 10s · 9:16 · 720p · audio on | 3 images (Nano Banana 2 face plates + env plate) | 210s | ❌ **REJECTED AT INPUT.** `content_policy_violation` — *"The images or videos provided may contain likenesses of real people or other private information that cannot be processed."* Settles the whitelist question: **a Nano Banana 2 face is not trusted.** |
| 2026-08-13 | corridor v1 `[Builder Diary]` | fal t2v | 10s · 9:16 · 720p · audio on | none | 180s | ⚠️ **Passed moderation, failed the brief.** Craft up, story down — see *The framing ate the story* below. Seed `746924417`, 3.50MB, -25.8 LUFS. |
| 2026-08-13 | back-office v2 (same beat, restyled) | fal t2v | 10s · 9:16 · 720p · audio on | none | 162s | ✅ **Passed.** 720x1280, 24fps, 10.08s, 1.55MB, AAC stereo 32kHz, seed `1632188029`. Character consistency across the full take was excellent. One constraint violation — see below. |

### What the 08-13 runs taught, one line each

- **Output moderation prefers plain daylit documentary styling over noir (08-13):** back-office v1 (night,
  rain, desk lamp, loosened tie) was rejected after `COMPLETED`; the same beats in flat daylight and a grey
  t-shirt passed. Five things changed at once, so styling is the inferred lever, not a proven one; the
  "must not resemble any real, famous or public figure" sentence is probably inert — keep the adjective
  "fictional", drop the sentence, and change ONE thing on the next re-roll.
- **Declare exactly one cut and forbid the rest, six beats per 30s, scope a reference to part of the film
  ("controls the OFFICE ENVIRONMENT ONLY for the first 21 seconds"), and the face-free scene plate is the
  highest-leverage control we have (08-13, THE OPERATOR):** two lines of art direction inside an image
  outperformed a paragraph of styling in the prompt, and 292s for 30s vs 208s for 10s means one long take
  beats blocks whenever continuity matters.
- **Measure the LRA before reaching for a target loudness (08-13):** the 30s film was -22.3 LUFS with a 17.2
  LRA and -1.68 dBTP, so a linear gain to -15.9 would have clipped; `volume=6.5dB,alimiter=limit=0.84`
  landed -17.8 LUFS / -1.3 dBTP. Prefer 2 LU quiet over flattening the one moment the film is built on.
- **Crop a tight headshot of every generated character and audit the face cold (08-13):** the Operator's
  Nano Banana 2 plate was a clear likeness of a well-known actor, invisible at walking distance in the
  clip; never feed such a plate back in, and avoid prompts that evoke a specific production, because the
  model will cast it.
- **The framing ate the story, twice the same way (08-13):**
  1. Name what the viewer must SEE, not what happens: "the phone buzzes" reached the audio, not the frame.
  2. Put the story element between the subject and the lens or at the near frame edge; in 9:16 anything
     past the mid-ground is set dressing.
  3. A camera choice is a story choice: one lens cannot serve the subject's face AND what happens to him.
  4. Count the beats against the seconds: three interruptions in ten seconds got quietly dropped.

### Still open

- Does 9:16 at 720p hold up in-feed next to our 1080p masters, or is the softness obvious?
- Does an audio reference carry a cast voice's timbre, or does it drift like the reported accent failures?
- Do music-industry specifics (artist names, venue names, label imagery) trip the output filter?
- A Seedream-generated face is untested as a reference; through fal it is expected to fail like every other
  face (09-14), so only a ModelArk account could settle it.
