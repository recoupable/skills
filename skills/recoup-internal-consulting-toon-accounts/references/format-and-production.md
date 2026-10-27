# Format analysis and toon production

Use this guide to inspect an existing format or produce episodes from approved canon. It supplies mechanics, not character ideas. The operational recommendations below are testable craft/engineering heuristics; source observations and provider-specific support are separated in `references/evidence.md`.

## Inspect the viewing experience

Build a small comparison set from the selected references. A practical starting sample is roughly a dozen chronological posts per account, expanded only when it could change the decision. Keep pinned hits as a separate discovery sample. Include weak and ordinary posts; do not only study the examples a successful creator chose to show. Without reliable public chronology/metrics, label the comparison qualitative and request an owner export only if required for the decision.

For each clip record:

| Layer | What to observe |
| --- | --- |
| Entry | First visible frame, initial movement, caption presence, focal point, whether the situation is legible on a phone |
| Character | Silhouette, scale, markings, facial vocabulary, prop ownership, recognizable habits; continuity across posts |
| Relationship | Who wants what, what creates friction or dependence, whose reaction gives the action meaning |
| Attention | Anomaly, recognizable situation, unanswered question, anticipation, delayed information—not simply “a hook” |
| Progression | Timestamped changes in state; action, reaction, escalation; redundant holds or confusing cuts |
| Payoff | The exact promise resolved; whether the last reaction changes the interpretation; whether the ending earns a replay |
| Craft | Shot scale, screen direction, camera behavior, edit rhythm, expression holds, staging, sound/music role |
| Packaging | On-screen premise versus post caption; text legibility; cover/profile promise; native format |
| Response | Available views/reach/watch/share/follow evidence with definitions and dates; unavailable fields remain unknown |

Record what was actually watched/heard. With frames alone, use intervals rather than asserting exact action/cut times, audio choices, fluidity or seamless loops. Inspect dense frames around a suspected failure, then return to playback. Never infer genuine engagement, audience demographics, AI tools or monetization from appearance.

## The viewer jobs to solve

Think of these as separate creative tests, not a proprietary ranking formula:

1. **Notice:** a clear situation or anomaly is visible immediately. Motion should reveal meaningful information; a random zoom can attract attention without making anyone care.
2. **Understand:** a stranger can identify the subject, desire/problem and action without reading a biography. In a duo, the contrast must be behavioral, not only two different colors.
3. **Anticipate:** the opening creates a specific question. Each beat changes the viewer's expectation instead of restating the setup.
4. **Feel the resolution:** the action answers that question. A generic affectionate ending cannot repair an unrelated setup; a surprise still needs readable causality.
5. **Send or return:** a recipient recognizes the relationship or emotion; a follower expects more of the same emotional promise with new situations. A CTA cannot substitute for either reason.

Not every format needs conflict. Ritual, competence, contrast, visual discovery and transformation can sustain attention. Identify the observed mechanism rather than forcing every clip into one joke template.

## Caption and story construction

Write the audience-facing premise before expensive production, then verify the visual story fulfills it. Keep on-screen text separate from the post caption and from generation prompts. Treat text as one layer of comprehension, not an explanation for an unreadable action.

- **Situational recognition:** identifies an everyday behavior the visual scene demonstrates. Useful when the audience thinks of a real person or shared experience.
- **Choice:** presents visibly distinguishable alternatives. The comparison must actually appear; arbitrary questions added after the fact are weak tests.
- **Explanation/fact:** a question leads to a supported answer. A cartoon is not evidence for a medical, financial or other factual claim; verify the claim independently or keep it clearly fictional.
- **Interpersonal sharing:** frames the emotion for a specific recipient. Natural relevance is more important than repeatedly ordering people to send it.

These categories come from the source article; they are options, not mandatory CTAs. Keep one main premise. Place captions using the actual platform UI and moving subjects; inspect beginning, midpoint and ending, not a single poster frame. Add text in post so copy and timing stay editable.

## Canon versus variation

The private cast/series bible should establish:

- Stable identity IDs, silhouettes, relative heights, distinctive markings/outfits and permitted variations.
- A pair/group relationship matrix: motives, habits, tenderness/friction, expected reactions and behaviors that would break character. One recurring character is valid; do not add another merely because an article recommends pairs.
- A small set/layout map, screen direction, prop ownership and scale; rules for any persistent story state.
- Visual language: 2D/3D treatment, line/material style, palette, lighting, camera grammar and expression range.
- Audience promise, content boundaries, caption voice, sound/voice references when needed, and approved-source provenance.

Maintain separate original anchors, reviewed derived references and held experiments. Use a clean per-character image and a joint scale/composition reference when supported. A collage with several faces is not automatically a valid model input. Verify provider limits and select a deliberate subset of references per shot.

Freeze the selected reference version within a comparison. Version intentional redesigns rather than forbidding character evolution forever. Compare new renders to the original anchors, not only the most recent generated frame, to catch gradual drift.

The episode may change its situation, action, reveal and supporting props while preserving that identity and emotional promise. New file hashes or seeds do not prove original performance. Inspect the visible action and story; recaptioning or recoloring the same clip remains reuse.

## Choose the cheapest controllable production route

| Route | Use when | Retain control through | Main failure to inspect |
| --- | --- | --- | --- |
| Deterministic 2D / cutout / rigged | Flat characters, a restricted set of poses, simple staging and precise reactions | Approved layered/vector assets, pose/expression library, keyframes, explicit shot timing | Stiff motion, unreadable poses, sliding contacts, insufficient acting |
| Reference-conditioned image-to-video | Soft 3D or textured worlds where generated motion adds value | Approved shot stills, simple action prompts, bounded shot lengths, reference/model versions | Face/marking swaps, fused bodies, prop changes, invented camera or actions |
| Edited multi-shot sequence | A story depends on reveals, locations, changing shot sizes, or exact musical timing | Storyboard/animatic, separate shot generation, continuity map, deterministic assembly | Missing causal links, inconsistent geography, mismatched character/prop state |

These are candidate implementations, not claims about how reference creators made their films. Reuse an established local renderer or content engine before building another. Simple 2D does not automatically require an AI video provider; complex animation is not automatically cheap or free. Record labor and rework as well as compute.

## From beat sheet to shots

For every shot specify its start state, one dominant observable action, intended end state and function in the story. Describe physical behavior rather than abstract adjectives. Resolve who is left/right, what each character holds and where the camera is. Keep a clear focal hierarchy; use reactions/cutaways when simultaneous interactions exceed the renderer's reliability.

Use an animatic or timed still sequence to test comprehension and pacing before motion spend. Length follows the actual beats and audience evidence. A short relational gesture, a multi-shot joke and a long choice montage need different structures; do not pad to a model's duration or compress a story into an arbitrary fifteen seconds.

For image-to-video:

1. Select approved character, environment and composition references. Make the shot still, then inspect identity, anatomy, prop state and staging before animating it.
2. Supply the still as the visual condition. Write motion, camera behavior and the essential transition; do not retell the entire series bible in every prompt.
3. Phrase instructions according to the exact model's documented behavior. For example, Runway's Gen-4 guide recommends positive descriptions and simple motion; do not generalize its unsupported-negative-prompt rule to every provider.
4. Simplify a failing interaction or split it into separate shots. Do not endlessly add constraints or disguise blocked content to force a provider through.
5. Use end-frame chaining only when the endpoint supports it and identity remains anchored; otherwise prepare the next shot independently from approved references. Track both shot boundaries and persistent prop states.

A neutral prompt structure is: **[subject locator] + [visible action] + [other subject's reaction if simple] + [camera behavior] + [end state]**. It is a planning structure, not a universal API schema or an invented account scene.

For submitted jobs, reconcile execution status and billing separately. A client timeout does not establish failure or zero cost. Pending: inspect the existing job rather than resubmit. Completed: retrieve/archive the result and review it. Confirmed terminal failure: retry only within the existing authorization and remaining budget, preserving the original attempt's cost. Unknown: hold a paid retry while continuing independent preparation that cannot duplicate the job.

## Edit and review

Trim dead lead-ins, retain enough anticipation/reaction to read the action, and cut at meaningful state changes. Do not add arbitrary movement, transitions or sound effects to disguise a weak payoff. A loop should arise from composition/story, not reversing speech or forcing a confusing reset.

Sound is a separate design pass: dialogue/voice, expressive nonverbal sounds, contact/action Foley, ambience and music. Decide which layer tells the story. For exact beat reveals, align cuts in the editor to the chosen audio; do not rely on generated motion to hit frame-accurate beats. Use authorized audio; a sound available in one platform's library is not evidence of rights for every destination. Check music/dialogue balance and clipping on the final export.

Inspect:

- Identity across all shots and expressions; distinct subjects do not fuse or exchange identifiers.
- Physical intent and prop contact; object permanence, scale, hands/limbs, eye lines and screen direction.
- Comprehension muted, and timing/emotion with sound. Wordless does not mean soundless.
- The actual promised payoff, including the final reaction and any loop seam.
- Platform crop, text-safe placement, readable contrast, cover and caption correspondence; no unwanted tool/platform watermark.
- Exact export duration, dimensions, frame rate and audio, plus source/final hashes.

The reviewer can pass, request a specific repair or reject. Keep reasons tied to frames/timestamps and the intended beat. Quantitative rubrics help compare iterations but do not certify future virality. Scale a batch only after the minimum acceptable output is reproducible within the declared cost and labor bounds.
