---
name: recoup-music-video
description: Make a narrative music video using the Small Room workflow — approved song, story bible, scene audit, character audition, props, location plates, shot list, reviewed stills and end frames, motion, and verified edit. Use for "make a music video", "turn this song into a film", or "follow the Small Room workflow". Reuse approved audio; stops at the asset unless publishing is requested.
hooks:
  Stop:
    - hooks:
        - type: prompt
          timeout: 30
          prompt: |
            You are the analyze-gate reviewer for the recoup-music-video skill. The main agent is about to stop. Decide whether to block.

            The rule: the agent must NOT claim a video is finished — 'ready', 'done', 'here's your music video', 'final', 'good to go', or any equivalent — unless an analyze-gate result for THAT render appears in the conversation. A render returning the right duration is NOT evidence it looks right; the agent cannot see motion without analyzing.

            Decide:

            1. If the agent produced or is presenting a generated VIDEO asset AND is claiming it is finished/ready AND there is no analyze-gate pass (or explicit visual inspection of read frames) for that asset in the conversation, block:
            {"decision": "block", "reason": "video presented as ready without an analyze-gate pass", "systemMessage": "Read frames from the finished render (or POST /api/content/analyze) and review the result before claiming it's ready. If it fails, regenerate and re-analyze; if borderline, surface the analysis to the user instead of asserting success."}

            2. Otherwise approve:
            {"decision": "approve"}
---

# Music video — the Small Room workflow

Follow the production sequence used to finish **SMALL ROOM / The Projectionist on
2026-09-03**. This is the combined workflow recorded in its bible, identity sheet,
final shot table, generators and render, not a ten-step procedure from one Higgsfield skill.
Read `references/small-room-production.md` for the evidence, final model settings and
historical-versus-current execution differences before selecting generation routes.

**Song → bible → scene audit → character and audition → props and plates → shot list →
reviewed stills → revised clip table and end frames → motion → verified edit.**

Start at the earliest unfinished step. Reuse approved artifacts and keep their approval
state in the project; do not regenerate the song or reopen unchanged decisions on resume.
Carry forward the user's visual direction. Reproduce the workflow, not Small Room's
protagonist, photoreal style, palette, plot, duration or exact number of shots.

## Supporting skills and precedence

Load the linked skill at its relevant step. The Higgsfield links are pinned to the reviewed
community library; its character-design framework credits **@vavavinca**. The essential
instructions used by Small Room are included below so no private project checkout is needed.
If an external skill cannot be loaded, disclose that limitation and use the included method.

| Stage | Accompanying skill | What this workflow takes from it |
|---|---|---|
| New song, only when needed | [recoup-song](https://github.com/recoupable/skills/tree/main/skills/recoup-song) | Four approvals; Recoup API generation; maximum duration headroom |
| Bible and character audition | [higgsfield-character-design](https://github.com/OSideMedia/higgsfield-ai-prompt-skill/tree/c0b73ab946df6658cca513db78bdc3909a655bfd/skills/higgsfield-character-design) | World-first bible, character sheet, screen test and identity lock |
| Story audit | [higgsfield-scene-engine](https://github.com/OSideMedia/higgsfield-ai-prompt-skill/tree/c0b73ab946df6658cca513db78bdc3909a655bfd/skills/higgsfield-scene-engine) | Goal, obstacle, tactic, reversal and audience value shift |
| Shot list | [higgsfield-shotlist-director](https://github.com/OSideMedia/higgsfield-ai-prompt-skill/tree/c0b73ab946df6658cca513db78bdc3909a655bfd/skills/higgsfield-shotlist-director) | Global style, reference glossary, named prompts, tempo and monotony audits |
| Composition and verification | [hyperframes](https://github.com/recoupable/skills/tree/main/skills/hyperframes) and [hyperframes-cli](https://github.com/recoupable/skills/tree/main/skills/hyperframes-cli) | HTML timeline, captions, lint, snapshots, render and inspection |
| Recoup authentication, when using its routes | [recoup-platform-api-access](https://github.com/recoupable/skills/tree/main/skills/recoup-platform-api-access) | Verify the account and API contract without exposing credentials |
| Authorized Recoup staff publishing | [recoup-internal-social-ship-posts](https://github.com/recoupable/skills/tree/main/skills/recoup-internal-social-ship-posts) | Approved copy, platform publication, verification and logging |

Small Room adapted these methods: its shot list was `SCRIPT.md`, its audition was silent,
and its scene motion was H3 Max Turbo. Do not import the linked skills' Seedance multi-cut
prompts, HTML shot-list deliverable, Soul training or dialogue audition as extra stages.
The finished bible supplies the visual identity for HyperFrames; do not choose a new style
while assembling the already approved film.

## 1. Approve the song and establish the actual timings

Use the exact approved recording and lyric sheet. If no song exists, follow `recoup-song`:
approve idea, genre, exact lyrics/prompt, then the paid request. Its current default is
maximum supported duration (300 seconds), allowing a natural ending. Do not copy Small Room's
historical 120-second request or generate another song merely to enter this workflow.

Save the master, generation ID and approved inputs under `audio/`. Measure the actual file
with ffprobe. Transcribe with **ElevenLabs Scribe**, retaining word timestamps in
`audio/scribe.json`; compare them with the approved lyrics and flag changes, omissions,
repeats and cutoff. Do not use Whisper for this workflow. Get the user's listening approval
before developing the film. An existing approval satisfies this gate.

The recording determines the film's musical runtime. A later end card has its own separately
approved duration. Do not truncate the song to a generic social-video target.

## 2. Write the story bible

Use the character-design method to write one project-level `BIBLE.md`, in this order:

1. **Premise:** an arguable claim, the counter-argument it must respect, and emotional promise.
2. **World:** physical, social, economic, ideological, historical and sensory rules, limited
   to the detail this film needs.
3. **Character:** thematic role, external/internal goals, psychological/moral needs, wound,
   spark, silhouette, contradiction and relevant relationships. World before casting.
4. **Story spine:** causal beats connected by consequences, with a turning point and ending.
5. **Style:** palette, lighting, materials, proportions, camera language, wardrobe, props,
   continuity and forbidden elements. Derive it from the approved song and user direction.

Record the audio source and measured length. Propose missing creative choices explicitly.
The bible is a reviewable file, not only prose scattered through the conversation.

## 3. Audit the story, then approve the bible

Run the scene-engine audit inside `BIBLE.md` before any character or scene generation:

- **Goal:** the lead's fixed objective; each scene must contribute to it.
- **Obstacle:** what threatens that goal or its current stage, and at what scale.
- **Tactic:** the action taken with available knowledge; a failed attempt must teach something.
- **Reversal:** at least one turn against expectation in each resolved sequence.
- **Value shift:** how that reversal changes the audience's judgment of the character.

Name the weakest point and offer a minimal fix and a fuller alternative. Apply the user's
choice, present the revised bible, and obtain approval. A plot turn without an audience
reassessment is not enough. Preserve approval for unchanged decisions; approve affected
revisions before they propagate into paid assets.

## 4. Design, audition and lock the character

Use **Muse Image** for the candidate stills and reference edits. Build character sheets on
plain grey, then separate face and body references: front/back wardrobe, face close-up and
needed angles; include mouth-open/closed variants when relevant. Present the candidates and
let the user select the character before motion testing.

Stage a **silent five-second screen test** of an actual demanding beat from the film,
using **H3 Max Turbo** at the settings in the production reference. It must prove the
character can act with gaze, posture and hands. Small Room tested looking from a failing
lamp to the projector, deciding, and beginning a hand movement; derive this film's test
from its own bible. Use the agreed audition take count, review the motion, and obtain the
user's choice before locking a winner.

Save the selected take and reference roster in `cast/`, with `cast/IDENTITY.md` containing:

- one appearance paragraph reused verbatim in every applicable still prompt;
- one movement sentence reused in applicable motion prompts;
- each reference's role and the state it preserves.

Appearance belongs in still prompts; motion prompts describe action and the movement lock.
Use the face plus at most two other relevant references per scene still, as Small Room did.
When identity drifts, inspect the reference selection before rewriting the character.

## 5. Build props, then empty location plates

Create prop sheets on grey before the scene stills. Lock relevant dimensions, construction,
orientation and state changes; derive variants as edits of the approved prop.

Then make empty location masters in `plates/`. Derive dark/lit/transformed versions as edits
of the same room, preserving geometry. Review and approve props and plates before combining
them with the character. State each reference's role; character, prop and location must
agree on the film's material and visual style. Do not automatically make extra camera-angle
plates for every location.

## 6. Write the song map and connected shot list

Use the shotlist-director method in **`SCRIPT.md`**. Include:

- the first-frame visual hook and the film's premise as readable action;
- song sections anchored to the measured word timings;
- one global style prefix from the bible and the locked identity paragraph;
- an `@`-glossary mapping character, prop, plate and state references to real files;
- per-row ID, song window, duration, story beat, framing, camera move, references, start
  state, intended end state, still prompt, motion and caption.

Start with the picture: no opening logo, title card or fade. The song supplies the voice;
do not introduce a separate narrator or an on-camera singing requirement.

Check that the windows cover the complete recording with no gaps or overlaps. Read the
framing and camera columns together: avoid three consecutive shots with the same size and
move. Vary scale and purpose, not merely duration. Show the table for approval before
scene still generation.

## 7. Generate and review scene stills

Use Muse edits of the approved references, with this prompt assembly:

`global style + identity (when present) + location lock + framing + scene state + continuity`

Attach face first when present, then the relevant plate and prop, with at most three
references. An approved earlier shot may supply a more precise location/state reference.
Keep reference roles explicit. Save the exact prompts, reference assignments and results.

Review a contact sheet and individual detail crops with the user before scene motion.
Check identity, hands, prop count/scale/orientation, lighting, background figures, stray
text and the physical cause of every effect. Fix the still first when the flaw is already
visible there. Feed corrections back into the bible's continuity rules and affected rows.

## 8. Revise the clip table and approve end frames

After still review, combine adjacent beats when **one camera setup can cover a continuous
unit of action within the model's duration limit**. Preserve the lyric windows. Split when
framing, location or action cannot be staged coherently together. Small Room changed from
26 planned shots to **17 final clips**; that count is evidence, not a target for every film.

For each clip, assign its approved start still. When a planned change needs an end frame,
make it as an **edit of that start still with the same camera position and framing**.
Only change the intended state. Show start and end side by side before motion spend.
For a held state, Small Room sometimes reused the start as its end anchor; some rows used
no end frame. Do not require a newly generated end frame for every clip.

Mark the revised table as current and archive superseded rows/stills. The active table,
render timeline and generation manifest must agree. Do not let an old build checklist
silently restore the superseded shot count.

## 9. Test the interpolation, then generate and review motion

Generate **one representative start/end clip first**. Small Room used the opening M01,
13 seconds, to test the interpolation. Review it before the scene batch.

Use **MiniMax H3 Max Turbo**, 768P, integer durations 5–15 seconds and
`prompt_expansion_mode: disabled`, subject to the verified route and approved spend scope
in `references/small-room-production.md`. Request enough clip duration for the assigned
window, then trim in the edit.

Motion prompt = row action + applicable movement lock + locked camera or named camera move
+ project-specific continuity exclusions. Do not re-describe appearance. Omit character
movement/face clauses from shots with no visible character. Preserve prop geometry and
light states explicitly where those are at risk.

Inspect motion and extracted frames for face drift, extra limbs, invented light/objects,
unintended camera moves and continuity errors. Keep useful takes; correct only failed
rows within the approved retry budget. If a shot keeps failing, revise or remove it and
update the table rather than repeatedly spending on the same broken action. Small Room
removed C14 and extended M12 while preserving the song timeline. Save kept and rejected
takes separately, along with model, prompt, start/end refs and requested/measured durations.

## 10. Assemble, inspect, render and deliver

Use **HyperFrames 0.7.5**, the version used by Small Room. If a tested local video harness
is available, reuse its structure and fonts; Small Room used the LETAL XLUG harness. Clear
its old media, captions, copy and timing. Otherwise scaffold the same pinned version; no
private reference project is required to run this skill.

Place the selected clips at the approved song windows, mute clip audio, and add captions
from the timestamped transcript. Use unique media IDs and explicit start/duration values.
Flag transcription-versus-lyric differences for the user; Small Room's written-word caption
override was explicit, not permission to silently alter captions in future films.

Run lint, validate and inspect, then snapshot important moments and caption transitions:

```bash
npx hyperframes@0.7.5 lint .
npx hyperframes@0.7.5 validate .
npx hyperframes@0.7.5 inspect .
npx hyperframes@0.7.5 snapshot --at <review-times> .
```

Review those images before rendering. Render the film, mux the approved master with FFmpeg
using **measured linear gain**, and measure the finished audio again. Small Room used
−1 dB; calculate this film's gain from its own measured levels. Keep the master unchanged;
do not apply `loudnorm`. If an end card is approved, append its duration explicitly and
pad only the card's audio tail with silence.

Read frames back from the finished MP4 at cuts, captions and previously troublesome shots;
check the actual movement as well as frame appearance. Confirm full song coverage,
continuous video, caption timing and the ending. A render completing is not a visual pass.
Record what was inspected and any unresolved defects. Return the playable film, measured
duration, source artifacts and actual cost when reported; label estimates as estimates.
Obtain the user's final viewing approval.

Small Room then used `recoup-internal-social-ship-posts`. Hand off to that linked skill only
for authorized Recoup staff publishing, honoring its scope. Video approval alone does not
authorize posts. Otherwise finish at the approved asset.
