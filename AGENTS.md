# Agent Instructions — Recoupable Skills

This file provides context for any AI agent operating within this repository.

## Repository Purpose

Public skills for AI agents working in the music industry. Skills teach agents how to complete specific tasks — from songwriting to analytics to release campaigns.

## Structure

```text
recoupable/skills/
├── .claude-plugin/           ← plugin manifest for Claude Code
├── .codex-plugin/            ← plugin manifest for OpenAI Codex
├── skills/                   ← all skills live here
│   ├── chart-metric/
│   ├── content-creation/
│   ├── music-industry-research/
│   ├── song-writing/
│   └── ...
├── README.md
├── contributing.md
└── AGENTS.md                 ← this file
```

## How Skills Load

Skills use progressive disclosure:

1. **Frontmatter** (`name` + `description`) — always in context. This is how you decide whether to load a skill.
2. **SKILL.md body** — loaded when you determine the skill is relevant.
3. **Linked files** (`references/`, `scripts/`, `assets/`) — loaded on-demand as needed.

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
└── assets/           ← optional — templates, fonts, icons
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

## Portable Skill Contract (cross-harness)

Every skill must run on **any** harness (Claude Code, Codex, Cursor, bare `npx skills`) — not just as a Claude marketplace plugin. To guarantee this, each skill follows these rules. They are enforced by `scripts/portability_lint.py` in CI.

1. **Self-contained.** A skill reads/executes **only files inside its own directory** (`references/`, `scripts/`, `templates/`, `fixtures/`). Never reference `../`, `../../references/`, another skill's directory, or a plugin-root `scripts/`/`templates/`.
2. **No platform variables in the body.** Do **not** write `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}`, or any `$CLAUDE_*` path. These only expand in JSON configs (hooks/`.mcp.json`) on Claude Code and **do not exist on other harnesses** — they ship as literal, broken strings. Use plain relative paths.
3. **Reference docs with backtick paths, never markdown links.** Write `` `references/foo.md` `` (a backtick path the agent can locate), not `[foo](./references/foo.md)`. Agents interpret markdown links as CWD-relative `Read` calls, and the CWD is never the skill directory.
4. **Co-locate scripts; invoke relatively.** Ship scripts in the skill's own `scripts/` and call them as `python3 scripts/foo.py`. Add a one-line note that scripts ship alongside the skill. If a script imports a sibling or helper, that sibling must also live in the same `scripts/`.
5. **Duplicate shared material; drift-check it.** If two skills need the same reference/script, **copy it into each** (do not centralize). Register every copy in `scripts/vendored.json` so `scripts/check_vendored.py` keeps them byte-identical. Vendoring is allowed; silent divergence is not.

> Why: `${CLAUDE_PLUGIN_ROOT}` is Claude-Code-only and doesn't expand in markdown (anthropics/claude-code#9354); runtime CWD is the user's project, not the skill dir. Self-containment with relative/backtick paths is the only pattern that travels across harnesses.
