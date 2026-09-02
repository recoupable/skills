# Artist music video — their released song, the story they could not afford to shoot

Make a finished vertical video cut to a song a real artist has already released. Two builds inform
this: **LETAL XLUG (brauxelion's verse)**, shipped and artist-approved 2026-08-28, and **Movamos el
Mundo (Tomás Mika)**, stopped mid-build on 2026-09-01 by the artist's own feedback. The second one
rewrote this document, so read the first section before anything else.

**Clone `content/letal-xlug/` in the account workspace and work from it.** `gen-scene.mjs`,
`gen-motion.mjs` and `video/` are written to be re-pointed at a new artist by swapping the refs, the
style string and the scene table.

## Route here when

A real artist owns a **released recording** and the deliverable is a finished vertical video cut to
**that recording**. The song is the story; there is no Recoup story inside the film and no number on
screen.

| Not this | Go here instead |
|---|---|
| The song itself is generated (a `/music` track), not a released master | Style F, `content/rough-draft/` |
| A number or weekly result is the hero | Style A, data-in-motion |
| A shipped feature, real UI | Style B, 3D product reveal |
| A customer-facing asset billed to an artist's org | `recoup-content-make-video` (credit-metered, analyze-gated) |
| A scene with no person in it at all | `references/seedance.md` |

## Where the story comes from

**If the artist gives direction, follow it. Otherwise write the story yourself, from the lyrics and
what you know about them.** Never reproduce the video they already have.

This document used to say *continue the artist's own world, do not invent one*. On 2026-09-01 that
rule took a 159-second film 33 stills deep into a faithful reproduction of the artist's existing
video — same field, same wardrobe — and he then said what he had actually wanted:

> "le pediría algo totalmente distinto al video que ya tengo filmado.. o sea estar cantando ahí en un
> campo fue justamente por falta de recursos jjajaj ... como una historia tal vez, o en distintas
> locaciones.. tal vez una pareja.. viviendo cosas juntos"

**An artist's existing video is evidence of their budget, not their taste.** One person alone in a
field is what a song gets when there is no money; rebuilding it faithfully hands them back their own
constraint at higher resolution. We have no locations, no crew, no second-actor fee and no weather.
The version they could not afford is the only thing we have that nobody else offered them, so read
their existing work for *world and wardrobe*, never for scope.

The lyric is the brief: Tomás's song names an earthquake of kindness, fire falling from an opening
sky, salt petals on the wind and living in freedom, and every one of those is a shot. Read the whole
lyric for images before writing a scene table.

## Cast the film; do not clone the artist

**There is no face-guide step and no `cast/<artist>/` requirement.** That was inherited from the
cinematic-narrative format, where a recurring Recoup character must look the same across episodes. A
music video has no such obligation, and the guide costs two to four generations before the first
scene still exists, must be seeded into every later call, and drags the likeness gate along with it.

**Default: cast the film with invented characters.** One identity paragraph per character, reused
verbatim in every still prompt, each character locked by its first approved still, which seeds the
rest. Same consistency mechanism, minus the guide. It also frees the story from the artist's body: a
song about two people can show two people, a song spanning years can span locations and ages.

**Put the artist on camera only when the film needs them there** — they asked, or the song is
first-person and performance is the concept. Then the likeness gate applies, you need photos supplied
by them (not frames scraped off their video), and the sung shots go to OmniHuman.

Cast as many characters as the story needs. Never seed one from a photograph of a real person, and
never imply a real person.

## The rights gates that still bite

They fail independently. Check each, write the status in the plan doc.

| Gate | When it applies | The trap |
|---|---|---|
| **The recording** | **always** | The artist posting it is their call; **us** posting their master on **our** channels needs their explicit written yes, plus the label or producer if they say those own it |
| **Likeness** | only if the artist is depicted | Their own supplied photos, and a per-cut approval even for a consented recurring character |
| **Featured voice** | only if you show a face for a co-credited vocalist you have no consent from | Cut to their verse, or keep the feature off screen |

**Brand-safety lock, decided here and written into the negative prompt string of every still.** Drill
lyrics do not have to become drill visuals: the reference locked *no weapons, no substances, no cash*
so the same file could go on Recoup's channels unedited, while the artist's own artwork carries guns,
which is his choice for his channel. If the artist wants the harder cut, that is a different file and
their post only.

**No number appears on screen**, so there is nothing to audit. Stats about the artist stay in the
plan doc.

## The three gates that cost money

**Confirm the track and the lyric sheet before the song map.** The reference run built a 20-shot
table, generated 19 stills and started motion on the wrong song: the lyric sheet was for the title
track. Get the track in writing, get their sheet, transcribe the audio you will actually cut and diff
the two. Settle the **section** here too; a featured artist's own verse is usually right and it
sidesteps the featured-voice gate.

**Decide lip-sync before the motion bake-off.** A three-model bake-off ran on the reference before
anyone noticed **none of the takes were lip-synced**. Image-to-video mouths are prompt-driven: they
move, they look plausible frozen, and they are not saying the words.

> **An i2v mouth is never synced to real audio.** Split the scene table into *mouth-visible* and
> *no-mouth* rows on the day you write it, and assign the model per row.

**Review the contact sheet before any motion spend.** Stills are cents; motion is dollars. Generate
every still, assemble `scenes/CONTACT-SHEET.jpg` and read the whole sheet in one look for character
consistency, hands, props, stray text, background people and brand-safety violations. Review the
plates and the character portraits on their own sheets first, before any shot is generated at all. **Fix physics at the still, never
at the clip** — a half-open car window survived two OmniHuman takes with a hand through the glass
before the still itself was regenerated, and re-rolling a clip to fix a still costs five to ten times
more.

## Artist approval — three gates, in sequence

Not one "do you like it". They land hours apart and each changes the build: **the look** (stills or
the first 30 seconds, where a wrong world is still cheap), **the cut** (finished render, and nothing
posts before this one in writing), **the credit** (the reference artist asked for a personal credit;
the owner ruled **"VIDEO BY Recoup"**).

Send it in the artist's own language, with no em dashes and run through the `unslop` skill, and use
it to ask for the **master WAV** and whether the label or producer has anything to say about us
reposting.

## The pipeline

### 1. Audio

Prefer the **master WAV** from the artist. Until it arrives a YouTube rip is the approval cut only:

```bash
yt-dlp -f 18 --extractor-args "youtube:player_client=android" -o audio/src.mp4 "<video url>"
ffmpeg -i audio/src.mp4 -vn -c:a pcm_s16le audio/song.wav
```

**Measure before you touch it, and use linear gain only, never `loudnorm`.** Masters differ: the
reference rip was brickwalled at -7.6 LUFS and needed -6.5 dB to land at -14.1; the Tomás master had
real dynamic range at -16.6 LUFS and needed roughly +2.5 dB. Measure again on the finished render.

If you cut a section, snap the in and out points to gaps in the transcript, not to bar positions, and
crossfade ~60 ms when joining non-adjacent sections. Keep the full WAV.

### 2. Word times

Auto-captions give you the words; you need word **times** to cut.

- **You have the master WAV** → transcribe it (`npx hyperframes transcribe`, or the Scribe pass in
  `scripts/audio.mjs`).
- **All you have is their YouTube upload** → scrape it through Recoup. `subtitles=true` is YouTube
  only and downloads each returned video's captions; the field is only populated when you ask for it,
  which is why a plain channel-list scrape comes back with none. Get the social `id` from
  `GET /api/artist/socials`, then:

  ```bash
  curl -sS -X POST "https://api.recoupable.dev/api/socials/<SOCIAL_ID>/scrape?posts=5&subtitles=true" \
    -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"
  # -> { runId, datasetId }; poll GET /api/apify/runs/<RUN_ID> until SUCCEEDED,
  #    then read the video's subtitles[0].plaintext
  ```

  That gives you the **words**. The Recoup YouTube connector separately 403s on
  `YOUTUBE_LOAD_CAPTIONS` for videos you do not own. For word **times** on a video you cannot
  transcribe, fall back to the auto-caption VTT:

  ```bash
  yt-dlp --skip-download --write-auto-sub --sub-langs "es,es-419,en" \
    --sub-format vtt --extractor-args "youtube:player_client=android" \
    -o "sub.%(ext)s" "<video url>"
  ```

  The VTT carries `<c>` word tags, so word-level timing survives. **The roll-up format repeats each
  line**: only cues containing `<c>` carry new words, and only their *last* line is new. Naive
  extraction scrambles the lyric.

Do not burn time on local whisper; `whisper-cpp 0.15.3` fails on `ggml-large-v3-turbo.bin`.

### 3. Song map and scene table

Sections (`Intro / Verse / Hook / Break / Tail`) with a lyric anchor each, then a scene table on top.
**Every beat ≤6.5s** (`references/hooks.md`). Each row carries: window, beat, still prompt, motion
prompt, **and which model owns it** — deciding that in the table is what makes the lip-sync gate
automatic.

The hook is a **specific image**, not a spoken line; a music video's VO is the song. First frame, no
logo, no fade, no title card.

Write one long `STYLE` string and one identity paragraph per character, and interpolate them into
every prompt. Consistency across 30 shots comes from the strings being literally identical, not from
describing the look 30 times. Put the negative list **inside** `STYLE`: `ABSOLUTELY NO text, letters,
numbers, logos, signs with words, watermarks, or user interface. NO weapons, NO drugs, NO cash.`

**Name the camera move, do not describe the effect.** "The horizon tilts" produced a hillside; **DUTCH
ANGLE** plus "NOT a hill, NOT a slope" produced the shot. And a corrective re-roll silently drops
whatever the prompt stops repeating — the tilt fix came back with warm blue-sky light and broke the
film's grade arc, so re-assert the grade in every corrective prompt.

### 4. Stills — Meta Muse Image

**Owner ruling 2026-09-01: `meta/muse-image` is the house still model, replacing Nano Banana 2.** It
is quoted at **$0.01 per image** against Nano Banana 2's $0.08, and NB2 bills 2K output at 1.5x
($0.12) — which is what our generators were actually set to. That is a 12x difference on a line we
pay 30 to 40 times per film, so re-rolls stop being something to ration.

| Call | Endpoint | Input |
|---|---|---|
| The first still of a character or world | `meta/muse-image/text-to-image` | `prompt`, `aspect_ratio: "9:16"`, `num_images`, `output_format` |
| Every still after it | `meta/muse-image/edit` | the same, plus `image_urls` — **1 to 10** reference images |

`output_format` defaults to **webp**; set `"png"` or `"jpeg"` so ffmpeg and the renderer take the
file. There is **no resolution field** (the aspect ratio sets the dimensions) and **no negative
prompt field**, so the negative list stays inside the `STYLE` string as above.

`image_urls` taking up to ten references is what the whole workflow below runs on.

**Verified 2026-09-01** on a 33-shot film: it holds a character across 30 prompts, returns 1152x2048
at 9:16, and honours "ABSOLUTELY NO text". It does **not** reliably follow layout or wardrobe
instructions that contradict a reference image, so name those harder than feels necessary.

### 5. Build the film in three layers: plates, then people, then camera

Do these in order. Skipping straight to shots cost two complete scene passes on the reference film.

**Layer 1 — the empty plates.** One still per location with **nobody in frame**, generated
text-to-image and approved before a single character shot exists. Where two plates are the same place
at different times (a roof at dawn and at sunrise, a field by day and at night), generate the second
as an **edit of the first** so it is demonstrably the same place: *"EXACTLY the same rooftop as the
reference image, same parapet, same water tank, same camera position. The only change is the light."*

Why: independently generated shots of "a kitchen at night" are a different kitchen every time. The
reference film shipped a contact sheet where two consecutive shots of the same room did not match.

**Layer 2 — camera coverage, and this is the step everyone skips.** Plate-seeding locks the
*composition* as well as the location, so every shot in an act comes back as the same photograph with
different content dropped in.

> **Test this before you spend on it (2026-09-02).** On `meta/muse-image` the plate does **not**
> lock the camera when the move is stated explicitly and emphatically: a top-down floor shot came
> straight out of a wide eye-level hall plate, first try, and four planned angle plates turned out
> to be unnecessary. Spend one image finding out which behaviour you are getting. And note a plate
> earns its place only when two or more shots share it; a plate for one shot is ceremony.
> Also read `video-pipeline.md` → *Reference discipline*: a plate transmits PLACE, a character
> transmits MEDIUM, and you cannot edit a photoreal plate into another medium at all. For each location generate **two more angles as edits of its master**
— a medium and a low or detail angle — then seed each shot on the angle it actually needs. At $0.01
a plate this is the cheapest quality in the pipeline.

> **A camera-coverage plate carries an implied camera POSITION, not just a framing.** A beach plate
> with the dunes at the top means the camera stands in the sea looking landward, so nothing seeded on
> it can walk away from camera out to sea. Check where the camera *is* before assigning a plate.

**Layer 3 — the shots.** Every character shot seeds on **its angle plate first, then the character
portraits**, and the prompt says which reference is which, because the model cannot guess:

```
The FIRST reference image is the LOCATION. Reproduce that place exactly: same architecture,
same objects, same light, same colour. Do not invent a different place.
The OTHER reference images are the two people. Same faces, same bone structure, same hair,
same age. Do not beautify them, do not change their age, do not swap the faces.
```

**Age a character by chaining edits.** Young via `text-to-image`, then middle and old as edits seeded
on the young portrait. That is what makes three ages read as one person instead of three lookalikes.

### The two prompt failures that will happen to you

> **Filter triggers confirmed so far:** kissing, wading, "human shadows", a "shaft" of light, a petal
> "hanging", anatomy language, and **"dead"** in any form ("hundreds of dead moths" was rejected;
> "hundreds of empty paper moth wings" passed and reads better). Reword around the trigger. Retrying
> identical text never works.

**1. The blanket negative does not stop stray background people at extreme wide.** `NO other people
in frame beyond those described` sat in the shared `STYLE` string and an extreme-wide road shot still
grew two extra figures near the horizon, where a person is a few pixels and costs the model nothing.
State the headcount **positively** and declare the background empty **by category**:

> EXACTLY TWO people are in this photograph and nobody else. The road beyond them is COMPLETELY
> EMPTY all the way to the horizon: no other figures, no distant walkers, no specks of people,
> no vehicles, no animals.

**2. fal's content filter rejects innocuous prompts — and it is NON-DETERMINISTIC, so RETRY BEFORE
YOU REWORD.** This corrects the advice that shipped in #129, which said only a reword clears a
rejection. It does not: on a 31-shot film **11 shots failed on the first pass and 9 of them succeeded
on retry with the prompt unchanged**. The same prompt was submitted twice back to back and passed
both times after failing minutes earlier, which means the checker is also judging something other
than your text — most likely the generated image as well.

> **The order is: retry up to ~4 times with backoff, and only reword what survives that.** Rewording
> first means rewriting good prompts for no reason and losing the shot you actually wanted. Build the
> retry into the generator, not into your patience:

```js
let res, lastErr;
for (let attempt = 1; attempt <= 4; attempt++) {
  try { res = await fal.subscribe(model, { input, logs: false }); break; }
  catch (err) { lastErr = err; if (attempt < 4) await new Promise(r => setTimeout(r, 1500 * attempt)); }
}
if (!res) throw lastErr;
```

Lower concurrency helps too; four in flight rejected noticeably more than two.

**What survives retry is a real trigger, and it is almost never the subject.** Fire is fine — a whole
hillside alight passes first time. What trips it is the *vocabulary* around the subject:

| Rejected | Passed |
|---|---|
| the fire has **SPREAD**; "nothing **destroyed**, nothing **charred**, no smoke **damage**" | "more small calm flames… like candles… everything intact" |
| **sparks** climbing, **embers** drifting, anything *rising* off a fire | "small bright points of light", "warm haze" |
| rain **hammering**, droplets **bursting** | "rain running over the paintwork", "raindrops catching the light" |
| people **dancing** | "out in the street together, celebrating, arms raised" |
| hands **gripping** a wheel | "two hands rest on the wheel" |
| two people **kissing** | "standing facing each other, foreheads touching, eyes closed" |
| anatomy spelled out — "**hips**, thighs, submerged" | "water at knee height, upright at full height" |
| "two long **human shadows**" | "two long narrow parallel bands of shade" |
| a "**shaft**" of light | "a band of light" |
| a petal "**hanging** suspended" | "a petal floats in the air" |

Two patterns cover almost all of it: **language of destruction or spreading**, even when you are
negating it, and **body-part or force words** on a human subject. Describe things as calm, contained
and decorative and the same shot passes.

Budget a minute and a penny per rejection. Across two films none of them cost a shot — but do not
reword a prompt that has not yet been retried.

### 6. Motion — two models

**Owner ruling 2026-08-31: MiniMax H3 Max is the house image-to-video model.** Everything that does
not mouth words goes to H3 Max. Do not bake off a third vendor.

| The shot | Model | Price | Call shape |
|---|---|---|---|
| **Mouth visible**, singing to camera | `fal-ai/bytedance/omnihuman/v1.5` | $0.16/s | `image_url`, `audio_url` = **the exact slice of the song for that window**, `prompt`, `resolution: "1080p"` |
| **Everything else** | `minimax/h3-max/image-to-video` | $0.08/s (the $0.04 promo ran to 2026-09-01) | `prompt`, `image_url`, `duration` (min 5), `resolution: "768P"`, `prompt_expansion_mode: "disabled"` |

OmniHuman's fetcher 400s on multi-megabyte PNG stills while H3 takes the same file; hand it a
1080-wide JPEG proxy.

**H3 Max invents things, and driving it is part of the job.** Across the two builds it added a
lettered pendant, numbered dashboard gauges, storefront signage and an anime woman who was not in the
still. So: carry the full negative list in **every motion prompt**, not just the still prompt; **name
the prop you do not want** ("plain chain, no pendant" fixed the pendant); budget two takes on wide
plates and slow push-ins, its two weak shots; and re-roll freely, because at $0.08/s the answer to a
bad take is another take.

Rejected once, so nobody re-runs the bake-off: **Kling Avatar** burns garbled subtitles into frame,
**LTX-2.3** drifts the face, **InfiniteTalk** did not return. **Sync Lipsync v2 Pro** ($5/min) is
worth keeping as the cheap way to re-sync a clip you already rendered.

### 7. Composite, render, mux

Clone `content/letal-xlug/video/`, place the clips on the song map by word time, **mute every clip**
(the master is muxed after render), and type any wordmark as HTML text.

- Pin every invocation: `npx hyperframes@0.7.5 snapshot --at <times> .` at ~6 points **before** you
  ever run `npm run render`.
- **Never cut a clip within ~0.15s of its file end** — the decoder returns black there. Verify by
  sampling frame brightness across the cut, not by eye.
- Where a generator returns a clip fractionally shorter than its window, clone the last frame
  (`tpad=stop_mode=clone`) rather than reflowing the timeline. **Lip-synced starts are absolute.**
- **The headless renderer ignores CSS `filter: invert` on JPEGs.** Type the wordmark.
- A still model turns "two shots of him" into a split grid. Prompt one continuous frame.
- Mux at measured linear gain, then read frames back out of the finished render. A render returning
  the right duration is not evidence it looks right.

## Cost

Quoted rates, 2026-09-01: **stills $0.01 each** (Muse Image), **$0.16/s of sung shot** (OmniHuman
1.5), **$0.08/s of everything else** (H3 Max). Motion is essentially the entire budget.

Measured on a 33-shot, 159s film: **$1.75 for every image in the project** — face-guide bake-off,
six character portraits, 24 plates, all 33 stills, and two complete scene passes that were thrown
away. The first 30 seconds of motion, six shots including one OmniHuman, came to **$3.13**. Stills
are now cheap enough that the expensive mistake is spending motion money on a shot list the artist
has not seen.

Two lines disappeared with this revision: the face guide and its failed attempts, and Nano Banana 2
at 2K, which took the stills line from ~$4.70 to ~$0.35 on a 33-shot film. Re-check every price on
fal before committing, and pull real spend from the api project's production `FAL_KEY` account.

## Publish

1. **The artist posts first**, on their channels, in their language, with their own caption.
2. **IG Collab invite** to `@recoupableai` / sweetman so it lives on both profiles. This is the whole
   distribution plan, and the measured reason we make these at all: the 2026-07-22 collab reel took
   **45 likes against 1 to 3** for every non-collab reel around it.
3. Then our four-platform cut via `recoup-internal-social-ship-posts`, **after clearing the gate in
   `references/publish-verify.md`** (it exits non-zero; do not publish past it):
   `utm_campaign=<artist-slug>`, tagged link in the **YouTube description only**, LinkedIn gets an
   **image** not the video, X body carries no link.
4. Log it in `posts-log.md` with both halves of the why. Instagram cannot carry a per-post link, so
   record it as **unattributable** rather than as a zero.

The film is a **trust and awareness beat, not a conversion post**, and also the demo we send the next
label — the piece where the artist is the customer, not the subject. Say both plainly in the plan doc
rather than dressing the commercial half as a gift.
