---
name: recoup-internal-marketing
description: 'INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke ONLY when the request explicitly includes "recoup-internal" (e.g. "recoup-internal do today''s marketing"). Never use for customer-facing or artist requests. The daily marketing run for one of our own social accounts, in order: read the account workspace (narrative canon, hook doctrine, video styles, post ledger), scrape the account''s own socials to learn what is working and what flopped, pick today''s topic (continue an arc, pull a logged idea, or draft a new one), then build the asset and hand off. Use when the user says "do today''s marketing", "today''s content run", "make today''s video", "our hooks are weak", or asks what to post today for one of OUR OWN accounts. Runs the whole day end to end. **Not for a single post''s copy** — drafting/publishing/measuring one LinkedIn or X post is recoup-internal-social-ship-posts, which this skill calls at step 5. Orchestrates: routes video production to the format skills and publish/measure to recoup-internal-social-ship-posts.'
---

# Recoup Internal — Marketing (the daily run)

The loop for a day of marketing on one of **our own** accounts. This skill is the **orchestrator**:
it owns deciding *what* to make and proving it is grounded in evidence. It delegates production to
the video-format skills and publishing to `recoup-internal-social-ship-posts`.

> **The goal is signups, not engagement.** Engagement is the leading indicator; a signup at
> `recoupable.dev` is the result. Every post carries a **tagged CTA link** so a visit can be
> attributed back to the post that caused it, and **step 6 closes the loop by reading conversions,
> not just likes.** A run that produced a well-liked post and zero attributable visits did not
> succeed — it just felt like it did.

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
| 3 | `HOOKS.md` | **Hook and retention doctrine** + the pre-render checklist. |
| 4 | `VIDEO-STYLES.md` | The style catalog, each pointing at a cloneable reference project. |
| 5 | `posts-log.md` (tail) | What has already shipped, with performance and the arc each post served. |
| 6 | `POSTING-PLAYBOOK.md`, `LINKEDIN.md` | Per-platform mechanics and gotchas. Read before publishing, not after. |
| 7 | `cast/<character>/` | Face guide + **consent status** for any recurring character you plan to use. |

Also read the production pipeline doc (`HEYGEN-HOWTO.md` or equivalent) before generating audio.

**Output of this step:** name the **arc** and the **character** today's post serves. A post that
serves no arc is an ad; reframe it or drop it. If the workspace has no `NARRATIVE.md`, say so to the
account owner rather than inventing a story.

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

Gate the pick on all of these before building — details in `references/topic-selection.md`:

- **Arc + character named.**
- **Consent.** Internal roster artists need no per-piece permission. External artists need explicit
  likeness consent, and their real numbers are a *separate* gate. Check `cast/<character>/`.
- **Numbers.** Any figure attributed to a real artist must be measured and verified, with
  measured-vs-estimated disclosed. Never publish a number you cannot audit, including numbers about
  ourselves.
- **NO AI disclosure in body copy.** Owner ruling, 2026-07-28: never spend caption, tweet,
  description or on-screen text saying the visuals are AI generated. It is already obvious to the
  audience, and the characters are worth more spent on substance. Where platform-policy labelling is
  wanted, use the platform's own **AI-content toggle at upload**. This **reverses** the earlier
  2026-07-06 A/B guidance; if an older workspace doc still says "always disclose", this ruling wins.
- **One idea per day.** Do not ship two competing assets into the same slot.

## Step 4 — Build the asset

1. **Clear the `HOOKS.md` checklist before writing the scene table.** Hook first, not last. Name
   which archetype the hook is (specific number, contrarian claim, list tease); if you cannot name
   one, rewrite it. Never open by qualifying the audience.
2. **Pick a style from `VIDEO-STYLES.md` and clone its reference project's `video/` dir.** Do not
   start from scratch. Route to the matching format skill where one exists (see
   `references/video-formats.md`); a format with no skill yet is built from its reference project.
3. **Write the plan doc first** (`SCRIPT.md` / `scene-plan.md`) with the arc named at the top, and
   get it reviewed **before** spending generation credits.
4. **QC at every gate.** Verify generated stills for likeness and prop continuity; verify clips
   first/mid/last frame before compositing; lint and inspect the composition; then **read frames out
   of the finished render** — a render returning the right duration is not evidence it looks right.
5. **Measure audio, do not blindly normalize.** House rule: measure first, prefer linear gain, and
   reserve dynamic normalization for genuinely quiet sources.

## Step 5 — Publish

**Run the pre-publish gate first, then publish, then verify.** Full checklists and the per-platform
traps: `references/publish-verify.md`. The gate is short and it has already caught a live defect
(a literal `<YT link>` placeholder about to ship inside a YouTube description, 2026-07-28).

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
- **Log it:** one row per post in `posts-log.md`, including the **arc and character** it served and
  which sign-off line was used. An unlogged arc breaks the serial.
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
- **A build that yields two assets queues the second one.** Do not orphan it. Name it as tomorrow's
  episode in `posts-log.md` or `NARRATIVE.md` so the next run finds it instead of starting cold.

## References

- `references/learn-from-socials.md` — the scrape, per-platform metric shapes, and reading gotchas
- `references/topic-selection.md` — choosing the day's beat, and the gates it must clear
- `references/video-formats.md` — format routing table and handoffs
- `references/hooks.md` — hook archetypes, retention constraints, the pre-render checklist
- `references/conversion.md` — tagged CTA links, the capture chain, per-platform caveats
- `references/publish-verify.md` — the pre-publish gate, post-publish verification, platform traps
