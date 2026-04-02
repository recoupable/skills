# Recoupable Skills

*Spend more time doing what you love. Let agents handle the rest.*

---

## What Is This?

This is the **Recoupable Skills Monorepo** — a single home for every AI skill we build and maintain across the organization.

Each skill is a self-contained set of instructions, resources, and references that teaches AI agents how to do specific work — from songwriting to brand design to music business operations. Think of them as playbooks that agents follow so you don't have to repeat yourself.

## Repository Structure

This repo uses **git submodules** to pull in skill repos from across the [Recoupable](https://github.com/recoupable) organization. Each skill lives at the top level — no nested categories.

```
skills/                              ← monorepo root
├── CLAUDE.md                        ← instructions for Claude
├── AGENTS.md                        ← instructions for all AI agents
├── README.md                        ← you are here
│
├── artist-growth-threshold/          ← streaming threshold growth playbook
├── brand-guidelines/                ← brand identity system (private, opt-in)
├── chartmetric/                     ← music analytics API
├── release-management/              ← release campaign management
├── setup-sandbox/                   ← org & artist folder setup via Recoup CLI
├── songwriting/                     ← songwriting with the 7 C's
└── trend-to-song/                   ← cultural moment → song → campaign pipeline
```

## Getting Started

### Clone with all public skills

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

> **Note:** Some skills are private repos (like `brand-guidelines`) and won't clone automatically. If you're a Recoupable team member with access, opt in manually:
>
> ```bash
> git submodule update --init -- brand-guidelines
> ```

## Skills

| Skill | Description | Access |
|-------|-------------|--------|
| [brand-guidelines](./brand-guidelines/) | Recoupable's complete brand identity system — colors, typography, voice, illustration style | 🔒 Private |
| [chartmetric](./chartmetric/) | Music analytics API — streaming data, playlist placements, audience demographics, competitive analysis | Public |
| [release-management](./release-management/) | Manage music release campaigns — DSP pitches, metadata, marketing, press materials, and more | Public |
| [setup-sandbox](./setup-sandbox/) | Create org and artist folder structure using the Recoup CLI | Public |
| [songwriting](./songwriting/) | Song evaluation and writing using the 7 C's framework | Public |
| [trend-to-song](./trend-to-song/) | Turn trending cultural moments into songs and test campaigns in 72 hours | Public |
| [artist-growth-threshold](./artist-growth-threshold/) | Playbook for growing new artists past key streaming thresholds (1K listeners, Showcase, Marquee, Popularity 50) | Public |

## Adding a New Skill

### 1. Add the submodule

```bash
git submodule add https://github.com/recoupable/<repo-name>.git <folder-name>
git commit -m "Add <repo-name> skill"
```

> For private skills, use the SSH URL (`git@github.com:...`) and add `update = none` in `.gitmodules` so public users aren't affected.

### 2. Update this README

Add a row to the appropriate skills table above.

## Skill Format

Every skill directory must contain a `SKILL.md`. It may also include:

```
my-skill/
├── SKILL.md          ← required — instructions + YAML frontmatter
├── scripts/          ← optional — executable code (Python, Bash)
├── references/       ← optional — docs loaded on-demand
└── assets/           ← optional — templates, fonts, icons
```

### SKILL.md structure

```markdown
---
name: your-skill-name
description: What this skill does and when to use it
---

# Your Skill Name

Instructions, examples, and guidelines go here.
```

### Writing a good description

The `description` field is how Claude decides whether to load your skill. Be specific:

```markdown
# Bad — too vague
description: Helps with music projects

# Good — what + when + trigger phrases
description: Guide for writing and evaluating song lyrics and concepts.
Use when brainstorming song ideas, writing lyrics, evaluating song drafts,
refining hooks, or improving existing songs.
```

### Guidelines

- Keep `SKILL.md` under **5,000 words** — move heavy content to `references/`
- Put critical instructions at the top
- Use bullet points and lists over prose
- No XML angle brackets (`< >`) in skill files

## Contributing

1. Work in the individual skill repo
2. Keep skills focused — one clear purpose per skill
3. Follow the [brand guidelines](./brand-guidelines/) for any user-facing output
4. Test before committing:
   - Does the skill trigger on relevant requests?
   - Does it avoid triggering on unrelated topics?
   - Does the workflow complete without errors?

---

Built by [Recoupable](https://recoupable.com) — the new music industry.
