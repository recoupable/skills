---
name: recoup-platform-capture-lesson
description: Capture a solved problem or reusable lesson so the next run is cheaper — the box's compounding memory. Use when the user says "that worked", "remember this", "capture this learning", "save this so we don't redo it", "write this down for next time", or after a non-trivial fix/decision in any Recoup work. Writes one deduplicated learning into the workspace's learnings/ store and makes sure future agents can find it.
---

# Recoup — Capture Lesson (compounding memory)

The box gets smarter per use by writing down what it learns. The discipline:
**research broadly, write once, never duplicate, make the store discoverable.**

## When this fires

The user signals a win or "remember this", or a non-trivial problem was just
solved (a fix, a workaround, a judgment call). Don't fire for trivial one-liners
or generic chat — a learning must be *reusable*.

## Procedure

1. **Gather (may read; don't write yet).** Reconstruct: **Problem** (what went
   wrong, one sentence) · **Context** (where it shows up) · **Root cause** (why,
   not just the symptom) · **Solution** (concretely — commands, the exact field,
   the decision) · **Prevention** (what to do first next time). Unknown → ask, don't
   invent.
2. **Dedup before create.** List existing learnings in the target store; score
   overlap against each on five dimensions (problem / root cause / solution /
   referenced files / prevention). High overlap → **update the existing file**,
   don't create a near-duplicate ("two docs on the same problem drift apart").
3. **Write exactly one file**, filed by **primary subject**:
   - tied to one artist → `artists/{slug}/learnings/{slug}.md`
   - tied to one deal → `deals/{id}/learnings/{slug}.md`
   - cross-cutting (a platform/API/process lesson) → root `learnings/{slug}.md`

   Frontmatter (`problem_type`, `component`, `tags`, `date`) + body
   (Problem / Context / Root cause / Solution / Prevention). Commit `learn: <title>`.
4. **Discoverability check.** A learning nobody reads is dead weight — confirm a
   fresh agent would find the store (does the workspace `README`/`RECOUP.md`
   mention `learnings/`? add the smallest natural pointer if not).

## Guardrails

- **One file per capture** — research may range; the write is single + deterministic.
- **Update, don't duplicate** — high overlap edits the existing learning.
- **File by subject, not by skill** — a voice lesson lives under the artist, even
  if a content task surfaced it.
- **Reusable only**; **never fabricate** a root cause or solution.
