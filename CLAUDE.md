# Claude — Recoupable Skills Monorepo

Welcome. Here's what you need to know about this codebase.

## What This Repo Is

This is a **monorepo** containing all of Recoupable's AI agent skills. Skills are instruction sets (markdown files) that teach AI agents how to perform specific tasks — songwriting, brand application, music operations, and more.

## Repo Structure

- **All skills** are pulled in as **git submodules** — each links to its own repo in the `recoupable` GitHub org
- Every skill directory contains a `SKILL.md` file with YAML frontmatter (`name`, `description`) and the full instruction set
- Skills are organized into two categories:
  - **`external/`** — outward-facing skills that power the product (customers, partners)
  - **`internal/`** — skills for the Recoupable team's own operations

## How Skills Load

Skills use progressive disclosure — three tiers:

1. **Frontmatter** (`name` + `description`) — always loaded. This is how you decide whether to load a skill.
2. **SKILL.md body** — loaded when the skill is relevant to the task.
3. **Linked files** (`references/`, `scripts/`) — loaded on-demand as needed.

The `description` field is the most important line in any skill — it determines when the skill activates.

## How to Work Here

1. **Read the skill's `SKILL.md`** before modifying or referencing any skill — it's the source of truth
2. **Follow brand guidelines** from `internal/brand-guidelines/SKILL.md` for any user-facing content or artifacts
3. **Keep skills self-contained** — each skill folder should work independently without relying on other skills
4. **One purpose per skill** — don't combine unrelated capabilities into a single skill

## Voice & Tone

Recoupable's voice is warm, brief, and human-first. When generating any content or copy:
- Write like a thoughtful friend, not a press release
- Short sentences. Breathe between thoughts.
- Guide, don't command
- Technology serves people, not the reverse

Refer to `internal/brand-guidelines/SKILL.md` for the full brand identity system.

## Submodules

This repo uses git submodules. If a directory appears empty, the submodule hasn't been initialized. Run:

```bash
git submodule init
git submodule update
```

## Key Files

| File | Purpose |
|------|---------|
| `README.md` | Repo overview and setup instructions |
| `CLAUDE.md` | This file — context for Claude |
| `AGENTS.md` | Instructions for all AI agents working in this repo |
| `internal/brand-guidelines/SKILL.md` | Full brand identity system |
| `*/*/SKILL.md` | Each skill's instruction set |
