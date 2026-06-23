---
name: skill-pack-benchmark
description: >-
  Benchmark ANY plugin, skill pack, or skills folder against the current
  frontier of skill/plugin design (gstack, gbrain, compound-engineering, PM OS).
  Use whenever someone wants to grade, audit, review, or compare a skills
  directory or plugin and asks things like "is this skill pack good?", "how does
  our plugin compare to the frontier?", "are these skills fat enough?", "should
  these skills be combined or split?", "what should we steal from gstack?",
  "benchmark this plugin", "rate my skills folder", or "audit this skill bundle".
  Works on any domain (engineering, music, finance, bio — anything) and any
  harness layout. It measures the pack deterministically (skill count, SKILL.md
  body sizes, tests/evals/resolver/hooks/learnings signals, catalog token
  budget, description-overlap risks), grades it on a 15-dimension scorecard, then
  produces a fat-enough / combine / split / parameterize diagnosis and a
  prioritized list of frontier moves to steal — each with its boundary. Do NOT
  use this to author a single new skill (use a skill-creator) or to run a pack's
  own tests.
---

# Skill Pack Benchmark

Grade any plugin or skills folder against the frontier bar for what makes skills
and plugins *good*. The output is an evidence-backed report: where the pack
sits, what's fat vs. thin, what should be combined/split/parameterized, and the
prioritized, boundary-carrying moves worth stealing.

This skill follows the very discipline it grades: a **deterministic** measurement
script does the counting (so numbers are never eyeballed), and the **latent**
judgment — scoring, diagnosis, recommendations — is the agent's job, grounded in
the reference standard. The script and references ship alongside this `SKILL.md`;
invoke them with the relative paths below.

## Inputs

- **Target** (required): a path to a plugin directory, a folder of skills, or a
  whole repo. The skill auto-discovers every `SKILL.md` underneath.
- **Goal of the pack** (infer or ask once): is it a vertical *"everything-in-a-box"*
  bundle, a focused *capability plugin*, or a *teaching demonstration*? The bar
  differs — grade against intent, not a single absolute.

If no target is given, ask for the path before doing anything else.

## The procedure (five phases)

### Phase 1 — Frame: what is this pack trying to be?

Before measuring, establish intent (one short paragraph). Read the pack's README
/ top-level manifest if present, and skim 2–3 skill descriptions. Decide which
archetype it is — it sets which scorecard dimensions matter most:

- **Vertical "in-a-box" bundle** (PM OS analog): expect tiering (system /
  workflow-orchestrator / reusable-leaf) and, past ~40 skills, tested routing.
- **Focused capability plugin**: expect a router + a handful of real leaves;
  routing tests are overkill below ~40 skills.
- **Teaching / demonstration pack**: thin and testless is *correct* — say so and
  grade gently.

### Phase 2 — Measure (deterministic; never guess the numbers)

Run the bundled measurement script against the target:

```bash
python3 scripts/measure.py <target-path>
# JSON for your own downstream use:
python3 scripts/measure.py <target-path> --json -o /tmp/bench.json
```

`scripts/measure.py` ships alongside this skill (stdlib-only, no network). It
reports: skill count; `SKILL.md` **body** line min/median/max + size bands
(tiny/leaf/deep/fat); per-skill footprint (body + co-located refs + scripts);
the always-loaded **catalog** token estimate vs the ~7K budget; the pack-level
**signals** that the frontier treats as the *defining properties* of a skill
pack (deterministic scripts, unit/integration tests, LLM evals, resolver/routing
tests, reachability gate, hooks, learnings store, distribution manifests); and
**description-overlap candidates** (pairs most likely to mis-route).

Take the numbers as given — your job is to interpret them, not re-derive them.

### Phase 3 — Grade against the 15-dimension scorecard

Read `references/scorecard.md` and fill one row per dimension, grading each
**✅ at/ahead of frontier · ⚠️ present-but-weak · ❌ gap**, with the measured
evidence and a one-line so-what. To grade the judgment-depth dimensions (1, 5,
9, 12) you must **read actual files**, not just the counts: open the 2–3 fattest
and 2–3 thinnest `SKILL.md` bodies and judge whether the lines are *encoded
judgment* (multi-phase procedure, interaction contract, verification loop) or
boilerplate/padding. The bar and the real frontier numbers are in
`references/frontier-benchmark.md` — cite it.

A signal the script can't see: when grading the **deterministic substrate** (dim
3), spot-read a script or two and ask the Foxconn-factory question — *is this
exact work (math, parsing, validation) or code written to distrust the model?*
Only the former earns its keep (see `references/frontier-benchmark.md` §7).

### Phase 4 — Diagnose: fat enough? combine? split? parameterize?

For each plugin or skill group, classify it **Hold / Fatten / Parameterize-or-
combine / Split** using the framework in `references/scorecard.md`. Anchor every
call in evidence:

- Use the **size bands** to spot thin skills doing deep jobs (→ Fatten).
- Use the **overlap candidates** as the shortlist for Parameterize-or-combine,
  but only recommend combining when the *process is the same* and only the
  input/depth varies — otherwise keep them split (the god-skill anti-pattern).
- Flag the **~40-skill threshold** explicitly if the pack is at/over it with no
  resolver eval or reachability audit.

### Phase 5 — Report: prioritized moves with boundaries

Produce the final report (structure below). Pull recommendations from the
prioritized "what to steal" list in `references/scorecard.md` (P1–P7), and
**carry each boundary** — when NOT to do the move. Always include a "keep what
you already lead on" section so a later refactor doesn't delete a strength.

## Output format

Deliver a single report with these sections:

1. **Verdict in one screen** — archetype, the headline gap, and the single
   highest-leverage move, in ~5 sentences.
2. **The numbers** — a compact table from `measure.py` (skills, body
   min/median/max, bands, catalog tokens, signals).
3. **Scorecard** — the 15-row table, graded, with evidence.
4. **Diagnosis** — per plugin/group: Hold / Fatten / Combine / Split, with the
   reason.
5. **Prioritized moves** — the P1–P7 steal-list filtered to what this pack
   actually needs, each with its boundary.
6. **Keep (don't regress)** — the dimensions the pack already leads on.

Lead with what's **measured**; present judgment calls as judgment. Never inflate
a grade the evidence doesn't support — an unbacked benchmark is worse than none.

## Boundaries (when this skill does NOT apply)

- **Authoring one skill** → use a skill-creator, not this.
- **Running a pack's own test suite** → that's the pack's CI, not a benchmark.
- **Grading a deliberate demonstration pack as if it were production** → don't;
  thin + testless is the *correct* shape for teaching the format.
- **Cargo-culting frontier features** → every recommendation must carry its
  boundary. Fat ≠ verbose; tests ≠ a Foxconn factory; an explicit resolver below
  ~40 skills is overhead, not progress.

## What to read

- `references/frontier-benchmark.md` — the standard: the frontier packs and
  their real numbers, the core patterns (thin-harness/fat-skills, latent vs.
  deterministic, skill-as-method-call, the tested bundle, resolver routing, the
  complexity ratchet + Foxconn counter-weight), the anatomy of fat with verified
  line counts, and the size-budget discipline. **Read before grading.**
- `references/scorecard.md` — the 15-dimension rubric, the
  Hold/Fatten/Combine/Split diagnosis framework, and the prioritized P1–P7 steal
  list with boundaries.
- `scripts/measure.py` — the deterministic measurement tool (ships with this
  skill; run it, don't reimplement it).
