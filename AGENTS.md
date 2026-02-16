# Agent Instructions — Recoupable Skills Monorepo

This file provides context for any AI agent operating within this repository.

## Repository Purpose

This monorepo holds all of Recoupable's AI agent skills. Each skill is a set of markdown-based instructions that teaches agents how to complete specific tasks reliably and consistently.

## Structure

Each skill lives at the top level as its own directory (git submodule). No nested categories.

```
skills/                              ← monorepo root
├── CLAUDE.md                        ← Claude-specific instructions
├── AGENTS.md                        ← this file (all agents)
├── README.md                        ← human-readable overview
│
├── brand-guidelines/                ← brand identity system (private, opt-in)
├── chartmetric/                     ← music analytics API
├── release-management/              ← release campaign management
└── songwriting/                     ← songwriting skill
```

## How Skills Load

Skills use **progressive disclosure** — Claude doesn't load everything at once:

1. **Frontmatter** (`name` + `description`) — always in context. This is how Claude decides whether to load a skill.
2. **SKILL.md body** — loaded when Claude determines the skill is relevant.
3. **Linked files** (`references/`, `scripts/`, `assets/`) — loaded on-demand as needed.

The `description` field is the trigger. Write it well or the skill won't activate.

## Rules for All Agents

1. **Read before you act.** Always read a skill's `SKILL.md` before executing, modifying, or referencing it.
2. **Respect boundaries.** Each skill is self-contained. Do not create cross-dependencies between skills.
3. **Design for composability.** Multiple skills may be loaded at once. Never assume yours is the only one active.
4. **Follow the brand.** Any user-facing output must follow `brand-guidelines/SKILL.md`. This includes voice, tone, colors, and typography.
5. **Keep it simple.** Prefer the simplest working solution. Don't over-engineer skills.
6. **One skill, one job.** Each skill should do one thing well. Don't merge unrelated capabilities.
7. **Document changes.** If you add or modify a skill, update the README's skills table.

## Submodules

All skill repos are linked via git submodules. If a skill folder appears empty, run:

```bash
git submodule init && git submodule update
```

> Some skills (like `brand-guidelines`) are private and won't auto-clone. They are opt-in — team members with access can run `git submodule update --init -- brand-guidelines`.

## Skill Format

Every skill directory must contain a `SKILL.md`. It may also include:

```
my-skill/
├── SKILL.md          ← required — instructions + YAML frontmatter
├── scripts/          ← optional — executable code (Python, Bash)
├── references/       ← optional — docs loaded on-demand
└── assets/           ← optional — templates, fonts, icons
```

### SKILL.md structure:

```markdown
---
name: skill-name
description: What it does and when to use it
---

# Skill Name

Instructions, workflows, examples, and guidelines.
```

### Writing the description:

- Start with **what** the skill does
- Include **when** to use it — mention trigger phrases users would actually say
- Be specific — vague descriptions won't trigger
- No XML angle brackets (`< >`) anywhere in skill files

### Skill size:

- Keep `SKILL.md` under **5,000 words**
- Move heavy reference material to `references/`
- Put critical instructions at the top
- Use bullet points and numbered lists over prose

## Brand Voice (Quick Reference)

- Warm, not corporate
- Short sentences
- Human-first — technology serves people
- Guide, don't command
- Never cold, dystopian, or jargon-heavy
