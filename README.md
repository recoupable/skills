# Recoup Skills

AI agent skills for the music industry. Teach your coding agent how to manage artists, write songs, analyze analytics, plan releases, and more.

## Install

### Claude Code

```bash
/plugin marketplace add recoupable/skills
```

### Manual

Clone and point your agent at the `skills/` directory:

```bash
git clone https://github.com/recoupable/skills.git
```

## Skills

| Skill | What it does |
|-------|-------------|
| [streaming-growth](skills/streaming-growth) | Grow a new artist past streaming milestones that unlock platform tools |
| [brand-guidelines](skills/brand-guidelines) | Apply Recoupable's brand identity to agent outputs |
| [chartmetric](skills/chartmetric) | Query and analyze music data from the Chartmetric API |
| [content-creation](skills/content-creation) | Create social videos, TikToks, Reels, and visual content using AI primitives |
| [music-industry-research](skills/music-industry-research) | Music industry research — artist analytics, people search, competitive analysis, web intelligence |
| [release-management](skills/release-management) | Plan and execute release campaigns |
| [songwriting](skills/songwriting) | Structured songwriting using the 7 C's method |
| [trend-to-song](skills/trend-to-song) | Turn cultural moments into songs and campaign strategies |

> **Setup, API access, and artist onboarding** now ship inside the **Recoup Records** plugin below.

## Plugins

Beyond the open skills library above, Recoup ships two **plugins** — richer bundles of skills, agents, and hooks. Add the marketplace once, then install what you need:

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-records@recoup
```

| Plugin | What it does |
|--------|-------------|
| [Recoup Records](plugins/recoup-records) | A record label in a box — the whole platform in one install: artist setup & API access, research, catalog deals, content, song analysis, and releases |
| [Recoup Internal](plugins/recoup-internal) | Recoup's internal engineering & ops — write and ship high-signal GitHub tracking issues docs-first and test-driven, benchmark skill packs against the frontier, work the catalog-valuation sales funnel in Attio, and produce account-health snapshots |

## Creating a Skill

Every skill needs:

1. A `SKILL.md` file with YAML frontmatter (`name` + `description`)
2. A clear description that tells the agent **when** to use it
3. Instructions the agent follows to complete the task

```text
skills/
└── my-skill/
    ├── SKILL.md              ← required
    ├── references/           ← optional — docs loaded on-demand
    ├── scripts/              ← optional — executable code
    ├── templates/            ← optional — scaffold files copied into a workspace
    └── fixtures/             ← optional — sample / golden data
```

See [contributing.md](contributing.md) for guidelines.

## About

[Recoupable](https://recoupable.com) is an AI-powered music management platform. These skills power the agents that help artists and labels manage their careers.

- **Website**: [recoupable.com](https://recoupable.com)
- **App**: [chat.recoupable.com](https://chat.recoupable.com)
- **Support**: agent@recoupable.com
