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

For server integrations, [Higgsfield's model catalog](https://open.higgsfield.ai/explore) is the discovery source. Read the exact selected model's API reference; names available in a consumer app or CLI do not establish REST access for a particular account. Two documented image options are [Recraft V4.1](https://open.higgsfield.ai/models/recraft/v4.1/text-to-image/api-reference) for illustration/graphic imagery and [Soul 2](https://open.higgsfield.ai/models/higgsfield-ai/soul/v2/standard/api-reference) for photographic editorial imagery. Select deliberately, preserve model/request provenance, and verify account access with a real generation. Documented availability is not proof of a funded account or a successful request.

Keep provider credentials server-side. Generation is asynchronous: retain the accepted request ID, poll the returned status URL, stop on terminal failure, and never repeat an ambiguous paid submission automatically. Copy completed media into durable workspace storage; provider URLs are temporary. Authenticate polling only against the provider's trusted origin, validate downloaded media and bound file size. Budget and meter the selected model's actual unit price rather than reusing another provider's rate. Follow the [request lifecycle](https://docs.higgsfield.ai/docs/concepts/requests) and [authentication guidance](https://docs.higgsfield.ai/docs/authentication).
