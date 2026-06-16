---
name: recoup-content-image
description: Create any still-image asset for an artist — DSP cover art, a YouTube thumbnail, a multi-slide carousel/photo dump, a date/announcement promo (out-now, pre-save, tour poster), or a single lyric/quote card. Use when the user says "cover art", "album art", "single artwork", "thumbnail", "YouTube thumbnail", "video cover", "carousel", "photo dump", "swipe post", "promo", "announcement", "release date graphic", "pre-save graphic", "tour poster", "out now post", "quote card", or "lyric card". Picks the right image mode, generates to spec, verifies with the analyze gate, and writes the asset back. Produces finished image(s); does not post. For motion (lyrics on screen) use recoup-content-lyric-video.
---

# Content Image

Every still-image job an artist needs, behind one door. The five modes share one
backbone and differ only in **aspect, text rules, and where the file lands** —
which is exactly why they're one skill, not five: the process is identical, only
the spec changes.

| Ask | Mode | Aspect | Text rule |
|---|---|---|---|
| "cover art", "album art", "single artwork", "DSP artwork" | **cover** | 1:1 square | minimal — name/title only, **no hooky text** |
| "thumbnail", "YouTube thumbnail", "video cover" | **thumbnail** | 16:9 | **hooky** — ≤5 huge words, off the face |
| "carousel", "photo dump", "swipe post" | **carousel** | 4:5 or 1:1 (consistent) | per-slide copy; one story |
| "promo", "announcement", "release date", "pre-save", "out now", "tour poster" | **promo** | 1:1 + 9:16 | exact title/date/CTA, dominant |
| "quote card", "lyric card", "typography post" | **quote** | 1:1 + 9:16 | one verified line, large |

Read `references/content-api.md` (image gen, edit/overlay, upscale, async),
`references/analyze-gate.md` (verify a render before claiming done),
`references/workspace-context.md` (read-context-first + write-back), and
`references/research-context.md` (live signals). All ship alongside this skill.

## Shared backbone (every mode runs this)

1. **Resolve** the artist + workspace (`references/workspace-context.md`); generic
   mode if no artist.
2. **Distill the visual identity** — in context mode, read the aesthetic the
   artist actually has rather than inventing one:
   ```bash
   cat "$ARTIST_DIR/context/artist.md" 2>/dev/null            # palette, motifs, treatment, do/don'ts
   cat "$ARTIST_DIR/releases/$RELEASE_SLUG/RELEASE.md" 2>/dev/null  # release theme/facts
   ```
   Write a short art-direction brief (palette/motifs/treatment + an explicit
   **avoid** list). This is what you check the render against.
3. **Pick the mode** from the table; gather that mode's specifics (below).
4. **Generate** to the mode's aspect (`references/content-api.md`); offer 2–3
   directions where the user is choosing an identity (cover) or concept.
5. **Verify with the analyze gate** (mandatory — you cannot see pixels) against
   the mode's checklist; **regenerate on any failure**.
6. **Persist** to the mode's path; commit `{what}: {why}`. No workspace → return
   the URL(s). This skill stops at the asset — it does not post.

## Mode specifics

### cover — brand-defining DSP identity
The durable image that represents the release everywhere it streams, for years.
**Not** a thumbnail: no hooky text, arrows, or shocked faces.
- **Spec:** square 1:1, ≥3000×3000 (generate → `upscale`); no streaming logos,
  URLs, or "explicit" badges; legible at ~120px queue-tile size.
- **Decision brief** when two real directions fork (e.g. photographic vs
  illustrated): ask one brief question (recommendation + one-line tradeoff), else
  default on-brand and note it.
- **Verify:** reads at ~120px · no garbled text/artifacts · matches the identity
  brief · title/name clean if shown · square + ≥3000px after upscale.
- **Persist:** `artists/{slug}/releases/{release-slug}/cover.png`; record the URL
  in that release's `RELEASE.md` (Section 18, visuals).

### thumbnail — maximize click-through
A 16:9 frame built to win the click: strong focal subject (usually a face with
emotion) + a few huge hook words. The opposite of cover — hooky text is the point.
- **Spec:** 16:9 (1280×720+), one focal point, ≤3–5 words huge/high-contrast
  **never covering the face**, room for the duration stamp (bottom-right).
- **Hook:** draft **3 short options** (≤5 words) framed on the video's payoff;
  pick the sharpest. Avoid clickbait the content doesn't pay off.
- **Verify (at phone-tile size):** focal point obvious in <1s · face clear ·
  text readable on a phone and off the face · high contrast. Weak hook → redo
  the words; muddy face → regen.
- **Persist:** `artists/{slug}/content/thumbnails/` (or beside the video).

### carousel — an ordered, cohesive multi-slide set
- **Outline first:** slide-by-slide copy (hook cover → body → CTA) so the set
  tells one story; confirm the outline before generating.
- **Spec:** default 5 slides (1 cover + 3 body + 1 CTA); one consistent
  palette/treatment/aspect across slides (reuse a seed/reference image); overlay
  each slide's text via the edit endpoint. 4:5 or 1:1, kept consistent.
- **Verify:** reads as one cohesive sequence; the cover earns the swipe.
- **Persist:** `artists/{slug}/content/carousels/{topic}/slide-01.png …`.

### promo — a date-forward announcement
- **Lock the facts first:** title, exact **date(s)**, CTA, handle/URL; tour/show
  = each date + city + venue. Pull from `releases/{slug}/RELEASE.md` when
  available; else have the user confirm. **Never guess a date — a wrong date is
  the one unrecoverable error here.**
- **Spec:** on-brand background, overlay title/date(s)/CTA with clear hierarchy
  (date + CTA dominate). Default 1:1 + 9:16 (tour posters often 4:5).
- **Verify:** every date/city/CTA correct and readable.
- **Persist:** `artists/{slug}/releases/{release-slug}/announcement-*.png`.

### quote — a lyric/quote as typography
- **Confirm wording first** (especially from a transcript or the
  `recoup-song-analyze` skills — a typo'd lyric card gets screenshotted).
- **Spec:** on-brand background, large well-kerned high-contrast text; 1:1 + 9:16.
- **Rights:** the artist's own lyrics are fine; don't reproduce third-party
  copyrighted lyrics; for covers/samples confirm rights.
- **Verify:** wording exact, legible, text doesn't fight the background.
- **Persist:** `artists/{slug}/content/quote-cards/`.

## Guardrails

- **Mode rules are opposites on purpose** — cover forbids the hooky text
  thumbnail requires. Pick the mode, then obey its rule; don't blend them.
- **Verify before delivery.** Presenting an un-analyzed image is the failure mode
  this skill exists to prevent — run the analyze gate every time.
- **promo: dates/venues exact; quote: wording verified.** These are the
  unrecoverable errors.
- **Likeness:** seed real faces with the artist's own reference; models may 422
  on celebrity likeness.
- **Stop at the asset** — this skill does not post or schedule.

## References

- `references/content-api.md` — image gen, edit/overlay, upscale, async.
- `references/analyze-gate.md` — verifying a rendered image before claiming done.
- `references/workspace-context.md` — read-context-first + write-back.
- `references/research-context.md` — live signals to ground the image in what's true.
