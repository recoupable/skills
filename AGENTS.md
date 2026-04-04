# Agent Instructions — Recoupable Skills

This file provides context for any AI agent operating within this repository.

## Repository Purpose

Public skills for AI agents working in the music industry. Skills teach agents how to complete specific tasks — from songwriting to analytics to release campaigns.

## Structure

```
recoupable/skills/
├── .claude-plugin/           ← plugin manifest for Claude Code
├── skills/                   ← all skills live here
│   ├── chartmetric/          ← general
│   ├── songwriting/          ← general
│   ├── artist-workspace/     ← platform (requires Recoup)
│   └── ...
├── template/                 ← starter template for new skills
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

```
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
