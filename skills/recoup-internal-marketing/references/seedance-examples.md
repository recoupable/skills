# Seedance 2.5 — example prompt library

Every example here is **verbatim**, with the source next to it so we can go back to the original when we
wonder where a technique came from. Companion to `seedance.md`, which holds the decision gate, the
constraints, costs and our run log.

**How to use this:** find the row in the index whose *problem* matches yours, read that prompt in
full, and steal its structure rather than its subject. The examples are far more instructive than
the prose guidance — the official doctrine says "use timestamps" but only the bodega prompt shows
what a timestamp block that carries physical state actually looks like. Rows that link out to a source
page are examples we no longer reproduce here; read them at the source.

## Sources

| Key | Source | Retrieved |
|---|---|---|
| **[SEED]** | [ByteDance Seed — "One-take Creation, Flexible Referencing: Introducing Seedance 2.5"](https://seed.bytedance.com/seedance2_5) (published 2026-07-31) | 2026-08-13 |
| **[ARK]** | [BytePlus ModelArk — Dreamina Seedance 2.5 prompt guide](https://docs.byteplus.com/en/docs/ModelArk/2607689) (last updated 2026-08-13) | 2026-08-13 |
| **[FAL]** | [fal — Seedance 2.5 Prompting Guide + Real Examples](https://fal.ai/learn/devs/seedance-2-5-prompting-guide), by Ilker (2026-08-07) | 2026-08-13 |
| **[OURS]** | Our own runs, logged in `seedance.md` | — |

Related: the ByteDance official prompt optimizer skill, `sd25-pe` —
`npx --yes skills@latest add "https://arkdocs-en.tos-ap-southeast-1.volces.com/skills/" --skill sd25-pe --yes`

## Index — pick by the problem you have

| Problem | Example | Source |
|---|---|---|
| A long shot turns into waiting or repetition | [Bodega, 30s](#bodega-30s-single-take) | FAL |
| A reaction lands before its cause | [Diner spill, 15s](#diner-spill-cause-before-reaction) | FAL |
| A subject changes when it passes behind something | [Chicago platform, 11s](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) | FAL |
| The camera "follows" but composition drifts | [Basketball, 14s](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) | FAL |
| Two references fight over the same job | [Espresso](#espresso-one-job-per-reference) · [Car](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) | FAL |
| A physical action skips its middle | [Skateboard, 12s](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) | FAL |
| Dialogue piles on top of the action | [UGC travel cup, 12s **9:16**](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) | FAL |
| Liquid or cloth never settles | [Pancakes, 15s](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) | FAL |
| Continuing a shot in a second generation | [Pancake continuation](https://fal.ai/learn/devs/seedance-2-5-prompting-guide) | FAL |
| A plain structured t2v with timestamps | [Panda cub](https://docs.byteplus.com/en/docs/ModelArk/2607689) | ARK |
| A whole story in one 30s take | [Singer backstage](https://seed.bytedance.com/seedance2_5) | SEED |
| Many characters, many references | [Concert orchestra, 18 images](https://seed.bytedance.com/seedance2_5) | SEED |
| Locking camera and blocking before you light it | [Clay render girl](https://docs.byteplus.com/en/docs/ModelArk/2607689) · [Car assembly](https://seed.bytedance.com/seedance2_5) | ARK · SEED |
| A storyboard the model should follow loosely | [Robot and grandmother, 9 shots](https://docs.byteplus.com/en/docs/ModelArk/2607689) | ARK |
| Keyframes the model must hit exactly | [Wuxia pixel art](https://docs.byteplus.com/en/docs/ModelArk/2607689) · [Spirit fish](https://docs.byteplus.com/en/docs/ModelArk/2607689) | ARK |
| Changing something inside an existing video | [Aging woman](https://docs.byteplus.com/en/docs/ModelArk/2607689) · [Duel](https://docs.byteplus.com/en/docs/ModelArk/2607689) | ARK |
| Changing only the camera, keeping the action | [Breakfast camera plan](https://seed.bytedance.com/seedance2_5) | SEED |
| Replacing a green-screen background | [Football green screen](https://seed.bytedance.com/seedance2_5) | SEED |
| Changing dialogue language and lip-sync | [Audio translation](https://docs.byteplus.com/en/docs/ModelArk/2607689) | ARK |
| Extending a clip seamlessly | [Bee pollination](https://docs.byteplus.com/en/docs/ModelArk/2607689) · [Subway boy](https://seed.bytedance.com/seedance2_5) | ARK · SEED |
| Stitching two clips with an invented middle | [Mahjong to buildings](https://docs.byteplus.com/en/docs/ModelArk/2607689) | ARK |
| Turning a pile of images into a video | [Puppy coffee shop](https://docs.byteplus.com/en/docs/ModelArk/2607689) | ARK |
| A face-free plate, a proof take, then a shipped 30s film | [THE OPERATOR ep1](#ours--the-operator-ep1-the-first-film-we-shipped-on-this-model) | OURS |

---

## The template FAL distilled

Not every section is needed every time — keep the ones that solve a real problem in the shot.

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

ARK's own framing of the same idea: **one-sentence summary** (subject + location + event +
genre/style + camera movement), then a **detailed plot description** by timestamp or shot number,
then **additional notes** for what stays constant throughout.

---

## FAL — the three worked examples our own prompts borrow from

### Bodega, 30s single take
*Teaches: a long shot needs a timeline, and each block must pick up the physical state the last one left.*

> 30-second continuous single take inside a small New York City bodega on a rainy morning, all action at natural real-time speed. The same bike messenger wears a yellow rain jacket and carries one red bicycle helmet in the left hand throughout. 0-5 seconds: the door bell rings as the messenger enters, closes the glass door with the right hand, and shakes rain from the shoulders without dropping the helmet. 5-10 seconds: the camera follows from behind at chest height as the messenger walks to the drink cooler, opens the cooler with the right hand, removes one clear bottle of seltzer, and closes the door. 10-16 seconds: the messenger turns toward the counter and walks around one stationary customer without changing hands; red helmet remains in the left hand, bottle remains in the right. 16-22 seconds: the messenger sets only the bottle on the counter, taps a black phone once on the card reader, waits for one confirmation beep, then picks up the same bottle with the right hand. 22-27 seconds: the clerk gives a small nod; the messenger turns back toward the entrance while the camera backs up and keeps a medium full-body frame. 27-30 seconds: the messenger opens the door with the right forearm, exits into the rain, and the door closes behind. The camera stops inside the store. Keep the same messenger, jacket, helmet, bottle, phone, clerk, counter, cooler, and store layout from first frame to last. No cuts, no slow motion, no repeated entrance, no duplicated bottle or helmet, no object teleportation. Audio: rain outside, door bell, cooler hum, footsteps, bottle on counter, one card-reader beep, quiet store room tone, no music.

**Note the hand discipline.** The helmet is in the left hand for the entire film and the bottle in
the right from the moment it leaves the cooler. That single invariant is what stops objects
teleporting between hands.

### Diner spill, cause before reaction
*Teaches: write contact → resulting movement → sound → reaction as separate beats.*

> 15-second continuous single take inside a busy Brooklyn neighborhood diner in the morning, natural real-time speed. Eye-level medium-wide camera at the end of the counter. 0-4 seconds: a server places a full ceramic coffee cup beside an open sketchbook and walks away. 4-8 seconds: a busboy passes behind the seated customer; the edge of his tray lightly catches the cup handle. The cup tips only after contact, strikes the counter, and coffee begins spreading toward the sketchbook. 8-11 seconds: the customer hears the impact, looks down, then lifts the sketchbook just before the coffee reaches it. Nearby diners turn toward the sound at slightly different delays. 11-15 seconds: the server returns with a towel and stops the spill. The camera begins a slow 30-centimeter push-in only after the cup tips. Keep the same cup, sketchbook, server, customer, counter layout, and clothing throughout. Coffee follows the counter surface and never moves uphill. No cuts, no slow motion, no repeated action, no duplicated props, no music. Audio: ordinary diner room tone, dishes, the ceramic impact, liquid spill, chair movement.

**"at slightly different delays"** is the phrase that stops a crowd reacting in unison.

### Espresso, one job per reference
*Teaches: assign each reference a narrow job AND state what must not transfer from it.*

> 14-second continuous product demonstration in the Los Angeles kitchen from @Image2. @Image1 controls only the exact portable espresso maker: preserve its short cylindrical proportions, matte cobalt-blue shell, black rubber grip ring, circular copper button, and clear lower chamber. Do not copy @Image1's studio background. @Image2 controls only the kitchen layout, oak countertop, white cup, beige towel, plants, window light, and warm daylight. Do not add the studio surface from @Image1. Start on a wide frame matching @Image2 with the product standing to the left of the white cup. 0-4 seconds: the camera makes a slow, level push toward the product while it remains still. 4-7 seconds: one natural right hand enters from frame right and presses the copper button once. 7-11 seconds: dark espresso begins flowing into the clear lower chamber; the liquid level rises naturally while the product body stays rigid and unchanged. 11-14 seconds: the hand withdraws and the camera shifts slightly right to place the product and cup side by side in the final frame. Keep the cup, towel, plants, countertop, product geometry, button position, and lighting consistent. No logo, no text, no extra machine, no extra hands, no cuts, no slow motion. Audio: quiet apartment room tone, soft button click, gentle brewing sound, distant Los Angeles traffic, no music.

**The reusable pattern FAL keeps returning to:**

```
@Image1 controls only [identity, product design, clothing, or another invariant].
Do not copy [pose, background, lighting, camera angle, or text] from @Image1.
```

---

## OURS — THE OPERATOR ep1, the first film we shipped on this model

**Published 2026-08-13** to [YouTube](https://youtube.com/shorts/vfI1aYBz6Vs) ·
[X @recoupai](https://x.com/recoupai/status/2088057350821216632) ·
[LinkedIn](https://www.linkedin.com/feed/update/urn:li:share:7493824522991669248) ·
[Instagram](https://www.instagram.com/reel/DcACIbukU5A/).
30.0s · 1080x1920 · 24fps · -17.9 LUFS. Seed `39363830`, 292s to generate.

**The shape that worked, in three artifacts.** Read them in order, because each depends on the one
before it: an art-directed **scene plate** (a face-free image doing all the cinematic work), a
**10s proof of concept** that de-risked the expensive run, then the **30s single generation**.

---

### 1. The scene plate — Nano Banana 2, face-free, the highest-leverage asset

This image is the style bible. Location, lighting, palette, lens character and set dressing all live
in it, and because it contains no face, none of that control touches the moderation filter that
rejects character references. **Two lines of art direction inside an image outperformed a paragraph
of styling language in the prompt.**

Model `fal-ai/nano-banana-2`, `aspect_ratio: "9:16"`, `resolution: "2K"`, `num_images: 4` — generate
several and pick the cleanest corridor recession.

> A photorealistic empty interior photograph.
>
> THE PLACE: the central corridor of a small, slightly cramped independent RECORD LABEL office — a converted older building, not a corporate tower. Scuffed painted brick or plaster on one side, half-height mismatched desk partitions on the other. Framed record sleeves and a few gold and platinum discs hanging slightly crooked on the wall. Stacks of vinyl and cardboard mailers on the floor against the wall. A guitar case leaning. Mismatched second-hand desks, a cheap office chair with a coat over the back, a small stack of flight cases. Worn wooden floor with a thin runner rug. Windows down the left side with venetian blinds half open, flat afternoon daylight coming through. A suspended ceiling is NOT present — exposed painted ceiling with surface conduit and a few hanging pendant lights.
>
> PHOTOGRAPHIC STYLE (this image defines the look of the finished film): shot on a 35mm cinema prime at eye level, mild natural wide-angle perspective down the length of the corridor, deep focus, subtle film grain, restrained naturalistic colour grade, slightly warm daylight falling off into cooler shadow at the far end. Documentary realism. Not glossy, not an advertisement, not a prestige-television set.
>
> STRICT: the corridor is COMPLETELY EMPTY — absolutely no people, no figures, no silhouettes, no reflections of people anywhere in frame. Vertical 9:16 framing, camera at chest height looking straight down the corridor so the corridor recedes to a vanishing point. Photorealistic. No text anywhere: no readable signage, no posters with legible words, no whiteboard writing, no name plates, no album titles. No brand marks or logos of any kind. No watermark, no caption.

---

### 2. The 10s proof of concept — test what is unproven, not the opening

**Do not test the first 10 seconds of the film.** Test the 10 seconds that stress what is unknown.
Walking down a corridor was already proven; what was not was whether a text-only character
description held without a face reference, whether the scene plate transferred, and above all
**whether a collision would read as an accident rather than temper** — the exact beat that had
already failed once.

**74% of this prompt is verbatim from the 30s below**, deliberately. Reword the test and it stops
validating the thing you are about to buy.

`bytedance/seedance-2.5/reference-to-video`, one image reference (the scene plate),
`duration: "10"`, `aspect_ratio: "9:16"`, `resolution: "720p"`, `generate_audio: true`.
208s, about $4.62.

> 10-second continuous single take, vertical 9:16, natural real-time speed, no cuts. Plain documentary realism, ordinary available light, handheld-steady camera. Not glossy, not an advertisement, not a scene from any film or television programme.
>
> @Image1 controls the OFFICE ENVIRONMENT ONLY: the corridor layout, scuffed painted walls, framed record sleeves and gold discs, stacked vinyl and cardboard mailers, mismatched desks, worn wooden floor and runner rug, windows with venetian blinds, pendant lights on exposed conduit, and the warm afternoon daylight. Do not take any person from @Image1.
>
> THE MAN, the same person in every frame: an ordinary man of about 42 with a ROUND soft face and a WEAK rounded jawline, noticeably THINNING dark-brown hair receding at both temples and cut short with no styling, plain WIRE-FRAME glasses with thin metal rims, a SHORT UNEVEN slightly unkempt dark beard, small deep-set brown eyes with tired shadows beneath them, a slightly heavy soft build with a small belly and rounded shoulders, pale ordinary skin with visible pores. He wears a plain grey crew-neck t-shirt and dark trousers. He is plain and unglamorous, an ordinary office worker, not a handsome leading man and not a model. He carries a phone in his LEFT hand from the first frame until he drops it, and never puts it in a pocket.
>
> 0-3 seconds: he walks fast toward camera down the middle of the corridor from @Image1, glancing down at the phone in his left hand. He then turns his head back over his right shoulder to look at something behind him. The camera retreats ahead of him at chest height, matching his speed and holding him in the centre third of frame.
>
> 3-6 seconds: still facing away from where he is going, he walks shoulder-first into a woman stepping out of a doorway with an armful of loose paper. The impact happens first. Only after the contact does the paper fly up and scatter, and both people stumble sideways. The phone leaves his left hand and lands face-up on the floor. Neither of them falls completely.
>
> 6-10 seconds: he stops. He crouches down among the scattered paper, one hand held out toward the woman in apology, and stays there. He picks up his own phone from the floor with his left hand, looks at it for a moment, then raises it to his ear and says quietly, "Hey. I need help." He stays crouched on the floor as the shot ends.
>
> Camera: a single continuous backward tracking shot at chest height, retreating ahead of him, never overtaking him and never turning around; it lowers with him as he crouches.
>
> Continuity: the same man with the same face, glasses, beard, thinning hair, grey t-shirt and dark trousers from the first frame to the last. The same phone throughout. Exactly one other person appears, the woman he collides with, and nobody else approaches him. The scattered paper stays on the floor and never increases in quantity.
>
> Audio: office room tone, keyboards, a muffled phone ringing somewhere, his footsteps on the runner rug, the impact of the collision and paper landing. One spoken line only, male American-accented, "Hey. I need help." Nobody else speaks. No music.
>
> Constraints: no cuts, no slow motion, no repeated action, no duplicated people, no duplicate copies of the main man, no crowd, no one entering frame twice, nobody falling to the ground completely, no anger and no deliberate pushing or throwing of the paper. No subtitles and no captions of any kind. No text anywhere in frame: no readable screens, no phone screen content, no signage, no legible posters or album titles, no whiteboard writing, no name plates. No brand marks or logos on any laptop, phone, wall or clothing; all laptops closed or turned away from camera.

---

### 3. The 30s film, as shipped

Same endpoint and settings, `duration: "30"`. 292s, about $14.19.

Three things here are why it held together. **The cut is declared explicitly and every other cut
forbidden**, matched on a prop the film already owns. **Six beats in thirty seconds**, each picking
up the physical state the last one left. And **the reference is scoped to part of the film** —
"controls the OFFICE ENVIRONMENT ONLY for the first 21 seconds ... do not use @Image1 for the final
beach shot" — which works cleanly.

> 30-second continuous vertical 9:16 film at natural real-time speed. Plain documentary realism, ordinary available light, handheld-steady camera. Not glossy, not an advertisement, not a scene from any film or television programme.
>
> @Image1 controls the OFFICE ENVIRONMENT ONLY for the first 21 seconds: the corridor layout, scuffed painted walls, framed record sleeves and gold discs, stacked vinyl and cardboard mailers, mismatched desks, worn wooden floor and runner rug, windows with venetian blinds, pendant lights on exposed conduit, and the warm afternoon daylight. Do not take any person from @Image1. Do not use @Image1 for the final beach shot.
>
> THE MAN, the same person in every frame: an ordinary man of about 42 with a ROUND soft face and a WEAK rounded jawline, noticeably THINNING dark-brown hair receding at both temples and cut short with no styling, plain WIRE-FRAME glasses with thin metal rims, a SHORT UNEVEN slightly unkempt dark beard, small deep-set brown eyes with tired shadows beneath them, a slightly heavy soft build with a small belly and rounded shoulders, pale ordinary skin with visible pores. He wears a plain grey crew-neck t-shirt and dark trousers. He is plain and unglamorous, an ordinary office worker, not a handsome leading man and not a model. He carries a phone in his LEFT hand from the first frame until he drops it, and never puts it in a pocket.
>
> 0-6 seconds: he walks fast toward camera down the middle of the corridor from @Image1, glancing down at the phone in his left hand then up ahead. The camera retreats ahead of him at chest height, matching his speed and holding him in the centre third of frame. A woman working at a desk on the left sees him coming, stands up, takes half a step into the corridor and begins to speak, lifting a paper folder toward him. He does not slow and does not turn his head. He passes her; behind him she lowers the folder and sits back down.
>
> 6-11 seconds: a man on the right steps out from between two desks holding a closed laptop and says, "Hey, you got two minutes?" Without stopping and without looking at him the walking man answers, "Not now," and keeps going. The camera keeps retreating at the same speed.
>
> 11-16 seconds: still walking, he turns his head back over his right shoulder to look at the man he has just passed. Facing away from where he is going, he walks shoulder-first into a woman stepping out of a doorway with an armful of loose paper. The impact happens first. Only after the contact does the paper fly up and scatter, and both people stumble sideways. The phone leaves his left hand and lands face-up on the floor. Neither of them falls completely.
>
> 16-21 seconds: he stops. He crouches down among the scattered paper, one hand out toward the woman in apology, and stays there. He picks up his own phone from the floor with his left hand, looks at it for a moment, then raises it to his ear and says quietly, "Hey. I need help." He stays crouched on the floor.
>
> 21-22 seconds: ONE single cut, matched on the phone. Cut from the phone held at his ear on the office floor to the same phone lying face-down on sand.
>
> 22-30 seconds: a beach in late afternoon. The same man sits on the sand in the same grey t-shirt beside a young child, both looking out at the water, the sea breeze moving his hair. His phone lies FACE-DOWN on the sand beside his right hand. At about 25 seconds the phone buzzes once against the sand. He looks down at it, picks it up, turns it face-down again WITHOUT reading it, and sets it back on the sand. He turns back to the child and says something we cannot hear over the surf. Hold on the two of them from behind as the shot ends.
>
> Camera: for the first 21 seconds a single continuous backward tracking shot at chest height, retreating ahead of him, never overtaking him and never turning around; it lowers with him as he crouches. After the cut, a slow wide handheld shot on the beach that settles and holds.
>
> Continuity: the same man with the same face, glasses, beard, thinning hair, grey t-shirt and dark trousers from the first frame to the last, in the office and on the beach. The same phone throughout. Exactly four other people appear in the office, one at a time in the order described, and nobody else approaches him. The scattered paper stays on the floor and never increases in quantity. Only ONE child on the beach.
>
> Audio: office room tone, keyboards, a muffled phone ringing somewhere, his footsteps on the runner rug, the impact of the collision and paper landing; then surf, wind and distant gulls on the beach. Three spoken lines only, all male American-accented except the first speaker: "Hey, you got two minutes?" then "Not now," then "Hey. I need help." Nobody else speaks and no line is repeated. No music anywhere.
>
> Constraints: exactly ONE cut, at 21 seconds, and no other cut anywhere. No slow motion, no repeated action, no duplicated people, no duplicate copies of the main man, no crowd, no one entering frame twice, nobody falling to the ground completely, no anger and no deliberate pushing or throwing of the paper. No subtitles and no captions of any kind. No text anywhere in frame: no readable screens, no phone screen content, no signage, no legible posters or album titles, no whiteboard writing, no name plates. No brand marks or logos on any laptop, phone, wall or clothing; all laptops closed or turned away from camera.
