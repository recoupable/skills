---
name: recoup-content-cover-art
description: Create square cover art for a release — single, EP, or album artwork sized for DSPs (Spotify, Apple Music). Use when the user says "cover art", "album art", "single artwork", "artwork for [release]", "make a cover for [song]", or "DSP artwork". Produces brand-defining 1:1 art with no clickbait text. Distinct from a YouTube thumbnail (use recoup-content-thumbnail). Works with or without artist context.
---

# Cover Art

Square release artwork for DSPs. This is **brand-defining, durable** art — the
single image that represents the release everywhere it streams, for years. It is
NOT a clickbait thumbnail: cover art carries at most the artist/title set cleanly,
never hooky overlay text, arrows, or shocked faces. For YouTube/video CTR art, use
`recoup-content-thumbnail`.

The job is a loop, not a one-shot: **distill the visual identity → generate
directions → upscale → verify it survives shrinking to a queue tile.** A cover you
haven't analyzed at thumbnail size is not done.

Read `references/content-api.md` (image gen, upscale, async) and
`references/analyze-gate.md` (verify before delivery). Both ship alongside this
skill; `references/workspace-context.md` covers read-context-first + write-back.

## DSP requirements (non-negotiable)

- **Square 1:1**, high resolution (aim ≥ 3000×3000 for store acceptance) —
  generate, then `upscale` (`type: image`) if needed.
- **Legible at thumbnail size** — it appears tiny in a queue/search row; the
  concept must read at ~120px.
- **No** streaming logos, URLs, "explicit" badges, or hooky text.

## Inputs

- **Artist** (optional — context mode vs generic mode).
- **Release** (required) — single/EP/album name; pull theme from its `RELEASE.md`.
- **Concept** (optional) — a direction or seed photo the user supplies.

## Procedure

### Phase 1 — Distill the visual identity (don't skip in context mode)

Build a short, concrete **art-direction brief** the way you'd brief a designer —
not a vibe word. In context mode, read the aesthetic the artist actually has:

```bash
cat "$ARTIST_DIR/context/artist.md" 2>/dev/null            # palette, motifs, aesthetic, do/don'ts
cat "$ARTIST_DIR/releases/$RELEASE_SLUG/RELEASE.md" 2>/dev/null  # release theme/narrative
```

Write down: **palette** (actual colors/hex if stated), **recurring motifs**,
**era/treatment** (film grain? high-gloss? collage?), **typography** if a title is
shown, and an explicit **avoid** list. In generic mode, derive the same brief from
the user's concept. This brief is what you check against in Phase 4.

### Phase 2 — Decision brief on direction (when it materially forks)

If two genuinely different visual directions are viable and the choice changes the
result, ask **one** decision-brief question before burning generations:

```
D1 — <direction question, e.g. "photographic or illustrated cover?">
Context: <release + the identity brief in one line>
Recommendation: <option> because <fits the artist's established look / the release theme>
A) <option> (recommended)   ✅ <concrete pro>   ❌ <honest con>
B) <option>                 ✅ <pro>            ❌ <con>
Net: <the actual tradeoff>
```

Otherwise pick the on-brand default and note it.

### Phase 3 — Generate + upscale

Generate the 1:1 image (`POST $BASE/content/image`, poll per
`references/content-api.md`); offer **2–3 directions** so the user chooses. Seed
with a supplied photo as `reference_image_url` when provided. Upscale the chosen
one to DSP resolution.

### Phase 4 — Verify (the analyze-gate loop; mandatory)

You cannot see pixels — analyze the rendered result before claiming done
(`references/analyze-gate.md`). Check, and **regenerate on any failure**:

- [ ] **Reads at ~120px** — shrink-test; the concept/subject still registers.
- [ ] **No garbled text or AI artifacts** (hands, melted type, warped logos).
- [ ] **Matches the identity brief** from Phase 1 — palette, motif, treatment.
- [ ] **Title/name legible** if included; clean, not hooky.
- [ ] **Square + ≥3000px** after upscale (or DSPs reject it).

A cover that fails the shrink test or shows artifacts goes back to Phase 3.

### Phase 5 — Persist

Workspace → `artists/{slug}/releases/{release-slug}/cover.png` and record the URL
in that release's `RELEASE.md` (Section 18, visuals). Commit `{what}: {why}`
(`references/workspace-context.md`). No workspace → return the image URL.

## Guardrails

- **Cover art ≠ thumbnail.** No hooky overlay text, arrows, or shocked faces.
- **Square + high-res**, or DSPs reject it.
- **Verify before delivery.** Presenting an un-analyzed cover is the failure mode
  this skill prevents.
- **Likeness:** if seeding with a real face, use the artist's own reference; image
  models may 422 on celebrity likeness.

## References

- `references/content-api.md` — image gen, upscale, async polling.
- `references/analyze-gate.md` — verifying a rendered image before claiming done.
- `references/workspace-context.md` — read-context-first + write-back.
