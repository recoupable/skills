# Recoup — Record Label in a Box

> ⚗️ **EXPERIMENT BRANCH (`experiment/rolled-up-skills`).** This variant restructures
> the plugin into a **middle tier grouped into domains** — **capability** domains
> (`roster`, `research`, `song`, `content`, `release`, `catalog`) plus a **platform**
> domain (operating the system). Every name is uniform
> `recoup-[domain]-[verb]-[noun]`. It sits between the focused and fat-skill extremes —
> the empirically-recommended hybrid (see `docs/ab-eval-results.md`,
> `docs/experiment-rolled-up-skills.md`, and the layout in
> `docs/skill-rename-proposal-v3.md`). Songwriting was removed.


> **First-class, hand-maintained plugin.** This is the flagship "everything in
> one install" bundle, maintained directly. It was originally generated from the
> focused plugins, which have since been consolidated into it — edit skills here
> directly.
>
> **Routing is governed by `RESOLVER.md`** (the skill dispatcher) and enforced by
> two CI gates: `scripts/check_resolvable.py` (every skill is reachable; no dark
> skills) and `scripts/run_resolver_eval.py` (routing fixtures in
> `resolver-eval.jsonl` at the plugin root, with coverage enforced — every skill
> needs a positive fixture). Add a `RESOLVER.md` row **and** a fixture whenever
> you add a skill.

The whole Recoup platform as a single plugin: artist setup and API access, music-industry research, catalog deal review, content creation, song audio analysis, and end-to-end release workflows — every skill, agent, and hook from the focused plugins, bundled together.

One install gives you the full platform — setup & API access, research, catalog
deals, content, song analysis, and releases — as a single self-contained plugin.

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
