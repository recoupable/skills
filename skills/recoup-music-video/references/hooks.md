# Step 4 — The first three seconds

The hook doctrine, kept in the skill rather than only in an account workspace: the constraints and
archetypes are account-agnostic, only the *evidence* is account-specific. An account workspace may
hold its own `HOOKS.md` with local performance data; this is the floor that applies everywhere.

Read this **before** writing a scene table. A hook is not a line you add at the end.

## The constraints

| Fact | Consequence |
|---|---|
| The scroll decision takes **~1.5–1.7s**; a spoken hook must land in **3s** | If the first line needs a second sentence to make sense, it has already failed |
| **Word budget depends on the narrator, so measure it.** 10–14 words assumes ~200 wpm. Our current narrator (W. L. Oxley, `eleven_v3`, stability 0.0) runs **~130 wpm and inserts ~0.45s between sentences**, so 3s is **about 8 spoken words and at most two clauses** | Generate the hook line and read its duration **before** writing the scene table |
| **60%+ of mobile viewers watch sound-off** | The hook must work as picture and on-screen text alone |
| Captions are worth **~12% more watch time** and **80% higher completion** | Burn in captions on every voiceover line. Not optional |
| **The first frame IS the visual hook.** No intros, no logos, no silence | Our wordmark does not belong at t=0. Brand after the hook lands |
| Peak engagement **21–34s**; process/BTS content tolerates **30–45s** | Cap explainers around 40s; longer needs a reason |
| Process content needs a new visual beat every **5–7s** | No beat in a scene table over ~6.5s |

## The three archetypes that convert

Ranked. Pick one and commit; do not blend.

1. **Specific number.** The highest-converting archetype. A real, odd, checkable figure —
   "eighteen images, eleven thrown away" beats "a lot of iterations".
2. **Contrarian claim.** Reject a widely-held belief in the first sentence; the viewer stays to
   resolve the contradiction. "No studio, no crew" over a beautiful frame is contrarian.
3. **List tease.** Promise a countable payoff. Pairs with a visible step counter.

## The rule that follows

> **Never open by qualifying the audience.**

A hook addressed to a niche ("your roster", "if you run a label") makes ~99% of a consumer feed
self-exclude inside the decision window. State a fact specific enough that a stranger stops, and let
the relevant people self-select on the way through.

Killed on 2026-07-28: *"Your roster posts every day. Your content budget does not."* — it qualified
the audience, carried no number and no contradiction, and its first frame was a grid of dim tiles with
our logo on it.

## One flat figure

The hook number is **ONE precise figure, stated flat.** No band, no "maybe", no second number, no
"estimated" — a hedge in the first seconds reads as not knowing your own number, and it kills trust
before the premise lands (owner, 2026-08-19: the flat "$662K" cold open was ruled excellent; the
hedged "$454K... maybe $931K" it replaced was killed for "losing all trust"). Ranges, "estimated",
and methodology get **one later beat, once** — the copy sells the idea; the minutiae live on the
page it links to. (A process payoff like "eleven of eighteen thrown away" still reads best after
the work is shown.)

## The cold-feed premise test

**The video itself must state its premise in its first beats — in VO or on-screen text — never by
relying on the caption.** Feeds autoplay; on IG and Shorts the viewer meets the film *before* any
caption. A cut whose story only works if the viewer arrived pre-briefed has no story for most of its
audience.

**Never open a narrated piece on silence.** On a cold autoplay feed, silent frames are
indistinguishable from a video that has not loaded, so they read as buffering rather than as a
pattern interrupt. An owner watching a 56s narrated changelog described its two silent opening
frames as feeling "like a glitch rather than a real part of the video" (2026-08-07). **If a piece
contains a before/after worth showing, put it where the voice explains it**, not in front of the
narration: on that rebuild the reveal moved into the beat that describes it and the film opened on
voice at t=0.25s.

Learned 2026-07-29: a wordless narrative cut (built to the "story you'd watch for free" doctrine)
failed owner review as "too subtle — the story gets lost." The wordless design had silently delegated
its premise to the caption. The fix that kept both doctrines: **a sparse character inner-monologue**
(~20–30% speech, front-loaded, silent through the film's held beat) stating the premise as the hook
line. Two corollaries:

- **First-person inner voice beats a narrator for story pieces.** The character stays the
  protagonist; a narrator turns the film into our ad. It also pairs perfectly with i2v footage
  generated with no lip movement — fatal for on-camera dialogue, ideal for thought.
- Adding any VO **obligates burned captions on every line** (the sound-off constraint above).

## Checklist before rendering

- [ ] Does the **first frame** stop a stranger with no sound and no context, and carry the
      subject's image? The poster frame IS the thumbnail; a bare number is not recognizable (owner,
      2026-08-19).
- [ ] **No logo and no fade** before ~5s?
- [ ] Spoken hook lands in **3s**, measured from the generated audio rather than estimated from the word count?
- [ ] Which **archetype** is it? (Cannot name one → rewrite.)
- [ ] **Cold-feed premise test:** does the video state its own premise (VO or on-screen) without the caption?
- [ ] **Captions burned in** on every line?
- [ ] Every beat **≤6.5s**?
- [ ] Runtime **≤40s** unless there is a stated reason?
- [ ] Does it avoid **qualifying the audience**?

### Then audit the SCREEN, not just the script

Added 2026-08-07, after a run that audited the script twice and the panels never. Both of that day's
number defects lived in the graphics: one figure was fixed in the voice and left standing on screen,
and another appeared on a panel having never been in the voice at all.

**Scope:** these apply to **claims and measurements** — figures the piece is asserting as evidence.
**Exempt:** structural notation (a `1/5` step counter, ordinals), dates, prices and other product
values shown as UI, and external standards being cited (`4.5:1 required`). Those are furniture, not
claims, and demanding the voice earn each one would forbid the step counter this skill recommends.

- [ ] Does **every number presented as evidence** appear in the VO, or get explained by it? A figure
      the narration never earns arrives as noise.
- [ ] Does every measurement carry its **unit**? ("155 accounts sat at zero" — zero what?)
- [ ] Is any on-screen figure a **lab number** rather than a customer number? One panel showed
      "280s of work survived", which came from a synthetic test harness (seven scripted 40s sleeps),
      not from anyone's real usage. It measured the test, not the product.
- [ ] Could two figures on one panel be read as a **claim you did not make**? "120s cap" beside
      "280s survived" reads as "we raised the cap from 120 to 280" — the one thing that piece was
      forbidden from implying.
- [ ] Does on-screen text **complement** the caption rather than paraphrase it? Paraphrase counts:
      "The measurement survived." under a caption reading "Deleting keeps the measurement you paid
      for." is the same waste as printing it verbatim.

## Sources

- [OpusClip, TikTok hooks that go viral 2026](https://www.opus.pro/blog/tiktok-hooks-that-go-viral-2026)
- [OpusClip, ideal Shorts length and format for retention](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention)
- [Terra Market Group, 7 hook formulas for 70%+ retention](https://www.terramarketgroup.com/digital-marketing-2/short-form-video-hooks-7-formulas-for-70-retention/)
- [virvid, the first 3 seconds for faceless Shorts](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026)
- [Kapwing, short-form video statistics 2026](https://www.kapwing.com/resources/short-form-video-statistics-tiktok-reels-and-shorts-by-the-numbers-in-2026/)


## Generate the hook line before you write the scene table (2026-08-11)

A hook written to the word count and generated afterwards ran **8.16s against a 3s target**, because
the model adds a dramatic pause at every sentence boundary and three clauses bought three pauses.
The whole scene table had to be retimed after the fact.

**Cheap fix, and it is now the order of operations:** generate the single hook line first, read its
duration and its per-word timings out of `audio_meta.json`, and only then write the table. The
retimed version put "one show" at **1.06s**, inside the scroll decision, on two clauses instead of three.

**What to check in the word timings, not just the total:** the moment the hook's *contradiction*
lands. A 4.0s line whose surprising word arrives at 1.1s beats a 3.0s line that resolves at 2.9s.
