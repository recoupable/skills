# Step 4 — Format routing and handoffs

The account workspace's `VIDEO-STYLES.md` is the source of truth for what each style is and which
project to clone. This page is the **routing table** from a brief to a format, plus the handoffs.

## Route by the JOB, not by what looks impressive

| The job | Format | Skill / source |
|---|---|---|
| A single number or a weekly result is the hero | **Data-in-motion** (stat cards, count-ups) | Clone the style's reference project |
| Announce a **shipped feature** where seeing the real UI is the point | **3D product reveal** | Clone the reference project. Validated winner for feature announcements |
| Brand film, manifesto, hype piece where the *feeling* is the point | **Kinetic keynote** | Clone the reference project. **Not** for feature explainers |
| Entertainment: emotional live-action carrying a **value**, not a feature | **Cinematic narrative** (face guide → stills → i2v → composite) | Clone the reference project; character kit from `cast/` |
| A two-person conversation / talking-head ad with real dialogue | **FaceTime call** | `recoup-internal-video-grok-1.5-imagine-facetime` |
| Explain a **method** — how something was made, how a number was derived | **Recipe / BTS artifact walk** | Clone the reference project |
| Captions or graphic overlays onto existing footage | hyperframes caption / overlay workflows | `embedded-captions`, `talking-head-recut` |

**The concrete-versus-stylish rule:** for a feature or product announcement, concreteness beats
styling. Show the real interface and the real change. A beautiful abstract treatment that hides the
product reads as generic and does not convert. Tested head-to-head and ruled on by the owner.

**LinkedIn is an image post, not video — on performance grounds.** Owner ruling 2026-07-28 from
personal-post data: images outperform video on LinkedIn. This is **not** a workaround for the
connector lacking native video upload, and the distinction matters — it means do not hand-upload a
video to LinkedIn "for consistency" with the other platforms either. Pick the still that depicts what
the copy's opening line describes, size it 1080x1350 (4:5), and put the link in the first comment.

**Future work:** each format above should get its own skill or reference, the way the FaceTime format
already has one. Until then, the reference project *is* the spec — clone it, never rebuild from
scratch.

## Non-negotiables before rendering

1. **Clear the `HOOKS.md` checklist.** Hook first, before the scene table exists. Name the archetype.
2. **Plan doc before credits.** `SCRIPT.md` / `scene-plan.md` with the arc at the top, reviewed before
   any paid generation.
3. **QC gates.** Stills for likeness and prop continuity → clips first/mid/last frame → lint,
   validate, inspect → **read frames from the finished render.** A render with the right duration is
   not evidence it looks right.
4. **Deterministic renders.** No wall-clock or randomness in a composition; it breaks reproducibility.
5. **Measure audio before normalizing.** Prefer linear gain; reserve dynamic normalization for
   genuinely quiet sources. Never let a music model own the dynamics — keep beds flat and author the
   arc as an explicit envelope so a lift lands on the exact cut.

## Production gotchas worth knowing before you hit them

- **`data-track-index` does not set z-index — DOM order does.** Persistent chrome (wordmark, counters)
  declared before full-bleed video clips gets painted over. Put chrome **last** in the DOM.
- **Never animate `innerText` for a text swap.** GSAP interpolates numbers inside it, so setting
  `innerText: "step 1 / 5"` can render a literal `step 0 / 0`. Use one timed clip per label.
- **Chrome over footage needs its own shadow**, or it vanishes into a bright frame.
- **Obey the contrast gate.** Muted greys that pass on a monitor fail on a phone. Residual warnings
  from scenes that overlap spatially but never appear simultaneously are false positives — the
  time-aware layout inspection is the one to trust.
- **The mixdown can attenuate voice** even at full clip volume. Verify levels on the render, not the
  source files.
- **Render heavy compositions in the background.** Foreground timeouts kill long renders.

## Handoffs

| Next | Skill |
|---|---|
| Publish, per-platform copy, ~48h re-pull | `recoup-internal-social-ship-posts` |
| Signup / funnel reads at the re-pull | `recoup-internal-sales`, `recoup-internal-funnel-valuation-pipeline` |
| Composition mechanics, timing contract, rendering | the `hyperframes*` skills |
| Media resolution (music, SFX, voice, images) | `media-use` |

Customer-facing or artist-facing assets do **not** go through this skill — they go through the
`recoup-content-*` skills, which are credit-metered, cost-confirmed, and analyze-gated.
