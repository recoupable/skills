# Fat Skills Benchmark — the frontier vs. Recoup

> **What this is.** A deep, self-contained comparison between (a) the current
> frontier thinking on what makes skills and plugins *good* — drawn from a
> research wiki that ingested Garry Tan's `gstack`/`gbrain`, Every's
> compound-engineering plugin, OpenAI's Codex marketplace, Anthropic's skills +
> financial-services marketplaces, and a paid 235-skill "PM OS" — and (b) the
> Recoup skills repo, especially the `recoup-records` "record label in a box"
> bundle. It answers: *what is a "fat skill", how fat is fat, how much does one
> skill actually do, are ours fat enough, should ours be combined or split, and
> what should we steal.*
>
> **Audience.** A teammate who has **not** seen the research and does **not**
> have the originating chat. Everything needed to act is written down here, with
> real numbers and file paths. Nothing assumes prior context.
>
> **Date of analysis:** 2026-06-15. gstack was pulled fresh to **v1.58.1.0**
> (commit `c7ae6320`) for this comparison; earlier figures in the research wiki
> were captured at v1.42.2.0, so where they differ the newer number is used and
> noted.
>
> **Sources.** Research wiki at `~/Documents/Projects/Sidney/research/` (its
> `patterns/`, `concepts/`, `artifacts/`, and cloned `sources/`). Our repo at
> `~/Documents/Projects/Recoup/mono/skills/`.

---

## 0. TL;DR — the verdict in one screen

**What "fat skill" means (frontier definition).** A *fat skill* is a reusable
**markdown procedure that carries ~90% of a system's capability as judgment**,
sitting on top of a *thin* harness and a *thin-but-exact* deterministic code
layer. "Fat" is about **depth of encoded judgment and process**, not word count
for its own sake — but in practice the frontier's *substantive* skills are
**large**: gstack's capability/workflow skills run **~840–2,301 lines of
`SKILL.md` each (median ≈ 1,030)**, on top of which the biggest ones **carve even
more content into a `sections/` folder** loaded on demand. (A handful of tiny
utility/toggle skills — `freeze`/`unfreeze`/`guard`/`careful` at 48–91 lines —
are the exception, not the norm.) A mature pack ships dozens-to-hundreds of these
**with tests**.

**How fat is fat? (real numbers.)**

| Pack | Skills | Typical `SKILL.md` size | Tests/evals | Deterministic substrate |
|---|---|---|---|---|
| **gstack** (Garry Tan) | 54 | **~840–2,301 lines** for substantive skills (median ~1,030; a few utility skills 48–91) + carved `sections/` | ~1,100+ incl. **LLM evals + resolver evals**, `skill-size-budget` test | 62+ `bin/` CLIs, compiled `browse/` browser tool |
| **compound-engineering** (Every) | 38 + **43 subagents** | hundreds of lines (e.g. `/ce-compound` ~580) | **~1,094 cases** incl. behavioral **contract tests** | TS converter + `validate-frontmatter.py` |
| **gbrain** (Garry Tan) | 53 | hundreds | BrainBench evals + `check-resolvable` | zero-LLM graph/vector engine |
| **PM OS** (paid, PM vertical) | **235** (13 system + 11 workflow + 214 reusable) | mixed; reusable ones thin, workflows fat | stated, mostly unshipped | `bin/memory/*.sh` single-writer scripts |
| **Recoup `recoup-records`** | **41** | **42–380 lines** (`SKILL.md` body) | **0 LLM evals, 0 resolver evals**; hooks + `validate_*.py` validators only | deals/releases: heavy scripts; content/research/song: **none** |

**The headline gap.** Our **workflow bundles** (`recoup-deals`, `recoup-releases`)
are genuinely fat and well-architected — `recoup-deal-start` is a ~4,600-line
*system* (orchestrator + 16 scripts + references + hooks). But our **capability
plugins** (`recoup-content`, `recoup-research`, `recoup-song-analysis`) are
**thin**: 44–223-line `SKILL.md` bodies, reference-backed, with **no deterministic
scripts, no LLM evals, and no resolver evals anywhere in the repo**. By the
frontier's own definition, deals/releases are fat skills; content/research/song
are closer to **Anthropic's *demonstration* skills** (correct-but-minimal) than
to gstack's production fat skills.

**Are ours fat enough?** *Deals/Releases: yes (arguably even over-bundled).
Content/Research/Song: no — they are thin wrappers.* The single biggest
structural deficiency across the **whole** repo, fat parts included, is the
**missing test/eval layer** that the frontier treats as the *defining* property
of a skill ("a skill pack has tests"). We have completion-gate hooks and Python
validators, but **zero LLM-as-judge evals and zero resolver (routing) evals**.

**The five highest-leverage moves** (detailed in §7):
1. **Add the tested-bundle layer** — LLM evals for judgment skills, **resolver
   evals** for routing (the rarest, most valuable, and we have *none*).
2. **Fatten the thin capability skills** — encode real multi-phase procedure,
   decision-brief interaction, and verification gates, not 50-line API wrappers.
3. **Parameterize instead of proliferate** (skill-as-method-call) — collapse
   near-duplicate content/research skills into fewer, fatter, mode-driven skills.
4. **Add a compounding learnings store** (complexity-ratchet) — a `docs/solutions/`
   equivalent so each run makes the next better.
5. **Don't over-rotate into a "Foxconn factory"** — keep our deal scripts as
   *exact work*, not model-policing code; fatness is judgment, not defensive code.

---

## 1. The principles — what the frontier believes about skills & plugins

This section distills the research wiki's confirmed patterns. Each is stated
plainly, with the real-world evidence behind it, so you can apply it without
reading the source material.

### 1.1 The core architecture: **thin harness, fat skills**

The namesake thesis (Garry Tan, YC CEO, author of `gstack` at ~105K GitHub
stars) is that the gap between a "2x" and a "100x" AI engineer running the *same
model* "isn't intelligence — it's architecture." The architecture has **three
layers**:

- **Top — fat skills (≈90% of the value).** Reusable markdown procedures that
  teach the model *how* to do a task. This is where judgment lives. Editable
  prose, not logic frozen in code.
- **Bottom — thin-but-exact deterministic code.** Narrow single-purpose CLIs,
  compiled tools, SQL, arithmetic — the things the model must **never improvise**.
  "Thin" here means *narrow and fast*, not small in count (gstack has 62+ of them).
- **Middle — a thin harness (~200 lines).** Just loops the model, reads/writes
  files, manages context, enforces safety. This is the part you *don't* own — it's
  Claude Code / Codex / Cursor. Skills are **harness-agnostic**.

The directional rule: **"push intelligence up, push execution down, keep the
harness thin."** The economic payoff: when a better model ships, *every* fat
skill improves for free (the judgment in latent steps gets better) while the
deterministic floor stays perfectly reliable. You bank model progress.

**The named anti-pattern is the inverse — a *fat harness* wrapping *thin*
skills**: 40+ tool definitions eating the context window, "god-tools", a
REST-wrapper-per-endpoint — measured at "3× tokens, 3× latency, 3× failure rate."

> **Caveat the research itself flags:** even gstack strains the word "thin" — its
> root `SKILL.md` runs a ~100-line bash preamble (telemetry, learnings, timeline,
> routing) *before any skill logic*. The wiki calls this "infrastructure as
> preamble" and an internal tension. Lesson for us: don't confuse "fat skill"
> with "heavy boilerplate on every call."

### 1.2 **latent vs. deterministic** — the triage discipline

Every step is either **latent** (needs model judgment: read, interpret, decide,
synthesize) or **deterministic** (same input → same output: SQL, math, sorting,
date conversion). Put each on the side it belongs.

> *"The most common mistake in agent design isn't a wrong answer — it's a wrong
> **side**."* — deterministic work (timezone math, calendar lookup, 800-person
> seating optimization) done in latent space, where the model improvises and gets
> it plausibly, confidently wrong.

The load-bearing move is a **loop**: the model *writes* the deterministic tool,
then the tool *constrains* the model. gstack's `/scrape` (latent page-exploration)
graduates via `/skillify` into a deterministic `script.ts` + `script.test.ts`;
the next run is ~200ms instead of ~30s of re-exploration. Every's
compound-engineering states the same rule as an authoring principle:
**"Skills are guardrails for an intelligent agent, not a step-by-step controller
for a non-intelligent one — calibrate prescription to the failure mode"** (hard
rules for deterministic safety, trust for judgment).

**The inverse error matters too:** don't hard-code genuine judgment into brittle
rules. Seating 8 people by personality is *correctly* latent; only the 800-person
optimization belongs in code.

### 1.3 **skill-as-method-call** — parameterize, don't proliferate

A skill file is a **parameterized procedure invoked like a method call**: the
user supplies the *what* (a target, a question, a dataset, a depth tier); the
skill supplies the fixed *how*. Same markdown, radically different capability per
invocation.

- gstack's `/qa` ships **Quick / Standard / Exhaustive** tiers — one file, one
  procedure, a named depth argument.
- gstack's `/investigate` is a fixed four-phase procedure ("investigate, analyze,
  hypothesize, implement; Iron Law: no fixes without root cause") that re-aims at
  whatever bug you hand it.
- Codex's `/goal` ships a literal six-slot signature.

**The diagnostic test:** if different arguments run *different steps*, those are
**N skills wearing one filename** (the "god-skill" anti-pattern) — split them. If
the *process* stays fixed and only the *input/depth* varies, it's one method —
**don't fork it, parameterize it.** The canonical example: gstack's
`/match-breakout`, `/match-lunch`, `/match-live` are three invocations of one
matching procedure, *not* one mega-`/match` with a `mode=` flag — but they share
the procedure rather than copy-pasting it.

### 1.4 **skill-pack-bundle** — "a skill pack has tests"

This is the frontier's definition of a skill as a *unit*: not just a `SKILL.md`,
but a **tested bundle**. The 10-step "skillify checklist" (Garry Tan's
Skillify Manifesto):

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
10. **filing rules** (a knowledge-writing skill files by primary subject)

> *"A feature that doesn't pass all ten is not a skill. It's just code that
> happens to work today."*

Real evidence: gstack ships all of it as files (`skill-validation.test.ts`,
`skill-llm-eval.test.ts` at ~$0.15/run, `skill-e2e-*.test.ts` at ~$3.85/run,
three `*-resolver*.test.ts`), run under **diff-based selection** + a
**gate/periodic tier split** (cheap deterministic tests block every PR; expensive
LLM evals run on a weekly cron). Every's compound-engineering ships **~1,094 test
cases** including **behavioral contract tests** (`review-skill-contract.test.ts`)
and convention-as-test (`frontmatter.test.ts` enforces the description
constraints that make routing fire). gbrain enforces the whole checklist as
`gbrain doctor`.

**The rarest, most-stealable part: the *resolver eval*** — a test that the right
skill *fires* (and the wrong ones *don't*), not just that its output is good.
Almost nobody tests skill *triggering*. **We test neither.**

### 1.5 **resolver-routing-table** — tested routing at scale

A **resolver** is a routing table for context: *when intent X appears, load skill
Y first.* Two philosophies:

- **Explicit** (gbrain): a `RESOLVER.md` `trigger → skill` dispatcher read once
  per request, plus a `_brain-filing-rules.md` (`content-type → directory`), plus
  **15 `routing-eval.jsonl` fixtures** with *both* polarities (must-fire positives
  AND adversarial must-not-fire negatives), plus `check-resolvable` (a build gate
  that fails if any skill is "dark"/unreachable).
- **Implicit** (gstack, Anthropic demos): lean on the harness's built-in
  `description`-field auto-matching — *"the description **is** the resolver."*

**The threshold that matters to us:** Garry's observed breaking point is **~40
skills**. Below that, the harness's implicit description-matching resolves
cleanly. Past it, three failures appear: skills drift in their filing, skills go
**"dark"** (built but unreachable — "a surgeon the hospital can't find"), and the
table rots within ~90 days. **`recoup-records` has 41 skills — we are exactly at
that threshold, with no resolver eval and no reachability audit.**

### 1.6 **complexity-ratchet** — forward-only quality (a.k.a. compound engineering)

Every session adds tests/docs/evals/learnings that **reload into context**, so
the quality floor only ever rises. Every's independently-named twin is **compound
engineering**: *"each unit of work makes the next one easier."* Its load-bearing
step is `/ce-compound` → writes the solved problem into `docs/solutions/` with a
**5-dimension overlap dedup** (update the existing doc, don't create a near-dup),
then a **discoverability check** (does the project's `AGENTS.md` lead a *fresh*
agent to the store?). Branch protection on `main` is the "can't regress below the
floor" mechanism. Budget rule: **50/50** — half your effort on the system that
produces work, not just the work.

> **The counter-weight the research is careful about — the "Foxconn factory."**
> The *same* author who preaches "test everything" warns against over-building
> "systems" that *police* a capable model: ~276K lines of tests, a 1,778-line
> fact-checker fanning every claim to five sources. The line: skill-pack tests
> **pin a thin unit so it can change safely** (contracts); a Foxconn factory is
> **mountains of code written to distrust the model** (a cage). Same word
> ("tests"), opposite spirit.

### 1.7 Other confirmed patterns worth naming

- **single-source-multi-surface-distribution** — author once, ship to many
  harnesses (CE converts to ~11 platforms; PM OS adapts *names* per surface;
  gbrain ships CLI + MCP + skillpack from one definition). *We already do a
  version of this:* one source tree → per-harness manifests (`.claude-plugin`,
  `.cursor-plugin`, `.codex-plugin`) + vendored copies with a drift check.
- **persona-lens-review-panel** — review via parallel narrow persona reviewers
  (read-only, structured returns) merged by an orchestrator. CE has 43 review
  subagents; PM OS has a 9-reviewer PRD panel. *We have 8 specialist subagents.*
- **diarization** — read everything about a subject, write **one page of distilled
  judgment** (the "says vs. actually building" gap). "No SQL query produces this."
  Relevant to our artist/deal briefs.
- **session-start-directive** — session-start hooks must emit *imperative,
  position-pinned* directives, not passive context. *We use SessionStart only for
  env checks — a missed opportunity.*
- **version-as-update-gate** — `version` is the update-delivery trigger; release
  automation owns it, hand-bumps forbidden.

---

## 2. How fat is "fat"? — the anatomy of a frontier skill, with real numbers

"Fat" is easy to mis-hear as "long." It isn't. A fat skill is one that **encodes
enough judgment and process that the model reliably produces a finished,
trustworthy result without the user micromanaging it.** In the frontier packs
that depth happens to be *large*. Here is exactly what fills those lines.

### 2.1 gstack skill sizes (verified fresh at v1.58.1.0, 2026-06-15)

Every number below is a real `wc -l` of a shipped `SKILL.md` body. gstack has
**54 `SKILL.md` files**. They split into three bands:

```
Tiny utility / toggle skills (the exception):
  unfreeze 48   careful 67   guard 90   freeze 91   gstack-upgrade 284

Setup / single-tool skills:
  setup-browser-cookies 603   benchmark-models 631   benchmark 756   make-pdf 758

Substantive capability / workflow skills (the norm — ~840 to 2,301):
  ios-sync 837   ios-fix 844   diagram 894   scrape 920   document-release 932
  investigate 1,045   plan-eng-review 1,003   cso 1,256   ship 1,331
  plan-ceo-review 1,447   qa 1,655   office-hours 1,668   retro 1,783
  autoplan 1,823   review 1,823   design-review 1,965   spec 2,301   ...
```

**Median ≈ 1,030 lines; the substantive skills cluster ~840–2,301.** Two
important nuances (both correcting an earlier draft of this doc):

1. **There *are* small skills.** The lifecycle/toggle skills
   (`freeze`/`unfreeze`/`guard`/`careful`) are 48–91 lines — proof that even a
   "fat" pack keeps genuinely thin skills where the *job* is small. Fatness is
   matched to the job, not applied uniformly.
2. **The biggest skills got *smaller* in v1.58 via progressive disclosure.**
   Before v1.58, `ship` was **3,056** and `plan-ceo-review` **2,223** lines. They
   now **carve content into a `sections/` folder loaded on demand**, so the
   `SKILL.md` body shrank (`ship` → **1,331**, `plan-ceo-review` → **1,447**) while
   the *total* content stayed large: `plan-ceo-review` = 1,447 body + 923
   `sections/review-sections.md` ≈ **2,370 effective lines**; `office-hours` ≈
   2,211; `plan-eng-review` ≈ 1,927. gstack also now ships a
   `test/skill-size-budget.test.ts` that **ratchets size against a frozen
   baseline** — so fatness is **deliberately bounded and progressively
   disclosed**, not unbounded sprawl.

#### How gstack's `skill-size-budget` test actually works (verified)

It is **not a fixed "max N lines" cap.** It's a free, gate-tier regression test
(pure file-IO + JSON diff, no LLM) that diffs the current tree against a captured
baseline snapshot (`test/fixtures/parity-baseline-v1.47.0.0.json`, produced by
`scripts/capture-baseline.ts`). It enforces **four** budgets:

1. **Per-skill growth ceiling — ≤ 1.5× baseline.** No skill's `SKILL.md` bytes
   may exceed its baseline × `RATIO` (`DEFAULT_RATIO = 1.50`). It started at
   **1.05 (5%)** and was loosened to 1.50 in v1.52 because 5% tripped on
   legitimate feature additions — their note: *"real bloat is 2-3×; this catches
   that while not tripping on normal feature scope."* An anti-bloat ratchet keyed
   to **growth**, not to an absolute count.
2. **Total-corpus ceiling — ≤ 1.5× baseline.** The summed byte count of all
   skills can't regress past baseline × ratio (stops death-by-a-thousand-cuts).
3. **Per-skill shrink *floor* — ≥ 80% of baseline.** Catches accidental
   body-stripping (a resolver returning empty, a template dropping a section).
   Skills that **carved into `sections/`** are exempted (`CARVED_SKILLS`) and
   guarded instead by a "sectioned invariant" that checks `minBytes` on the
   **skeleton + sections union** — so progressive disclosure doesn't false-trip.
4. **The only *absolute* cap — the always-loaded catalog ≤ ~7,000 tokens**
   (`estTotalCatalogTokens ≤ 7000`). The "catalog" is the set of skill
   **descriptions** that load into **every** context window. Skill *bodies* load
   on demand, so they're only ratcheted (1–3); the catalog is paid on every
   request, so *it* gets a hard ceiling. This is "attention is the scarce
   resource" turned into a test.

Escape hatch: `GSTACK_SIZE_BUDGET_OVERRIDE_REASON="why"` lets a regression pass
but audit-logs it to `~/.gstack/analytics/spend-overrides.jsonl`;
`GSTACK_SIZE_BUDGET_RATIO=<n>` tunes the ratio. (A sibling test,
`skill-budget-regression.test.ts`, separately budgets *live* eval runs — tool
calls, turns, cost.)

**The lesson for us (sharpens P3):** the rule is *not* "cap skills at N lines."
It's a two-sided ratchet — **bodies may grow only ~1.5× between baselines and may
not silently shrink below 80%**, while the **always-loaded descriptions are
hard-capped (~7K tokens)**. Fat bodies are fine because they're lazy-loaded; a fat
*catalog* is not. Keep the always-loaded surface tight; push depth into on-demand
`sections/`/`references/`.

### 2.2 What actually fills those 1,000+ lines (the `/investigate` dissection)

Reading gstack's `investigate/SKILL.md` (1,045 lines) top to bottom, the line
budget breaks down roughly like this — and *this* is the anatomy of fat:

1. **Rich frontmatter** (~60 lines): `description` with explicit trigger phrases
   AND "proactively invoke when the user reports 500 errors / stack traces / 'it
   was working yesterday'"; `allowed-tools`; `triggers:` list; **PreToolUse hooks**
   wiring a freeze-scope check; a `gbrain:` block declaring context queries (prior
   investigations, project learnings, recent eureka moments).
2. **A bash preamble** (~120 lines): update check, session tracking, telemetry,
   per-project learnings load + grep, timeline logging, routing detection.
3. **First-run onboarding flow** (~100 lines): telemetry opt-in, proactive-mode
   prompt, CLAUDE.md routing-injection offer, vendoring-migration offer — all
   gated on marker files so they fire once.
4. **A strict interaction contract** (~80 lines): the **AskUserQuestion
   "decision brief" format** — every question must carry an ELI10 explanation,
   "stakes if we pick wrong," a recommendation, a completeness score, ≥2
   pros/≥1 con per option ≥40 chars, a "Net" tradeoff line, and effort labeled in
   *both* human-time and AI-time. This is encoded *judgment about how to ask*.
5. **The actual four-phase procedure** with an "Iron Law," worked sub-steps,
   evidence requirements, and exit criteria for each phase.
6. **Completion + write-back + reporting** discipline.

**Takeaway:** maybe ~250 of those lines are boilerplate preamble (the part the
research flags as a "thin"-tension). The other **~750 lines are encoded judgment**:
how to ask, how to decide, what counts as a root cause, what evidence to demand,
how to report. *That* is fat. The skill doesn't just say "debug the thing" — it
encodes a senior engineer's entire debugging discipline.

### 2.3 The two shapes of "how much one skill does"

The frontier packs show that "how much a skill does" splits cleanly:

- **Leaf / capability skills** do **one focused job** very thoroughly. gstack's
  `/qa`, `/investigate`, `/cso` (security audit), `/review`. Even these are
  1,000–1,700 lines because the *job* is deep (a full OWASP+STRIDE pass, a
  multi-phase debug). Each is independently invocable.
- **Orchestrator / workflow skills** **run a pipeline of other skills** and own a
  shared artifact. gstack's `/autoplan` (runs the whole plan-review pipeline),
  `/ship`. Every's `/ce-*` loop. PM OS's 11 **workflow skills** that chain its
  **214 reusable single-task skills**.

PM OS is the cleanest model for an "X-in-a-box" pack and the closest analog to
`recoup-records`: **235 skills in three explicit tiers** — 13 *system* skills
(onboarding, memory, tidy), 11 *workflow* orchestrators (`/strategy`, `/prd`,
`/research`), and **214 *reusable* single-task skills** (`bug-triage`,
`churn-reduction`, `breadboarding`). The workflows are fat; the 214 reusables are
deliberately thinner `jtbd` ("job to be done") units the workflows compose. So the
answer to *"how fat should every skill be?"* is **not "uniformly enormous"** — it
is **tiered**: fat orchestrators over a library of focused (but still real,
references-backed) leaf skills.

### 2.4 So: how fat is fat?

| Skill role | Frontier norm | What fills it |
|---|---|---|
| **Orchestrator / workflow** | 1,300–3,000 effective lines | pipeline control, workspace contract, phase gates, landing recap |
| **Deep capability / leaf** | 800–1,700 lines | full multi-phase procedure + interaction contract + verification |
| **Reusable single-task leaf** (PM OS tier) | 100–400 lines + `references/` | one job, references for shared context, still has a real procedure |
| **Demonstration skill** (Anthropic) | 30–150 lines | shows the *format*; intentionally minimal; not production |

**Our content/research/song skills (44–223 line bodies) sit in the bottom two
rows.** Our deal/release orchestrators sit in the top row *by total footprint*
(scripts included) but their `SKILL.md` *bodies* are still only 132–380 lines —
they push the depth into scripts and references rather than into the prose
procedure, which is a legitimate (and arguably better) choice for deterministic
work, but means the *judgment* layer is comparatively lean.

---

## 3. Our system — `recoup-records` and the source plugins, in depth

### 3.1 How our repo is organized

We author **six focused plugins** and **generate** a seventh, `recoup-records`,
which is the **"record label in a box"** — a build script
(`scripts/build_records_plugin.py`) copies every skill, agent, hook, reference,
script, template, and fixture from the focused plugins into one installable
bundle. (We copy, not symlink, because symlinks break on Windows checkouts.)
`recoup-records` is **generated, never hand-edited** — to change it you edit the
source plugin and re-run the builder.

The six sources, by archetype (we already have a documented taxonomy in
`docs/capability-plugins.md` and `docs/workflow-plugins.md`):

| Plugin | Archetype | Skills | What it is |
|---|---|---|---|
| `recoup-essentials` | **general** | 5 | the handful every team needs: API access, artist create, workspace, setup |
| `recoup-research` | **capability** | 11 | A&R/research toolbox: artist research, audience, playlists, scout, competition, tiktok, outreach, brief, streaming-monitor, web-research |
| `recoup-content` | **capability** | 11 | content toolbox: router + caption, video, lyric-video, visualizer, cover-art, thumbnail, graphic, trend, pack, reformat |
| `recoup-song-analysis` | **capability** | 3 | audio LM (Music Flamingo): analyze, hook, pitch-kit |
| `recoup-deals` | **workflow bundle** | 6 | catalog deal review: orchestrator + ingest, value, dashboard, report, demo |
| `recoup-releases` | **workflow bundle** | 5 | release campaign: orchestrator + brief, doc, campaign, demo |
| **`recoup-records`** | **mega-bundle** | **41** | all of the above, generated |

`recoup-records` also ships **8 specialist subagents**, a **hooks layer**, **37
scripts**, and **15 shared references**.

### 3.2 The hooks layer (this is genuinely strong)

`recoup-records/hooks/hooks.json` is a real, sophisticated guardrail layer — and
it directly embodies the research's **latent/deterministic split** and
**evidence-gated completion**:

- **`PreToolUse` (Write|Edit|MultiEdit) → `protect-source-files.sh`** — blocks any
  write into `deals/{id}/source/` (immutable evidence). This is the
  "agent can't cheat / source is immutable" principle from our own
  `workflow-plugins.md`.
- **`SessionStart` → `check-env.sh`** — advises on missing `RECOUP_API_KEY` /
  `ffmpeg` without blocking.
- **Three `Stop` completion-gate hooks** (prompt-type, LLM-judged):
  - *recoup-deals gate* — blocks "ready for IC/buyer/lender" claims unless
    `run-deal-checks.py` passed, `readiness-check` isn't `blocked`,
    `assumptions.yaml` + `evidence-ledger.json` exist, findings are closed, and
    memo claims trace to evidence. **Plus a mid-workflow gate** so
    `/recoup-deal-start` can't quit before producing a validated `DASHBOARD.html`.
  - *recoup-content analyze-gate* — blocks "here's your video/thumbnail, it's
    ready" unless an `/api/content/analyze` pass for that asset is in the
    conversation ("a render returning the right size is NOT evidence the content
    is good; the agent cannot see pixels without analyzing").
  - *recoup-releases gate* — blocks "release is ready" unless
    `validate_release.py` returned `status: ok`, required files exist, and no
    fabricated numbers.

This is **better than most frontier packs at completion-gating** (PM OS only
*self-attests*; we externally verify with scripts). It's a real strength.

### 3.3 Skill footprint — the actual numbers (SKILL.md + references + scripts)

Total lines per skill, measured 2026-06-15. This is the honest picture of where
our "fat" is and isn't:

**`recoup-deals` — a real workflow bundle, genuinely fat at the system level:**
```
recoup-deal-start    SKILL=287   refs=527/3f    scripts=3,818/16f   TOTAL=4,632
recoup-deal-ingest   SKILL=139   refs=650/5f    scripts=2,774/9f    TOTAL=3,563
recoup-deal-value    SKILL=189   refs=816/10f   scripts=1,701/10f   TOTAL=2,706
recoup-deal-report   SKILL=380   refs=0         scripts=1,632/9f    TOTAL=2,012
recoup-deal-dashboard SKILL=232  refs=0         scripts=1,632/9f    TOTAL=1,864
recoup-deal-demo     SKILL=132   refs=0         scripts=0           TOTAL=132
```

**`recoup-releases` — workflow bundle, fat via references:**
```
recoup-release-doc   SKILL=238   refs=1,547/3f  scripts=0           TOTAL=1,785
recoup-release-brief SKILL=258   refs=200/2f    scripts=0           TOTAL=458
recoup-release-start SKILL=164   refs=50/1f     scripts=208/2f      TOTAL=422
recoup-release-campaign SKILL=95 refs=0         scripts=113/1f      TOTAL=208
recoup-release-demo  SKILL=42    refs=0         scripts=0           TOTAL=42
```

**`recoup-research` — capability plugin, thin bodies + heavy *shared* references:**
```
recoup-artist-research    SKILL=223  refs=1,234/3f  scripts=0   TOTAL=1,457
recoup-artist-competition SKILL=152  refs=1,234/3f  scripts=0   TOTAL=1,386
recoup-artist-playlists   SKILL=128  refs=1,234/3f  scripts=0   TOTAL=1,362
recoup-artist-scout       SKILL=151  refs=974/2f    scripts=0   TOTAL=1,125
recoup-artist-audience    SKILL=149  refs=974/2f    scripts=0   TOTAL=1,123
recoup-web-research       SKILL=136  refs=974/2f    scripts=0   TOTAL=1,110
recoup-artist-outreach    SKILL=123  refs=974/2f    scripts=0   TOTAL=1,097
recoup-artist-brief       SKILL=223  refs=577/2f    scripts=0   TOTAL=800
recoup-artist-tiktok      SKILL=214  refs=577/2f    scripts=0   TOTAL=791
recoup-release-monitor    SKILL=117  refs=577/2f    scripts=0   TOTAL=694
recoup-artist-streaming   SKILL=103  refs=577/2f    scripts=0   TOTAL=680
```
*(Note: those big reference numbers are the **same** vendored files copied into
each skill — the per-skill *unique* content is the 103–223-line body. The shared
1,234/974/577-line reference bundles are byte-identical copies.)*

**`recoup-content` — capability plugin, the thinnest bodies in the repo:**
```
recoup-content-video      SKILL=154  refs=638/6f   scripts=0   TOTAL=792
recoup-content-trend      SKILL=95   refs=588/5f   scripts=0   TOTAL=683
recoup-content-pack       SKILL=70   refs=588/5f   scripts=0   TOTAL=658
recoup-content-lyric-video SKILL=67  refs=536/5f   scripts=0   TOTAL=603
recoup-content-visualizer SKILL=46   refs=536/5f   scripts=0   TOTAL=582
recoup-content-graphic    SKILL=68   refs=486/4f   scripts=0   TOTAL=554
recoup-content-reformat   SKILL=48   refs=486/4f   scripts=0   TOTAL=534
recoup-content-cover-art  SKILL=44   refs=486/4f   scripts=0   TOTAL=530
recoup-content-thumbnail  SKILL=44   refs=486/4f   scripts=0   TOTAL=530
recoup-content-caption    SKILL=123  refs=392/3f   scripts=0   TOTAL=515
recoup-content (router)   SKILL=87   refs=0        scripts=0   TOTAL=87
```

**`recoup-song-analysis` (thin) and `recoup-essentials` (general):**
```
recoup-song-analyze    SKILL=92   refs=199/1f  TOTAL=291      (song-analysis)
recoup-song-hook       SKILL=58   refs=199/1f  TOTAL=257
recoup-song-pitch-kit  SKILL=56   refs=199/1f  TOTAL=255
recoup-artist-workspace SKILL=247 refs=651/4f  TOTAL=898      (essentials)
recoup-artist-create   SKILL=285  refs=0       TOTAL=285
recoup-api             SKILL=244  refs=0       TOTAL=244
recoup-setup           SKILL=198  refs=0       TOTAL=198
recoup-setup-sandbox   SKILL=109  refs=0       TOTAL=109
```

### 3.4 What's good about our skills (don't lose this)

Reading representative skills (`recoup-content` router, `recoup-content-caption`,
`recoup-deal-start`), the craft is genuinely good:

- **Excellent descriptions** with explicit trigger phrases ("write a caption for
  [artist]", "what should [artist] post") — exactly what the implicit
  description-resolver needs to fire.
- **A real router skill** (`recoup-content`) with a decision tree and explicit
  cross-routing ("find the hook → that's *audio analysis*, use `recoup-song-hook`,
  not a transcript"). This is the capability-plugin router pattern, done right.
- **Self-containment + vendoring with a drift check** — matches the frontier's
  portability rule (CE's "skill references only its own directory; duplicate
  shared files"). Our `scripts/check_vendored.py` is our `check_vendored` gate.
- **Latent/deterministic awareness** — the caption skill lets the *model* draft
  in-voice (latent) and only calls the styling API for burned-in video text
  (deterministic-ish); deals push exact work into 16 scripts.
- **Strong guardrails** — "never fabricate the voice," analyze-gate before
  claiming a visual is done, immutable source files, completion gates.
- **A documented plugin taxonomy** (`docs/capability-plugins.md`,
  `docs/workflow-plugins.md`) that *already* articulates orchestrator vs router,
  workspace contracts, bundle-vs-chain, scope tokens, and modality suffixes. We
  are not naive about this.

---

## 4. Head-to-head — ours vs. theirs, by dimension

| Dimension | gstack / gbrain / CE / PM OS (frontier) | Recoup | Verdict |
|---|---|---|---|
| **`SKILL.md` body depth** | 800–3,000 lines; deep encoded judgment + interaction contracts | 42–380 lines; deals/releases lean on scripts/refs, content/research lean on tiny bodies | ⚠️ **Thin** on the judgment layer |
| **Total skill footprint** | huge across the board | deals 1.8K–4.6K (fat); content/research/song 250–1.5K (mostly vendored refs) | ✅ deals/releases fat · ⚠️ rest thin |
| **Deterministic substrate** | 62+ CLIs (gstack), converters (CE), zero-LLM graph (gbrain) | deals: 3.8K-line script suites ✅; **content/research/song: zero scripts** | ✅ deals · ❌ everywhere else |
| **Unit/integration tests** | gstack ~1,100+; CE ~1,094 | Python validators exist; **no unit-test suite per skill** | ❌ Gap |
| **LLM-as-judge evals** | gstack `skill-llm-eval.test.ts`; gbrain BrainBench | **none** | ❌ Major gap |
| **Resolver evals (does the right skill *fire*?)** | gstack 3 + gbrain 15 fixtures w/ adversarial negatives | **none** | ❌ Major gap (and we're at the 40-skill threshold) |
| **Reachability audit (`check-resolvable`)** | gbrain ships it as a build gate | **none** (we have manifest parity + vendoring drift checks, not routing reachability) | ❌ Gap |
| **Routing / resolver** | explicit `RESOLVER.md` (gbrain) or tested description-match (gstack) | router *skills* + good descriptions + cross-routing prose | ⚠️ Present but **untested** |
| **Completion gating** | PM OS self-attests; CE validates frontmatter | **3 LLM-judged Stop gates + script validators** | ✅ **We lead here** |
| **Immutable-source / anti-cheat** | implied | explicit `protect-source-files.sh` PreToolUse hook | ✅ **We lead here** |
| **Compounding learnings store** | CE `docs/solutions/` + dedup; gstack `learnings.jsonl` | **none** | ❌ Gap |
| **Parameterization (method-call)** | `/qa` tiers, `/goal` signature | demo skills have modes; most skills single-purpose | ⚠️ Under-used; some proliferation |
| **Multi-surface distribution** | CE converts to 11; PM OS adapts names | 3 per-harness manifests + vendoring | ✅ Comparable |
| **Persona review subagents** | CE 43, PM OS 12 | **8** | ✅ Proportionate to our scale |
| **Progressive disclosure (carve `sections/`)** | gstack v1.58 carves + size-budget test | references/ (similar idea) | ✅ Comparable in spirit |
| **Skill count** | gstack ~50, gbrain 53, CE 38, PM OS 235 | 41 (records) | ✅ Reasonable |

**Reading the table:** we are **at or ahead of the frontier on guardrails,
anti-cheat, completion gating, and distribution hygiene**, and **behind on the
entire test/eval layer and on judgment-depth for the capability skills.** The
deals/releases bundles are frontier-grade in *architecture*; what they lack is the
*tested-bundle* proof layer. The content/research/song skills lack both depth and
tests.

---

## 5. Diagnosis — are ours fat enough? combine? split?

### 5.1 `recoup-deals` — **fat enough; possibly over-engineered. Hold.**

`recoup-deal-start` is a 4,632-line system: orchestrator + 16 deterministic
scripts + 3 references + completion + mid-workflow hooks + immutable source. This
*is* a thin-harness/fat-skills system with a real deterministic substrate. It's
our best work and the closest thing we have to gstack-grade.

- **Fat enough?** Yes. This is a genuine workflow bundle.
- **Combine/split?** Leave the stages split (each is independently invocable —
  correct per our own `workflow-plugins.md`). Do **not** merge.
- **Watch:** the 3,818 lines of scripts on one skill flirt with the **Foxconn
  factory** line. Audit that those scripts are *exact work* (royalty math,
  normalization, validation) and not *model-policing* code. If any script exists
  to distrust the model rather than to compute something exact, it's a cage. (Most
  appear to be genuine ingestion/valuation math — good — but this is the one place
  we could be over-building.)
- **Real gap:** no LLM eval that "the IC memo is actually good," no resolver eval
  that "deal intents route to the deal skills." The gates check *existence and
  provenance*, not *quality*.

### 5.2 `recoup-releases` — **fat enough structurally; thinner substrate. Hold + harden.**

A workflow bundle with an orchestrator, a 1,547-line reference behind
`recoup-release-doc`, and a `validate_release.py` completion gate. Less
deterministic code than deals (208 script lines total) because release work is
more latent (briefs, campaigns). That's a defensible latent/deterministic call.

- **Fat enough?** Borderline-yes. `recoup-release-campaign` (95 lines, 0 refs,
  113 script lines) and `recoup-release-brief` are on the thin side for stage
  skills — they could encode more procedure.
- **Combine/split?** Keep split. Consider whether `campaign` and `brief` should be
  fatter rather than more numerous.

### 5.3 `recoup-research` — **thin; the prime candidate for parameterization.**

Eleven skills, each a 103–223-line body over the *same* vendored reference bundle
(1,234 / 974 / 577 lines copied repeatedly). The skills are essentially **API
wrappers with good descriptions**. They share a procedure (resolve artist → call
research API → synthesize) and differ mainly in *which slice of data* they pull
and *what question* they answer.

- **Fat enough?** No — these are thin. The depth lives in vendored references, not
  in encoded judgment.
- **This is the textbook `skill-as-method-call` situation.** `recoup-artist-research`,
  `recoup-artist-audience`, `recoup-artist-competition`, `recoup-artist-playlists`
  largely run the same procedure against different facets. The frontier move:
  **one fatter `recoup-artist-research` skill with a focus/depth parameter** (the
  `/qa` Quick/Standard/Exhaustive model), *or* keep them split but make each a
  genuinely deep analyst procedure (diarization: "write the one-page intelligence
  dossier, not a metrics dump").
- **Combine candidates:** `artist-streaming` (monitor) ↔ `artist-research`
  (on-demand) are an intentional on-demand/scheduled twin per our own docs — keep
  both but ensure they cross-route. `web-research` + `artist-research` overlap.
- **Split candidates:** none; if anything this plugin has *too many* thin skills.

### 5.4 `recoup-content` — **thinnest; combine the near-duplicate image/video skills OR fatten each.**

Eleven skills with 44–154-line bodies. Three of them — `cover-art` (44),
`thumbnail` (44), `graphic` (68) — are near-identical image-generation skills that
differ mainly by aspect ratio and overlay text. `visualizer` / `lyric-video` /
`video` are three motion skills sharing a backbone. The router (`recoup-content`,
87 lines) is good.

- **Fat enough?** No — these are the closest things in the repo to *demonstration*
  skills.
- **Two valid paths (pick per skill):**
  - **Parameterize/combine:** fold `cover-art` + `thumbnail` + (graphic's promo
    mode) into one `recoup-image` skill with an output-spec argument — exactly the
    "don't fork it, parameterize it" rule. The `graphic` skill *already* proves we
    do this (it has "carousel, promo, and quote modes" in one skill).
  - **Or fatten each leaf:** add a real procedure — reference-image handling,
    composition rules, the analyze-gate verification loop spelled out, benchmark
    against the artist's real top posts. The analyze-gate hook already exists;
    encode the *loop* (generate → analyze → regenerate if it fails) in the body.
- **Combine recommendation:** collapse the 3 static-image skills toward 1–2
  mode-driven skills; keep the 3 motion skills (the jobs differ more), but fatten
  their procedures. Net: ~11 → ~7–8 fatter skills.

### 5.5 `recoup-song-analysis` — **thin but correctly scoped; fatten lightly.**

Three skills over one 199-line reference. These are focused leaf skills on a real
capability (audio LM). They're thin but the *job* is narrow, so that's more
defensible than content/research. Fatten the procedure (what to extract, how to
turn analysis into a pitch) rather than splitting further.

### 5.6 `recoup-essentials` — **right-sized for a general plugin. Hold.**

`recoup-artist-create` (285) and `recoup-artist-workspace` (247 + 651 ref) are
appropriately substantial; `recoup-api` is a reference-style skill. Correct for
the "everyone needs these" tier. No change.

### 5.7 The `recoup-records` mega-bundle — **the 40-skill threshold is here.**

At 41 skills with no resolver eval and no reachability audit, `recoup-records` is
**exactly where the research says implicit description-routing starts to break**
(dark skills, drift, ambiguous fires). Two of our skills already overlap on
"playlists" and "research" across plugins. This is the strongest single argument
for adding the resolver-eval + `check-resolvable`-style layer **now**, before the
count grows.

---

## 6. What to steal — prioritized, with boundaries

Each item names the pattern, the concrete move, **and the boundary (when NOT to
do it)** — because carrying the boundary is what keeps us from cargo-culting.

### ★ P1 — Ship the tested-bundle layer (the #1 gap)

**Steal:** "a skill pack has tests." Add, per skill that matters:
- a **resolver eval** — a small fixtures file (`{intent, expected_skill,
  must_not_fire}`) with **adversarial negatives**, run as a test that the right
  skill fires for real user phrasings and overlapping intents *don't* mis-fire.
  This is the rarest, highest-value test and **we have zero**. Start with the
  overlapping pairs (`artist-research` vs `web-research`; the 3 image skills;
  `content` router vs `song-hook`).
- an **LLM-as-judge eval** for the judgment-heavy outputs (the IC memo, the
  brand-voice caption, the artist brief) — "is this actually good / in-voice /
  evidence-backed?", not just "does the file exist?".
- keep them **affordable** with gstack's trick: cheap deterministic checks gate
  every change; expensive LLM evals run on a cron/periodic tier.

**Boundary (when NOT to):** don't put resolver/LLM evals on *demonstration* or
*throwaway* skills, and don't build evals before a skill's shape stabilizes —
this is a *graduation* step. Don't let the eval suite become a Foxconn factory.

### ★ P2 — Add a `check-resolvable`-style reachability + routing layer to `recoup-records`

**Steal:** gbrain's reachability audit. At 41 skills we're at the threshold. Add a
CI check that every skill has a path that fires it (no "dark" skills) and that
overlapping descriptions are MECE. We already have `validate_manifests.py` and
`check_vendored.py` — add a `check_resolvable.py` sibling.

**Boundary:** below ~40 skills the implicit description-matcher is *correct* and a
`RESOLVER.md` is overhead. Don't add an explicit routing file for the *focused*
plugins (5–11 skills each) — only for the `recoup-records` mega-bundle.

### ★ P3 — Fatten the capability skills (content/research/song)

**Steal:** the *anatomy of fat* from §2.2. For each thin leaf, encode the actual
**multi-phase procedure + interaction contract + verification loop**, not a
50-line API wrapper. Concretely:
- a **decision-brief interaction format** (gstack's AskUserQuestion contract) for
  skills that must ask the user something — recommendation + stakes + tradeoff.
- **the analyze-gate loop written into the body** (generate → analyze →
  regenerate-if-failed → benchmark against the artist's real top posts), since the
  hook already enforces the gate.
- **diarization** for the briefs: "write the one-page intelligence dossier (what
  do they believe, what's actually working), not a metrics dump."

**Boundary:** fat ≠ verbose. gstack ships a `skill-size-budget` test *because*
fatness must be bounded and progressively disclosed. Push depth into
`references/` (we already do) and keep the `SKILL.md` body a tight, high-judgment
procedure. Don't pad.

### ★ P4 — Parameterize instead of proliferate (content + research)

**Steal:** `skill-as-method-call`. Collapse near-duplicate skills into fewer,
fatter, mode-driven ones (the 3 static-image skills → 1–2; consider a
focus-parameter on the artist-research family). Our `recoup-content-graphic`
already does this (carousel/promo/quote modes) — extend the pattern.

**Boundary:** only parameterize when the *process is the same* and only the
*input/depth* varies. If two "modes" would run genuinely different steps, they're
two skills — keep them split (the god-skill anti-pattern). The motion skills
(video/lyric/visualizer) differ enough to stay separate.

### P5 — Add a compounding learnings store (complexity-ratchet)

**Steal:** CE's `/ce-compound` → `docs/solutions/` with 5-dimension dedup + a
discoverability check. Give each workflow (deal, release) a place to write "what
we learned this run" that reloads next time, so the system gets smarter per use.

**Boundary:** only worth it for the *recurring* workflows (deals, releases), not
one-off content jobs. And keep the dedup discipline (update, don't duplicate) or
the store rots.

### P6 — Promote `SessionStart` from passive to imperative (session-start-directive)

**Steal:** PM OS's lesson that session-start hooks must emit *imperative,
position-pinned* directives, not passive context the model silently ignores. Our
`check-env.sh` just advises; it could *direct* ("RECOUP_API_KEY missing — run
`/recoup-setup` before any artist work").

**Boundary:** one directive per session; passive walls of context get ignored.

### P7 — Keep what we already lead on

Do **not** regress: the 3 LLM-judged completion gates, the immutable-source
PreToolUse hook, the analyze-gate, the vendoring drift-check, the documented
plugin taxonomy, the per-harness manifests. These are at or above frontier grade.

---

## 7. Applying this to "a record label in a box"

`recoup-records` is our PM-OS analog: a vertical "everything in a box." PM OS's
**tiered** structure is the model to converge toward:

- **System tier** (PM OS: 13 skills) — onboarding, memory, setup. *Ours:*
  `recoup-essentials` (setup, api, artist-create, workspace). ✅ Have it.
- **Workflow/orchestrator tier** (PM OS: 11) — fat front-doors that chain leaves.
  *Ours:* `recoup-deal-start`, `recoup-release-start`, the `recoup-content`
  router. ✅ Have a start; the content/research areas lack a true orchestrator
  beyond the router.
- **Reusable leaf tier** (PM OS: 214) — focused jobs the workflows compose.
  *Ours:* the content/research/song skills. ⚠️ These are leaves, but they're
  **thin** and **untested**, and there's no resolver layer tying 41 of them
  together.

**The "record label in a box" thesis works only if the box is trustworthy and
navigable.** From the research, the three things that make an X-in-a-box pack
actually deliver:

1. **Tested routing at scale** — the user (or an orchestrating agent) lands on the
   *right* skill every time. We're at the 40-skill threshold with no routing test.
   **(P1, P2.)**
2. **Fat, verifiable workflows over a library of real leaves** — fat orchestrators
   (deals/releases ✅) composing leaves that each do real, verified work. Our
   leaves need depth + verification loops. **(P3, P4.)**
3. **It compounds** — every deal, every release, every content pack makes the next
   one better via a learnings store. We have none. **(P5.)**

If we do P1–P5, `recoup-records` moves from "a good, well-guarded collection of
mostly-thin skills with two genuinely-fat workflow bundles" to "a tested,
self-improving, navigable label-in-a-box" — which is the frontier bar.

---

## 8. Appendix — the frontier packs at a glance (for the reader who wants receipts)

- **gstack** (Garry Tan / YC) — Claude Code skill pack, "virtual engineering team"
  (CEO, Designer, QA Lead, CSO, Release Engineer personas). ~50 skills @
  ~840–2,301 lines (median ~1,030; a few utility skills at 48–91) + carved
  `sections/`; 62+ `bin/` CLIs; compiled `browse/`
  browser tool (Playwright CLI, "75x faster" than a Chrome MCP for
  screenshot→click→read loops); ~1,100+ tests incl. LLM evals + 3 resolver evals;
  `skill-size-budget` test; diff-based gate/periodic test tiers. ~105,761 GitHub
  stars (verified). Pulled fresh at **v1.58.1.0** for this doc.
- **gbrain** (Garry Tan) — hybrid vector+graph memory; 53-skill skillpack over a
  thin CLI + zero-LLM-call knowledge graph; ships explicit `RESOLVER.md`,
  `_brain-filing-rules.md`, 15 `routing-eval.jsonl` fixtures, and
  `check-resolvable` as a build gate (`gbrain doctor`). The reference
  implementation of tested routing.
- **compound-engineering** (Every / Kieran Klaassen) — 38 skills + 43 review
  subagents; an 8-step loop (ideate→brainstorm→plan→work→review→compound) that
  dogfoods itself (27 brainstorms → 57 plans → 30 `docs/solutions/`); ~1,094 test
  cases incl. behavioral *contract* tests; authored once and converted to ~11
  harnesses. The non-Garry proof that "fat skills + tested bundle + forward-only
  quality" is a field-level idea, not one person's style. MIT.
- **PM OS** (prodmgmt.world, paid $99) — 235 skills (13 system + 11 workflow + 214
  reusable) + 12 agents + 2 hooks + 6 MCP servers + a paired workspace folder,
  governed by a deliberately *fat* 364-line behavioral harness (pre-flight
  attestation, Context Guard, deliverable gate). The closest structural analog to
  `recoup-records`, and the model for *tiering* skills.
- **Anthropic skills marketplace** — demonstration skills: minimal-frontmatter
  `SKILL.md` reference implementations, no tests, no resolver. The *correct*
  shape for teaching the format — and the "before" state the fat-skill patterns
  are a response to. Our thin content skills currently resemble these more than
  they resemble gstack.

### Key files in this repo referenced above
- `plugins/recoup-records/hooks/hooks.json` — the completion-gate + source-protect layer
- `docs/capability-plugins.md`, `docs/workflow-plugins.md` — our plugin taxonomy
- `scripts/build_records_plugin.py` — the mega-bundle generator
- `scripts/check_vendored.py`, `scripts/validate_manifests.py`,
  `scripts/portability_lint.py` — our existing gates (add a `check_resolvable.py` sibling — P2)

### Research wiki entry points (for deeper reading)
- `~/Documents/Projects/Sidney/research/for-builders.md` — the consumer front door
- `patterns/structural/thin-harness-fat-skills.md`, `patterns/quality-bar/skill-pack-bundle.md`,
  `patterns/behavioral/skill-as-method-call.md`, `patterns/behavioral/latent-vs-deterministic-split.md`,
  `patterns/composition/resolver-routing-table.md`, `patterns/quality-bar/complexity-ratchet.md`
- `artifacts/plugins/gstack.md`, `artifacts/plugins/compound-engineering.md`, `artifacts/plugins/pm-os.md`





