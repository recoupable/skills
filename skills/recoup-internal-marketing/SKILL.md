---
name: recoup-internal-marketing
description: 'INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke ONLY when the request explicitly includes "recoup-internal" (e.g. "recoup-internal do today''s marketing"). Never use for customer-facing or artist requests. The daily marketing run for one of our own social accounts, in order: read the account workspace (narrative canon, hook doctrine, video styles, post ledger), scrape the account''s own socials to learn what is working and what flopped, pick today''s topic (continue an arc, pull a logged idea, or draft a new one), then build the asset and hand off. Use when the user says "do today''s marketing", "today''s content run", "make today''s video", "our hooks are weak", or asks what to post today for one of OUR OWN accounts. Runs the whole day end to end. Its stated goal: convert a free content viewer into a paying Recoup subscriber — and know which post did it; so the run opens on the funnel numbers and refuses to ship into a destination that cannot convert. **Not for a single post''s copy** — drafting/publishing/measuring one LinkedIn or X post is recoup-internal-social-ship-posts, which this skill calls at step 5. Orchestrates: routes video production to the format skills and publish/measure to recoup-internal-social-ship-posts.'
---

# Recoup Internal — Marketing (the daily run)

The loop for a day of marketing on one of **our own** accounts. This skill is the **orchestrator**:
it owns deciding *what* to make and proving it is grounded in evidence. It delegates production to
the video-format skills and publishing to `recoup-internal-social-ship-posts`.

## The goal — read this before anything else

> **Convert a free content viewer into a paying Recoup subscriber — and know which post did it.**

That sentence is the job; any step that stops serving it should be changed rather than performed.
Likes, views and followers are leading indicators, not the result. The destination is the other half
of every conversion; you own the path from first frame to subscription. If the result cannot be
measured, say so in writing, every run. You are allowed to not post: when the bottleneck is
downstream, saying so is the day's highest-value marketing act. Steps 2a and 5 exist because on
2026-07-30 a full day of craft shipped into a page with zero trials in eight weeks
(`references/conversion.md`). **Do the steps in order.**

## Step 0 — Identify the account

Read `ACCOUNT.md` in the account workspace for the `artist_account_id` and the connected socials
(they live on the **artist account**, not the token's default identity). The personal **sweetman**
and the **Recoup official** accounts have their own IDs; confirm which one today's post is for.

## Step 1 — Read the workspace (never skim)

| Order | File | What you are extracting |
|---|---|---|
| 1 | `README.md` | The workspace map and the daily loop. Start here. |
| 2 | `NARRATIVE.md` | **Story canon.** Premise, recurring cast, live storylines, serialization rules. |
| 3 | `HOOKS.md` | **Hook and retention doctrine** + the pre-render checklist, including the audit of on-screen numbers. |
| 4 | `VIDEO-STYLES.md` | The style catalog, each pointing at a cloneable reference project. |
| 5 | `posts-log.md` (tail) | What has already shipped, with performance and the arc each post served. |
| 6 | `POSTING-PLAYBOOK.md`, `LINKEDIN.md` | Per-platform mechanics and gotchas. Read before publishing, not after. |
| 7 | `cast/<character>/` | Face guide and **canonical voice** for any recurring character you plan to use. |

Also read `references/video-pipeline.md` and `references/voice.md` before generating audio.
**Output of this step:** name the **arc** and the **character** today's post serves. A post that
serves no arc is an ad. No `NARRATIVE.md` in the workspace: say so rather than inventing a story.

## Step 2a — Read the funnel BEFORE the feed

**Open every run with one number: trials/subscriptions started since the last run.** Pull it from
`recoup-internal-sales` / `recoup-internal-funnel-valuation-pipeline` (Privy signups, Stripe trials
and cards, credits, Attio stage), not from the social scrape, which cannot see it. Then state, in one
line each:

- **trials/subscriptions since the last run**;
- **whether the destination for today's likely CTA converts at all** (gate in step 5);
- **whether conversion is readable**: visit capture is live (verified 2026-08-18; Vercel Web Analytics
  records `utm_*` on both properties). Run `references/conversion.md` → *The attributed-visits pull*.
  The visit→**signup** join stays unreadable (chat#1889 row 29); declare that gap in writing.

If trials have been flat at zero across several runs, **that is the finding**, and it outranks
today's post. See the funnel guardrail below.

## Step 2 — Scrape the account's own socials

**Do not skip this and do not substitute the posts-log for it.** The log is what we *thought*
happened at the last re-pull; the scrape is what is true now (2026-07-28: a full video was built off
the log alone, and the weak recent hooks a scrape would have shown surfaced only afterwards).
Scrape and poll per `references/learn-from-socials.md` → *The scrape*.

Then **rank recent posts by engagement and name the differences** between the top performer and the
flatliners: hook type, format, collaborator tagged, AI disclosed, length, posting slot. Those
differences are today's brief. **Report deltas, not all-time totals.** A platform whose numbers have
structurally collapsed outranks today's post (see guardrails).

## Step 3 — Pick today's topic

Three legitimate sources, in preference order:

1. **Continue a live arc.** Best default; the canon asks recurring segments to end on a cliffhanger.
2. **Pull a logged content idea** from the workspace or `NARRATIVE.md`'s upcoming canon dates.
3. **Draft a new idea** that advances an arc *and* is worth adding to the canon. A new storyline
   needs its own arc-proposal doc and an owner ruling before it is canon.

**Gate zero, before every other gate: name the KIND of piece** (launch, incident, or report) from the
source, not from what scored last week. Our strongest register is confession, so a shipped feature
gets pulled toward a story about our own mistake; that cost a full rebuild on 2026-08-12. Structures
and the beat-budget test: `references/topic-selection.md` → *Gate zero*.

Gate the pick on all of these before building (details in `references/topic-selection.md`):

- **Why named, theirs first, then ours.** One sentence on what the person in the piece gets, one on
  what we get, both at the top of the plan doc. **If you cannot write the first sentence, do not
  build the piece.** Where it publishes an artist's real numbers, state the risk to them in the same
  breath, then let them decide. Ours is allowed to be commercial; say so plainly.
- **Arc + character named.**
- **Destination named.** Say where a convinced viewer goes *before* you build. If the honest answer
  is "the homepage," this is a trust/awareness beat, not a conversion one; both are legitimate,
  conflating them is not.
- **Collaborator named, or explicitly none.** Featuring the artist as a **collaborator** and inviting
  them to co-post is the largest measured lever we have: the 2026-07-22 collab reel took **45 likes
  against 1–3** for every non-collab reel after it. "None" is allowed and costs reach.
- **Numbers.** Any figure attributed to a real artist must be measured and verified; never publish a
  number you cannot audit, including about ourselves. Measured-vs-estimated disclosure is **one
  later beat, never part of the opening figure** (`references/hooks.md` → *One flat figure*).
- **NO AI disclosure in body copy.** Owner ruling 2026-07-28: never spend caption, tweet,
  description or on-screen text saying the visuals are AI generated; use the platform's own
  **AI-content toggle at upload** where labelling is wanted. This **reverses** the 2026-07-06 A/B
  guidance; if an older workspace doc still says "always disclose", this ruling wins.
- **One idea per day.** Do not ship two competing assets into the same slot.

## Step 4 — Build the asset

**Route the format first** (`references/video-formats.md`): pick a style from `VIDEO-STYLES.md`
and clone its reference project's `video/` dir; never start from scratch. Spoken-word ad / talking
character: a lip-synced clip from a generated still, see `references/video-pipeline.md` → *Lip-synced
VO over a still*. Artist music video is the separate `recoup-music-video` skill.

**Build in this order, for EVERY video.** Each stage is approved before the next begins, because
each one seeds the next and a mistake compounds.

1. **Concept lock.** One reviewed paragraph: premise, character, structure. Not changed once
   generation starts (09-02: the concept moved three times mid-build and orphaned a complete
   21-still pass; "$2.85 for garbage"). An imprecise vision is not fixable downstream.
2. **Plan doc `SCRIPT.md`.** Why theirs then ours (risk to a real person stated alongside), arc,
   character, destination, collaborator, and the hook archetype named (specific number, contrarian
   claim, list tease; if you cannot name one, rewrite it). Never open by qualifying the audience.
   **Cold-feed premise test:** the video states its premise in its first beats, VO or on-screen,
   because a cut that relies on the caption has no story for most viewers (`references/hooks.md`).
   Name the final act before the hook: every number in the last three beats belongs to something the
   film already introduced; for a shipped feature that is the contract and a runnable CTA, not a
   benchmark (`references/video-formats.md` → *The third act*). A multi-item piece gets its
   scaffolding here (`references/structure.md`). Reviewed **before** a credit is spent.
3. **Hook line generated and MEASURED from audio** (08-11): the spoken hook lands in 3s read from the
   generated audio's duration, not estimated from the word count (`references/hooks.md`).
4. **Voice chosen by checking the MODEL first** (`references/voice.md`); most "robotic VO" is a stale
   `model_id` in a cloned script (08-06). Bake off on the film's lines at equal loudness, record the
   winner; a recurring character keeps its canonical voice in `cast/<character>/`. Then **audio
   approved before compositing**: one concatenated review file, owner listens (08-07: this caught a
   mechanical voice before the timeline existed; a voice change later is a timeline rebuild).
5. **Character sheets.**
6. **Location plates**, only when two or more shots share one.
7. **Stills**, then the **contact-sheet gate**.
8. **Motion.**
9. **Composite.** Read the plan doc's Screen column back against the composition row by row (08-12).
10. **Snapshot** with `npx hyperframes@0.7.5 snapshot --at <times> .` (pin the version; ~15s) before
    any render. One run burned **seven full renders** on findings visible in a still.
11. **Render**, in the background.
12. **Frames read out of the MP4 at caption times.** The right duration is not evidence it looks
    right, and `inspect` samples fixed points so it misses collisions between them.

Two audits ride along. **Audit the SCREEN, not only the script:** run the second half of the
`references/hooks.md` checklist over every panel; it scopes to **claims and measurements** (a `1/5`
counter, ordinals, dates, prices shown as UI and cited standards are exempt): each figure in the VO,
with its unit, from a customer rather than a test harness? A run that audited the script twice and
the panels never shipped a lab number to camera. **Measure audio, do not blindly normalize:** prefer
linear gain, reserve dynamic normalization for genuinely quiet sources.

## Step 5 — Publish

**Run the executable pre-flight first; it exits non-zero, so do not publish past it.** Then publish,
then verify the published text against the config with a **strict equality check**, not by eye
(2026-08-12 empty-tweet-to-the-wrong-account; 2026-07-28 literal `<YT link>` placeholder caught).
`references/publish-verify.md` → *Gate zero* and the per-platform traps.

**Load the destination before you publish.** Open the CTA URL today: 200 *and* what loads pays off
the post's promise (2026-07-30: every CTA in a four-platform slate resolved fine and pointed at a
homepage with zero trials in eight weeks). Declare at publish time: visits readable by
`utm_campaign`; signup join unreadable (row 29). Write it into `posts-log.md` then, not at the re-pull.

**The CTA is a direct tagged link, never a comment-gate:** tried twice, zero leads both times. Tag
per `references/conversion.md`.

**LinkedIn gets an IMAGE, not video, because images outperform video there** (owner ruling
2026-07-28, from personal-post data). A performance decision, not a connector workaround, so do not
hand-upload a video "for consistency" either. The image depicts what the copy's opening line describes.

- **Publish + measure:** `recoup-internal-social-ship-posts` owns per-platform copy, the connector
  mechanics, and the ~48h re-pull.
- **Log it:** one row per post in `posts-log.md` with the **arc and character**, **the why** (theirs
  and ours, as in the plan doc), and the sign-off line used.
- **Capture what you learned** in the workspace doc that owns it (`HOOKS.md`, `VIDEO-STYLES.md`,
  `NARRATIVE.md`), not just the chat.

## Step 6 — Did it convert?

**A post's job is to move a passive viewer to a signup.**

1. **Every CTA link is tagged** at publish time. Convention, capture chain and per-platform caveats
   (Instagram cannot carry a per-post link in the caption): `references/conversion.md`. Signup join
   tracked as row 29 of [chat#1889](https://github.com/recoupable/chat/issues/1889).
2. **At the ~48h re-pull, read conversions alongside engagement**: attributed visits, then signups
   via `recoup-internal-sales` / `recoup-internal-funnel-valuation-pipeline`.
3. **Log both** in `posts-log.md`, even when the answer is zero. A written zero is a finding.
4. **Feed it back into step 2.** Next run ranks by what converted; where likes disagree, conversion wins.

## Guardrails

- **No em dashes in published copy** (captions, tweets, titles, descriptions, first comments,
  on-screen text; internal docs exempt). Rewrite the sentence rather than substituting a comma.
- **No third-party provider or model names on anything published** (owner ruling 09-04): no fal,
  MiniMax, Seedance, ElevenLabs, Grok, OmniHuman on cards, captions, descriptions or on-screen text;
  describe by function; label costs "as billed" or "at list price".
- **No why, no build.** Permission is not a reason: "they consented" answers whether we *may*, never
  whether we *should*.
- **Nothing publishes without explicit owner go-ahead.** "My goal is to post X" is a draft
  instruction, not authorization. Build it, then ask.
- **Never re-trigger a live customer's task to test a change.** Every run emails the customer.
- **Real numbers or nothing**, including about ourselves; publish the counts you can audit.
- **Our own accounts only.** Customer- or artist-facing content goes through `recoup-content-*`.
- **A structural distribution collapse STOPS the run.** If step 2 shows a platform down an order of
  magnitude, report it and get a decision before building for it; diagnose against a like-for-like
  baseline and check tagged clicks before writing a platform off (`learn-from-socials.md`); yt has
  sent the most tagged visitors from the lowest view counts. (07-28: flagged twice, built past twice.)
- **A BROKEN FUNNEL STOPS THE RUN**, one layer down. A dead destination burns *first-time* visitors
  and hides behind healthy engagement (2026-07-30: `/pricing` was the #2 marketing page with zero
  trials since 06-06, and a full slate shipped into it). **Fix the path, do not post.**
- **A build that yields two assets queues the second one** as tomorrow's episode in `posts-log.md`
  or `NARRATIVE.md`.

## References

- `references/learn-from-socials.md` — the scrape, per-platform metric shapes, reading gotchas, the like-for-like baseline
- `references/topic-selection.md` — choosing the day's beat, and the gates it must clear
- `references/video-formats.md` — format routing table and the third act of a shipped-feature film
- `references/hooks.md` — hook archetypes, retention constraints, the pre-render checklist
- `references/conversion.md` — tagged CTA links, the capture chain, the attributed-visits pull
- `references/publish-verify.md` — the pre-publish gate, post-publish verification, platform traps
- `references/video-pipeline.md` — the shared build recipe: scaffold, rebuilt UI panels, captions, lip-synced VO over a still, render, frame QC
- `references/voice.md` — model vs voice vs delivery, the bake-off, audio tags, loudness
- `references/seedance.md` — Seedance 2.5 generated plates: constraints, the fal call, prompt doctrine, run log
- `references/seedance-examples.md` — every Seedance 2.5 example prompt we have, verbatim and sourced
- `references/structure.md` — holding a multi-item piece together after the hook
- `references/character-swap-edit.md` — recreating a trend by swapping the cast of a real performance clip (reAPI Seedance 2.5 edit): casting limits, the 3-reference rule, hosting, QC; script `scripts/reapi-edit.sh`
- **artist music video** lives in the separate `recoup-music-video` skill. Route there; do not rebuild the pipeline here.
