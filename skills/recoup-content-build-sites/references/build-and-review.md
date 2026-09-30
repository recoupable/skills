# Carry the idea through the build

## Before implementation

Extract the selected action, first payoff and subject connection from the brief. List the actual inputs and assets available. Identify what must be authored rather than inferred from metadata. Preserve any exact controls, routes or output contracts required by the host.

Choose the simplest implementation that delivers the intended consequence. A creation tool needs meaningful editing and output. A challenge needs understandable rules and fair feedback. An interactive story needs authored changes. Shared participation needs real persistence or coordination.

## During implementation

- Put the activity at the center of the composition, with a clear entry point and appropriate loading state.
- Make feedback timely and proportionate. Sound, motion and visual change should clarify the action or constitute its reward.
- Let the interface respond to actual state. Do not fabricate progress, crowd counts, personalization, saved results or successful sharing.
- Use artwork and animation deliberately. Keep them readable at the device size where the interaction will happen.
- Provide keyboard access and visible focus for core controls. Support touch without requiring hover. Respect reduced-motion preferences and allow audio control.
- If sharing is part of the concept, produce the promised result and handle unavailable native sharing. Do not make sharing mandatory to receive the payoff.
- Show recoverable states for unavailable assets or services. Do not conceal a missing core capability behind a decorative fallback.

## A short outcome review

Try entry → first action → consequence → next meaningful action or ending. Ask:

1. Is the action apparent without reading the project pitch?
2. Does the result reflect the actual input and deliver the promise?
3. Is the content interesting, expressive or useful enough to carry the mechanism?
4. Does the subject contribute more than labels and colors?
5. Are controls and feedback usable on the intended device?
6. Are any external or shared features real and available?

Report specific observations and distinguish tested behavior from inferred quality. Use one focused repair pass when appropriate rather than repeatedly generating a new concept to escape implementation problems.

## Two important contrasts

**Weak adaptation:** “Rank three generic emotions and get a random artist personality.”

**Better proposal structure:** identify an opinion the audience already has, offer choices drawn from actual relevant material, and compose an output that clearly reflects those choices. Netflix's personal ranking is a reference for the pattern, not proof that the same execution fits every artist.

**Weak adaptation:** “Drag blobs while a song plays” presented as equivalent to Blob Opera.

**Better capability decision:** determine whether the system can produce responsive, musically coherent audio. If it cannot, choose a different payoff that the available assets can deliver rather than promising the missing musical behavior.


## Art and motion craft

Use `visual-experiences/GUIDE.md` and select the relevant chapters. Commit to one striking visual rule and a defining interactive moment. Specify composition, material and motion behavior concretely, not with adjectives like premium or cinematic. Let the first gesture visibly change the world within a moment. Develop the consequence more than the explanatory UI.

Borrow separately: an activity pattern from the interactive library, a visual language from a visual reference, and a motion mechanism from a motion reference. Do not copy another artist's identity or proprietary media. Keep the evidence labels: indexed clips and creator claims are not independent one-shot benchmarks.

Procedural art is not limited to placeholder geometry. Canvas, SVG and native WebGL can support painterly texture, articulated figures, lighting, parallax, fields and dimensional scenes when the implementation provides the actual rendering and behavior. Use real generated imagery when it solves a specific visual need. Preserve stable seeded texture, deliberate silhouettes and material consistency.

A small game needs responsive feel: anticipation, contact, response and readable recovery; a spatial scene needs grounded scale and motivated camera movement; a creative tool needs expressive variation and a result worth seeing. Do not require every experience to have a score, win/loss, camera orbit, particles or a download.

Review normal-motion output before judging animation. Inspect entry, the key action and payoff, and retain the payoff evidence before replay/reset. Reduced-motion support is a separate usability check, not the only view of the work. Compare against the selected reference mechanisms and repair the largest visible weakness; do not invent additional approval tests unrelated to the promised experience.

## Game craft: reference, build, critique, repair

Apply this section when the approved experience is a game or playable scene. For a creative tool or story, borrow the evidence and repair discipline without adding game mechanics. This is Recoup's adaptation of `ericzakariasson/skills` game-builder, reviewed at commit `090915f84d75a38c4d42fc3e5034e4fef94d8fbb`: https://github.com/ericzakariasson/skills/tree/090915f84d75a38c4d42fc3e5034e4fef94d8fbb/skills/game-builder. The source is MIT licensed. Consult `references/game-builder-source.md` for provenance and the adaptation boundary in file-capable hosts; this section carries the runtime guidance in full.

### Lock a visual target before polishing

Preserve the approved activity, opening sequence, controls and payoff. Select a small set of relevant shipped-game references that demonstrate the intended camera distance, composition, art treatment and interface. Record source URLs and distinguish screenshots actually inspected from descriptions only. References are review material, not assets to ship. Use original art and approved artist assets; do not lift another game's characters, UI or music.

Write a compact visual bar into the direction or persistent working summary: criterion, reference, observable pass condition and visible failure signs. Cover coherent art/material treatment, silhouette and composition, readable controls, feedback, and consistency from entry through payoff. Add only criteria justified by this experience. Keep the bar fixed during repair; improvement over the last round is not sufficient evidence of completion.

Choose rendering technology to fit that target and the host's supported stack. Pixel art, illustration, flat graphic design, Canvas, SVG and 3D can each be finished art. Do not force PBR, shadows, bloom, dense geometry, Blender or a new engine onto a 2D or deliberately minimal concept. If the target needs spatial depth, implement real depth cues and coherent perspective rather than disguising a flat backdrop as a working 3D world.

### Build playability and art as distinct milestones

First prove the core loop: invitation, one understandable first action, immediate response, earned result and replay or ending. A successful loop is a functional milestone, not visual approval. Keep input, simulation/state and rendering separable so art improvements do not break controls or outcomes.

Then refine in deliberate passes: overall value structure and composition; material or illustration treatment; silhouettes and scene detail; typography and controls; motion and response. In 3D, establish light and camera before polishing individual assets. In 2D, establish shape, palette, layering and texture instead. Detail must support readability, not merely fill space.

Maintain an asset ledger in the working summary with role, source, draft/final status and remaining defect. Review generated media inside the actual composition at the intended camera and screen size. A successful generation request does not establish visual suitability. Replace accidental placeholders before finishing. Intentional geometric art is valid when it delivers the selected style; a debug box standing in for a promised character is not.

### Review current evidence independently

Use the host's separate review call or a fresh critic context where available. Keep builder self-assessment out of the visual verdict. Evaluate current rendered captures, not a pitch or claims of effort. Pair the opening, active interaction and payoff on mobile and desktop with the selected reference views when those images are available. Match scale and framing; a blur comparison can expose weak value hierarchy or empty composition before surface detail distracts. Never claim a side-by-side comparison when reference images were not supplied.

Judge each applicable criterion independently; do not average away an unreadable control or weak payoff with an attractive background. Preserve the host's verdict schema. A visual pass does not replace functional, opening-sequence or accessibility checks. Stills cannot establish smooth animation; inspect motion evidence when available and name any unverified temporal qualities. Record which build the evidence represents and recapture after repairs.

Write repairs as: criterion → capture and region → observed defect → reference or intended behavior → observable completion condition. Example: “At the mobile result, the reward covers the replay control. Complete when both remain readable and the replay action works without dismissing the reward.” Avoid vague praise, conditional passes and instructions to make it more premium.

### Diagnose repetition instead of repeating it

Carry the visual bar, asset ledger, unresolved defects and last repair outcome in the host's persistent summary so compaction preserves decisions. When the same defect survives two repair rounds, change the implementation approach. After three rounds with the same failure family, diagnose why: wrong art source, incompatible renderer, faulty framing, inadequate capture, or a repair that only changes decoration. State what to stop doing, a different next action and what visible evidence will demonstrate progress. Use a separate diagnosis context if the host supports it; otherwise record the diagnosis explicitly without pretending another agent ran.

Continue through the host's repair workflow. Do not replace its orchestration with a nested unbounded loop or require unavailable tools. Keep a usable draft and report capability gaps honestly. Missing comparison or motion evidence is unverified, not a fabricated pass and not a reason to repeatedly request unsupported captures. Finish only when the promised activity and supported quality checks pass; preserve publication permissions and subscription gates.
