# When an end-to-end process is a skill vs. when it needs a plugin

> Build-time reference for plugin authors. This doc is **not shipped** with any
> install and a `SKILL.md` must **never** link to it — embody the guidance as
> behavior instead. Companions: `capability-plugins.md`, `workflow-plugins.md`.

A whole, multi-step **end-to-end process** does not automatically require a
plugin. Sometimes the entire process belongs in **one skill**; sometimes it
genuinely needs a **plugin** (a bundle of skills + orchestration + non-skill
components). Getting this call right is the difference between a clean, editable
capability and either (a) an over-engineered plugin around something that was
always one skill, or (b) a 1,500-line mega-skill straining to be a system.

This doc is the **atom-vs-molecule** decision. The other two docs cover *what
shape of plugin* to build **once you've decided you need one**.

---

## First, the two things precisely

- **A skill** (`SKILL.md` + optional co-located `references/`, `scripts/`,
  `assets/`) is **one callable capability** — think of it as a parameterized
  method the agent invokes when its trigger matches. Its "stages" are *internal
  steps the model runs in sequence within a single invocation*. It can be
  surprisingly fat: a skill can run a 10-step procedure, call its own scripts, and
  produce a finished artifact — all on its own.
- **A plugin** is a **multi-component bundle**: one or more skills *plus*
  optionally subagents, hooks, an MCP/connector, evals, fixtures, and a
  marketplace entry — installed and versioned as a unit. (Per the cross-lab plugin
  spec, those are the components a plugin can carry.)

So the real question is **not** "is this process big?" It's: **can this process
live as one callable capability, or does it need machinery a single skill can't
hold?**

---

## A single skill CAN be the entire end-to-end process when…

Default here. Reach for one skill first; only escalate when a trigger below fires.

A single skill suffices when **all** of these hold:

- **One coherent capability, one primary artifact.** The process produces one
  deliverable (a model, a brief, a report) and a user asks for it as one job.
- **One invocation completes it.** The model can run the whole procedure start to
  finish in a single conversation/turn-sequence without the user needing to
  invoke separate pieces.
- **The "stages" are internal steps, not independently-useful skills.** Nobody
  would run "stage 3" on its own; the steps only make sense as part of the whole.
- **It fits the size budget.** The instructions fit a scannable `SKILL.md` body
  (rule of thumb: keep the body well under ~500 lines), with detail pushed into
  the skill's own `references/` via progressive disclosure.
- **No components beyond skill + its own files.** No need for parallel specialist
  subagents, completion/guardrail hooks, or an MCP server.
- **The deterministic work is a thin, co-located layer.** Any exact computation
  lives in the skill's own `scripts/` — not a large shared toolchain several
  skills depend on.

**Grounded examples (single-skill end-to-end processes):**
A financial-modeling skill (e.g. an LBO model, a DCF, a 3-statement model) is a
*complete multi-step process* — map the template, populate historicals, build
projections, run integrity checks, deliver the workbook — and it lives entirely
in **one** `SKILL.md` with its own scripts. In this repo, the weekly artist brief
and the pre-release creative brief are the same shape: full multi-step procedures,
one artifact, one skill.

> The litmus: **"Would anyone ever want to run just one stage of this on its
> own?"** If no → it's internal steps → one skill.

---

## You need a PLUGIN for the process when ANY of these is true

Escalate from one skill to a plugin the moment a process needs machinery a skill
can't carry. Any single trigger is enough:

1. **Independently-invocable stages.** Power users will want to run one phase
   (just the ingest, just the dashboard) without the whole run. That implies
   multiple **stage skills** + a front-door **orchestrator** → a plugin.
2. **A shared workspace/state across stages.** If multiple skills must read and
   write the *same* accumulating artifact (a structured folder, a master doc),
   you need the workspace-contract + orchestration of a plugin, not one skill.
3. **Non-skill components are required:**
   - **Subagents** dispatched (often in parallel) for specialist review.
   - **Hooks** — guardrails that protect inputs or *gate completion* (don't let
     the agent quit until the artifact exists and validates).
   - An **MCP server / connector** the capability depends on.
   - **Evals / golden fixtures / a demo** shipped with the capability.
4. **A shared deterministic toolchain.** Several stages depend on the same
   co-located scripts (normalizers, validators, calculators) with their own test
   suite — that shared `scripts/` belongs at plugin root, vendored into the skills
   that use it.
5. **It won't fit one coherent `SKILL.md`.** If progressive disclosure can't keep
   a single skill scannable and the body sprawls past its budget, the process is
   probably several skills.
6. **You want to ship/version/distribute it as one installable unit** with its own
   marketplace entry and update cadence.

**Grounded examples (plugin-required end-to-end processes):**
A catalog **deal review** or a **release rollout** — each spans distinct stages
(intake → analysis/brief → build → report/monitor), accumulates into a shared
workspace, dispatches specialist reviewers, and gates completion. None of that
fits one skill; it's a plugin (specifically a *workflow bundle* — see
`workflow-plugins.md`).

> Note the asymmetry: **the skill can be fat; the trigger to escalate is
> structural, not size.** A 400-line skill that runs 12 internal steps is still a
> skill. A 3-step process where each step is independently invocable, shares a
> workspace, and needs a completion hook is already a plugin.

---

## The decision in one pass

```text
Is the whole process one callable capability with one primary artifact,
completable in a single invocation, with no independently-useful stages
and no need for subagents / hooks / MCP / a shared toolchain?
        │
        ├── YES → ONE SKILL (fat skill + its own references/scripts). Stop here.
        │
        └── NO  → a PLUGIN. Then choose the plugin shape:
                  • One named process, staged, shared workspace, one artifact
                      → workflow-bundle plugin   (workflow-plugins.md)
                  • A team's many independent end-to-end skills, no fixed order
                      → capability plugin         (capability-plugins.md)
```

Two failure modes this prevents:

- **Over-building:** wrapping a single-skill capability in a plugin (orchestrator,
  workspace, hooks) it never needed. If there are no independent stages and no
  non-skill components, you built a molecule where an atom would do.
- **Cramming:** forcing a true multi-stage system (independent stages, shared
  state, guardrails) into one giant `SKILL.md`. Prose has no compiler; a 1,500-line
  skill drifts silently and can't be run stage-by-stage. Split it into a plugin.

---

## A subtlety: "plugin" answers two different needs

Deciding you need a plugin doesn't always mean you need an *orchestrated process*.
A plugin is also just the **install/ownership unit** for a **team's collection of
independent end-to-end skills** — e.g. a financial-analysis plugin that ships a
dozen standalone modeling skills (LBO, DCF, comps, …), each its own complete
process, with no mandatory order among them. That's a **capability plugin**, not a
workflow bundle. So:

- Many independent end-to-end skills for one audience → **capability plugin**
  (each skill is still a single-skill end-to-end process; the plugin just packages
  and ships them together).
- One end-to-end process whose stages must be orchestrated over shared state →
  **workflow-bundle plugin**.

Both are "plugins"; only the second is a process that *couldn't* have been one
skill.

---

## Quality bar

- A single-skill end-to-end process reads as one scannable `SKILL.md`, produces one
  artifact, and never asks the user to invoke a sub-step.
- A process promoted to a plugin has a real reason from the trigger list — name it
  ("needs a completion hook + independently-runnable stages"), don't promote by
  reflex.
- No plugin exists solely to hold one skill that had no independent stages and no
  non-skill components.
- No `SKILL.md` is secretly a multi-stage system with shared state crammed into one
  file.

If you can't name which escalation trigger forced the plugin, you probably have a
(possibly fat) single skill — ship it as one skill.
