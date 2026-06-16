---
name: recoup-learn
description: Capture a solved problem or reusable lesson so the next run is cheaper — the compounding-memory step for Recoup work. Use when the user says "that worked", "remember this", "capture this learning", "save this so we don't redo it", "write this down for next time", or after a non-trivial fix/decision in a deal, release, research, or content job. Writes one deduplicated learning file into the workspace's learnings/ store and makes sure future agents can find it.
---

# Capture a Learning (compounding memory)

Recoup work is recurring: the same catalog quirks, the same artist-voice
footguns, the same "the API wants the row `id` not `account_id`" lessons keep
coming back. Without a store, every session re-learns them. This skill makes each
solved problem a **permanent, searchable lesson** so the next run starts ahead —
the forward-only "ratchet" from `docs/fat-skills-benchmark.md` (P5).

The discipline mirrors a single durable rule: **research broadly, write once,
never duplicate, and make sure the store is discoverable.**

## When this fires

- The user signals a win or a "remember this" ("that worked", "save this").
- A non-trivial problem was just solved (a fix, a workaround, a judgment call) in
  any workspace — a deal, a release, an artist, or a content job.
- Do **not** fire for trivial one-liners or generic chat — a learning must be
  *reusable*, not a diary entry.

## Where learnings live

A learning is filed by **primary subject**, not by the skill that produced it:

- Tied to one artist → `artists/{slug}/learnings/{slug}.md`
- Tied to one deal → `deals/{deal-id}/learnings/{slug}.md`
- Tied to one release → `releases/{artist}/{release}/learnings/{slug}.md`
- Cross-cutting (a platform/API/process lesson) → `learnings/{slug}.md` at the
  workspace root.

If no workspace exists, write to `learnings/{slug}.md` in the current directory.

## Procedure

### Phase 1 — Gather (latent; may read, must not write yet)

Reconstruct the learning from the conversation and workspace:

- **Problem** — what went wrong or was hard (one sentence).
- **Context** — where it happened (which workspace/skill/endpoint), enough to
  recognize the situation again.
- **Root cause** — *why* it happened (not just the symptom).
- **Solution** — what actually fixed it, concretely (commands, the exact field,
  the decision made).
- **Prevention** — how to avoid it next time / what to do first.

If any of these is unknown, ask one short question rather than inventing it.

### Phase 2 — Dedup before create (the anti-rot rule)

List existing learnings in the target store and check for overlap **before**
writing:

```bash
ls "$STORE"/*.md 2>/dev/null
```

Score overlap against each existing learning on five dimensions: **problem,
root cause, solution, referenced files, prevention**. If overlap is high
(the same problem with a better/expanded answer), **update the existing file**
— do not create a near-duplicate. "Two files describing the same problem will
inevitably drift apart." Only create a new file when the lesson is genuinely new.

### Phase 3 — Write exactly one file (deterministic; single writer)

Write (or update) **one** learning file with this frontmatter + body:

```markdown
---
problem_type: <api | valuation | voice | rights | workflow | tooling | data | other>
component: <artist-slug | deal-id | release | platform | endpoint>
tags: [<short>, <tags>]
date: <YYYY-MM-DD>
---

# <short title — the problem in a phrase>

**Problem:** <one sentence>
**Context:** <where/when it shows up>
**Root cause:** <why>
**Solution:** <concretely what fixed it — commands, fields, decisions>
**Prevention:** <what to do first next time>
```

Then commit:

```bash
git add "$STORE" && git commit -m "learn: <short title>"
```

### Phase 4 — Discoverability check (the store only compounds if it's found)

A learning nobody reads is dead weight. Confirm a fresh agent would discover the
store: if the workspace's `README.md` / `RECOUP.md` / `RELEASE.md` doesn't mention
`learnings/`, add the smallest natural pointer (e.g. "Past lessons:
`learnings/`"). Don't restructure the doc — add one line if missing.

## Guardrails

- **One file per capture.** Research may range; the write is single and
  deterministic. Never scatter the same lesson across files.
- **Update, don't duplicate.** High overlap → edit the existing learning.
- **File by subject, not by skill.** The lesson about an artist's voice lives
  under that artist, even if a content skill surfaced it.
- **Reusable only.** If it won't help a future run, don't capture it.
- **Never fabricate.** Unknown root cause/solution → ask, don't guess.
