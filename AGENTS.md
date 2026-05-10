# Agent Instructions — Recoupable Skills Marketplace

This file provides context for any AI agent operating within this repository.

## Repository Purpose

This is **Recoupable's unified marketplace** of agent skills and plugins for the music industry. It is simultaneously:

1. A **skill collection** — broad music skills under `skills/`.
2. A **plugin marketplace** — installable bundles listed in three platform marketplace files at the repo root.
3. A **plugin host** — self-contained vertical plugins live under `plugins/`.

Supported agents: **Claude Code**, **OpenAI Codex**, **Cursor**.

## Structure

```text
recoupable/skills/
├── .claude-plugin/marketplace.json       ← Claude Code marketplace (generated)
├── .agents/plugins/marketplace.json      ← Codex marketplace (generated)
├── .cursor-plugin/marketplace.json       ← Cursor marketplace (generated)
│
├── marketplace.source.json               ← SINGLE SOURCE OF TRUTH — edit this
│
├── skills/                               ← Broad music skills
│   └── {skill-name}/
│       ├── SKILL.md          ← required — instructions + YAML frontmatter
│       ├── references/       ← optional — docs loaded on-demand
│       ├── scripts/          ← optional — executable code
│       └── assets/           ← optional — templates, fonts, icons
│
├── plugins/                              ← Self-contained vertical plugins
│   └── {plugin-name}/
│       ├── .claude-plugin/plugin.json
│       ├── .codex-plugin/plugin.json
│       ├── .cursor-plugin/plugin.json
│       ├── skills/
│       ├── agents/
│       ├── commands/
│       ├── scripts/
│       ├── templates/
│       ├── evals/
│       ├── fixtures/
│       └── references/
│
└── scripts/
    ├── generate-marketplaces.py          ← Regenerate platform marketplace JSONs
    └── validate-manifests.py             ← Validate every manifest + skill
```

## How Skills Load (progressive disclosure)

1. **Frontmatter** (`name` + `description`) — always in context. This is how the agent decides whether to load the skill.
2. **SKILL.md body** — loaded when the agent decides the skill is relevant.
3. **Linked files** (`references/`, `scripts/`, `assets/`) — loaded on-demand.

The `description` field is the trigger. If it's vague, the skill won't activate.

## Two Skill Locations

| Location | Owned by | When to add here |
| -------- | -------- | ---------------- |
| `skills/{name}/` | the `recoupable-skills` virtual plugin | Generic music skill that any music operator might use |
| `plugins/{plugin-name}/skills/{name}/` | that specific plugin | Skill that depends on the plugin's templates, scripts, agents, commands, or workspace |

A new vertical plugin earns its own folder under `plugins/` when it has **at least 3 related skills** AND needs commands, agents, scripts, templates, or MCP integrations.

## Rules

1. **Read before you act.** Always read a skill's `SKILL.md` before executing or referencing it.
2. **Respect boundaries.** Skills are self-contained. No cross-dependencies between skills.
3. **Design for composability.** Multiple skills may be loaded at once. Never assume yours is the only one active.
4. **Keep it simple.** Prefer the simplest working solution.
5. **One skill, one job.** Each skill does one thing well.
6. **No secrets in skills.** Reference environment variables — never hardcode credentials.
7. **`marketplace.source.json` is the source of truth.** Never hand-edit the three generated marketplace files. Edit the source and run `python3 scripts/generate-marketplaces.py`.

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
description: What it does and when to use it. Include trigger phrases.
---
```

### Writing the description

- Start with **what** the skill does.
- Include **when** to use it — mention trigger phrases users would say.
- Be specific — vague descriptions won't trigger.

## Validation

Before committing changes:

```bash
python3 scripts/validate-manifests.py
```

Checks performed:

1. Generated marketplace files match `marketplace.source.json`.
2. Every plugin's `source` path exists.
3. Every skill listed in a virtual plugin exists and has valid frontmatter.
4. Every plugin folder under `plugins/` has `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and `.cursor-plugin/plugin.json`.
5. Every `SKILL.md` has `name` and `description` frontmatter.

Validation runs on every PR via CI.
