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
consistency, hands, props, stray text and brand-safety violations. **Fix physics at the still, never
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

`image_urls` taking up to ten references is what the casting workflow runs on: the first approved
still of each character is the seed for every later shot they appear in, alongside the world and
wardrobe references.

**Unverified at the time of the swap:** the resolution it returns, how tightly it holds a character
across 30 prompts, and whether it honours "ABSOLUTELY NO text". Four shots of one character costs
four cents, so prove all three on the first film rather than mid-build.

### 5. Motion — two models

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

### 6. Composite, render, mux

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
1.5), **$0.08/s of everything else** (H3 Max). Motion is now essentially the entire budget: a ~160s
film with 8 sung shots is about **$0.35 of stills against ~$16 of motion**.

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
