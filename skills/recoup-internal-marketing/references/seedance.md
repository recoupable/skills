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

**🔴 Routes 2 and 3 appear to be consumer-app flows, not API flows.** Published guides describe them
as: registering your own face as a verified asset (**分身**, a digital twin) inside the Jimeng app
via liveness check; ByteDance's **XYQ** character library; or a third-party front end. **None of
those is reachable from an API key.** For an API-based pipeline like ours, **route 1 is the only
candidate**, which raises the stakes on testing it. Sourced from community guides written against
Seedance **2.0**, so verify before relying on it.

**Practical rule:** an original character invented in the prompt is fully available today. A
recurring cast member whose likeness is a real person is not, until route 1 is proven.

### 🔴 Do NOT composite a character sheet — it breaks trust AND causes duplicate people

The obvious move is to generate four angles of a character, stitch them into one 2×4 plate, and pass
that as a subject reference. **That is wrong on Seedance 2.5, for two independent reasons.** An
earlier version of this doc recommended exactly that; it is retracted.

**1. Compositing voids the face-trust exemption.** The "trusted model output" route only covers a
model's *original* artifact: *"仅信任模型原始产物，二次剪辑或超过有效期后均不可使用"* — only the
model's original product is trusted; secondary editing, or expiry, invalidates it. **Stitching four
generated images into one plate is secondary editing.** The composite gets rejected by the face
filter while the four originals would each pass on their own. The English docs say the same thing
more vaguely: *"Compressing or forwarding files may invalidate trust verification."*

**2. Multi-view plates cause the "twin problem."** ByteDance names it — **双胞胎问题** — and gives
the mechanism the English docs never explain: **人脸占比过小**, the face region occupies too little
of the frame for the model to weight its features. *"以人物三视图/多视图作为参考素材时，易造成模型
人物识别混淆，从而生成重复同款人物"* — using three- or multi-view sheets as reference confuses
identity and makes the model **emit duplicate copies of the character**. A 2×4 contact sheet
mechanically drops the face to about an eighth of the frame.

**What to do instead:** pass the angles as **separate images**, each an unedited original from the
generator, and bind them individually in the prompt ("Images 1–3 are the same man from three
angles"). Pair a **tight headshot** as its own reference alongside any wider plate, so at least one
asset carries a large face region. This is also what ARK's own "split viewpoints into separate
images" guidance says — the two findings agree.

_The Chinese-language sourcing here is second-hand and one tier below our English-verified facts,
but it is specific, it is mechanistic, and it agrees with ARK's published English guidance. Treat as
a strong prior, and if you ever test the composite route, expect to lose the generation._

### Are rejected generations billed? Apparently not

*"仅对成功生成的视频计费。因审核等原因导致生成失败的，不收取费用。"* — only successfully generated
videos are billed; failures caused by moderation are not charged. If true this materially de-risks
iteration against an aggressive face filter, and it means our 2026-08-13 spend was **$13.87 for
three runs, not $18.49**. **Spot-check the fal dashboard before relying on it** — this is CN-sourced
and unverified by us, and fal is a reseller whose billing may not mirror ByteDance's.

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

## Reference assets — how many, how long, how to bind them

ARK publishes tuning guidance that is easy to miss and directly changes hit rate. **These are
stability thresholds, not hard limits** — you may exceed them, but expect to re-roll.

| Question | ARK's recommendation |
|---|---|
| Hard caps | ≤30 images (up to 4K), ≤10 videos (combined ≤30s), ≤10 audio (combined ≤30s), ≤50 assets total |
| How many subjects via **image** reference | **1–8 works well.** 9–12 possible, stability drops, expect retries |
| How many subjects via **audio/video** reference | **1–5 works well.** 6–10 possible, less stable |
| How long should a subject audio/video ref be | **5–10 seconds.** Longer reduces stability |
| Multi-view character sheets | Supported for 1–5 subjects (new in 2.5; 2.0 discouraged it). Above 5 subjects prefer single-view. If you need several angles, **split them into separate images — do not put multiple viewpoints inside one image** |
| Storyboard panels | **≤15.** More causes still frames or wrong ordering. Prefer stick-figure / line art, and **never put text on the storyboard image** |
| 3D clay-model granularity | **Coarse beats fine.** Simple geometric primitives for people and objects read better than detailed models |
| Video length for an **edit** task | **≤20 seconds.** Longer is less stable |
| Reference images alongside a video edit | **1–5.** 6–8 possible with reduced stability |
| Extension format | Use **`mov`** for both input and output to preserve colour, brightness and audio continuity |

### Do not fill the slots, and mind the order

Two pieces of official guidance that contradict the instinct to use the full 50:

- **"不建议用满素材上限" — do not use the full asset limit.** The recommended working set is
  **4–5 assets**: 1–2 character images, 1 scene, 1 camera-motion video, 1 audio.
- **"重要素材前置" — put the most important assets first.** Upload order is not just addressing;
  earlier assets get more precise adherence. Order is load-bearing by design.
- Minor but relevant to us: **landscape output produces spurious subtitles noticeably less often
  than vertical.** We shoot 9:16, so budget for an unwanted subtitle appearing and keep saying
  "no subtitles" in the prompt.

_Source: CN-language Volcengine docs, read second-hand. One confidence tier below the English
sources; worth re-verifying before it drives an expensive decision._

### Binding assets in the prompt — the part that actually fails

Numbering follows **upload order**: `@Image1`, `@Video1`, `@Audio1`. ARK's guidance on getting the
mapping right, all of which is about avoiding character confusion:

- **Bind every asset explicitly in the text.** Do not rely on information *inside* the image.
  ARK's own anti-pattern: writing "John" on the protagonist's picture and then saying "John is at
  school…" in the prompt. That reliably causes duplicated or swapped characters.
- **List mappings one by one** when there are several subjects, as a list rather than prose.
  *"Images 1-2 are Character 1 and correspond to Audio 1; Images 3-4 are Character 2 and correspond
  to Audio 2."*
- **State what each asset is a reference FOR**, and which part of it if only part applies.
  *"Refer to the action of casting the spell in Video 1 and the wrap-around camera movement in
  Video 2."* · *"Refer to Image 1 for lighting and filters."*
- **When the asset is already accurate, just point at it.** Do not re-describe a scene the reference
  already carries — say "strictly refer to the actions and camera movements in Video 1" and stop.
- **First/last frame has two modes.** Setting `role` to `first_frame`/`last_frame` is strict but
  **locks the output aspect ratio** to the first frame's. Passing the same images as
  `reference_image` and naming them in the prompt ("Image 1 is the first frame") does **not** lock
  the ratio, but the result only approximates them.

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

**BytePlus ModelArk** is the canonical API: model `dreamina-seedance-2-5-260628`, base
`https://ark.ap-southeast.bytepluses.com/api/v3`, async create-task → poll or `callback_url`.

**Exact request body, read off the live API reference 2026-08-13:**

```bash
curl -X POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks \
  -H "Content-Type: application/json" -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "dreamina-seedance-2-5-260628",
    "content": [
      { "type": "text",  "text": "… refers to @Image1 … camera movement of @Video1 …" },
      { "type": "image_url", "image_url": { "url": "https://…" }, "role": "reference_image" },
      { "type": "video_url", "video_url": { "url": "https://…" }, "role": "reference_video" }
    ],
    "generate_audio": true,
    "ratio": "16:9",
    "duration": 15
  }'
```

Note the nesting: `image_url` is an **object with a `url` key**, not a bare string, and `role` sits
as a sibling of `type`. `duration` is an **integer** here where fal takes a **string**. The example
sets an explicit `ratio` on a multimodal-reference task, which confirms reference tasks are
*unlocked*. Response is `{ id }`; poll it. There are also documented variants for edit, extend,
first-frame, **first-and-last-frames**, base64 image input, and plain t2v.

Full body params: `model` · `content[]` · `callback_url` · `return_last_frame` · `service_tier` ·
`execution_expires_after` · `generate_audio` · `draft` · `safety_identifier` · `priority` ·
`resolution` · `ratio` · `duration` · `omni_reference_task_type` · `frames` · `output_format` ·
`seed` · `camera_fixed` · `watermark`.

**⚠️ Unresolved conflict on `seed`, `camera_fixed` and `draft`.** They are all listed on ModelArk's
create-task page, which is the **generic** endpoint shared by every video model — a listed parameter
is not proof a given model honours it, and the Seedance 2.5 capability matrix reportedly marks
draft mode unsupported. What we know for certain: **fal does not accept `seed` as an input for
Seedance 2.5** (its schema says output-only) and **our two runs confirm it**. Do not assume a
reproducibility or draft lever exists until someone tests it on ModelArk directly.
It exposes fields the wrappers do not: `content[].role`
(`first_frame` · `last_frame` · `reference_image` · `reference_video` · `reference_audio`),
`camera_fixed`, `watermark`, `return_last_frame`, `omni_reference_task_type`, `service_tier`.

**⚠️ `seed` is NOT an input on Seedance 2.5 — it is output only.** fal's schema says so explicitly
and **our own runs confirm it**: we never sent a seed and got one back on both runs
(`1632188029`, `746924417`). An earlier version of this doc listed `seed` as a settable parameter on
every provider; that was wrong. **There is no reproducibility lever.** A CN-language Volcengine
source says `camera_fixed` is likewise unsupported on 2.5 — unverified by us, treat as likely.
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
| 2026-08-13 | PoC: collision `[The Operator]` | fal **ref2v** | 10s · 9:16 · 720p · audio on | **1 face-free scene plate** | 208s | ✅ **Best result yet.** Scene plate transferred completely; the collision read as an accident; the crouch + phone-to-ear + line all landed. Seed `927418445`. |
| 2026-08-13 | corridor v2 — **first reference call** | fal **ref2v** | 10s · 9:16 · 720p · audio on | 3 images (Nano Banana 2 face plates + env plate) | 210s | ❌ **REJECTED AT INPUT.** `content_policy_violation` — *"The images or videos provided may contain likenesses of real people or other private information that cannot be processed."* Settles the whitelist question: **a Nano Banana 2 face is not trusted.** |
| 2026-08-13 | corridor v1 `[Builder Diary]` | fal t2v | 10s · 9:16 · 720p · audio on | none | 180s | ⚠️ **Passed moderation, failed the brief.** Craft up, story down — see *The framing ate the story* below. Seed `746924417`, 3.50MB, -25.8 LUFS. |
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

### ✅ The face-free SCENE PLATE is the highest-leverage control we have

**2026-08-13.** After face references were ruled out, we passed a single **environment** plate —
an empty, art-directed corridor of an independent record label, generated with Nano Banana 2 — as
`@Image1`, bound as *"controls the OFFICE ENVIRONMENT ONLY … do not take any person from @Image1."*

**It passed moderation instantly and transferred almost completely.** Scuffed plaster, framed record
sleeves, gold discs, pendant lights on exposed conduit, worn wooden floor with a runner rug, the
window light and its direction — all present in the render, and the film stopped looking like a
generic corporate office.

**Why this matters more than it sounds.** Everything cinematic — location identity, lighting,
palette, lens character, set dressing, era — lives in the plate, and none of it involves a face, so
none of it touches the filter that closed the character route. **A scene plate is the cheapest
cinematic upgrade available on this model.** Generate it deliberately as a still, art-direct it
properly, and let Seedance populate it.

The corollary: **invest in the plate, not in adjectives.** Two lines of art direction inside an image
outperformed a paragraph of styling language in the prompt.

### 🔴 SETTLED: a third-party generated face is rejected as a reference

**2026-08-13, tested directly.** We passed three plates to `reference-to-video` — two character
plates generated with **Nano Banana 2** plus a face-free environment plate. Result after 210s:

```
422 content_policy_violation · partner_validation_failed
"The images or videos provided may contain likenesses of real people or other
 private information that cannot be processed."
```

**What this establishes:**

1. **The filter cannot distinguish a generated face from a real one.** It rejects *any*
   face-containing reference whose provenance it does not trust. "It's AI-generated" is not a
   defence and does not need to be true to be irrelevant.
2. **Nano Banana 2 output is not on the trust whitelist.** That is Google's model; the whitelist is
   reported to cover ByteDance's own image models (Seedream). Our house
   `faceguide-model-workflow` — Nano Banana 2 builds the guide, another model consumes it — **does
   not transfer to Seedance.**
3. **The "trusted model output" route is narrower than we hoped.** It is not "any AI-generated
   face"; it is "a face this vendor's own pipeline produced, unedited."

**What still works:** face-free reference images. An environment, product, style or layout plate has
no likeness to object to. Character identity has to come from either the prompt text or a
ByteDance-native generator.

**Untested and now the obvious next experiment:** generate the character plates with **Seedream**
(ByteDance's own text-to-image, reported on the trust whitelist) and retry. That is the one
remaining path to reference-controlled recurring characters on this model.

**Note the cost of failing:** 210 seconds, the same as a successful generation. Input rejection is
not fast — budget for it like a full run.

### 🔴 A generated "ordinary man" can be a real actor, and you will not see it until you crop in

**2026-08-13.** We generated character plates with Nano Banana 2, using frames from our own approved
corridor clip as the identity reference. The resulting studio headshot is a **clear likeness of a
well-known actor** — same face across both variants and both plates. Nothing in the chain asked for
a celebrity: the Seedance prompt said "an ordinary man in his early forties, plain everyday face."

**Why it hid.** In a 10-second walking shot, at distance, with motion blur, the face read as
"generic man" and passed review. Isolated as a clean 1792×2400 portrait, it is unmistakably
somebody. **The defect was present in the video the whole time; the crop only revealed it.**

**Two consequences:**

1. **Audit the FACE, not just the frame.** Before any generated character is reused or published,
   crop a tight headshot from the plate and look at it cold. A likeness that is invisible at walking
   distance is still a likeness, and the still frames we publish alongside a video are exactly the
   crop that exposes it.
2. **It gives a much better hypothesis for the v1 moderation rejection.** We blamed "noir styling"
   abstractly. The stronger explanation: a night office scene with a man in a loosened tie pulled the
   model toward *a specific show*, and generated a face from it — which is precisely what an
   output-side copyright classifier would catch. Styling did not trip the filter as an aesthetic;
   it steered the casting. That reframes the working rule from "avoid noir" to **"avoid prompts that
   evoke a specific production, because the model will cast it."**

**Do not feed a plate like this back into Seedance as a reference.** It stacks a likeness problem on
top of a filter that is explicitly looking for one.

### 🔴 The framing ate the story — twice, the same way

Two runs, two different subjects, **the same root failure: the thing carrying the story was not
visible enough to read.**

- **back-office v2:** the interruption was a phone *buzz*. Audio-only, so the cause was invisible,
  and the paper falling read as the man sweeping it off the desk in anger rather than knocking it
  by accident.
- **corridor v1:** the interruptions were *people*, which should have fixed it. They did not read
  either. The prompt asked three colleagues to step into the corridor and try to speak to him; in
  the render they stay at their desks, small, deep in the background and out of focus. Ten seconds
  of a man walking down a corridor, and nothing else.

**The cause the second time was the camera, and it was chosen badly on purpose.** A backward
tracking shot retreating ahead of the subject puts him large in the centre of a 9:16 frame and
everyone else far away at desk level. Optimising the shot to show *his* face structurally guaranteed
that the people who make the scene mean something would be background. The instruction "steps out
from between two desks" cannot beat a lens that is thirty feet away and pointed at someone else.

**Rules this produces:**

1. **Name what the viewer must SEE, not what happens.** "The phone buzzes" and "she begins to speak"
   are events, not images. Both got honoured in some invisible sense and neither reached the frame.
2. **Put the story element between the subject and the lens, or at the frame edge close to camera.**
   In a vertical frame anything past the mid-ground is set dressing. FAL's bodega prompt has the
   messenger *walk around* a stationary customer — an interaction inside the near field.
3. **A camera choice is a story choice.** Decide which the shot is about — the subject's face or what
   is happening to him — before picking the camera, because one lens cannot serve both in 9:16.
4. **Count the beats against the seconds.** Three interruptions in ten seconds at a fast walking pace
   is roughly three seconds each including approach and recovery. That is not enough room; the model
   quietly dropped them rather than rushing.

### ⚠️ Negative constraints are not reliably honoured for brand marks

The prompt said **"no logos"** and the render still put a clearly readable **Apple logo** on the
laptop lid, on screen for roughly half the take. **The corridor run fixed this** by saying *how*
rather than only forbidding it — "no brand marks or logos on any laptop, phone, wall or clothing;
all laptops closed or turned away from camera" — and no logo appeared. Prescribe the staging, do not
just ban the outcome. Do not trust a negative instruction to keep brands
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
3. ~~Does the "trusted model output" route clear the real-face filter?~~ **PARTLY ANSWERED
   2026-08-13: a Nano Banana 2 face is rejected.** Third-party generators are not trusted. The
   remaining question is narrower and worth one run: **does a Seedream-generated face pass?**
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
