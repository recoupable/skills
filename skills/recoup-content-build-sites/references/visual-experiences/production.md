# Production: time, sound, performance, and delivery

## Choose the correct time model

**Live UI:** Respond to current state and input. Make transitions interruptible; do not queue decorative animations behind rapidly changing user intent. A spring can preserve velocity when retargeted if the chosen implementation supports it. A fixed easing curve may be simpler for a known transition. See [spring physics](https://www.joshwcomeau.com/animation/a-friendly-introduction-to-spring-physics/).

**Authored film:** Prefer explicit timeline data and a render function evaluated at a requested timestamp. Seed randomness and keep frame evaluation independent of previous calls. Render frame i at i/fps; test repeated timestamps in different orders. [Opus JS Animations](https://github.com/klsoen/opus-js-animations) documents this approach and frame inspection tools.

**Stateful simulation:** Integrate at an appropriate fixed step; render from the current or interpolated state. Export with deterministic replay or cached trajectories. Do not retrofit a pure time function by ignoring the solver's history.

## Timing and easing

Define a small motion vocabulary appropriate to the brand and medium. Distinguish quick feedback, ordinary state changes, larger spatial changes, and expressive moments. Tune durations by distance, content, frequency, and device. [Carbon's motion guidance](https://carbondesignsystem.com/elements/motion/overview/) is a useful concrete system, but its token values and no-bounce style are not universal.

For films, translate tempo into useful event times when music drives the structure: beat duration is 60/BPM seconds. Sync selected important actions; not everything must hit every beat. Reading time, acting, and explanation can override the grid. [JavaScript Animation Skills](https://github.com/iart-ai/javascript-animation-skills) provides an example of shared shot and sound event timing.

## Sound that belongs to the picture

Keep one event schedule for major visible actions and their audio cues. Separate ambience, music, speech, and transient effects so levels can be adjusted independently. Preserve supplied audio according to the brief; do not silently change it. Check headroom, intelligibility, start/end cuts, and tails. Sound should reinforce physical or narrative events rather than cover every movement.

Compare the actual mixed export with the visual at both normal playback and key contacts. Nominally matching durations do not prove synchronization. If sample rate divided by frame rate is not integral, use timestamps or rational arithmetic rather than accumulating rounded samples per frame. Keep captions or a visual explanation when speech carries essential meaning.

## Review passes with distinct jobs

| Pass | What it catches | What it cannot prove |
|---|---|---|
| Opening / key stills | Hierarchy, composition, material, type | Rhythm or smoothness |
| Contact sheet | Visual consistency and scene progression | Fast-action continuity or audio sync |
| Consecutive-frame strip around a transition | Clipping, pose discontinuities, occlusion | Overall pacing |
| Normal-speed playback with sound | Rhythm, synchronization, readability | Interactive correctness |
| Live controls and repeated use | State, input, interruption, recovery | Export correctness |
| Final-file inspection and playback | Format, dimensions, timing, actual delivery | Quality in every untested environment |

Use a quick preview to solve the visual problem before an expensive full-resolution render. After the final encode, inspect the final file again. Keep a known-good output until the replacement has finished successfully. The [Claude Animation harness](https://github.com/buildwithhanif/claude-animation-skill) illustrates frame strips, deterministic verification, and staged export.

## Keep live motion responsive

Prefer transform and opacity for ordinary DOM movement when they fit. Profile the rendering pipeline before selecting costlier effects, and avoid adding `will-change` everywhere. [web.dev](https://web.dev/articles/animations-guide) explains compositing, layout/paint costs, and profiling.

Reduce render resolution or expensive scene work based on measured need. Stop or reduce unnecessary work when the experience is hidden, and clean up observers, animation loops, listeners, and GPU resources on teardown. For libraries with breakpoint helpers, check their cleanup semantics; [GSAP matchMedia](https://gsap.com/docs/v3/GSAP/gsap.matchMedia()/) supports responsive and reduced-motion animation contexts.

## Accessibility without losing the idea

Honor reduced-motion preferences for nonessential movement. Replace large parallax, zooms, and repeated motion with stable compositions, direct state changes, or restrained alternatives that preserve the information. Keep controls operable by the relevant input methods and expose meaningful labels or explanations outside an inaccessible canvas when needed.

Provide pause/stop/hide for qualifying automatically moving content presented alongside other content. [WCAG 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) is Level A and includes specific conditions and exceptions. [Animation from Interactions, 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) is Level AAA; do not misstate it as a blanket Level AA requirement. Reduced motion is a design behavior, not proof of complete accessibility conformance.

## Deliver to the actual destination

Verify requested dimensions/aspect ratio, duration, frame rate, file type, sound, and loop behavior. Check safe areas and readable type in the final crop. Do not blindly crop a horizontal composition into vertical; recompose when it changes the focal hierarchy.

For websites or apps, show the running result and summarize tested paths. For a film, deliver the playable export with editable source and relevant credits. State constraints plainly: “repository reviewed,” “frames inspected,” “controls tested,” and “export played” describe different evidence.

## Generated art as an input to an interactive world

Use generated media for a specific job: a painted environment, tactile material, editorial photograph, or composed illustration. Write the intended crop, silhouette, palette, lighting, empty interaction area and relationship to foreground controls. A beautiful image that obscures the controls fails its job. Generate small previews before committing to expensive video.

Keep live interaction in the site: a cinematic background is not a playable scene, and a still character does not supply a walk cycle. Use code for responsive movement, object manipulation and branching state; use generated media where it supplies material or imagery the chosen world needs. Do not paste a video behind a generic card and call the result immersive. Recompose for phone and desktop rather than assuming a centered crop works.

## Choose a model for the asset's job

The Sites director must name a production model and explain the choice for each asset. These are candidates to evaluate, not a universal quality ranking:

| Job | Current candidate | Constraints |
|---|---|---|
| Authored hero illustration, precise composition, convincing materials | GPT Image 2 through Vercel AI Gateway (`openai/gpt-image-2`) | Use explicit supported pixel dimensions; the current adapter uses landscape 1536×1024, portrait 1024×1536 or square 1024×1024. Compose safe crops for the requested layout. |
| Reference-led character or product artwork | Nano Banana Pro through Fal (`fal-ai/nano-banana-pro`, `/edit` with references) | 2K still image. Identity consistency is a test requirement, not a promise. |
| Short cinematic reveal or environmental motion | Seedance 2.5 through Higgsfield (`bytedance/seedance-2.5/text-to-video`) | Current Sites budget: one silent 4–6 second 720p clip, static fallback, pause and reduced-motion behavior. A seamless loop is not guaranteed. |
| Precise kinetic type, responsive feedback, game state, user-controlled motion | Live HTML/CSS/SVG/Canvas | Keep input and state in code. Never simulate controls inside a generated video. |

Do not use the retired Recraft, Soul or Muse defaults. Choose at most two generated assets and only when they serve the activity. Model novelty does not excuse poor composition. Preserve a coherent visual language across the generated art and live graphics. A cinematic clip behind generic cards is not an immersive experience.

Primary references: [Gateway image generation](https://vercel.com/docs/ai-gateway/modalities/image-generation), [Nano Banana Pro API](https://fal.ai/models/fal-ai/nano-banana-pro/api), [Nano Banana Pro editing](https://fal.ai/models/fal-ai/nano-banana-pro/edit/api), [Seedance 2.5 API](https://open.higgsfield.ai/models/bytedance/seedance-2.5/text-to-video/api-reference).

### Learn from actual outputs

Keep the selected model, rationale, request identifier and elapsed generation time with the saved asset. Read previous completed site reviews from the same workspace before choosing again. Asset-specific failures are evidence to change a choice or prompt. A whole-site verdict does not isolate model quality; do not turn it into a model leaderboard or claim the model was trained. Failed or unreviewed generations are not positive examples. Inspect the image at its actual crop; review video over time, not only its first frame.

A same-brief exploratory comparison on 2026-09-29 produced two usable lunar toy-stage images: GPT Image 2 took about 92 seconds and emphasized detailed glass/materials; Nano Banana Pro took about 38 seconds and produced cleaner toy silhouettes and a wide stage composition. These are observations from one prompt without reference images, not evidence of general superiority or identity preservation. Seedance 2.5 also completed the five-second silent video request. Completion alone does not establish motion quality. Compare again on a different visual task before generalizing.

### Hyperframes and authored motion

[Hyperframes](https://github.com/heygen-com/hyperframes) renders HTML/CSS and seekable animations into video. It fits deterministic title sequences, trailers or result films, not the state engine of a live game. [Claude Motion Director](https://github.com/abdullatif06/claude-motion-director) is one concrete Opus 5.5 project built on Hyperframes; this does not establish what every viral demo used.

Useful principles to borrow now: define the visual look before animation, write a short shot plan, use explicit timing, inspect representative frames, then watch normal-speed playback and revise. The current Sites engine does **not** have a Hyperframes rendering service. Do not invent a render endpoint or claim an export exists. Keep live motion in the available web runtime; introduce a separate deterministic render adapter only when a real export requirement calls for one.

Keep provider credentials server-side. Generation is asynchronous: retain the accepted request ID, poll the returned status URL, stop on terminal failure, and never repeat an ambiguous paid submission automatically. Copy completed media into durable workspace storage; provider URLs are temporary. Authenticate polling only against the provider's trusted origin, validate downloaded media and bound file size. Budget and meter the selected model's actual unit price rather than reusing another provider's rate. Follow the [request lifecycle](https://docs.higgsfield.ai/docs/concepts/requests) and [authentication guidance](https://docs.higgsfield.ai/docs/authentication).
