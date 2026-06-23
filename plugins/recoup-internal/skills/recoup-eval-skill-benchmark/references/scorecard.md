# The benchmark scorecard — 15 dimensions to grade any skill pack

Fill one row per dimension for the pack under review. Grade each
**✅ at/ahead of frontier · ⚠️ present but weak/untested · ❌ gap**, cite the
**measured evidence** (from `scripts/measure.py` or a file path), and give a
one-line **so-what**. The frontier column is the bar from
`references/frontier-benchmark.md`. Do not invent a numeric score; the three-way
grade + evidence is the deliverable.

> A pack does **not** need ✅ on all 15. Demonstration packs *should* be thin and
> untestless on purpose. Grade against what the pack is *trying to be* (vertical
> "in-a-box" bundle vs. focused capability plugin vs. teaching demo), which you
> establish in Phase 1 of the SKILL.md procedure.

| # | Dimension | Frontier bar | How to measure it | Grade |
|---|---|---|---|---|
| 1 | **`SKILL.md` body depth** | 800–3,000 lines for substantive skills; deep encoded judgment + interaction contracts | `measure.py` body min/median/max + bands; read the 2–3 fattest + 2–3 thinnest bodies | |
| 2 | **Total skill footprint** | large across the board (body + refs + scripts) | `measure.py` per-skill total column | |
| 3 | **Deterministic substrate** | many narrow CLIs (gstack 62+); converters; zero-LLM engines | `measure.py` "deterministic substrate" count; spot-read 1–2 scripts | |
| 4 | **Unit / integration tests** | gstack ~1,100+; CE ~1,094 | `measure.py` "unit/integration tests" signal | |
| 5 | **LLM-as-judge evals** | gstack `skill-llm-eval`; gbrain BrainBench | `measure.py` "LLM evals" signal; confirm it judges *quality*, not just existence | |
| 6 | **Resolver evals (does the right skill *fire*?)** | gstack 3 + gbrain 15 fixtures w/ adversarial negatives | `measure.py` "resolver/routing tests"; the rarest, highest-value test | |
| 7 | **Reachability audit (`check-resolvable`)** | gbrain ships it as a build gate | `measure.py` "reachability gate" signal | |
| 8 | **Routing / resolver design** | explicit `RESOLVER.md` (>40 skills) or tested description-match (<40) | skill count vs ~40 threshold; read a few `description:` fields for trigger phrases | |
| 9 | **Completion gating** | externally-verified "it's ready" gate beats self-attestation | look for `Stop`/completion hooks, validators that return `ok` | |
| 10 | **Immutable-source / anti-cheat** | PreToolUse hook blocking writes to evidence/source | read `hooks.json` if present | |
| 11 | **Compounding learnings store** | CE `docs/solutions/` + dedup; gstack `learnings.jsonl` | `measure.py` "learnings store" signal | |
| 12 | **Parameterization (method-call)** | `/qa` tiers, `/goal` signature | look for depth/mode args vs. near-duplicate skills (see overlap candidates) | |
| 13 | **Multi-surface distribution** | author once → ~11 harnesses; per-harness manifests | `measure.py` "multi-surface distribution" manifests | |
| 14 | **Always-loaded catalog budget** | ≤ ~7,000 tokens of descriptions | `measure.py` catalog est_tokens vs 7K | |
| 15 | **Progressive disclosure** | carve `sections/`/`references/`; size-budget ratchet | refs present? bodies lazy vs. everything in one file? | |

## Turning grades into a diagnosis (per plugin / sub-pack)

After grading, classify each skill (or group) with the **fat-enough? combine?
split?** framework from the benchmark methodology:

- **Hold** — fat enough and correctly scoped. Don't touch.
- **Fatten** — thin body for a deep job: encode the real multi-phase procedure +
  interaction contract + verification loop (anatomy in `frontier-benchmark.md`
  §9). Boundary: fat ≠ verbose; push depth into `references/`, keep the body a
  tight high-judgment procedure.
- **Parameterize / combine** — near-duplicate skills running the *same* process
  on different inputs → collapse into one mode-driven skill (use the
  `measure.py` overlap candidates as the shortlist). Boundary: only when the
  *process is the same*; if two "modes" run genuinely different steps, keep them
  split (the god-skill anti-pattern).
- **Split** — one filename running different steps per argument → break apart.

## The prioritized "what to steal" moves (apply only what the grade calls for)

Ordered by typical leverage. Each carries its boundary — carrying the boundary
is what keeps a benchmark from cargo-culting.

- **P1 — Ship the tested-bundle layer** (dims 4–7). Add resolver evals
  (`{intent, expected_skill, must_not_fire}` with adversarial negatives) and
  LLM-as-judge evals for judgment-heavy outputs. Keep them affordable: cheap
  deterministic checks gate every change, expensive LLM evals run periodically.
  *Boundary:* not on demonstration/throwaway skills; don't build evals before a
  skill's shape stabilizes (it's a *graduation* step), and don't let the suite
  become a Foxconn factory.
- **P2 — Add a reachability + routing layer** (dims 7–8) *only if the pack is
  at/over ~40 skills*. A CI check that every skill is reachable (no "dark"
  skills) and overlapping descriptions are MECE. *Boundary:* below ~40 skills
  the implicit description-matcher is correct and an explicit `RESOLVER.md` is
  overhead.
- **P3 — Fatten the thin capability skills** (dims 1–2). Encode the actual
  procedure + interaction contract + verification loop, not a 50-line API
  wrapper. *Boundary:* fat ≠ verbose; bound it (the size-budget discipline).
- **P4 — Parameterize instead of proliferate** (dim 12). Collapse near-duplicate
  skills into fewer, fatter, mode-driven ones. *Boundary:* only when the process
  is identical and only input/depth varies.
- **P5 — Add a compounding learnings store** (dim 11) for *recurring* workflows.
  *Boundary:* not for one-off jobs; keep dedup discipline or the store rots.
- **P6 — Promote session-start from passive to imperative** (one directive per
  session; passive walls of context get ignored).
- **P7 — Keep what the pack already leads on** (don't regress completion gates,
  anti-cheat hooks, distribution hygiene). Name these explicitly so a later
  refactor doesn't delete a strength.
