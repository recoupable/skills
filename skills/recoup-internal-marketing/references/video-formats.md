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
| A **scene we could never shoot** carries the beat: a character in a place, a physical action, a location | **Generated plate** (Seedance 2.5), our typography composited over it | `references/seedance.md`. Invented characters are fine; a **real person's photo** cannot be used as a reference |
| A **real artist's released song** is the whole story, cut to 9:16 against their real master | **Artist music video** (ask what they would make with no limits → cast characters → stills → OmniHuman for mouths, H3 Max for everything else → composite to the track) | `references/music-video.md`. Clone `content/letal-xlug/`. No face guide; the artist is on camera only if the film needs them. The artist approves the look, the cut and the credit |

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

## The third act of a shipped-feature film (2026-08-11)

Owner feedback on a cut that worked for 24 seconds and then lost him: *"38 checked, what does that
mean? All the numbers on this scene make me confused based on the previous story."*

The film told a single-artist story (one wrong show, one corrected answer) and then cut to a strip
reading `38 QUERIED · 38 RETURNED · 0 FAILURES · 111 SHOWS`. Every figure was true and measured. It
still failed, because **38 was a population the story had never introduced.** The viewer had one
artist in their head and was handed a roster.

**The rule this produces:**

> **Every number in the final act must attach to a noun the film has already put on screen.**
> A true number about a new subject is a subject change, and a subject change 24 seconds into a
> 40-second film reads as a different video.

**What the third act should be instead, for a shipped API or feature:** the contract, not the
benchmark. Three beats that a viewer can act on:

1. **The request.** The literal call, with the real field names. `POST /api/research/events` over
   `{ "artist_id": "…" }`, captioned "one required field."
2. **The constraint that makes it safe.** Show the field that does *not* exist. A schema list with
   `artist_id REQUIRED`, `date OPTIONAL`, and `name` struck as `NOT A FIELD` proves the fix
   structurally, in a way a success metric never can.
3. **Every answer it can give**, including the unglamorous ones: real events, an empty list, and the
   error. The error card is the most persuasive frame in the film, because it is the one a
   competitor would hide.

**Then end on something the viewer can run.** Not "learn more." The last beat of this one was two
URLs, `docs.recoupable.dev/llms.txt` and `chat.recoupable.dev/keys`, under the line "give your agent
the docs and a key." It converts a viewer into a caller in two steps.

### Verify the CTA path before you script it

The obvious CTA here was "tell Claude to use it through our MCP." **The MCP does not expose the
research endpoints** — it carries `prompt_sandbox` and `run_sandbox_command` and nothing else, so
that line would have been a confident, checkable lie in a film whose entire subject is not
fabricating answers.

**Before a CTA goes in a script, curl it.** `llms.txt` 200, `llms-full.txt` 200 and containing the
endpoint, the keys page 200. All three were checked; the MCP claim was cut on the evidence.

### A CTA can route around a broken destination

`/pricing` hardcodes `utm_campaign=free` on its own free CTA and overwrites the campaign tag on the
converting click, which is why five consecutive slates were unattributable. Pointing this film at
`chat.recoupable.dev/keys` instead **sidesteps the defect entirely** — the click never passes through
the page that eats the tag. Where the film's own logic supports a different destination, prefer the
one that is not broken, and say in `posts-log.md` which defect you routed around.

## Handoffs

| Next | Skill |
|---|---|
| Publish, per-platform copy, ~48h re-pull | `recoup-internal-social-ship-posts` |
| Signup / funnel reads at the re-pull | `recoup-internal-sales`, `recoup-internal-funnel-valuation-pipeline` |
| Composition mechanics, timing contract, rendering | the `hyperframes*` skills |
| Media resolution (music, SFX, voice, images) | `media-use` |

Customer-facing or artist-facing assets do **not** go through this skill — they go through the
`recoup-content-*` skills, which are credit-metered, cost-confirmed, and analyze-gated.
