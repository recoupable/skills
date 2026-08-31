# Artist music video — a real artist's own song, cut to 9:16

Make a finished vertical music video from a song a real artist has already released, using their real
face and their real master. Codified 2026-08-31 from the one build that has shipped this way:
**LETAL XLUG (brauxelion's verse), 27.0s, four platforms, artist-approved** —
`content/letal-xlug/` in the account workspace, whose `SCRIPT.md` is the full build log.

**Clone `content/letal-xlug/` and work from it.** Every script in that folder (`gen-scene.mjs`,
`gen-motion.mjs`, the three `bakeoff-*.mjs`, the `reroll-*.mjs`) is written to be re-pointed at a new
artist by swapping the refs, the style string and the scene table.

## Route here when

A real artist owns a **released recording** and the deliverable is a finished vertical video cut to
**that recording**. The song is the story; there is no Recoup story inside the film and no number on
screen.

| Not this | Go here instead |
|---|---|
| Invented characters singing a `/music` generation | Style F, `content/rough-draft/` |
| A number or weekly result is the hero | Style A, data-in-motion |
| A shipped feature, real UI | Style B, 3D product reveal |
| A customer-facing asset billed to an artist's org | `recoup-content-make-video` (credit-metered, analyze-gated) |
| A scene with no real person in it | `references/seedance.md` |

## Why we make these at all

Not as a favour and not as a portfolio piece. Two measured reasons, both worth restating in the plan
doc:

1. **The collaborator lever is the largest one we have.** Featuring an artist and getting invited to
   co-post took the 2026-07-22 collab reel to **45 likes against 1 to 3** for every non-collab reel
   around it. A music video is the strongest possible version of that ask, because the artist
   genuinely wants to post it.
2. **It is the demo we send the next label.** The reference build is the first piece where the artist
   is the **customer, not the subject** — which is the thing the roster pitch has never had a sample
   of. That is commercial, and the plan doc says so plainly rather than dressing it as a gift.

The film itself is a **trust and awareness beat, not a conversion post.** Say that in the plan doc.
The link that matters is the artist's, not ours; ours goes in the YouTube description only.

## The five gates, in the order they bite

Each one below cost real money or a real rebuild on the reference run. They are ordered by how early
they fire, and every one of them fires **before** the expensive step it protects.

### Gate 1 — confirm which track, with the artist, before the song map

The reference run built a 20-shot scene table, generated 19 stills and started motion on *Drift* —
then the artist's lyric sheet turned out to be for the **title track**, and the film was recut to his
verse of a different song (08-28 15:40). Everything upstream of the audio survived only because the
art direction was shared between the two.

**So:** get the track confirmed in writing, and get the artist's own lyric sheet, before you write the
song map. Then transcribe the audio you will actually cut and diff it against that sheet. A lyric
sheet that does not match the waveform is the cheapest possible catch and the most expensive miss.

Also settle at this point which **section** you are cutting. Their verse only is usually the right
answer for a featured artist, and it is what the artist asked for on the reference
("dale foco a mi parte"). It also sidesteps the featured-vocalist consent problem below.

### Gate 2 — the why, and the three rights gates, before any paid pixels

`references/topic-selection.md` applies in full, and the "why theirs" sentence carries more weight
here than anywhere else, because we are spending our money on someone else's release. The reference
doc's version is the model: *his EP is seven days old, this version has no video, he gets a finished
vertical cut in the world he already built, at zero cost, his to post first, and nothing leaves the
folder until he says yes.*

Rights are **three separate gates**, not one, and they fail independently:

| Gate | What it covers | How it failed on the reference |
|---|---|---|
| **Likeness** | permission to depict this face | already cleared as a recurring cast member; still added a per-cut approval |
| **The recording** | permission for *us* to post *their* master on *our* channels | never assume: the artist posting it is their call, us posting it needs their explicit written yes, plus the label or producer if they say those own it |
| **Featured voice** | a co-credited vocalist we have no consent from | the reference shot verse 2 **masked** so no unconsented face appeared, then dropped it entirely when the artist confirmed the feature sings it |

**Brand-safety lock, decided here and written down.** Drill lyrics do not have to become drill
visuals. The reference locked *no weapons, no substances, no cash* into the negative prompt string of
every single still, so the same file could go on Recoup's channels without an edit — while the
artist's own artwork carries guns, which is his choice for his channel. If the artist asks for the
harder cut, that is a different file and their post only.

**No figure appears on screen**, so there is nothing to audit. Any stats you gathered about the
artist stay in the plan doc.

### Gate 3 — decide lip-sync BEFORE the motion bake-off

The single most expensive process error on the reference: a full three-model motion bake-off ran and
was reviewed before the owner noticed that **none of the takes were lip-synced**. Image-to-video
mouths are prompt-driven; they move, they look plausible in a still frame, and they are not saying
the words. That bake-off (~$1.10) was spent to answer the wrong question.

> **Rule: an i2v mouth is never synced to real audio.** Split the scene table into
> *mouth-visible* and *no-mouth* shots on the day you write it, and bake off the two groups
> separately, against the real audio slice.

### Gate 4 — the contact sheet, before any motion spend

Stills are cents; motion is dollars. Generate every still, assemble `scenes/CONTACT-SHEET.jpg`, and
review the whole sheet in one look for likeness, hands, props, stray text and brand-safety
violations. The reference caught a wrong facial expression this way (S7 came out grinning on the
stress verse; re-rolled, and the reject kept as `scenes/s7-grin-rejected.png`).

**Fix physics at the still, never at the clip.** S2's still had the car window half up. Both
OmniHuman takes rolled it further and put his hand through the glass; the owner caught it twice
before the still itself was regenerated with the window fully down and his hand on the sill. A
motion model will animate whatever ambiguity you hand it, and re-rolling a clip to fix a still costs
5 to 10 times more.

### Gate 5 — artist approval is three gates, arriving in sequence

Not one "do you like it." On the reference they landed hours apart and each changed the build:

1. **The look** (stills, 14:25) — "está superduro", plus a direction that reshaped the whole cut.
2. **The cut** (finished render, 15:54) — "durísimo". Nothing posts before this one, in writing.
3. **The credit** (16:45) — he asked for a personal credit, the owner ruled **"VIDEO BY Recoup"** on
   the title card.

Send the approval message in the artist's own language, with no em dashes, and use it to ask for the
two things you still need: the **master WAV** and whether the beat or the label has anything to say
about us reposting. The reference's Spanish draft is in `content/letal-xlug/SCRIPT.md`.

## The pipeline

### 1. Audio

Prefer the **master WAV** from the artist; ask for it in the approval message. Until it arrives, a
YouTube rip is the approval cut only:

```bash
yt-dlp -f 18 --extractor-args "youtube:player_client=android" -o audio/src.mp4 "<video url>"
ffmpeg -i audio/src.mp4 -vn -c:a pcm_s16le audio/song.wav
```

**Measure before you touch it.** The reference rip was **-5.9 LUFS / +1.9 dBTP** — already
brickwalled. A released master usually is. Mux with **linear gain only, never `loudnorm`**: the
reference shipped at -6.5 dB linear gain, landing at -14.1 LUFS / -4.8 dBTP.

If you are cutting a section, snap the in and out points to gaps in the transcript, not to bar
positions, and crossfade ~60 ms if you are joining two non-adjacent sections. Keep the full WAV.

### 2. Words and word times

Two different problems. **Auto-captions give you the words; you need word times to cut.**

- **You have the master WAV** → transcribe it. `npx hyperframes transcribe`, or the Scribe pass in
  the project's `scripts/audio.mjs`. The reference's `assets/drift.scribe.json` is 412 words with
  per-word times, and every scene window in the scene table is snapped to it.
- **All you have is their YouTube upload** → auto-captions via `yt-dlp`. The Recoup **YouTube
  connector 403s** on `YOUTUBE_LOAD_CAPTIONS` for videos you do not own, and the Apify scraper's
  `subtitles` field comes back `null` on channel-list scrapes (verified 2026-08-31 on a five-video
  batch). This is the working path:

  ```bash
  yt-dlp --skip-download --write-auto-sub --sub-langs "es,es-419,en" \
    --sub-format vtt --extractor-args "youtube:player_client=android" \
    -o "sub.%(ext)s" "<video url>"
  ```

  The VTT carries `<c>` word tags, so word-level timing survives. Clean it: strip `<[^>]+>`, drop
  timestamp lines and `[Music]` / `[Música]`, and **dedupe consecutive repeats** — auto-subs repeat
  each line about three times for the karaoke roll-up.

Do not burn time on local whisper. `whisper-cpp 0.15.3` against `ggml-large-v3-turbo.bin` failed
`expected 587 tensors got 111` on 2026-08-31; the hosted paths above are faster and free.

### 3. Song map and scene table

Turn the word times into sections (`Intro / Verse / Hook / Break / Tail`) with a lyric anchor per
section, then a scene table on top of it. **Every beat ≤6.5s** (`references/hooks.md`). The reference
was 19 generated shots plus one HTML title card over 112s.

Each row carries: window, beat, the still prompt, the motion prompt, **and which of the three motion
models owns it** (below). Deciding the model in the table is what makes Gate 3 automatic.

The hook is a **specific image**, not a spoken line — a music video's VO is the song. First frame, no
logo, no fade, no title card. State the premise visually by the end of the intro.

### 4. Art direction and the face guide

- **Continue the artist's own world**, do not invent one. The reference read the EP's official video
  as a stylised 3D Metal Slug homage and made this one *the racing level of the same game* — same
  city, same rain, same neon, the tank swapped for a drift car (and parked in the far background of
  one shot as an easter egg). Pull the official artwork or thumbnail in as a style reference on
  every call.
- **Face guide** in `cast/<artist>/`: a white-background expression sheet built with **Nano Banana 2**
  (`fal-ai/nano-banana-2/edit`, multi-reference fusion), plus a real frontal photo, plus the official
  artwork, plus any alternate persona (the reference has a masked one). Seed **all** of them into
  every still call. See the `faceguide-model-workflow` notes for how the guide itself is built.
- Write one long `STYLE` string and one long identity string and interpolate them into every prompt,
  as `gen-scene.mjs` does. Consistency across 19 shots comes from the strings being literally
  identical, not from describing the look 19 times.
- Put the negative list **inside** `STYLE`: `ABSOLUTELY NO text, letters, numbers, logos, signs with
  words, watermarks, or user interface. NO weapons, NO guns, NO drugs, NO cash, NO other people.`

### 5. Motion — two models

**Owner ruling 2026-08-31: MiniMax H3 Max is the house image-to-video model.** Everything that does
not have to mouth the words goes to H3 Max, at every price point, regardless of shot type. Do not
bake off a third vendor; the split below is the whole decision.

| The shot | Model | Price | Call shape |
|---|---|---|---|
| **Mouth visible** — he raps or sings on camera | `fal-ai/bytedance/omnihuman/v1.5` | $0.16/s | `image_url`, `audio_url` = **the exact slice of the song for that window**, `prompt`, `resolution: "1080p"` |
| **Everything else** — held portrait, push-in, blink, car, hands, city, cutaways | `minimax/h3-max/image-to-video` | $0.04/s promo, $0.08/s after | `prompt`, `image_url`, `duration` (min 5), `resolution: "768P"`, `prompt_expansion_mode: "disabled"` |

**H3 Max invents things, and driving it is part of the job.** In the reference run it produced, in
separate takes: lettering on a pendant it added to the chain, numbered gauges on a blank dashboard,
storefront signage reading "Crolate", Japanese shop signs, an anime woman who was not in the still,
and a face morph on a slow push-in. None of that is a reason to reach for another model; it is the
budget line you plan for. Four things keep it in hand:

1. **Carry the full negative list in every motion prompt**, not just the still prompt: `no text, no
   signage, no letters, no numbers, no logos, no people in the background`.
2. **Name the prop you do not want.** "Plain chain, no pendant" fixed the invented pendant. H3
   embellishes whatever it finds ambiguous, so close the ambiguity by name.
3. **Wide street plates and slow push-ins are its two weak shots.** Budget two takes for each,
   and prefer a tighter frame or a held camera over a wide one where the composition allows.
4. **Review every clip, then re-roll.** Re-rolls at $0.04 to $0.08 per second are cheap enough that
   the answer to a bad take is always another take.

**Rejected, with the reason, so nobody re-runs the bake-off:**

| Model | Why not |
|---|---|
| Kling Avatar v2 Pro | burned garbled subtitles into the frame, plus a chest logo |
| Kling LipSync | strong mouth, but inherits every artifact of the clip underneath |
| Sync Lipsync v2 Pro | works, $5/min — keep as the **cheap way to re-sync a clip you already rendered**, not as the primary |
| LTX-2.3 | drifts the face |
| InfiniteTalk | did not return inside 10 minutes |

### 6. Composite, render, mux

Clone `content/letal-xlug/video/`, place the clips on the song map by word time, **mute every clip
except the lip-sync sources**, and type any wordmark as HTML text.

- `npx hyperframes@0.7.5 snapshot --at <times> .` at ~6 points before you ever run `npm run render`.
  Pin the version.
- **Never cut a clip within ~0.15s of its file end.** The reference's first render had a black frame
  at 4.6s because the cut sat two frames from the end of a 4.68s file, where the decoder returns
  black. Fix is 0.18s of headroom; verify by sampling frame brightness across the cut, not by eye.
- **The headless renderer ignores CSS `filter: invert` on JPEGs.** A wordmark image rendered as a
  white box. Type the wordmark.
- Nano Banana 2 will turn "two shots of him" into a **split grid** if you let it. Prompt one
  continuous frame.
- Mux the song at measured linear gain, then read frames back out of the finished render. A render
  returning the right duration is not evidence it looks right.

## Cost — budget the bake-offs, they are not optional

Measured on the reference (27.0s finished, from a 112s scene table):

| Item | Spend |
|---|---|
| Nano Banana 2 stills, 19 + ~6 re-rolls | ~$2.00 |
| Bake-off 1 — motion, 3 models on one shot | ~$1.10 *(wasted: wrong question, see Gate 3)* |
| Bake-off 2 — lip-sync, 5 models on one shot against real audio | ~$3.00 |
| Bake-off 3 — silent face, 4 models on one shot | ~$2.20 |
| Final motion, 19 shots | ~$9.50 |
| Re-rolls after review | remainder |
| **Session total** | **≈ $30** |

**Two of those three bake-offs no longer run.** Bake-off 1 asked the wrong question (Gate 3) and
bake-off 3 chose a silent-face model that the 08-31 ruling has since settled — H3 Max takes those
shots. What a new film actually pays for is stills, motion and re-rolls, so a first film in a new
visual world should now come in **well under the ~$30 the reference cost**, and a second film in the
same world nearer **$8 to $10**.

Estimating a fresh film from the two-model split: ~16 non-mouth shots at ~5.5s is ~88s of H3 Max
(**~$3.50 at the promo rate, ~$7 after**), plus ~16s of OmniHuman at $0.16/s (**~$2.60**), plus ~$2
of stills. The $0.04/s H3 rate is a launch promo running to 2026-09-01. Treat all of it as the
shape of the budget, not a quote — re-check both prices on fal before
committing, and pull real spend from the api project's production `FAL_KEY` account, not a local
key.

## Publish

1. **The artist posts first**, on their channels, in their language, with their own caption.
2. **IG Collab invite** to `@recoupableai` / sweetman, so it lives on both profiles. This is the
   whole distribution plan — see "Why we make these" above.
3. Then our four-platform cut via `recoup-internal-social-ship-posts`:
   `utm_campaign=<artist-slug>`, tagged link in the **YouTube description only**, LinkedIn gets an
   **image** not the video, and the X body carries no link.
4. Log it in `posts-log.md` with the arc, the character, both halves of the why, and the sign-off
   used. Instagram cannot carry a per-post link, so record it as **unattributable** rather than as a
   zero.

## Open items from the reference run

- The master WAV never arrived; the shipped cut uses a YouTube Topic rip. If it lands, re-mux and
  consider re-uploading YouTube only.
- The artist's other two versions of the track have no video, and 19 usable clips for one of them
  already exist in `content/letal-xlug/clips/`.
- `embeddable` cannot be set through the YouTube connector — it is a manual Studio flip.
