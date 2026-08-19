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

That sentence is the job. Everything below serves it, and any step that stops serving it should be
changed rather than performed.

What follows from it, in order of how often it gets forgotten:

1. **Likes, views and followers are leading indicators, not the result.** A run that produced a
   well-liked post and zero attributable signups did not succeed — it just felt like it did.
2. **A post is one half of a conversion; the destination is the other.** A brilliant asset pointed
   at a page that cannot convert is a wasted asset *and* a burned first-time visitor. You own the
   whole path from the first frame to the subscription, not just the frame.
3. **If the result cannot be measured, say so out loud** — every run, in writing. An unmeasured
   conversion is not a zero, and reporting engagement in its place is how a broken funnel stays
   invisible for weeks.
4. **You are allowed to not post.** If the evidence says the bottleneck is downstream — a dead
   destination, a broken signup path — the highest-value marketing act that day is to say so and get
   it fixed. Shipping a post into a funnel that converts nobody is activity, not progress.

**Why this is written so bluntly:** on 2026-07-30 a full day went into craft for a four-platform
slate while the page it pointed at had produced zero trials in eight weeks, and nothing in this skill
would have surfaced that. Steps 2a and 5 now do. Full account: `references/conversion.md`.

**Do the steps in order.** Each one exists because skipping it has cost us something specific, noted
inline. Step 2 is the one most often skipped and the most expensive to skip.

## Step 0 — Identify the account

Read `ACCOUNT.md` in the account workspace for the `artist_account_id` and the connected socials.
Connections live on the **artist account**, not the token's default identity.

Our accounts are distinct and must not be mixed: the personal **sweetman** account and the
**Recoup official** accounts each have their own IDs. Confirm which one today's post is for before
writing a word.

## Step 1 — Read the workspace (never skim)

The account workspace holds the durable marketing knowledge. Read in this order:

| Order | File | What you are extracting |
|---|---|---|
| 1 | `README.md` | The workspace map and the daily loop. Start here. |
| 2 | `NARRATIVE.md` | **Story canon.** Premise, recurring cast, live storylines, serialization rules. |
| 3 | `HOOKS.md` | **Hook and retention doctrine** + the pre-render checklist, including the audit of on-screen numbers. |
| 4 | `VIDEO-STYLES.md` | The style catalog, each pointing at a cloneable reference project. |
| 5 | `posts-log.md` (tail) | What has already shipped, with performance and the arc each post served. |
| 6 | `POSTING-PLAYBOOK.md`, `LINKEDIN.md` | Per-platform mechanics and gotchas. Read before publishing, not after. |
| 7 | `cast/<character>/` | Face guide, **canonical voice**, + **consent status** for any recurring character you plan to use. |

Also read `references/video-pipeline.md` (the shared build recipe) and `references/voice.md`
(voice choice, audio tags, loudness) before generating audio.

**Output of this step:** name the **arc** and the **character** today's post serves. A post that
serves no arc is an ad; reframe it or drop it. If the workspace has no `NARRATIVE.md`, say so to the
account owner rather than inventing a story.

## Step 2a — Read the funnel BEFORE the feed

**Open every run with one number: trials/subscriptions started since the last run.** It is the only
number that says whether the marketing is working. Pull it from `recoup-internal-sales` /
`recoup-internal-funnel-valuation-pipeline` (Privy signups, Stripe trials and cards, credits, Attio
stage) — not from the social scrape, which cannot see it.

Then state, in one line each:

- **trials/subscriptions since the last run** — the result;
- **whether the destination for today's likely CTA converts at all** — see the gate in step 5;
- **whether conversion is currently readable** — visit capture IS live (verified 2026-08-18):
  Vercel Web Analytics records `utm_*` on both properties automatically. Run the attributed-visits
  pull in `references/conversion.md` → *The attributed-visits pull* for the per-campaign numbers.
  What stays unreadable is the visit→**signup** join (chat#1889 row 29) — declare that gap in
  writing rather than discovering it at the re-pull.

If trials have been flat at zero across several runs, **that is the finding**, and it outranks
today's post. Say so, and see the funnel guardrail below.

## Step 2 — Scrape the account's own socials

**Do not skip this and do not substitute the posts-log for it.** The log is what we *thought*
happened at the last re-pull; the scrape is what is true now. On 2026-07-28 a full announcement video
was built off the log alone, and the owner then reported that recent hooks had been weak — which a
fresh scrape would have shown before the build, not after.

```bash
# One {runId, datasetId} per linked profile. Costs 5 credits + 1 per requested post, PER PROFILE.
curl -sS -X POST "https://api.recoupable.dev/api/artist/socials/scrape" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" -H "Content-Type: application/json" \
  -d '{"artist_account_id":"<ARTIST_ACCOUNT_ID>","posts":20}'

# Poll each run until SUCCEEDED (~1-3 min), then read `data`
curl -sS "https://api.recoupable.dev/api/apify/runs/<RUN_ID>" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"
```

Then **rank recent posts by engagement and name the differences** between the top performer and the
flatliners: hook type, format, whether a collaborator was tagged, whether AI was disclosed, length,
posting slot. Those differences are today's brief. Details and per-platform metric shapes:
`references/learn-from-socials.md`.

**Report deltas, not all-time totals.** Also flag any platform whose numbers have structurally
collapsed (e.g. Shorts views dropping an order of magnitude) — that is a distribution problem no
amount of asset quality will fix, and it outranks today's post.

## Step 3 — Pick today's topic

Three legitimate sources, in preference order:

1. **Continue a live arc.** Best default. Serialized beats compound and the canon asks recurring
   segments to end on a cliffhanger. Check `NARRATIVE.md` for what is mid-arc and what was teased.
2. **Pull a logged content idea.** Ideas parked in the workspace or in `NARRATIVE.md`'s upcoming
   canon dates (anniversaries, launches, scheduled milestones).
3. **Draft a new idea** that advances an arc *and* is worth adding to the canon. If it needs a new
   storyline, write the arc proposal as its own doc and get an owner ruling before treating it as
   canon.

**Gate zero, before every other gate: name the KIND of piece** — launch, incident, or report — from
the source, not from what scored last week. Our strongest register is confession, so a shipped
feature gets pulled toward being a story about our own mistake. That cost a full rebuild on
2026-08-12. Structures and the beat-budget test: `references/topic-selection.md` → *Gate zero*.

Gate the pick on all of these before building — details in `references/topic-selection.md`:

- **Why named — theirs first, then ours.** One sentence on what the person in the piece gets out of
  it, one on what we get. Both at the top of the plan doc. **If you cannot write the first
  sentence, do not build the piece** — it is an ad wearing someone's name. Where it publishes an
  artist's real numbers, state the risk to them in the same breath as the case, then let them
  decide. Ours is allowed to be commercial; say so plainly rather than dressing it as a favour.
  Arguments that hold up, and the incident that added this gate: `references/topic-selection.md`.
- **Arc + character named.**
- **Destination named.** Say where a convinced viewer goes *before* you build, and make sure it
  continues this post's promise. If the honest answer is "the homepage," the idea is not yet a
  conversion post — either find the page that pays off its promise, or accept and state that this is
  a trust/awareness beat, not a conversion one. Both are legitimate; conflating them is not.
- **Collaborator named, or explicitly none.** Featuring the artist as a **collaborator** and
  inviting them to co-post is the largest measured lever we have: the 2026-07-22 collab reel took
  **45 likes against 1–3** for every non-collab reel in the weeks after. Ask every run: who is the
  collaborator, and have they been invited? "None" is an allowed answer that costs reach.
- **Consent.** Internal roster artists need no per-piece permission. External artists need explicit
  likeness consent, and their real numbers are a *separate* gate. Check `cast/<character>/`.
- **Numbers.** Any figure attributed to a real artist must be measured and verified. Never publish
  a number you cannot audit, including numbers about ourselves. Measured-vs-estimated disclosure is
  **one later beat in the piece, never part of the opening figure** — see `references/hooks.md` →
  *One flat figure*.
- **NO AI disclosure in body copy.** Owner ruling, 2026-07-28: never spend caption, tweet,
  description or on-screen text saying the visuals are AI generated. It is already obvious to the
  audience, and the characters are worth more spent on substance. Where platform-policy labelling is
  wanted, use the platform's own **AI-content toggle at upload**. This **reverses** the earlier
  2026-07-06 A/B guidance; if an older workspace doc still says "always disclose", this ruling wins.
- **One idea per day.** Do not ship two competing assets into the same slot.

## Step 4 — Build the asset

1. **Clear the `HOOKS.md` checklist before writing the scene table.** Hook first, not last. Name
   which archetype the hook is (specific number, contrarian claim, list tease); if you cannot name
   one, rewrite it. Never open by qualifying the audience. **Cold-feed premise test:** the video
   itself must state its premise in its first beats (VO or on-screen text) — feeds autoplay, so a
   cut that relies on the caption for its story has no story for most viewers
   (`references/hooks.md`).
2. **Pick a style from `VIDEO-STYLES.md` and clone its reference project's `video/` dir.** Do not
   start from scratch. Route to the matching format skill where one exists (see
   `references/video-formats.md`); a format with no skill yet is built from its reference project.
3. **Choose the voice deliberately, and check the MODEL before the voice** — `references/voice.md`.
   Most "the VO sounds robotic" problems are a stale `model_id` inherited from a cloned generator
   script, not the voice. A real listener called our narration "mechanical, not human" on 2026-08-06
   and was right: we were on a stock voice driven by a model two generations old. Run a bake-off on
   the film's actual lines, normalise every candidate to the same loudness before listening, and
   record the winner (voice id, model, settings, date). A recurring **character** keeps its canonical
   voice in `cast/<character>/` and prefers a first-person inner voice over a narrator; a **narrator**
   may change whenever the old one is the problem. Verify every audio tag by transcribing the output
   back — an unrecognised tag gets spoken aloud.
4. **Name the final act before the hook.** A film that opens well and ends on an unrelated metric
   loses the viewer at the turn, which is the most expensive place to lose them. Say in one line what
   the last three beats are *about*, and check that every number in them belongs to something the
   film already introduced. For a shipped API or feature that means the contract and a runnable CTA,
   not a benchmark: `references/video-formats.md` → *The third act of a shipped-feature film*.
5. **Write the plan doc first** (`SCRIPT.md` / `scene-plan.md`). It opens with **the why — theirs,
   then ours — above the arc**, both as single sentences, and where a real person's numbers are
   published, the risk to them stated alongside. A plan doc that starts at the scene table has
   skipped the only question the audience cannot see you skip. Get it reviewed **before** spending
   generation credits.
5. **Structure the piece, not just the hook** — `references/structure.md`. A multi-item piece
   (a changelog, a roundup, a list) assembled by writing each item well and running them in order
   reads as a jumble. State the count in the frame line, speak the ordinals, show a `1/5` step
   counter, and bookend with a contents card that ticks off. Put any confession in the frame line
   rather than inside one item.
6. **Get the AUDIO approved before you composite.** A separate gate from the plan doc, and the
   cheapest one in the run. Generate the VO, normalise it, concatenate the lines into one review
   file with short gaps, and have the owner listen. On 2026-08-07 this caught a voice the owner's
   own family had called mechanical — while the timeline did not yet exist. Compositing first would
   have made a rejected read invalidate the whole build, because a voice change moves every beat and
   every caption and is a timeline rebuild, not a file swap.
7. **Climb the QC ladder cheaply. Render is the last rung, not the first.**
   `plan doc → audio approved → stills → render → frames out of the render.`
   Use **`npx hyperframes@0.7.5 snapshot --at <times> .`** (pin the version, same as every
   other invocation; ~15s, writes PNGs and a contact sheet) to look
   at your work; `npm run render` takes minutes. One run burned **seven full renders** on findings
   that were all visible in a still. Then read frames out of the finished render anyway — a render
   returning the right duration is not evidence it looks right, and `inspect` samples fixed points
   so it misses collisions between them.
8. **Audit the SCREEN, not only the script.** Run the second half of the `references/hooks.md`
   checklist over every panel. It scopes to **claims and measurements** — structural notation (a
   `1/5` counter, ordinals), dates, prices shown as UI and cited standards are exempt. For each
   figure presented as evidence: does it appear in the VO, carry its unit, and come from a customer
   rather than a test harness? Could two figures on one panel read as a claim you did not make? A
   run that audited the script twice and the panels never shipped a lab number to camera.
9. **Measure audio, do not blindly normalize.** House rule: measure first, prefer linear gain, and
   reserve dynamic normalization for genuinely quiet sources.

## Step 5 — Publish

**Run the executable pre-flight first; it exits non-zero, so do not publish past it.** A checklist
validates the copy you can read; only the script validates that the runner will read it. Then publish,
then verify the published text against the config with a **strict equality check** rather than by
eye. Both, and the 2026-08-12 empty-tweet-to-the-wrong-account incident behind them:
`references/publish-verify.md` → *Gate zero*. Full checklists and the per-platform
traps: `references/publish-verify.md`. The gate is short and it has already caught a live defect
(a literal `<YT link>` placeholder about to ship inside a YouTube description, 2026-07-28).

**Load the destination before you publish, and declare whether conversion is readable.** Two lines
in the gate, both cheap, both catching failures nothing else catches:

- **Open the CTA URL today.** Confirm it returns 200 *and* that what loads pays off the post's
  promise. A 200 from a page that cannot convert is not a pass — on 2026-07-30 every CTA in a
  four-platform slate resolved fine and pointed at a homepage that had produced zero trials in
  eight weeks.
- **Declare attribution: readable or not.** If `utm_campaign` capture is not live, write
  "conversion unreadable for this slate" into `posts-log.md` **at publish time**, not at the
  re-pull. A tag that nothing records is not measurement, and calling it one hides the gap.

**The CTA is a direct tagged link, not a comment-gate.** Ruling from our own results: comment-gates
were tried twice and produced **zero** gated comments and zero leads both times. `ship-posts` still
describes comment-gating as the lead-gen option — that advice is refuted by our data; do not run the
experiment a third time. Direct link, tagged per `references/conversion.md`.

**LinkedIn gets an IMAGE, not video — because images outperform video there** (owner ruling
2026-07-28, from personal-post data). This is a performance decision, *not* a workaround for the
connector lacking video upload. Consequence: do **not** hand-upload a video to LinkedIn "for
consistency" either. The image must depict what the copy's opening line describes.

- **Publish + measure:** `recoup-internal-social-ship-posts`. That skill owns copy per platform, the
  connector mechanics, and the ~48h re-pull.
- **Log it:** one row per post in `posts-log.md`, including the **arc and character** it served,
  **the why it was built on** (theirs and ours, as written in the plan doc), and which sign-off line
  was used. An unlogged arc breaks the serial; an unlogged why means the next run cannot tell
  whether the reason held up.
- **Capture what you learned:** if the run produced a durable lesson (a new gotcha, a style that
  worked, a hook that landed), write it into the workspace doc that owns it — `HOOKS.md`,
  `VIDEO-STYLES.md`, or `NARRATIVE.md` — not just into the chat.

## Step 6 — Did it convert?

Engagement is not the deliverable. **A post's job is to move a passive viewer to a signup**, and
until this step runs we do not know whether any post ever has.

1. **Every CTA link is tagged** at publish time so the visit is attributable. Convention, capture
   chain and the per-platform caveats (Instagram cannot carry a per-post link in the caption) live in
   `references/conversion.md`. Tracked for implementation as row 29 of
   [chat#1889](https://github.com/recoupable/chat/issues/1889).
2. **At the ~48h re-pull, read conversions alongside engagement.** Attributed visits, then signups.
   `recoup-internal-sales` and `recoup-internal-funnel-valuation-pipeline` own the account-side reads
   (Privy signups, Stripe, credits, Attio stage).
3. **Log both** in `posts-log.md` — engagement *and* what it converted, even when the answer is zero.
   A zero that is written down is a finding; a zero that is never measured is a story we tell
   ourselves.
4. **Feed it back into step 2.** Next run ranks by what converted, not by what got likes. Where the
   two disagree, conversion wins.

**Until attribution ships, say so explicitly** rather than implying a post worked because it got
engagement. As of 2026-07-28 no post on any Recoup account is attributable to a signup: every CTA is
a bare `recoupable.dev` or "link in bio" with no tag.

## Guardrails

- **No em dashes in published copy.** `—` and `–` read as AI-written and cost more credibility than
  the clause is worth. Rewrite the sentence rather than substituting a comma. Applies to captions,
  tweets, titles, descriptions, first comments and on-screen text; internal docs are exempt.
- **No why, no build.** Every piece carries a written why for the person in it, not only for us.
  Permission is not a reason: "they consented" answers whether we *may*, never whether we *should*.
  A piece that cannot say what its subject gets is an ad using their name, however real its numbers.
- **Nothing publishes without explicit owner go-ahead.** "My goal is to post X" is a draft
  instruction, not authorization. Build it, then ask.
- **Never re-trigger a live customer's task to test a change.** Every run emails the customer. Use a
  test account.
- **Real numbers or nothing**, including about ourselves. If a cost or result cannot be verified
  today, publish the counts you can audit and leave the rest blank.
- **Our own accounts only.** Customer-facing or artist-facing content goes through the
  `recoup-content-*` skills, which are credit-metered and analyze-gated.
- **A structural distribution collapse STOPS the run.** If step 2 shows a platform's numbers down an
  order of magnitude, do not build an asset for that platform and hope. Report it and get a decision
  first. Asset quality is not the bottleneck when distribution is broken, and shipping into it wastes
  the asset *and* hides the real problem. (On 2026-07-28 this was flagged twice and built past twice:
  YouTube Shorts had fallen from 129-397 views to 7-10 and the day's post shipped into it anyway.)
- **A BROKEN FUNNEL STOPS THE RUN — same rule as a distribution collapse, one layer down.** If the
  destination is dead-ending or trials have been flat at zero, do not build an asset and hope.
  Report it and get a decision. The failure mode is worse than the distribution one: a broken
  destination burns *first-time* visitors, who do not come back, and it hides behind healthy
  engagement numbers indefinitely. (2026-07-30: `/pricing` was the #2 marketing page with zero
  trials since 06-06, and a funded outreach customer's valuation dead-ended on prod. A full slate
  shipped into it that day.) **The highest-value marketing act on such a day is to fix the path, not
  to post.**
- **A build that yields two assets queues the second one.** Do not orphan it. Name it as tomorrow's
  episode in `posts-log.md` or `NARRATIVE.md` so the next run finds it instead of starting cold.

## References

- `references/learn-from-socials.md` — the scrape, per-platform metric shapes, and reading gotchas
- `references/topic-selection.md` — choosing the day's beat, and the gates it must clear
- `references/video-formats.md` — format routing table and handoffs
- `references/hooks.md` — hook archetypes, retention constraints, the pre-render checklist
- `references/conversion.md` — tagged CTA links, the capture chain, per-platform caveats
- `references/publish-verify.md` — the pre-publish gate, post-publish verification, platform traps
- `references/video-pipeline.md` — the shared build recipe: scaffold, rebuilt UI panels, captions, render, frame QC
- `references/voice.md` — model vs voice vs delivery, the bake-off, audio tags, loudness, the checks before compositing
- `references/seedance.md` — Seedance 2.5 (generated live-action plates): hard constraints, locked-vs-unlocked tasks, the fal call, prompt doctrine, which existing skill owns each downstream step, and the run log we grow
- `references/seedance-examples.md` — every Seedance 2.5 example prompt we have, verbatim and sourced (ByteDance Seed, BytePlus ModelArk, fal, plus our own runs); read it before writing a prompt
- `references/structure.md` — holding a multi-item piece together after the hook: the count, the ordinals, the step counter, the bookend
