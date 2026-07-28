---
name: recoup-internal-marketing
description: 'INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke ONLY when the request explicitly includes "recoup-internal" (e.g. "recoup-internal do today''s marketing"). Never use for customer-facing or artist requests. The daily marketing run for one of our own social accounts, in order: read the account workspace (narrative canon, hook doctrine, video styles, post ledger), scrape the account''s own socials to learn what is working and what flopped, pick today''s topic (continue an arc, pull a logged idea, or draft a new one), then build the asset and hand off. Use when the user says "do today''s marketing", "what should we post today", "make today''s video", "our hooks are weak", or names a day''s content run. Orchestrates: routes video production to the format skills and publish/measure to recoup-internal-social-ship-posts.'
---

# Recoup Internal — Marketing (the daily run)

The loop for a day of marketing on one of **our own** accounts. This skill is the **orchestrator**:
it owns deciding *what* to make and proving it is grounded in evidence. It delegates production to
the video-format skills and publishing to `recoup-internal-social-ship-posts`.

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
- **AI disclosure.** Always, on generated visuals. This is a performance decision, not a legal one:
  disclosed variants have been our platform-bests and the undisclosed one flatlined.
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

## Step 5 — Hand off

- **Publish + measure:** `recoup-internal-social-ship-posts`. That skill owns copy per platform, the
  CTA decision, the connector mechanics, and the ~48h re-pull.
- **Log it:** one row per post in `posts-log.md`, including the **arc and character** it served and
  which sign-off line was used. An unlogged arc breaks the serial.
- **Capture what you learned:** if the run produced a durable lesson (a new gotcha, a style that
  worked, a hook that landed), write it into the workspace doc that owns it — `HOOKS.md`,
  `VIDEO-STYLES.md`, or `NARRATIVE.md` — not just into the chat.

## Guardrails

- **Nothing publishes without explicit owner go-ahead.** "My goal is to post X" is a draft
  instruction, not authorization. Build it, then ask.
- **Never re-trigger a live customer's task to test a change.** Every run emails the customer. Use a
  test account.
- **Real numbers or nothing**, including about ourselves. If a cost or result cannot be verified
  today, publish the counts you can audit and leave the rest blank.
- **Our own accounts only.** Customer-facing or artist-facing content goes through the
  `recoup-content-*` skills, which are credit-metered and analyze-gated.

## References

- `references/learn-from-socials.md` — the scrape, per-platform metric shapes, and reading gotchas
- `references/topic-selection.md` — choosing the day's beat, and the gates it must clear
- `references/video-formats.md` — format routing table and handoffs
