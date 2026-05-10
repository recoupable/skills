# Agent Instructions — Recoup Skills Marketplace

Context for any AI agent operating within this repository.

## Repository Purpose

Recoup's unified marketplace of agent skills and plugins for the music industry. It is simultaneously a **skill collection** (broad skills under `skills/`), a **plugin marketplace** (manifests at the repo root), and a **plugin host** (self-contained plugins under `plugins/`).

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
│       └── references/
│
└── scripts/
    ├── generate-marketplaces.py          ← Regenerate platform marketplace JSONs
    └── validate-manifests.py             ← Validate every manifest + skill
```

A new vertical plugin earns its own folder under `plugins/` when it has **at least 3 related skills** AND needs commands, agents, scripts, templates, or MCP integrations.

## Rules

1. **Read before you act.** Always read a skill's `SKILL.md` before executing or referencing it.
2. **Respect boundaries.** Skills are self-contained. No cross-dependencies between skills.
3. **Design for composability.** Multiple skills may be loaded at once. Never assume yours is the only one active.
4. **Keep it simple.** Prefer the simplest working solution.
5. **One skill, one job.** Each skill does one thing well.
6. **Description is the trigger.** Vague descriptions don't activate the skill — include trigger phrases users would say.
7. **No secrets in skills.** Reference environment variables — never hardcode credentials.
8. **`marketplace.source.json` is the source of truth.** Never hand-edit the three generated marketplace files. Edit the source and run `python3 scripts/generate-marketplaces.py`.

## Skill Format

Every skill directory must contain a `SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name
description: What it does and when to use it. Include trigger phrases.
---
```

## Validation

Before committing changes:

```bash
python3 scripts/validate-manifests.py
```

Checks performed:

1. Generated marketplace files match `marketplace.source.json`.
2. Every plugin's `source` path exists and is a directory.
3. Every skill listed in a virtual plugin is a directory with valid `SKILL.md` frontmatter.
4. Every plugin folder under `plugins/` has `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and `.cursor-plugin/plugin.json`.
5. Every `SKILL.md` has `name` and `description` frontmatter.

Validation runs on every PR via CI.
