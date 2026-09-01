# Artist music video — their released song, the story they could not afford to shoot

Make a finished vertical video cut to a song a real artist has already released. Two builds inform
this: **LETAL XLUG (brauxelion's verse)**, shipped and artist-approved 2026-08-28, and **Movamos el
Mundo (Tomás Mika)**, stopped mid-build on 2026-09-01 by the artist's own feedback. The second one
rewrote this document, so read the first section before anything else.

**Clone `content/letal-xlug/` and work from it.** `gen-scene.mjs`, `gen-motion.mjs` and `video/` are
written to be re-pointed at a new artist by swapping the refs, the style string and the scene table.

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

## Gate 0 — ask what they would make with no limits, and build THAT

This document used to say *continue the artist's own world, do not invent one*. On 2026-09-01 that
rule took a 159-second film 33 stills deep into a faithful reproduction of the artist's existing
video — same field, same wardrobe — before he was asked what he actually wanted:

> "le pediría algo totalmente distinto al video que ya tengo filmado.. o sea estar cantando ahí en un
> campo fue justamente por falta de recursos jjajaj ... como una historia tal vez, o en distintas
> locaciones.. tal vez una pareja.. viviendo cosas juntos"

**An artist's existing video is evidence of their budget, not their taste.** One person alone in a
field is what a song gets when there is no money; rebuilding it faithfully hands them back their own
constraint at higher resolution. We have no locations, no crew, no second-actor fee and no weather.
The version they could not afford is the only thing we have that nobody else offered them.

**A polite yes is not a brief.** That same message opened "obvio que está buenísimo lo que estás
haciendo" and closed "sea lo que sea que puedas hacer voy a estar agradecido". Gratitude is what an
artist says to a gift; it carries no direction, and reading it as approval is how a build goes 33
stills deep in the wrong film. The real answer only appeared because someone asked the counterfactual.

**So, in the first message, before any paid pixel:** *if you could have any video for this song, with
no budget and no limits, what would it be?* Then build their answer, not their back catalogue. No
answer is also an answer and frees you to invent — but ask, because the question costs one message
and the wrong world costs the film.

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

**A second person on screen is allowed** (owner ruling 2026-09-01, overriding the earlier
no-second-face rule): a generated character is not a real person whose consent we bypassed. Never
seed one from a real photograph, and never imply a real person.

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

**No figure appears on screen**, so there is nothing to audit. Stats about the artist stay in the
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

Send it in the artist's own language, with no em dashes, and use it to ask for the **master WAV** and
whether the label or producer has anything to say about us reposting.

## The pipeline

### 1. Audio

Prefer the **master WAV** from the artist. Until it arrives a YouTube rip is the approval cut only:

```bash
yt-dlp -f 18 --extractor-args "youtube:player_client=android" -o audio/src.mp4 "<video url>"
ffmpeg -i audio/src.mp4 -vn -c:a pcm_s16le audio/song.wav
```

**Measure before you touch it, and use linear gain only, never `loudnorm`.** Masters differ: the
reference rip was brickwalled at -5.9 LUFS and needed -6.5 dB to land at -14.1; the Tomás master had
real dynamic range at -16.6 LUFS and needed roughly +2.5 dB. Measure again on the finished render.

If you cut a section, snap the in and out points to gaps in the transcript, not to bar positions, and
crossfade ~60 ms when joining non-adjacent sections. Keep the full WAV.

### 2. Word times

Auto-captions give you the words; you need word **times** to cut.

- **You have the master WAV** → transcribe it (`npx hyperframes transcribe`, or the Scribe pass in
  `scripts/audio.mjs`).
- **All you have is their YouTube upload** → the Recoup YouTube connector 403s on
  `YOUTUBE_LOAD_CAPTIONS` for videos you do not own and the Apify `subtitles` field comes back null
  on channel-list scrapes, so:

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
**Every beat ≤6.8s** (`references/hooks.md`). Each row carries: window, beat, still prompt, motion
prompt, **and which model owns it** — deciding that in the table is what makes the lip-sync gate
automatic.

The hook is a **specific image**, not a spoken line; a music video's VO is the song. First frame, no
logo, no fade, no title card.

Write one long `STYLE` string and one identity paragraph per character, and interpolate them into
every prompt. Consistency across 30 shots comes from the strings being literally identical, not from
describing the look 30 times. Put the negative list **inside** `STYLE`: `ABSOLUTELY NO text, letters,
numbers, logos, signs with words, watermarks, or user interface.`

**Name the camera move, do not describe the effect.** "The horizon tilts" produced a hillside; **DUTCH
ANGLE** plus "NOT a hill, NOT a slope" produced the shot. And a corrective re-roll silently drops
whatever the prompt stops repeating — the tilt fix came back with warm blue-sky light and broke the
film's grade arc, so re-assert the grade in every corrective prompt.

### 4. Motion — two models

**Owner ruling 2026-08-31: MiniMax H3 Max is the house image-to-video model.** Everything that does
not mouth words goes to H3 Max. Do not bake off a third vendor.

| The shot | Model | Price | Call shape |
|---|---|---|---|
| **Mouth visible**, singing to camera | `fal-ai/bytedance/omnihuman/v1.5` | $0.16/s | `image_url`, `audio_url` = **the exact slice of the song for that window**, `prompt`, `resolution: "1080p"` |
| **Everything else** | `minimax/h3-max/image-to-video` | $0.08/s (the $0.04 promo ran to 2026-09-01) | `prompt`, `image_url`, `duration` (min 5), `resolution: "768P"`, `prompt_expansion_mode: "disabled"` |

OmniHuman's fetcher 400s on multi-megabyte 2K PNG stills while H3 takes the same file; hand it a
1080-wide JPEG proxy.

**H3 Max invents things, and driving it is part of the job.** Across the two builds it added a
lettered pendant, numbered dashboard gauges, storefront signage, Japanese shop signs and an anime
woman who was not in the still. That is a budget line, not a reason to change model:

1. **Carry the full negative list in every motion prompt**, not just the still prompt.
2. **Name the prop you do not want.** "Plain chain, no pendant" fixed the pendant. Close the
   ambiguity by name.
3. **Wide plates and slow push-ins are its two weak shots.** Budget two takes for each.
4. **Re-roll freely.** At $0.08/s the answer to a bad take is another take.

Rejected once, so nobody re-runs the bake-off: **Kling Avatar** burns garbled subtitles into frame,
**LTX-2.3** drifts the face, **InfiniteTalk** did not return. **Sync Lipsync v2 Pro** ($5/min) is
worth keeping as the cheap way to re-sync a clip you already rendered.

### 5. Composite, render, mux

Clone `content/letal-xlug/video/`, place the clips on the song map by word time, **mute every clip**
(the master is muxed after render), and type any wordmark as HTML text.

- Pin every invocation: `npx hyperframes@0.7.5 snapshot --at <times> .` at ~6 points **before** you
  ever run `npm run render`.
- **Never cut a clip within ~0.15s of its file end** — the decoder returns black there. Verify by
  sampling frame brightness across the cut, not by eye.
- Where a generator returns a clip fractionally shorter than its window, clone the last frame
  (`tpad=stop_mode=clone`) rather than reflowing the timeline. **Lip-synced starts are absolute.**
- **The headless renderer ignores CSS `filter: invert` on JPEGs.** Type the wordmark.
- Nano Banana 2 turns "two shots of him" into a split grid. Prompt one continuous frame.
- Mux at measured linear gain, then read frames back out of the finished render. A render returning
  the right duration is not evidence it looks right.

## Cost

Stills are ~$0.09 each; motion is the whole budget: **$0.16/s of sung shot + $0.08/s of everything
else**. A ~160s film with 8 sung shots is roughly **$19**. Casting instead of face-guiding removes
the guide line (~$0.60 and its failed attempts) entirely. Re-check both prices on fal before
committing, and pull real spend from the api project's production `FAL_KEY` account, not a local key.

## Publish

1. **The artist posts first**, on their channels, in their language, with their own caption.
2. **IG Collab invite** to `@recoupableai` / sweetman so it lives on both profiles. This is the whole
   distribution plan, and the measured reason we make these at all: the 2026-07-22 collab reel took
   **45 likes against 1 to 3** for every non-collab reel around it.
3. Then our four-platform cut via `recoup-internal-social-ship-posts`: `utm_campaign=<artist-slug>`,
   tagged link in the **YouTube description only**, LinkedIn gets an **image** not the video, X body
   carries no link.
4. Log it in `posts-log.md` with both halves of the why. Instagram cannot carry a per-post link, so
   record it as **unattributable** rather than as a zero.

The film is a **trust and awareness beat, not a conversion post**, and also the demo we send the next
label — the piece where the artist is the customer, not the subject. Say both plainly in the plan doc
rather than dressing the commercial half as a gift.
