# Step 4 — The first three seconds

The hook doctrine: the constraints and archetypes are account-agnostic, only the *evidence* is
account-specific. An account workspace may hold its own `HOOKS.md` with local performance data;
this is the floor that applies everywhere. Read it **before** writing a scene table.

## The constraints

| Fact | Consequence |
|---|---|
| The scroll decision takes **~1.5–1.7s**; a spoken hook must land in **3s** | If the first line needs a second sentence to make sense, it has already failed |
| **The narrator's rate must be measured from generated audio** (`references/voice.md` owns the current default); do not budget words, budget seconds | Generate the hook line and read its duration **before** writing the scene table |
| **60%+ of mobile viewers watch sound-off** | The hook must work as picture and on-screen text alone |
| Captions are worth **~12% more watch time** and **80% higher completion** | Burn in captions on every voiceover line. Not optional |
| **The first frame IS the visual hook.** No intros, no logos, no silence | Our wordmark does not belong at t=0. Brand after the hook lands |
| Peak engagement **21–34s**; process/BTS content tolerates **30–45s** | Cap explainers around 40s; longer needs a reason |
| Process content needs a new visual beat every **5–7s** | No beat in a scene table over ~6.5s |

## The three archetypes that convert

Ranked. Pick one and commit; do not blend.

1. **Specific number.** The highest-converting archetype: a real, odd, checkable figure.
   "Eighteen images, eleven thrown away" beats "a lot of iterations".
2. **Contrarian claim.** Reject a widely-held belief in the first sentence; the viewer stays to
   resolve the contradiction. "No studio, no crew" over a beautiful frame is contrarian.
3. **List tease.** Promise a countable payoff. Pairs with a visible step counter.

## Never open by qualifying the audience

A hook addressed to a niche ("your roster", "if you run a label") makes ~99% of a consumer feed
self-exclude inside the decision window. State a fact specific enough that a stranger stops, and let
the relevant people self-select. (Killed 2026-07-28: *"Your roster posts every day. Your content
budget does not."* — qualified the audience, no number, no contradiction, logo on the first frame.)

## One flat figure

The hook number is **ONE precise figure, stated flat.** No band, no "maybe", no second number, no
"estimated": a hedge in the first seconds reads as not knowing your own number and kills trust
before the premise lands (owner, 2026-08-19: the flat "$662K" cold open was ruled excellent; the
hedged "$454K... maybe $931K" it replaced was killed for "losing all trust"). Ranges, "estimated"
and methodology get **one later beat, once**; the minutiae live on the page it links to. A process
payoff like "eleven of eighteen thrown away" still reads best after the work is shown.

## The cold-feed premise test

**The video itself must state its premise in its first beats — in VO or on-screen text — never by
relying on the caption.** Feeds autoplay; on IG and Shorts the viewer meets the film *before* any
caption, so a cut that only works pre-briefed has no story for most of its audience.

- **Never open a narrated piece on silence.** On a cold autoplay feed silent frames read as
  buffering, not as a pattern interrupt (owner, 2026-08-07: two silent opening frames felt "like a
  glitch"). Put a before/after reveal where the voice explains it, and open on voice.
- **First-person inner voice beats a narrator for story pieces.** A wordless narrative cut failed
  review as "too subtle" on 2026-07-29 because it had delegated its premise to the caption; the fix
  was a sparse character inner monologue (~20–30% speech, front-loaded) stating the premise as the
  hook line. The character stays the protagonist, a narrator turns the film into our ad, and it
  pairs with i2v footage generated without lip movement.
- Adding any VO **obligates burned captions on every line**.

## Checklist before rendering

- [ ] Does the **first frame** stop a stranger with no sound and no context, and carry the
      subject's image? The poster frame IS the thumbnail; a bare number is not recognizable (owner,
      2026-08-19).
- [ ] **No logo and no fade** before ~5s?
- [ ] Spoken hook lands in **3s**, measured from the generated audio and generated **before** the
      scene table? (2026-08-11: a hook written to the word count ran 8.16s; every sentence boundary
      buys a pause, so two clauses, not three.)
- [ ] In the per-word timings (`audio_meta.json`), does the hook's **contradiction** land early? A
      4.0s line whose surprising word arrives at 1.1s beats a 3.0s line that resolves at 2.9s.
- [ ] Which **archetype** is it? (Cannot name one → rewrite.)
- [ ] **Cold-feed premise test:** does the video state its own premise (VO or on-screen) without the caption?
- [ ] **Captions burned in** on every line?
- [ ] Every beat **≤6.5s**? Runtime **≤40s** unless there is a stated reason?
- [ ] Does it avoid **qualifying the audience**?

### Then audit the SCREEN, not just the script

Added 2026-08-07 after a run audited the script twice and the panels never; both number defects
lived in the graphics. **Scope:** claims and measurements, the figures the piece asserts as
evidence. **Exempt:** structural notation (a `1/5` step counter, ordinals), dates, prices and other
product values shown as UI, and external standards being cited (`4.5:1 required`); those are
furniture, not claims.

- [ ] Does **every number presented as evidence** appear in the VO, or get explained by it? A figure
      the narration never earns arrives as noise.
- [ ] Does every measurement carry its **unit**? ("155 accounts sat at zero" — zero what?)
- [ ] Is any on-screen figure a **lab number** rather than a customer number? ("280s of work
      survived" came from a synthetic test harness; it measured the test, not the product.)
- [ ] Could two figures on one panel be read as a **claim you did not make**? ("120s cap" beside
      "280s survived" reads as a raised cap.)
- [ ] Does on-screen text **complement** the caption rather than paraphrase it? Paraphrase counts
      as restating.

## Sources

- [OpusClip, TikTok hooks that go viral 2026](https://www.opus.pro/blog/tiktok-hooks-that-go-viral-2026)
- [OpusClip, ideal Shorts length and format for retention](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention)
- [Terra Market Group, 7 hook formulas for 70%+ retention](https://www.terramarketgroup.com/digital-marketing-2/short-form-video-hooks-7-formulas-for-70-retention/)
- [virvid, the first 3 seconds for faceless Shorts](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026)
- [Kapwing, short-form video statistics 2026](https://www.kapwing.com/resources/short-form-video-statistics-tiktok-reels-and-shorts-by-the-numbers-in-2026/)
