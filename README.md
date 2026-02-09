# Recoupable Skills

*Spend more time doing what you love. Let agents handle the rest.*

---

## What Is This?

This is the **Recoupable Skills Monorepo** — a single home for every AI skill we build and maintain across the organization.

Each skill is a self-contained set of instructions, resources, and references that teaches AI agents how to do specific work — from songwriting to brand design to music business operations. Think of them as playbooks that agents follow so you don't have to repeat yourself.

## Repository Structure

This repo uses **git submodules** to pull in skill repos from across the [Recoupable](https://github.com/recoupable) organization. Skills are organized into two categories:

- **`external/`** — Skills that power outward-facing agent work (product, customers, partners)
- **`internal/`** — Skills for the Recoupable team's own operations

```
skills/                              ← monorepo root
├── CLAUDE.md                        ← instructions for Claude
├── AGENTS.md                        ← instructions for all AI agents
├── README.md                        ← you are here
│
├── external/                        ← outward-facing skills
│   ├── chartmetric/                 ← music analytics API
│   ├── release-management/          ← release campaign management
│   └── songwriting/                 ← songwriting with the 7 C's
│
└── internal/                        ← Recoupable team skills
    └── brand-guidelines/            ← brand identity system
```

## Getting Started

### Clone with all submodules

```bash
git clone --recurse-submodules https://github.com/recoupable/skills.git
```

### Already cloned? Pull in submodules

```bash
git submodule init
git submodule update
```

### Update all submodules to latest

```bash
git submodule update --remote --merge
```

## Skills

### External

Skills that power Recoupable's AI agents — the capabilities customers and partners interact with.

| Skill | Description |
|-------|-------------|
| [chartmetric](./external/chartmetric/) | Music analytics API — streaming data, playlist placements, audience demographics, competitive analysis |
| [release-management](./external/release-management/) | Manage music release campaigns — DSP pitches, metadata, marketing, press materials, and more |
| [songwriting](./external/songwriting/) | Song evaluation and writing using the 7 C's framework |

### Internal

Skills for the Recoupable team — how we operate, communicate, and stay on-brand.

| Skill | Description |
|-------|-------------|
| [brand-guidelines](./internal/brand-guidelines/) | Recoupable's complete brand identity system — colors, typography, voice, illustration style |

## Adding a New Skill

### 1. Decide the category

- Does it serve customers or partners? → `external/`
- Does it serve the Recoupable team? → `internal/`

### 2. Add the submodule

```bash
git submodule add https://github.com/recoupable/<repo-name>.git external/<folder-name>
git commit -m "Add <repo-name> as external skill"
```

### 3. Update this README

Add a row to the appropriate skills table above.

## Skill Format

Every skill directory must contain a `SKILL.md` with this structure:

```markdown
---
name: your-skill-name
description: What this skill does and when to use it
---

# Your Skill Name

Instructions, examples, and guidelines go here.
```

## Contributing

1. Work in the individual skill repo
2. Keep skills focused — one clear purpose per skill
3. Follow the [brand guidelines](./internal/brand-guidelines/) for any user-facing output
4. Test your skill before committing

---

Built by [Recoupable](https://recoupable.com) — the new music industry.
