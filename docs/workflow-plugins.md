# Pattern: the workflow-bundle plugin

> Build-time reference for plugin authors. This doc is **not shipped** with any
> install and a `SKILL.md` must **never** link to it — embody the guidance as
> behavior instead.

Most plugins are a **capability area** — a cluster of related skills for one team
(e.g. a marketing toolkit, a research toolkit). A **workflow-bundle plugin** is a
different, higher-order shape: it packages an *entire end-to-end process* — every
stage, the shared artifact it builds, the deterministic tooling, and the
guardrails — behind a single front door, so the user types one thing and walks
away with a finished, trustworthy deliverable.

Think "type one command → get a populated workspace and an artifact you can open,"
not "here are twelve skills, sequence them yourself."

---

## When to use this pattern (and when not to)

Use a workflow bundle when **all** of these hold:

- There's a **named, recurring process** the user thinks of as one job (a release,
  a deal, a tour, an onboarding) — not just a topic.
- The process has **distinct stages** that hand off to each other.
- The stages accumulate into a **shared artifact** (a folder, a document, a
  dashboard) rather than producing disconnected one-off answers.
- The payoff of "run the whole thing in order" clearly beats "run pieces ad hoc."

Prefer a plain **capability plugin** when the skills are a loose family used
independently (analysis tools, content generators) with no single artifact or
mandatory order.

A repo can have **both**: capability/team plugins *and* one or more flagship
workflow bundles next to them. That mix is healthy — the bundle is just another
plugin type, not a replacement for the team plugins.

---

## The central idea: a shared workspace contract

A workflow only *bundles* if every stage advances the **same** artifact. The
single most important design decision is the **workspace contract**: a strict,
documented folder/document schema that every stage reads from and writes to.

```text
{process}/{instance-id}/
├── source/        # raw inputs, treated as immutable evidence
├── working/       # normalized / intermediate artifacts
├── findings/      # structured issues, gaps, exceptions
├── outputs/       # human-facing deliverables (memo, plan, dashboard)
├── assumptions.*  # values that affect the work but aren't in the inputs
└── evidence.*     # traces every material claim back to a source
```

(The exact subfolders are domain-specific — the point is the *contract*.) Each
stage's job becomes simple and composable: **read the workspace → do my phase →
write back → leave evidence.** The orchestrator is the conductor; the workspace is
the score. This is what lets stages compose instead of collide, and it's what lets
a chained-in skill from another plugin drop its output into the bundle cleanly.

A **template** of this workspace is scaffolded at the start of every run so every
instance begins identical.

---

## Anatomy (the ingredients of a strong bundle)

| Ingredient | What it is | Why it matters |
| --- | --- | --- |
| **Front-door orchestrator** | One entry-point skill that runs every stage in order, end-to-end, **without stopping to ask between phases** | The user types one thing and gets a finished artifact |
| **Stage skills** | One skill per phase of the process | Each phase is real work and also runnable on its own |
| **Shared workspace contract** | The strict folder/doc schema above | The connective tissue — see the section above |
| **Workspace template** | A scaffold copied in at the first phase | Deterministic, identical starting point |
| **Deterministic scripts** | Co-located code for the exact parts (math, normalization, validation) | The precise work is code, not prose; testable |
| **Specialist subagents** | Focused reviewers the orchestrator dispatches (often in parallel) | Deep review without bloating the main skill |
| **Guardrail hooks** | Protect immutable inputs; block "done" until the artifact exists and validates | The agent can't quit early or claim false completion |
| **Evidence / trust contract** | Every material claim traces to evidence or is labeled an assumption; a validator enforces it | The deliverable is *defensible*, not just pretty |
| **One customer-facing artifact** | A single "open this first" deliverable; everything else is provenance | Clear payoff; no ambiguity about what to look at |
| **Demo + golden fixtures** | A demo path that runs the full flow on synthetic data; input→expected pairs | Onboarding and regression testing in one |
| **Variants via references** | Process modes (e.g. by deal type, by release type) swap a *reference deep-dive*, not a whole skill | Flexes the workflow without skill proliferation |
| **Power-user escape hatches** | Each stage is also invocable directly | Beginners run the front door; experts run one stage |

Not every bundle needs all twelve. A solid **v1** is: orchestrator + workspace
contract + template + the stage skills + one clear artifact + a demo. Scripts,
hooks, subagents, and the trust validator are the **v2** hardening that makes it
production-grade.

---

## Two principles that make the output *delightful*

1. **Determinism where it counts, creativity where it delights.** Put the exact,
   must-be-right work (calculations, normalization, validation) in co-located
   scripts with tests. Let the agent **author** the final deliverable (a
   dashboard, a plan, a memo) with full creative freedom on layout and
   narrative — but gate it with a validator that rejects unverified claims.
   Trustworthy *and* beautiful.

2. **The agent can't cheat.** Make source inputs immutable (a pre-write hook) and
   refuse to let the run end until the artifact exists and passes validation (a
   stop-gate). This is what turns "want me to continue?" stalls into a reliably
   finished artifact.

---

## Closed vs. open domains: bundle vs. chain

The hardest design question is **scope** — what lives *inside* the bundle.

- **Closed-domain workflow:** every stage skill is specific to this process and
  reused nowhere else. Bundle *everything* — the whole pipeline is self-contained.
- **Open-domain workflow:** some stages use **general-purpose** skills that are
  also used outside this process (e.g. audience analysis used for both a release
  and a tour; a monitor that runs whether or not there's an active campaign).

For an **open-domain** workflow, do **not** copy the general skills into the
bundle (that causes drift) and do **not** rip them out of their home team (that
guts the capability plugins). Instead:

> **Bundle the process-specific skills + the orchestrator + the workspace.
> *Chain* the general-purpose skills** — they stay in their team plugin and the
> orchestrator invokes them by name, with the shared workspace as the hand-off
> surface.

A skill still lives in exactly one plugin. The orchestrator composing a skill that
lives elsewhere is fine — that's chaining, not ownership. The workspace contract is
what keeps a chained-out skill's output coherent with the rest of the bundle.

**Litmus test for each stage skill:** *"Is this skill meaningless outside this
process?"* If yes → it belongs in the bundle. If it has standalone value → leave it
in its team plugin and chain to it.

---

## Build blueprint

1. **Name the process and its artifact.** What single thing does a finished run
   produce? ("a populated release workspace + a rollout plan", etc.)
2. **Define the workspace contract** (folders/doc schema + assumptions + evidence)
   and write a **template** for it.
3. **List the stages** in order. For each, decide **bundle vs. chain** with the
   litmus test above.
4. **Write the orchestrator skill** as the front door: run all stages in order,
   don't pause between phases, end on the artifact, and print a final landing
   recap (what's ready, what to open first, what was skipped and why).
5. **Write/locate the stage skills.** Bundle the process-only ones; cross-route to
   the general ones.
6. **Add a demo** that runs the full flow on synthetic data.
7. **(Hardening)** Add deterministic scripts + tests for exact work, a completion
   hook, an evidence/trust validator for the artifact, and specialist review
   subagents.
8. **Add power-user commands** for running a single stage.

---

## Quality bar

- One command produces a real, openable artifact — not a "want me to continue?".
- Every material number in the artifact traces to evidence or a labeled assumption.
- The run is honest about gaps ("skipped X because Y") instead of papering over them.
- A newcomer can run the demo and immediately see what the bundle produces.
- A power user can run any single stage without the orchestrator.

If a "bundle" is really just several skills in a folder with no shared workspace,
no orchestrator, and no single artifact — it's a capability plugin wearing a
costume. The workspace contract and the front door are what make it a workflow
bundle.
