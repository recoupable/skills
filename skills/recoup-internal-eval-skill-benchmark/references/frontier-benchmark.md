# The frontier bar — what makes a skill pack good (the standard to benchmark against)

This is the reference standard the `recoup-internal-eval-skill-benchmark` skill scores any
plugin or skills folder against. It distills the confirmed patterns and **real,
measured numbers** from the current frontier of skill/plugin design. It is
domain-agnostic: the pack under review can be about engineering, music,
finance, biology — anything. The bar is structural, not topical.

## Table of contents
1. The frontier packs (the receipts)
2. The core architecture: thin harness, fat skills
3. latent vs. deterministic — the triage discipline
4. skill-as-method-call — parameterize, don't proliferate
5. skill-pack-bundle — "a skill pack has tests" (the defining property)
6. resolver-routing-table — tested routing at scale (the ~40-skill threshold)
7. complexity-ratchet — forward-only quality (and the Foxconn-factory counter-weight)
8. Other confirmed patterns
9. How fat is "fat" — the anatomy, with real line numbers
10. The size-budget discipline (fat ≠ unbounded)

---

## 1. The frontier packs (the receipts)

The bar below is drawn from these shipped packs. When you cite a number in a
benchmark, it traces back here.

- **gstack** (Garry Tan / YC) — Claude Code "virtual engineering team". ~54
  skills @ **~840–2,301 lines** for substantive skills (median ~1,030; a few
  utility skills 48–91) + carved `sections/`; 62+ `bin/` CLIs; a compiled
  browser tool; **~1,100+ tests** incl. LLM evals + **3 resolver evals**; a
  `skill-size-budget` test; diff-based gate/periodic test tiers.
- **gbrain** (Garry Tan) — 53-skill pack over a thin CLI + zero-LLM knowledge
  graph; ships an explicit `RESOLVER.md`, filing rules, **15 `routing-eval.jsonl`
  fixtures** (with adversarial must-not-fire negatives), and `check-resolvable`
  as a build gate (`gbrain doctor`). The reference implementation of *tested
  routing*.
- **compound-engineering** (Every / Kieran Klaassen) — 38 skills + 43 review
  subagents; an 8-step ideate→brainstorm→plan→work→review→compound loop;
  **~1,094 test cases** incl. behavioral *contract* tests and a
  `frontmatter.test.ts` that enforces the description constraints routing needs;
  authored once, converted to ~11 harnesses; writes solved problems to
  `docs/solutions/`.
- **PM OS** (paid, PM vertical) — **235 skills** in three explicit tiers (13
  system + 11 workflow + 214 reusable) + 12 agents + 2 hooks + 6 MCP servers,
  governed by a 364-line behavioral harness. The cleanest model for an
  "everything-in-a-box" vertical pack and for *tiering* skills.
- **Anthropic skills marketplace** — *demonstration* skills: minimal-frontmatter
  `SKILL.md` reference implementations, **no tests, no resolver**. The correct
  shape for *teaching the format* — and the "before" state the fat-skill
  patterns are a response to. A thin, untested capability skill resembles these.

---

## 2. The core architecture: thin harness, fat skills

The namesake thesis (Garry Tan): the gap between a "2x" and a "100x" agent
running the *same model* "isn't intelligence — it's architecture." Three layers:

- **Top — fat skills (≈90% of the value).** Reusable markdown procedures that
  teach the model *how* to do a task. Judgment lives here, as editable prose,
  not logic frozen in code.
- **Bottom — thin-but-exact deterministic code.** Narrow single-purpose CLIs,
  compiled tools, SQL, arithmetic — things the model must **never improvise**.
  "Thin" = *narrow and fast*, not few (gstack has 62+).
- **Middle — a thin harness (~200 lines).** Loops the model, reads/writes files,
  manages context, enforces safety. You don't own it — it's Claude Code / Codex
  / Cursor. Skills are **harness-agnostic**.

Directional rule: **push intelligence up, push execution down, keep the harness
thin.** Payoff: when a better model ships, every fat skill improves for free
while the deterministic floor stays reliable.

**The named anti-pattern is the inverse — a *fat harness* wrapping *thin*
skills**: 40+ tool definitions eating the context window, "god-tools", a
REST-wrapper-per-endpoint — measured at "3× tokens, 3× latency, 3× failure
rate."

> Caveat the frontier itself flags: even gstack strains "thin" — its root
> `SKILL.md` runs a ~100-line bash preamble before any skill logic
> ("infrastructure as preamble"). Lesson: don't confuse "fat skill" with "heavy
> boilerplate on every call."

---

## 3. latent vs. deterministic — the triage discipline

Every step is either **latent** (needs judgment: read, interpret, decide,
synthesize) or **deterministic** (same input → same output: SQL, math, sorting,
date conversion). Put each on the side it belongs.

> "The most common mistake in agent design isn't a wrong answer — it's a wrong
> **side**." Deterministic work done in latent space gets plausibly,
> confidently wrong.

The load-bearing move is a **loop**: the model *writes* the deterministic tool,
then the tool *constrains* the model (gstack's `/scrape` graduates into a
deterministic `script.ts` + `script.test.ts`; the next run is ~200ms instead of
~30s). Stated as an authoring principle: **"skills are guardrails for an
intelligent agent, not a step-by-step controller for a non-intelligent one —
calibrate prescription to the failure mode"** (hard rules for deterministic
safety, trust for judgment).

**The inverse error matters too:** don't hard-code genuine judgment into brittle
rules. Seating 8 people by personality is *correctly* latent; only the
800-person optimization belongs in code.

---

## 4. skill-as-method-call — parameterize, don't proliferate

A skill file is a **parameterized procedure invoked like a method call**: the
user supplies the *what* (a target, a question, a depth tier); the skill
supplies the fixed *how*.

- gstack's `/qa` ships **Quick / Standard / Exhaustive** tiers — one file, one
  procedure, a named depth argument.
- gstack's `/investigate` is a fixed four-phase procedure re-aimed at any bug.
- Codex's `/goal` ships a literal six-slot signature.

**The diagnostic test:** if different arguments run *different steps*, those are
**N skills wearing one filename** (the "god-skill" anti-pattern) — split them.
If the *process* stays fixed and only the *input/depth* varies, it's one method
— **don't fork it, parameterize it.**

---

## 5. skill-pack-bundle — "a skill pack has tests" (the defining property)

The frontier's definition of a skill as a *unit*: not just a `SKILL.md`, but a
**tested bundle**. The 10-step "skillify checklist":

1. `SKILL.md` — the contract (name, triggers, rules)
2. deterministic code (`scripts/*`) — no LLM for what code can do
3. **unit tests** for the code
4. **integration tests** (live endpoints)
5. **LLM evals** (quality + correctness, LLM-as-judge)
6. **resolver trigger** (a routing-table entry)
7. **resolver eval** (verify the trigger actually routes)
8. **check-resolvable + DRY audit** (is the skill reachable? does it duplicate
   another's lane?)
9. **E2E smoke test**
10. **filing rules** (knowledge-writing files by primary subject)

> "A feature that doesn't pass all ten is not a skill. It's just code that
> happens to work today."

Evidence: gstack ships `skill-validation.test.ts`, `skill-llm-eval.test.ts`
(~$0.15/run), `skill-e2e-*.test.ts` (~$3.85/run), three `*-resolver*.test.ts`,
run under **diff-based selection** + a **gate/periodic tier split** (cheap
deterministic tests block every PR; expensive LLM evals run on a weekly cron).
CE ships ~1,094 cases incl. behavioral *contract* tests.

**The rarest, most-stealable part: the resolver eval** — a test that the right
skill *fires* (and wrong ones *don't*), not just that its output is good. Almost
nobody tests skill *triggering*.

---

## 6. resolver-routing-table — tested routing at scale

A **resolver** is a routing table for context: *when intent X appears, load
skill Y first.* Two philosophies:

- **Explicit** (gbrain): a `RESOLVER.md` `trigger → skill` dispatcher read once
  per request, plus filing rules, plus **15 `routing-eval.jsonl` fixtures** with
  *both* polarities (must-fire positives AND adversarial must-not-fire
  negatives), plus `check-resolvable` (a build gate that fails if any skill is
  "dark"/unreachable).
- **Implicit** (gstack, Anthropic demos): lean on the harness's built-in
  `description`-field auto-matching — *"the description **is** the resolver."*

**The threshold that matters:** the observed breaking point is **~40 skills**.
Below it, the harness's implicit description-matching resolves cleanly. Past it,
three failures appear: skills drift in their filing; skills go **"dark"** (built
but unreachable — "a surgeon the hospital can't find"); and the table rots
within ~90 days. **A pack at/over ~40 skills with no resolver eval and no
reachability audit is exactly where implicit routing starts to break.**

---

## 7. complexity-ratchet — forward-only quality

Every session adds tests/docs/evals/learnings that **reload into context**, so
the quality floor only ever rises. Its load-bearing step (CE's `/ce-compound`):
write the solved problem into `docs/solutions/` with a **5-dimension overlap
dedup** (update the existing doc, don't create a near-dup), then a
**discoverability check** (does the project's `AGENTS.md` lead a *fresh* agent to
the store?). Branch protection is the "can't regress below the floor" mechanism.
Budget rule: **50/50** — half your effort on the system that produces work.

> **The counter-weight — the "Foxconn factory."** The *same* author who preaches
> "test everything" warns against over-building systems that *police* a capable
> model: ~276K lines of tests, a 1,778-line fact-checker fanning every claim to
> five sources. The line: skill-pack tests **pin a thin unit so it can change
> safely** (contracts); a Foxconn factory is **mountains of code written to
> distrust the model** (a cage). Same word ("tests"), opposite spirit. When you
> score a pack's deterministic substrate, ask of each script: *is this exact
> work (math, parsing, validation) or model-policing code?* Only the first earns
> its keep.

---

## 8. Other confirmed patterns worth naming

- **single-source-multi-surface-distribution** — author once, ship to many
  harnesses (CE converts to ~11; gbrain ships CLI + MCP + skillpack from one
  definition; per-harness manifests + vendored copies with a drift check).
- **persona-lens-review-panel** — review via parallel narrow persona reviewers
  (read-only, structured returns) merged by an orchestrator (CE: 43 review
  subagents; PM OS: a 9-reviewer PRD panel).
- **diarization** — read everything about a subject, write **one page of
  distilled judgment** (the "says vs. actually doing" gap). "No SQL query
  produces this." The shape a good brief/dossier skill should target.
- **session-start-directive** — session-start hooks must emit *imperative,
  position-pinned* directives, not passive context the model silently ignores.
- **version-as-update-gate** — `version` is the update-delivery trigger; release
  automation owns it, hand-bumps forbidden.
- **completion-gating** — block "it's ready" claims until evidence exists. The
  strongest form *externally verifies* (a script returns `ok`, required files
  exist, no fabricated numbers) rather than letting the model *self-attest*.
- **immutable-source / anti-cheat** — a PreToolUse hook that blocks writes into
  the immutable evidence/source tree, so the agent can't launder its inputs.

---

## 9. How fat is "fat" — the anatomy, with real line numbers

"Fat" is easy to mis-hear as "long." It isn't. A **fat skill encodes enough
judgment and process that the model reliably produces a finished, trustworthy
result without the user micromanaging it.** In the frontier packs that depth
*happens to be large*. Verified gstack `wc -l` of shipped `SKILL.md` bodies:

```
Tiny utility / toggle skills (the exception):
  unfreeze 48   careful 67   guard 90   freeze 91   gstack-upgrade 284
Setup / single-tool skills:
  setup-browser-cookies 603   benchmark-models 631   benchmark 756   make-pdf 758
Substantive capability / workflow skills (the norm — ~840 to 2,301):
  investigate 1,045   qa 1,655   retro 1,783   autoplan 1,823   review 1,823
  design-review 1,965   spec 2,301   ...   (median ≈ 1,030)
```

**What fills 1,000+ lines (the `/investigate` dissection):** ~60 lines rich
frontmatter (explicit trigger phrases + proactive-invoke conditions +
allowed-tools + context queries); ~120 lines bash preamble; ~100 lines first-run
onboarding; **~80 lines a strict interaction contract** (the AskUserQuestion
"decision brief" format: every question carries an ELI10 explanation, "stakes if
we pick wrong," a recommendation, ≥2 pros/≥1 con per option, a "Net" tradeoff
line, effort in both human-time and AI-time); then **the actual multi-phase
procedure** with an "Iron Law," worked sub-steps, evidence requirements, and exit
criteria; then completion + write-back discipline. Roughly **~750 of 1,045 lines
are encoded judgment** — *that* is fat. It encodes a senior engineer's entire
debugging discipline, not "debug the thing."

### The four roles and their fatness norms

| Skill role | Frontier norm | What fills it |
|---|---|---|
| **Orchestrator / workflow** | 1,300–3,000 effective lines | pipeline control, workspace contract, phase gates, landing recap |
| **Deep capability / leaf** | 800–1,700 lines | full multi-phase procedure + interaction contract + verification |
| **Reusable single-task leaf** | 100–400 lines + `references/` | one job, references for shared context, still a real procedure |
| **Demonstration skill** | 30–150 lines | shows the *format*; intentionally minimal; not production |

So *"how fat should every skill be?"* is **not "uniformly enormous"** — it is
**tiered**: fat orchestrators over a library of focused (but still real,
references-backed) leaf skills. A pack whose substantive skills sit in the
bottom two rows is **thin** by the frontier bar; one whose workflow front-doors
sit in the top two rows (whether the depth is in the body *or* pushed into
scripts/references) is **fat**.

> Depth can live in the `SKILL.md` body **or** in co-located `scripts/` +
> `references/`. Pushing deterministic depth into scripts is a *legitimate* (often
> better) choice — but it means the *judgment* layer (the prose procedure) can
> still be lean. Score both: total footprint **and** body judgment-depth.

---

## 10. The size-budget discipline (fat ≠ unbounded)

gstack ships a `skill-size-budget` test. It is **not** a fixed "max N lines"
cap. It's a free, gate-tier regression test that diffs the current tree against
a captured baseline and enforces four budgets:

1. **Per-skill growth ceiling — ≤ 1.5× baseline.** A body may grow only ~1.5×
   between baselines (started at 1.05, loosened to 1.50: "real bloat is 2-3×;
   this catches that without tripping on normal feature scope"). An anti-bloat
   ratchet keyed to *growth*, not an absolute count.
2. **Total-corpus ceiling — ≤ 1.5× baseline** (stops death-by-a-thousand-cuts).
3. **Per-skill shrink floor — ≥ 80% of baseline** (catches accidental
   body-stripping; skills carved into `sections/` are exempted and guarded by a
   skeleton+sections-union minimum instead).
4. **The only *absolute* cap — the always-loaded catalog ≤ ~7,000 tokens.** The
   "catalog" is the set of skill **descriptions** that load into **every**
   context window. Bodies load on demand (so they're only ratcheted); the
   catalog is paid on every request (so it gets a hard ceiling). "Attention is
   the scarce resource" turned into a test.

**The rule for benchmarking:** fat *bodies* are fine because they're
lazy-loaded; a fat *catalog* is not. A pack whose summed descriptions exceed
~7K tokens has a real, measurable problem regardless of how good each skill is.
Push depth into on-demand `sections/`/`references/`; keep the always-loaded
description surface tight.
