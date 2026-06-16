# Recoup — Record Label in a Box

> ⚗️ **EXPERIMENT BRANCH (`experiment/rolled-up-skills`).** This variant folds the
> 41 focused skills into **12** — five fat, mode-dispatching skills
> (`recoup-research`, `recoup-content`, `recoup-release`, `recoup-catalog`,
> `recoup-song`) + seven standalone foundation/utility skills. It exists to A/B
> the fat-skill style against the focused style on the main branch. See
> `docs/experiment-rolled-up-skills.md`.


> **First-class, hand-maintained plugin.** This is the flagship "everything in
> one install" bundle and is now maintained directly (it was originally generated
> from the focused plugins; that generation model is retired for it — see
> `docs/fat-skills-benchmark.md`). Edit skills here directly. The source plugins
> may drift from this bundle; that is expected and accepted.
>
> **Routing is governed by `RESOLVER.md`** (the skill dispatcher) and enforced by
> two CI gates: `scripts/check_resolvable.py` (every skill is reachable; no dark
> skills) and `scripts/run_resolver_eval.py` (routing fixtures in
> `resolver-eval.jsonl` at the plugin root, with coverage enforced — every skill
> needs a positive fixture). Add a `RESOLVER.md` row **and** a fixture whenever
> you add a skill.

The whole Recoup platform as a single plugin: artist setup and API access, music-industry research, catalog deal review, content creation, song audio analysis, and end-to-end release workflows — every skill, agent, and hook from the focused plugins, bundled together.

One install gives you everything below. Prefer a focused install? Install the
individual plugin instead — same skills, smaller surface.

| Source plugin | Status |
|---------------|--------|
| recoup-essentials | bundled |
| recoup-research | bundled |
| recoup-deals | bundled |
| recoup-content | bundled |
| recoup-song-analysis | bundled |
| recoup-releases | bundled |

## Install

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-records@recoup
```

## Maintain

Edit skills in `skills/` directly. After any change to the skill set, run the
routing gates (also run in CI):

```bash
python3 scripts/check_resolvable.py     # every skill reachable from RESOLVER.md
python3 scripts/run_resolver_eval.py     # routing fixtures valid + full coverage
```

The old generator (`scripts/build_records_plugin.py`) still exists for a one-off
reseed from the focused plugins, but it no longer gates CI and will overwrite
hand edits — use it only deliberately.
