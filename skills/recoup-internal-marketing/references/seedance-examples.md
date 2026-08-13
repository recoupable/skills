# Seedance 2.5 — example prompt library

Every worked example we have collected, **verbatim**, with the source next to each so we can go back
to the original when we wonder where a technique came from. Companion to `seedance.md`, which holds
the constraints, costs and our run log.

**How to use this:** find the row in the index whose *problem* matches yours, read that prompt in
full, and steal its structure rather than its subject. The examples are far more instructive than
the prose guidance — the official doctrine says "use timestamps" but only the bodega prompt shows
what a timestamp block that carries physical state actually looks like.

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
| A subject changes when it passes behind something | [Chicago platform, 11s](#chicago-platform-occlusion) | FAL |
| The camera "follows" but composition drifts | [Basketball, 14s](#basketball-camera-position-in-frame) | FAL |
| Two references fight over the same job | [Espresso](#espresso-one-job-per-reference) · [Car](#car-image-vs-video-reference) | FAL |
| A physical action skips its middle | [Skateboard, 12s](#skateboard-break-motion-into-contacts) | FAL |
| Dialogue piles on top of the action | [UGC travel cup, 12s **9:16**](#ugc-travel-cup-dialogue-as-performance) | FAL |
| Liquid or cloth never settles | [Pancakes, 15s](#pancakes-where-fluid-motion-ends) | FAL |
| Continuing a shot in a second generation | [Pancake continuation](#pancake-continuation-final-frame-as-first-frame) | FAL |
| A plain structured t2v with timestamps | [Panda cub](#panda-cub-the-official-structured-template) | ARK |
| A whole story in one 30s take | [Singer backstage](#singer-backstage-one-take-story) | SEED |
| Many characters, many references | [Concert orchestra, 18 images](#concert-orchestra-18-references) | SEED |
| Locking camera and blocking before you light it | [Clay render girl](#clay-render-girl-and-the-airplane-30s) · [Car assembly](#car-assembly-clay-render) | ARK · SEED |
| A storyboard the model should follow loosely | [Robot and grandmother, 9 shots](#robot-and-grandmother-multi-panel-storyboard) | ARK |
| Keyframes the model must hit exactly | [Wuxia pixel art](#wuxia-pixel-art-keyframes) · [Spirit fish](#spirit-fish-keyframes) | ARK |
| Changing something inside an existing video | [Aging woman](#aging-woman-instruction-editing) · [Duel](#duel-editing-with-reference-images) | ARK |
| Changing only the camera, keeping the action | [Breakfast camera plan](#breakfast-camera-only-edit) | SEED |
| Replacing a green-screen background | [Football green screen](#football-green-screen-edit) | SEED |
| Changing dialogue language and lip-sync | [Audio translation](#audio-translation-edit) | ARK |
| Extending a clip seamlessly | [Bee pollination](#bee-pollination-extension) · [Subway boy](#subway-boy-extension) | ARK · SEED |
| Stitching two clips with an invented middle | [Mahjong to buildings](#mahjong-to-buildings-seamless-transition) | ARK |
| Turning a pile of images into a video | [Puppy coffee shop](#puppy-coffee-shop-one-click-creation) | ARK |
| Our own, and what tripped moderation | [Back office v1 / v2](#our-runs-back-office) | OURS |

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

## FAL — the ten worked examples

Each of these shipped with a generated video on the source page.

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

### Chicago platform, occlusion
*Teaches: say how long a subject is hidden and repeat what must survive re-emergence.*

> 11-second continuous locked wide shot on a Chicago elevated train platform in overcast afternoon light, natural real-time speed. A woman in a bright green wool coat pulls one small red rolling suitcase from frame left toward frame right. 0–3.2 seconds: she walks steadily beside the yellow platform line, right hand holding the extended suitcase handle, suitcase rolling one step behind her. 3.2–5.1 seconds: she passes completely behind one thick concrete support column; both woman and suitcase are fully hidden for just under two seconds. 5.1–9.5 seconds: the same woman emerges from the opposite side of the column with the same face, hair, green coat, black boots, red suitcase, extended handle, walking speed, and direction. 9.5–10.8 seconds: she continues toward the right edge and the shot ends mid-stride as she is about to exit frame. The camera never moves. The column remains fixed. No person or suitcase appears on both sides of the column at once. No identity change, clothing change, color change, duplication, jump cut, morph, slow motion, or disappearing luggage. Audio: light wind, distant city traffic, suitcase wheels on concrete, a far train announcement, no music.

Note this is the one example using **sub-second timestamps** (3.2, 5.1, 9.5). ARK's guidance says
integer seconds; FAL used decimals here and it worked.

### Basketball, camera position in frame
*Teaches: put the subject in a named part of the frame; tie each camera move to a visible event.*

> 14-second continuous sideline tracking shot in a public high school basketball gym in Indiana, natural real-time speed. One player in a plain red jersey owns the ball at the start; one teammate in a plain white jersey waits near the right side of the lane. 0-5 seconds: the red-jersey player dribbles with the right hand from frame left toward the free-throw line. The camera moves parallel and keeps the red player in the left third of frame, with the hoop visible on the right. 5-8 seconds: the red player plants the left foot and makes one chest pass across frame. The camera does not pan until the ball has fully left both hands. 8-11 seconds: the camera pans right with the airborne ball; the white-jersey player catches it with both hands near the right block and takes one step toward the hoop. 11-14 seconds: the white player makes a right-handed layup, lands on both feet, and the ball drops through the net. Keep the basket on the same side of frame and never cross the court axis. Preserve both players, jersey colors, ball ownership, direction, court markings, and light. No cuts, no slow motion, no extra ball, no duplicated players, no impossible handoff. Audio: sneaker squeaks, two dribbles, pass impact, backboard and net, small gym crowd, no music.

### Espresso, one job per reference
*Teaches: assign each reference a narrow job AND state what must not transfer from it.*

> 14-second continuous product demonstration in the Los Angeles kitchen from @Image2. @Image1 controls only the exact portable espresso maker: preserve its short cylindrical proportions, matte cobalt-blue shell, black rubber grip ring, circular copper button, and clear lower chamber. Do not copy @Image1's studio background. @Image2 controls only the kitchen layout, oak countertop, white cup, beige towel, plants, window light, and warm daylight. Do not add the studio surface from @Image1. Start on a wide frame matching @Image2 with the product standing to the left of the white cup. 0-4 seconds: the camera makes a slow, level push toward the product while it remains still. 4-7 seconds: one natural right hand enters from frame right and presses the copper button once. 7-11 seconds: dark espresso begins flowing into the clear lower chamber; the liquid level rises naturally while the product body stays rigid and unchanged. 11-14 seconds: the hand withdraws and the camera shifts slightly right to place the product and cup side by side in the final frame. Keep the cup, towel, plants, countertop, product geometry, button position, and lighting consistent. No logo, no text, no extra machine, no extra hands, no cuts, no slow motion. Audio: quiet apartment room tone, soft button click, gentle brewing sound, distant Los Angeles traffic, no music.

**The reusable pattern FAL keeps returning to:**

```
@Image1 controls only [identity, product design, clothing, or another invariant].
Do not copy [pose, background, lighting, camera angle, or text] from @Image1.
```

### Skateboard, break motion into contacts
*Teaches: approach, contact, transfer of force, recovery — and how it settles.*

> 12-second continuous low side-tracking shot at the Venice Beach skatepark in late afternoon, natural real-time speed. A skater wearing a faded red T-shirt rides a black skateboard toward one yellow traffic cone. 0-3 seconds: he pushes once with his right foot, places it back on the board, and centers his weight. 3-6 seconds: he bends both knees while approaching the cone; the camera moves parallel and keeps his full body centered. 6-8 seconds: the rear foot snaps the tail against the concrete, the board rises, the front foot slides forward, and both rider and board clear the cone together. 8-10 seconds: the front wheels contact first, then the rear wheels; his knees compress from the landing and his arms correct his balance. 10-12 seconds: he straightens and rides away without another trick. Preserve the same person, shirt, board, cone, direction of travel, and sunlight. Believable wheel rotation, board contact, gravity, and body weight. No cuts, no slow motion, no floating board, no duplicated limbs, no repeated jump. Audio: skateboard wheels on concrete, tail pop, landing impact, distant beach ambience, no music.

### Car, image vs video reference
*Teaches: never let an image and a video reference do the same job.*

> 16-second continuous automotive tracking shot. @Image1 controls only the exact fictional silver sports car: preserve its body shape, silver paint, front light signature, black roof, wheel-spoke design, proportions, vents, and ride height. Do not copy @Image1's sunny San Francisco waterfront or parked composition. @Video1 controls only the low side-tracking camera height, parallel motion, subject framing, and real-time movement rhythm. Do not copy the skater, skateboard, cone, clothing, beach, or concrete setting from @Video1. Place the car on a rain-wet downtown Seattle avenue at blue hour. 0-4 seconds: the car waits at a red traffic light while the camera holds a low front-side angle. 4-11 seconds: the light turns green and the car accelerates smoothly; the camera tracks parallel at door height while keeping the full car centered and sharp. Wheels rotate at the correct speed, suspension settles under acceleration, reflections move across the exact silver body, and water sprays backward from the tires. 11-16 seconds: the car eases into the right lane and maintains speed while the camera falls half a car length behind into a rear three-quarter view. Preserve one car and the same design in every frame. No cuts, no redesign, no extra spoiler, no logo, no copied human subject, no skateboard, no cone, no slow motion. Audio: wet tire noise, restrained electric motor whine, distant traffic, rain on road, no music.

Note the car is described as **"fictional"** — the same defensive move that got our own run past
the output moderation filter.

### UGC travel cup, dialogue as performance
*Teaches: block dialogue with start and end times, and say when the mouth is closed. Also our only **9:16 vertical** example.*

> 12-second vertical 9:16 handheld phone video in a sunlit Austin apartment kitchen, natural real-time performance, one continuous take. A woman in her late twenties stands at the counter holding a small plain insulated travel cup with no logo. 0-3 seconds: she looks into the phone camera, briefly raises the cup, and says, "I bought this for the commute, but I use it at home every day." 3-6 seconds: she stops speaking, looks down, turns the lid one quarter turn with both hands, and waits until it clicks. 6-9 seconds: she tilts the sealed cup sideways over the sink for two seconds; no liquid leaks. 9-12 seconds: she returns the cup upright, looks back at the camera, and says, "That is the whole reason." Her mouth moves only during her own lines. Keep the same face, hair, shirt, cup, lid, kitchen, hand count, and daylight throughout. Subtle natural phone-camera shake, ordinary skin texture, no beauty filter, no cuts, no zoom, no slow motion, no extra products, no text, no logo, no music. Audio: clean lip-synced speech, quiet apartment room tone, soft lid click, distant traffic.

### Pancakes, where fluid motion ends
*Teaches: name the direction of force and the state left behind after motion stops.*

> 15-second continuous 21:9 macro food shot at a roadside diner breakfast counter, natural real-time speed. A stack of three plain buttermilk pancakes sits on one white ceramic plate with a square of butter centered on top and six blueberries around the base. 0-4 seconds: a small glass syrup pitcher enters from frame upper right and tilts above the butter; the camera begins a slow ten-degree clockwise arc around the plate. 4-9 seconds: one continuous amber stream lands on the butter, divides around it, and runs down the pancake edges under gravity. Syrup pools on the plate and does not flow uphill. 9-12 seconds: the pitcher tilts upright; the stream narrows, stretches, then breaks cleanly before the pitcher leaves frame. 12-15 seconds: the butter softens slightly and slides only a few millimeters before stopping; the syrup continues settling into one pool. Preserve the same three pancakes, butter, six blueberries, white plate, counter, and warm window light. No cuts, no slow motion, no extra fruit, no changing food count, no floating liquid, no text, no logo. Audio: quiet diner room tone, soft glass movement, syrup landing on food, distant dishes, no music.

### Pancake continuation, final frame as first frame
*Teaches: extract the last frame, pass it as the image reference, and describe only what already finished plus the first new action.*

> Use @Image1 as the exact first frame and continue forward from that moment. Preserve the same stack of three buttermilk pancakes, softened square of butter, six blueberries, white ceramic plate, amber syrup pool, counter, warm diner light, 21:9 framing, macro lens, and camera position. Do not replay or recreate the syrup pour that happened before this frame. 0-4 seconds: hold the same composition while the syrup pool makes only small natural settling movements. 4-8 seconds: one clean stainless-steel fork enters from frame right with no hand visible, presses into the front edge of the top pancake, and separates one bite-sized piece. 8-10 seconds: the fork lifts the same piece upward; one thin syrup strand stretches from the piece to the stack. 10-12 seconds: the syrup strand narrows and breaks, and the fork exits toward frame right with the piece. The remaining stack stays on the plate with one small missing bite at the front. No new pour, no pitcher, no hand, no extra fork, no extra pancakes, no changing blueberry count, no cut, no slow motion, no text, no music. Audio is quiet diner room tone with a soft fork contact and sticky syrup separation.

**This is the multi-shot strategy for a piece longer than one generation** — and it is cheaper and
more controllable than asking for 30 seconds in one pass.

---

## ARK — the official examples

### Panda cub, the official structured template
*The canonical shape: one-sentence summary, then constants, then timestamped blocks, then overall notes.*

> Realistic nature documentary style, natural lighting and shadows. On a warm afternoon, on a grassy slope in the forest, a chubby panda cub rolls down the hill.
>
> The panda has fluffy, realistic black-and-white fur, a small round body, and clumsy, adorable movements. The scene is a green forest slope. The ground is covered with grass, moss, clover, soil, small stones, dry branches, and a few small yellow flowers. Tall tree trunks and dense woods are softly blurred in the background. The camera is a low-angle medium-wide shot with a slight handheld feel. The framing remains mostly stable, keeping the panda in frame at all times.
>
> 0s-3s: A panda cub lies on a green grassy slope, its body round and chubby. It begins to slowly roll sideways down the slope with clumsy movements, gently bending the grass beneath its body. A light breeze passes through, and sunlight filters through the trees from the upper left, creating dappled light and shadow.
>
> 3s-8s: The panda rolls toward the lower right of the frame and gradually comes to a stop, shifting from lying on its side to lying on its belly. Its round face turns toward the camera, and its front paws press into the grass. The panda lies in the foreground grass, adjusts into a comfortable position, slightly raises and lowers its head, and makes a soft little humming sound.
>
> Low camera position, slight handheld feel, subtly following the panda as it moves toward the lower right. Natural depth of field: the foreground grass is slightly blurred, the panda remains clear, and the background forest is softly out of focus. Natural environmental audio only, including wind, rustling grass, and the soft plop of the panda rolling. The overall mood is warm, realistic, and natural.

### Clay render, girl and the airplane, 30s
*Teaches: a clay-render video locks camera, blocking and pacing; keyframe images control the look of each stage.*

> Use the 3D clay-model reference video <video1> as the only reference for the entire video's camera movement, shot rhythm, shot-size changes, subject motion trajectory, and camera blocking. Strictly preserve the shot order, camera position changes, movement patterns, and pacing of the 3D clay-model video. Do not change the shot structure, add new shots, or alter the subject's motion logic.
>
> Using the keyframe reference images for each stage, generate a 30-second high-quality 3D animated short film. The overall style should be dreamy, fairytale-like, warm, and full of childlike fantasy. The character's appearance should remain consistent with the keyframes for each stage. Do not change the character design. The character's facial expressions and emotions should change naturally with the scene.
>
> 0-3s (first-frame reference: <2pic>): The shot starts from an overhead wide view and slowly pushes in toward a little girl on the floor. The girl sits on the carpet in her room, playing with a toy airplane. She stands up, turns left, and forcefully swings her right hand to launch the airplane. The toy airplane flies in an arc from left to right into the foreground. The sound gradually transitions from the sound of throwing a paper airplane into the engine sound of a real animated airplane, accompanied by gentle, soothing, cheerful background music.
>
> 3-5s (reference: <3pic>): The airplane flies from left to right through hanging star decorations in the room. The girl rides the airplane into a fantasy sky. A flock of birds flies across the foreground, creating a natural transition. The camera continues side-following and rotating.
>
> 5-8s (reference: <4pic>): The camera continues side-following and orbiting around the little girl. Throughout this segment, the girl keeps piloting the small airplane through a sea of sunset clouds. Around her, a flock of strange birds and giant mythic birds fly alongside her. The white dragon from the reference image swims forward through the air, a winged horse spreads its wings and flies, and a flying whale calls out. Floating islands appear in the background.
>
> 8-10s (reference: <5pic>): The camera orbits to the back of the airplane. The airplane slowly dives toward the sea surface. The girl falls into the water, creating many bubbles in the frame. She swims toward the deep sea, now wearing a bubble-shaped oxygen helmet.
>
> 10-19s (references: <6pic>, <7pic>): The girl continues swimming deeper into the ocean. Suddenly, a manta ray swims into frame and carries the girl forward. The camera continues following the manta ray and the girl as they travel through a dazzling underwater world. The girl looks amazed by the beautiful underwater scenery. The camera keeps pushing forward, revealing a huge space-time rift ahead. The area around the rift looks like broken mirrors, while inside the rift is a brilliant cosmic galaxy. The girl feels a little frightened, but is eventually pulled into the space-time rift and arrives in a fantasy universe.
>
> 19-23s (reference: <8pic>): The girl bursts out of the space-time rift into the fantasy universe, and her outfit changes into the spacesuit shown in the keyframe. Wearing the spacesuit, she jumps from one planet to another. She reaches out, leaps forward, and catches a glowing star. The frame freezes.
>
> 23-24s (reference: <9pic>): In the foreground, the girl and the planets begin to flip forward, gradually transforming and disappearing. In the background, the overhead view of the bedroom from the opening scene (reference: <1pic>) slowly fades in.
>
> 24-28s (reference: <9pic>): The overhead camera continues pushing in. The girl lies asleep on the carpet, still holding the star-catching pose with her hand. A toy airplane and a space-themed picture book lie beside her. Her Asian father enters the frame and gently covers her with a blanket. The lighting slowly shifts from warm dusk light to cool moonlight at night.
>
> 28-30s (reference: <10pic>): The camera continues pushing in toward the picture book. The father enters the frame and gently closes the picture book on the floor with his right hand. The final frame freezes on the picture book.
>
> Overall requirements: All visuals should reference the corresponding keyframes. The 3D clay-model video should only be used as a reference for camera movement, camera motion, shot rhythm, camera blocking, and character animation. Do not reference its visual content. The long-take transitions should feel natural and smooth. Actions should remain continuous, and character proportions and movement should remain consistent. Generate a 30-second video in a 16:9 widescreen format.

### Raccoon cyberpunk, fine-grained clay render
*Teaches: with a complete 3D model, the prompt is only about "colouring" it.*

> Render Video 1. No BGM; generate only environmental sounds and action sounds.
>
> Rendering requirements: The background is a nighttime cyberpunk city in deep blue and purple tones, filled with dense skyscrapers. Huge holographic billboards and neon lights glow between the buildings. Several flying vehicles move through the sky, flashing faint lights and producing subtle mechanical sounds. The character is a small raccoon dressed in a black stealth suit, appearing mostly as a silhouette. Its footsteps are cautious and quiet. The character moves across the rooftop of one of the skyscrapers.

### Robot and grandmother, multi-panel storyboard
*Teaches: bind each reference explicitly, then a shot list. Also the clearest example of a **negative style block**.*

> Image 1: Nine-panel storyboard reference, used for the overall shot structure, shot sizes, and camera-movement rhythm.
> Image 2: Live-action reference of a rocket launch site on a dusk grassland, used as the benchmark for environmental composition, warm golden sunset light, cool twilight blue tones, and realistic color live-action texture.
> Image 3: Subject 1 (guardian robot) character appearance reference.
> Image 4: Subject 2 (elderly grandmother) character appearance reference.
>
> [Subject settings]
> Subject 1 (guardian robot): Refer to Image 3. A near-future weathered retro robot with an aged blue-green metal body, mottled rust, a domed head, two glowing red circular camera eyes, thin antennas, and slender articulated limbs. It is very tall, about twice the height of a human.
> Subject 2 (elderly grandmother): Refer to Image 4. A frail elderly woman with silver hair tied into a low bun, deep wrinkles, wearing a bright golden floor-length dress with gold-and-blue embroidered details on the chest. Her expression is full of reluctance and sorrow. Her height only reaches the robot's chest.
> Environment (dusk grassland launch site): Refer to Image 2. A near-future grassland at dusk, with the sky gradually shifting from warm gold to cool blue. On the distant horizon, a launch tower stands with a white rocket, steam rising around it. Knee-high wild grass sways in the wind across a vast, open landscape.
>
> [Overall style]
> Live-action color cinematic film, realistic photoreal texture, full-color visuals throughout. Color 35mm film look, fine realistic film grain, rich cinematic color grading, IMAX large-format feel. Handheld cinematography with breathing-like camera shake, shallow depth of field, wide aperture, continuous drifting foreground grass, sparks, and ash. Slight Dutch angle. Strong contrast between warm golden sunset light, cool twilight blue, and explosive warm orange. 16:9 horizontal frame. Near-future emotional disaster-film atmosphere: quiet, tragic, protective, and filled with reluctance.
>
> [Strictly exclude]
> Black-and-white, monochrome, grayscale, desaturated visuals; hand-drawn, sketch, line art, illustration, comics, animation; storyboard frames, rough sketches; tilt-shift miniature look, toy-like appearance, plastic CG, glossy overexposed CG.
>
> [Shot list] (9 shots, approximately 30 seconds)
> Shot 1 (0-3s): Extreme wide shot, ultra-low camera position close to the ground, looking upward, handheld camera slowly tilting downward. Refer to the grassland composition in Image 2. The dusk grassland feels vast and empty. Knee-high wild grass in the foreground sways out of focus, and warm golden lens flare sweeps across the frame.
> Shot 2 (3-6s): Medium front shot with a handheld camera. The robot supports the elderly woman.
> Shot 3 (6-10s): Facial close-up. The elderly woman looks reluctant to part. Dialogue (elderly woman): "Fly safe, my child. Come back to me."
> Shot 4 (10-14s): Extreme wide shot tilting upward. The rocket rises with a thick white smoke trail. Dialogue (elderly woman): "There he goes... there he goes."
> Shot 5 (14-18s): Extreme wide shot. The rocket explodes and breaks apart in midair. Dialogue (elderly woman): "No... no, no—"
> Shot 6 (18-22s): Extreme facial close-up. The elderly woman's pupils contract and tears fall. Dialogue (elderly woman): "...he was almost there."
> Shot 7 (22-25s): Close-up transitioning to a medium close-up. The elderly woman breaks down in tears. Dialogue (elderly woman): "Bring him back! Please—bring him back!"
> Shot 8 (25-28s): Ultra-low-angle, nearly vertical upward shot. The robot embraces the elderly woman, forming a protective dome around her. Dialogue (robot): "Don't look up. I've got you."
> Shot 9 (28-30s): Extreme wide rear shot. The two figures embrace tightly in silhouette. Dialogue (robot): "I'm still here. I'll stay... as long as you need."

**The `[Strictly exclude]` block is the closest thing to a negative prompt Seedance has**, and it is
worth copying wholesale when a look keeps drifting.

### Line-art storyboard, snow bedroom
*Teaches: the recommended storyboard style — simple line art, mapped assets, shot list.*

> Visual Style: Domestic realistic short drama, shot on Arri Alexa Mini LF, 35 mm cinema lens, cinematic realistic lighting, indoor night scene with snow-falling night view outside the window, film grain, authentic skin texture, natural lifelike performance, subtle micro-expressions, real adult facial bone structure and facial features, no excessive beautification or skin smoothing.
> Asset Bindings: Storyboard @Image1, bedroom @Image2, Li Tian @Image3, Li Qian @Image4, book *Happy Times* @Image5.
> Shot 1: [Wide shot, locked-off camera, eye-level, rule-of-thirds composition] Room on a snowy winter night. In front of floor-to-ceiling windows, a man stands sideways with both hands in his pockets, gazing out at falling snow. A young girl stands beside him, watching the man quietly. Calm and restrained atmosphere. Snowflakes keep drifting against the glass window.
> Shot 2: [Medium shot, over-the-shoulder shot] The girl's back serves as foreground. The man turns his head and looks gently toward the girl. The girl bows her head slightly in silence. Snow keeps falling outside the window.
> Shot 3: [Medium close-up, diagonal composition] The man holds the book *Happy Times* and extends it slowly. The young girl raises her hands to receive the book.
> Shot 4: [Close-up on the girl's face, central composition] The girl clutches the book tight against her chest. Her eyes turn red, teardrops roll slowly down her cheeks with a sorrowful look.
> Shot 5: [Close-up on the man's face, oblique composition] The man wears a soft faint smile, gazing quietly at the tearful girl with melancholy in his eyes.
> Shot 6: [Wide shot, locked-off camera] The girl turns and walks slowly out of frame. Only the man remains standing alone by the window, hands in pockets, staring out into the blowing snow. The room feels empty and still.

### Wuxia pixel art, keyframes
*Teaches: keyframes align strictly, unlike storyboards. Also a **vertical** example.*

> Create a one-shot vertical pixel-art wuxia-themed video based on @Image 1 to @Image 6. Use Chinese-style 8-bit wuxia background music. The entire video should use a unified light-blue background, consistent pixel-art style, and a clean, bright, transparent visual look.
> Shot 1: Hold on the ink-wash-style "江湖风云" logo from @Image 1. The background is the unified light-blue color. Keep the frame still for about 1 second.
> Shot 2: After the text area from @Image 1 disappears, the pixel-art close-up face of the male wuxia character from @Image 2 slides in from the bottom of the frame. The character blinks and looks toward the camera, then quickly moves downward and exits the frame. After the character exits, the original logo area transforms into the blue pixel-art "武功秘籍" martial arts manual from @Image 3.
> Shot 3: Immediately transition to @Image 4. A small pixel-art wuxia character jumps forcefully upward from the bottom of the frame and hits the blue diamond-shaped question mark icon above. Bold dark-blue text "今日闯江湖!" pops out above the question mark icon. After landing, the character strikes the standing pose from @Image 4, then raises a hand to greet the viewer. Next, the character prepares to run, turns toward the right side of the frame, and runs to the right, with the running pose referencing @Image 5. The camera follows the character smoothly to the right, and the character jumps out of frame from the right side.
> Shot 4: The UI interface from @Image 6 slides into the frame from the right. The pixel-art wuxia character jumps in from the upper-right corner and lands at the lower-right side of the large "三月廿七日" text. The character opens both arms in an enthusiastic presentation pose and freezes. The final frame holds on this composition.
> Overall requirements: Pixel-art wuxia visual style throughout, with a unified light-blue background tone. The camera movement should be continuous and smooth, presenting a one-shot flow with seamless position shifts and follow movement. Element transitions should feel natural, and character actions should connect smoothly. No stuttering, no flickering. Text and UI must remain clear and stable.

### Spirit fish, keyframes
*Teaches: the opening incantation for strict keyframe alignment.*

> Use Images 1 to 7 in order as keyframes. In a sea of clouds and mountains, blue-and-pink long-tailed spirit fish soar through the air. The camera slowly moves toward an ancient town built into the mountainside, focusing on the ancient pagoda at the top of the mountain. The scene then enters an elegant Chinese-style hall, where the spirit fish flies in through the window, lands in the round pool at the center of the hall, and swims leisurely. Finally, the perspective cuts to a dark ancient temple, where an old monk with a white beard stands with his back to the camera, quietly gazing at a huge framed painting. Inside the painting are the hall and the spirit fish swimming in the pond. The overall style is a new Chinese Ukiyo-e illustration.

### Aging woman, instruction editing
*Teaches: preserve-then-change. State what stays before what moves.*

> Preserve the composition, camera position, lighting, and performance rhythm of @Video 1. Only modify the female lead's appearance and expression: let her naturally age from her twenties to around sixty. The restraint in her eyes gradually softens, tears slide past the corners of her eyes, and the corners of her mouth slowly lift until she finally smiles through her tears. The entire video should be a continuous one-shot, with no jump cuts and no flickering. Her facial features should gradually age without drifting or changing identity.

### Duel, editing with reference images
*Teaches: swap subjects and setting while keeping the original action and rhythm.*

> Replace the two-person fight in @Video 1 with an empty-handed probing exchange before a cold-weapon duel.
> Replace the scene with a medieval stone castle platform, an ancient courtyard, an outer platform of a mountain fortress, or a simple stone-brick duel arena. The background should include castle walls, wind, fog, distant mountain ridges, and a flat stone ground. Refer to @Image 1 for the environment.
> Replace the man in dark clothing in the video with @Image 2, and replace the man in light-colored clothing with @Image 3. Keep the original actions and rhythm unchanged.
> AI effects should only enhance the environment and texture: wind-blown clothing, light fog, a small amount of dust at contact points, cool metallic reflections, subtle film grain, and an epic color palette. The overall style should be restrained, realistic, and evoke a classic hardcore duel atmosphere. Keep the background music synchronized with the action beats.

### Audio translation edit
*Teaches: audio-only editing with lip-sync correction.*

> Translate the spoken dialogue in the video into Chinese, with no subtitles. Precisely adjust the lip movements to match the translated speech, while keeping everything else unchanged.

### Bee pollination, extension
*Teaches: extension by duration plus the new action only. Use `mov` output.*

> Extend @Video 1 by 5 seconds. A bee flies in and lands on the flower. Then, in a macro close-up, its legs and abdomen are covered with golden pollen particles. The bee flaps its wings and takes off, and the camera follows it as it flies toward another flower of the same species. In slow motion, pollen shakes loose from the bee's fine hairs and falls precisely into the flower's stamen, magnifying the moment of pollination.

### Puppy coffee shop, one-click creation
*Teaches: turning a pile of stills into a video without altering them.*

> Turn all images into a one-click video. The image order can be freely arranged. Generate a coffee shop vlog in a hand-drawn animated doodle cutout style, documenting the fun daily moments of a puppy wearing different cute outfits and taking photos at the coffee shop. Generate trendy, internet-style playful audio or BGM.
> The images may move slightly, creating a live-photo effect, but do not alter the original images. Keep the visuals highly consistent with the original images.

### Mahjong to buildings, seamless transition
*Teaches: generating the missing middle between two clips.*

> Seamlessly connect [Video 1] and [Video 2]. At the end of [Video 1], the camera should quickly fly upward to the top, rapidly turn back, and then dive vertically downward, creating a natural seamless transition into [Video 2]. During the transition, the mahjong tiles gradually transform into high-rise buildings, and the entire scene changes accordingly. Do not alter the two uploaded videos themselves.

---

## SEED — the launch-post examples

### Singer backstage, one-take story
*Teaches: a 30s take should be a story with stages, not one extended moment.*

> One-take handheld gimbal tracking shot. The camera slowly pushes in through a gap in a heavy red curtain and enters a warm-toned backstage dressing room. A young female singer, with her back to the camera, is adjusting her earpiece as a staff member reminds her it's time to go on. She turns toward the camera and starts singing citypop. The camera pulls back and tracks her as she passes through the curtain into a dim backstage corridor, interacting naturally with her dancers along the way; one staff member hands her a microphone. She and the dancers then step onto the stage, and the camera arcs around to the back, gradually revealing the red-and-black stage design, LED screens, spotlights, haze, and reflective floor. The camera finally pulls out to a wide shot of the arena, showing the packed audience, light boards, glow sticks, and cheering crowd, capturing the youthful, free-spirited climax of the concert.

**This is the closest published example to a walking-through-a-workplace shot** — one character
moving through connected spaces, interacting with people along the way, with the camera handing off
between stages. Worth studying before any corridor film.

### Subway boy, extension
> Extend the video. Continue from the visuals and subjects in @Video 1 and generate another 30-second clip, keeping the character subjects, scene, visual style, and sound effects consistent. The little boy runs along the train carriage holding a soccer ball. When the subway stops, the side door opens and he immediately dashes out, with the male lead chasing after him. The two run across the platform and out onto the street, startling passersby and vehicles along the way. The male lead finally catches up and grabs him. The boy looks up, aggrieved. The male lead's anger slowly fades; he pats the boy's head and shows a helpless smile.

### Peking Opera, circular camera
> 16:9 widescreen, cinematic texture, single continuous take, smooth camera movement, no cuts. Scene reference: @Image 4. 0–5s: Open with a close-up of the Overlord from @Image 2. The camera slowly circles his upper body and transitions into a medium shot. The Overlord spins and turns, his body and back flags sweeping quickly past the lens to form a natural occlusion, and the camera follows through to Consort Yu's side in @Image 1. 6–10s: The camera steadily circles Consort Yu in a medium shot from @Image 1, following her water sleeves through the arc. She raises her arm, flicks her wrist, unfurls the sleeves, and half-turns. She then draws the sleeves back, holds the pose, and looks sideways toward the Overlord. 11–20s: The male warrior from @Image 3 enters with an aerial flip. The Overlord takes center stage while the warrior advances and retreats on the opposite side in a combat exchange. Consort Yu stands slightly behind and to the side of the Overlord, weaving in water-sleeve movements to set softness against strength. The camera slowly pulls back from a medium-close shot of the warrior to a full stage view. At the end, all three face the audience and strike a synchronized Peking opera finale pose.

Note the **occlusion-as-transition** trick: the back flags sweep past the lens to hide the cut.

### Concert orchestra, 18 references
*Teaches: how to bind many references without confusion — one clause each, in order.*

> A 30-second concert sequence in 16:9 landscape, with cinematic realism, authentic concert hall lighting and shadows, warm golden stage lighting, and the atmosphere of a formal classical concert. Use @Image 1 for the venue. Reference @Image 2 for the pianist. Reference @Image 3 for the cello. Reference @Image 4 for the violin. The lead vocalist must strictly follow @Image 5. Reference @Images 6 to 10 for the rest of the orchestra. Reference @Images 11 to 14 for the choir. Reference @Images 15 to 18 for the audience seating. The lead vocalist walks from center stage toward the front edge. The pianist is positioned by the piano. The orchestra is arranged on both sides and toward the rear. The choir stands at the back of the stage. Open with a high-angle wide shot of the full concert hall. The pianist strikes the keys, and the lead vocalist steps into the spotlight and begins singing. The camera naturally moves across the violin, cello, and orchestra as they perform together, with the violin feeling bright and the cello warm. In the latter part, the choir joins in. The lead vocalist briefly makes eye contact with front-row audience members, who respond with a smile and a slight nod. In the closing shot, the camera pulls back. The singing ends, and the audience joins in the applause.

### Football green screen edit
> Using @Video 1, render the green-screen background, obstacles, wardrobe, and supporting characters. 0–4s: outdoor training, replace the obstacles with rocks, bricks, tires, and wooden crates. 4–10s: locker room, friends offering encouragement. 10–15s: international match, replace the training poles with original defenders and a goalkeeper, and the protagonist scores. Overall photorealistic, cinematic quality.

### Breakfast, camera-only edit
*Teaches: changing the camera plan while freezing everything else.*

> Edit @Video 1. Keep the characters, actions, and visual style unchanged. Adjust only the camera movement. A 15-second segmented camera plan: 0–4s, a micro-FPV move skims tightly past the pan, then follows the popping toast and whip-pans to the coffee; 4–7s, push in and track laterally along the rim of the pan, following the fried egg as it flips up and lands back in place; 7–11s, rapidly rise to a top-down view, then descend at a steady pace, sweeping across the plate and keys; 11–15s, use a handheld close-up to follow the hands with a fast lateral whip, then push in on the breakfast and pull back to a medium two-shot. Keep the entire sequence smooth, continuous, and stable.

### Lin'an street, education example
> Expressive Eastern painterly style. A street scene in Lin'an during the Southern Song dynasty. Several children run and shout through the bustling street, chanting, "I turn around, and there he is, where the lantern lights grow dim." The camera follows the children as they run, sweeping past the lively street. The camera then tilts up to reveal Xin Qiji from @Image 1. Xin Qiji turns his head, and in the distance stands a man among the fading lantern lights. The shot stays continuous throughout.

### Car assembly, clay render
> Reference the camera work, composition, shot scale, spatial relationships, part positions, model structure, assembly order, and motion paths from @Clay Render 1. Reference the materials, lighting, color, reflections, and atmosphere from @Image 1, and turn the clay render into a high-end, photorealistic car assembly sequence.

---

## OURS — back office

Full context in `seedance.md` → Run log. Both 10s, 9:16, 720p, audio on, t2v via fal.

### v1 — REJECTED by output moderation
`content_policy_violation` · "potential copyright violation" · `partner_validation_failed`, after
reaching `COMPLETED` at 142s. The styling below is the suspected cause: night, rain, loosened tie,
desk lamp — a film-noir register.

> 10-second continuous single take, vertical 9:16, natural real-time speed, no cuts. A cramped independent record-label back office, late at night. One man in his forties sits at a desk: rolled shirtsleeves, collar open, tie pulled loose. An open laptop faces away from camera. To his left, a leaning stack of paper contracts. A phone lies face-up beside the laptop. Overhead fluorescent light mixed with cool spill from the laptop screen. Rain runs down a window behind him. 0-3 seconds: he is mid-work, both hands on the keyboard, eyes down, jaw tight. The phone buzzes once against the desk and lights up. He does not look at it. 3-6 seconds: the phone buzzes a second time, longer. He exhales, reaches right for it without looking, and his forearm catches the stack of contracts; the top third slides off the desk and falls past the front of frame. 6-8 seconds: he stops. He looks at the fallen paper on the floor, then at the still-buzzing phone, then back at the laptop. He picks up nothing. 8-10 seconds: he sits back in the chair, drags one hand down his face, and lets it fall into his lap. The phone stops buzzing on its own. He says quietly, "Yeah. I know." The shot ends on him still. Camera: locked-off medium shot at seated eye level, the man held in the centre third with headroom above him. Starting at 6 seconds only, a very slow push in of about fifteen centimetres. The camera never pans, never cuts, and never leaves the room. Keep the same man, shirt, tie, desk layout, laptop position and phone from first frame to last. Paper falls downward under gravity and stays on the floor; the amount of paper never increases. Audio: quiet office room tone, rain on the window behind him, two phone vibrations against a wooden desk, paper sliding and landing, one chair creak, and one line of male American-accented dialogue, "Yeah. I know." No music. No cuts, no slow motion, no repeated action, no duplicated paper or phones, no second person entering frame. No text anywhere in frame: no readable laptop screen, no phone screen content, no signage, no labels, no subtitles, no captions, no logos, no watermark.

### v2 — PASSED
Same beats, restyled to plain daylight plus an explicit fictional-person statement. Seed
`1632188029`, 162s. **Defects observed:** an Apple logo rendered despite "no logos"; the phone
buzz read as invisible so the paper fall looked like anger rather than distraction.

> 10-second continuous single take, vertical 9:16, natural real-time speed, no cuts. Plain documentary realism, ordinary modern office lighting, no cinematic stylisation, no film-noir look.
>
> A small, cluttered independent music-office room on an ordinary weekday afternoon. Flat daylight comes through half-open venetian blinds. One ordinary man in his early forties sits at a cheap desk. He is a fictional, unremarkable person with a plain everyday face, short dark hair, light stubble, wearing a plain grey crew-neck t-shirt. He must not resemble any real, famous or public figure, and this is not a scene from any film or television programme.
>
> An open laptop faces away from camera. To his left, a leaning stack of loose paper. A phone lies face-up beside the laptop.
>
> 0-3 seconds: he is mid-work, both hands on the keyboard, eyes down. The phone buzzes once against the desk. He does not look at it.
>
> 3-6 seconds: the phone buzzes a second time, longer. He exhales, reaches right for it without looking, and his forearm catches the stack of paper; the top third slides off the desk and falls past the front of frame.
>
> 6-8 seconds: he stops. He looks at the fallen paper on the floor, then at the still-buzzing phone, then back at the laptop. He picks up nothing.
>
> 8-10 seconds: he sits back in the chair, drags one hand down his face, and lets it fall into his lap. The phone stops buzzing on its own. He says quietly, "Yeah. I know." The shot ends on him still.
>
> Camera: locked-off medium shot at seated eye level, the man held in the centre third with headroom above him. Starting at 6 seconds only, a very slow push in of about fifteen centimetres. The camera never pans, never cuts, and never leaves the room.
>
> Keep the same man, t-shirt, desk layout, laptop position and phone from first frame to last. Paper falls downward under gravity and stays on the floor; the amount of paper never increases.
>
> Audio: quiet room tone, two phone vibrations against a wooden desk, paper sliding and landing, one chair creak, and one line of male American-accented dialogue, "Yeah. I know." No music.
>
> No cuts, no slow motion, no repeated action, no duplicated paper or phones, no second person entering frame. No text anywhere in frame: no readable laptop screen, no phone screen content, no signage, no labels, no subtitles, no captions, no logos, no watermark.

---

## Patterns worth stealing, ranked by how often they appear

1. **"Keep the same X, Y and Z from first frame to last."** In every FAL example without exception.
2. **A closing constraint list**: `No cuts, no slow motion, no repeated action, no duplicated props,
   no text, no logo, no music.` Also universal.
3. **An explicit `Audio:` clause** naming room tone, contact sounds and whether music exists.
   Silence must be asked for.
4. **`@ImageN controls only … Do not copy … from @ImageN.`** The two-clause reference binding.
5. **"natural real-time speed"** — appears in every FAL prompt, and is the counter to the model's
   drift toward slow motion.
6. **Calling a subject "fictional"** — used by FAL for the car and by us to clear moderation.
7. **A named frame position** ("the left third", "the centre third with headroom") rather than
   "centred" or "dynamic".
8. **State what a camera move waits for**: "the camera does not pan until the ball has fully left
   both hands."
