# Agent Instructions — Recoup Skills

This file provides context for any AI agent operating within this repository.

## Repository Purpose

Public skills for AI agents working in the music industry. Skills teach agents how to complete specific tasks — from songwriting to analytics to release campaigns.

## Structure

This repo **is a single flat plugin** rooted at the repo root: every skill lives in `skills/`, and the shared components (agents, hooks, references, templates, fixtures, the resolver) sit alongside it. It installs across every harness — as a Claude/agents marketplace plugin, a Codex plugin, or a bare `npx skills add recoupable/skills`.

```text
recoupable/skills/            ← the repo root IS the plugin
├── skills/                   ← every skill (recoup-[domain]-[verb]-[noun]); recoup-internal-* are staff-gated
│   ├── recoup-roster-add-artist/
│   ├── recoup-research-the-web/
│   ├── recoup-internal-dev-issue-tracker/
│   └── ...                   (31 skills, flat)
├── agents/                   ← specialized subagents
├── hooks/                    ← lifecycle hooks (hooks.json + *.sh)
├── references/               ← shared docs (canonical sources for any vendored copies)
├── templates/                ← workspace scaffolds
├── fixtures/                 ← golden / demo data
├── RESOLVER.md               ← routing table (request → one skill)
├── resolver-eval.jsonl       ← routing fixtures
├── scripts/                  ← validation gates + vendored.json (shared-file registry)
├── .claude-plugin/           ← plugin.json + marketplace.json (Claude registry)
├── .codex-plugin/            ← plugin.json (Codex)
├── .agents/plugins/          ← marketplace.json (Cursor / agents registry)
├── README.md
├── contributing.md
└── AGENTS.md                 ← this file (CLAUDE.md symlinks here)
```

## Glossary

- **Skill** — a `SKILL.md` folder that teaches one task. Portable; runs on any agent.
- **Plugin** — this repo, rooted at the repo root: it ships every skill in `skills/` **plus** agents, hooks, and shared references, installed through a runtime's plugin system or `npx skills`. A skill is a subset of the plugin. (No slash-`commands/` — skills only; see "No slash-commands".)
- **Harness** — a runtime that loads skills/plugins: Claude Code, Codex, Cursor, or bare `npx skills`.
- **Marketplace registry** — the single installable-plugin entry (`recoup-skills`, `source "."`), written in `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`.
- **Canonical / vendored** — when two places need the same file, one copy is the *canonical* source and the rest are byte-identical *vendored* copies tracked in `scripts/vendored.json` (currently empty — no shared copies today).
- **Resolver** — the repo-root `RESOLVER.md` routing table that maps a user request to the one skill that should handle it. Skills stay flat and discoverable; there is no separate "router" entry-point skill. Reachability is enforced by `scripts/check_resolvable.py`.

## How Skills Load

Skills use progressive disclosure:

1. **Frontmatter** (`name` + `description`) — always in context. This is how you decide whether to load a skill.
2. **SKILL.md body** — loaded when you determine the skill is relevant.
3. **Linked files** (`references/`, `scripts/`, `templates/`, `fixtures/`) — loaded on-demand as needed.

The `description` field is the trigger. If it's vague, the skill won't activate.

## Rules

1. **Read before you act.** Always read a skill's `SKILL.md` before executing or referencing it.
2. **Respect boundaries.** Each skill is self-contained. No cross-dependencies between skills.
3. **Design for composability.** Multiple skills may be loaded at once. Never assume yours is the only one active.
4. **Keep it simple.** Prefer the simplest working solution.
5. **One skill, one job.** Each skill does one thing well.
6. **No secrets in skills.** Reference environment variables — never hardcode credentials.

## Skill Format

Every skill directory must contain a `SKILL.md`:

```text
my-skill/
├── SKILL.md          ← required — instructions + YAML frontmatter
├── references/       ← optional — docs loaded on-demand
├── scripts/          ← optional — executable code
├── templates/        ← optional — scaffold files copied into a workspace
└── fixtures/         ← optional — sample / golden data
```

### Frontmatter

```yaml
---
name: skill-name
description: What it does and when to use it
---
```

### Writing the description

- Start with **what** the skill does
- Include **when** to use it — mention trigger phrases users would say
- Be specific — vague descriptions won't trigger

## The plugin (this repo)

The whole repo is one flat plugin. There is **no `plugins/` directory** and no per-plugin subfolders — add capabilities by adding **skills** to `skills/`, not by creating new plugins.

- **Add a skill** by creating `skills/recoup-[domain]-[verb]-[noun]/SKILL.md` (see "Skill Format"), then add a route in `RESOLVER.md` and a fixture in `resolver-eval.jsonl`. CI fails on any skill that isn't reachable from the resolver.
- **Manifests live at the repo root** — `.claude-plugin/plugin.json` (Claude), `.codex-plugin/plugin.json` (Codex), and the two `marketplace.json` files. Skills auto-resolve from `skills/`; you don't enumerate them in the manifest.
- **Shared components sit at the root** too: `agents/`, `hooks/`, `references/`, `templates/`, `fixtures/`. A skill must still be **self-contained** — it may reference only files inside its own directory, so a skill that needs a shared reference vendors its own copy (Portable Skill Contract rule 5). The root `references/` is the canonical source for any such copies and is also used by `agents/` and `hooks/`.
- Every skill follows the **Portable Skill Contract** below.

## No slash-commands — skills only

**Do not author `commands/` (slash-command files) in any plugin.** This repo
standardizes on **skills** as the single authoring primitive across every harness.

Why:

- **A skill already gives you a `/slash` entry for free.** Every harness
  auto-registers `/skill-name` when it loads a `SKILL.md` — you don't need a
  command file to get a typed entry point.
- **Commands are redundant or gone on the harnesses we ship to.** Claude Code
  *merged* custom commands into skills (a command file is just the old format).
  Codex *deprecated and removed* standalone prompts/commands in favor of skills.
  Only Cursor still treats commands as a distinct primitive — not enough to
  justify a layer that's dead weight everywhere else.
- **One primitive, no drift.** A command that wraps a single skill is pure
  duplication to keep in sync. Skills also do everything commands did *plus*
  supporting files, invocation control, and auto-invocation.

What to do instead:

- **Need a branded/orchestrating entry point** (e.g. "run research + audience +
  playlists, then synthesize")? Write a **skill** that names and chains the other
  skills. Make it manual-only with `disable-model-invocation: true` if it must
  not auto-fire.
- **Never** add a `commands` path to any `plugin.json`.

> Exception: hook **commands** in `hooks/hooks.json` (`"type": "command"`) are a
> different thing — shell commands run on lifecycle events. Those are fine.

## The marketplace registry

The single plugin (`recoup-skills`, `source "."`) is listed in **two files that must stay identical in content**:

- `.claude-plugin/marketplace.json` (Claude)
- `.agents/plugins/marketplace.json` (Cursor / agents)

`scripts/validate_manifests.py` enforces this "dual-manifest parity" on `(name, source, version)` — **edit one, edit the other**. Keep the version in both marketplaces and both `plugin.json` files in sync.

**Author email must match across layers:** the marketplace entry's email must equal the email in `plugin.json`. Use `agent@recoupable.com` everywhere (the support email documented in `CLAUDE.md`).

## Naming & branding

- Slugs are **plain-English, lowercase, hyphenated** — no filler suffixes: `recoup-song-find-hook`, not `recoup-song-find-hook-finder`.
- **The plugin name drops any `-plugin` suffix**: `recoup-skills`, not `recoup-skills-plugin`.
- Pattern: `recoup-[domain]-[verb]-[noun]` — four words, domain-first, so the `/` list auto-clusters by domain and every name says what it does. Domains are a small, stable set (`platform`, `roster`, `research`, `song`, `content`, `release`, `catalog`); a skill slots into an existing one. **Internal staff skills** add an `internal` segment — `recoup-internal-[domain]-[verb]-[noun]` (five tokens) — and are gated behind the literal `recoup-internal` trigger keyword in their `description`. The plugin routes to its skills through the root `RESOLVER.md` table — no separate router skill.
- Preserve history on renames/moves with `git mv`, then update the `name:` frontmatter, cross-references, README tables, and `scripts/vendored.json` paths.

## Portable Skill Contract (cross-harness)

Every skill must run on **any** harness (Claude Code, Codex, Cursor, bare `npx skills`) — not just as a Claude marketplace plugin. To guarantee this, each skill follows these rules. They are enforced by `scripts/portability_lint.py` in CI.

1. **Self-contained.** A skill reads/executes **only files inside its own directory** (`references/`, `scripts/`, `templates/`, `fixtures/`). Never reference `../`, `../../references/`, another skill's directory, or a plugin-root `scripts/`/`templates/`.
2. **No platform variables in the body.** Do **not** write `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}`, or any `$CLAUDE_*` path. These only expand in JSON configs (hooks/`.mcp.json`) on Claude Code and **do not exist on other harnesses** — they ship as literal, broken strings. Use plain relative paths.
3. **Reference docs with backtick paths, never markdown links.** Write `` `references/foo.md` `` (a backtick path the agent can locate), not `[foo](./references/foo.md)`. Agents interpret markdown links as CWD-relative `Read` calls, and the CWD is never the skill directory.
4. **Co-locate scripts; invoke relatively.** Ship scripts in the skill's own `scripts/` and call them as `python3 scripts/foo.py`. Add a one-line note that scripts ship alongside the skill. If a script imports a sibling or helper, that sibling must also live in the same `scripts/`. If a script needs a third-party package, **guard the import and name the package in the error** (`except ImportError: sys.exit("needs X — pip3 install X")`) rather than shipping a `requirements.txt` — the failing script then tells the agent exactly what to install.
5. **Duplicate shared material; drift-check it.** If two skills need the same reference/script, **copy it into each** (do not centralize). Register every copy in `scripts/vendored.json` so `scripts/check_vendored.py` keeps them byte-identical. Vendoring is allowed; silent divergence is not.

> Why: `${CLAUDE_PLUGIN_ROOT}` is Claude-Code-only and doesn't expand in markdown (anthropics/claude-code#9354); runtime CWD is the user's project, not the skill dir. Self-containment with relative/backtick paths is the only pattern that travels across harnesses.

## Validation gates (run before every PR)

Five scripts gate the repo. **All five must exit 0** — don't track the counts, track the exit code:

```bash
python3 scripts/portability_lint.py        # every skill is cross-harness portable
python3 scripts/check_vendored.py          # vendored copies are byte-identical to canonical
python3 scripts/validate_manifests.py      # manifests valid + marketplace parity
python3 scripts/check_resolvable.py        # every skill reachable from RESOLVER.md (no dark skills)
python3 scripts/run_resolver_eval.py       # routing fixtures valid + full coverage
```

**This repo is the flagship, hand-maintained plugin** — "a record label in a box" rooted at the repo root that ships the full platform in one install: artist setup and API access, research, catalog deals, content, song analysis, and releases — every skill (in `skills/`), agent, hook, reference, script, template, and fixture. It also ships Recoup's internal eng/ops skills (`recoup-internal-*`, staff-gated behind the `recoup-internal` keyword). Edit the skills directly.

**Editing a shared (vendored) file:** change the *canonical* copy only, then re-sync every copy listed in `scripts/vendored.json` (there is no `--sync` flag — copy them yourself), then re-check. Groups come in two shapes: single files (`canonical`/`copies`) and whole directories (`canonical_dir`/`copies_dirs`):

```bash
python3 - <<'PY'
import json, shutil
for group in json.load(open("scripts/vendored.json"))["groups"]:
    if "canonical" in group:                       # single-file group
        for copy in group["copies"]:
            shutil.copyfile(group["canonical"], copy)
    else:                                           # directory group
        for dest in group["copies_dirs"]:
            shutil.copytree(group["canonical_dir"], dest, dirs_exist_ok=True)
PY
python3 scripts/check_vendored.py
```

Never hand-edit a vendored copy — `check_vendored.py` fails on any drift.
