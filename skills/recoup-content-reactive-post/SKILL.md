---
name: recoup-content-reactive-post
description: Turn a real milestone or trend into a timely post — finds the real moment (a chart entry, a streaming milestone, a fresh trend), picks an angle in the artist's voice, then routes to the right format. Use for "they just hit 1M, make something", "react to this trend", or "make something timely". Real moments only; never invents a milestone. The underlying data comes from recoup-research-artist-overview.
---

# Recoup Content — Reactive Post

Answers "something happened — what do we make of it?" Read the bundled references
first: `references/workspace-context.md`, `references/account-resolver.md`,
`references/research-context.md`, `references/analyze-gate.md`.

## Procedure

**Find the real trigger** (don't invent one): pull `milestones`/`career`/`playlists`
from the research feed (`references/research-context.md`); triage fresh-real vs stale
(months old → tell the user there's no fresh moment, offer evergreen) vs trend-only
(use as direction, keep facts from context). Pick the angle + the carrying format,
write a one-line angle in the artist's voice, then **route to the format**:
recoup-content-make-graphics (promo) / recoup-content-write-caption /
recoup-content-make-video — don't double-run a pipeline. Real or nothing: every
number/date traces to the feed or workspace.

## Guardrails

- **Never fabricate** a milestone, date, or number — it traces to the feed or workspace.
- **Stale ≠ fresh** — months-old isn't a moment; say so and offer evergreen.
- **Stop at the asset** (via the routed format skill) — no posting.

## References

- `references/workspace-context.md` · `references/account-resolver.md` ·
  `references/research-context.md` · `references/analyze-gate.md`
