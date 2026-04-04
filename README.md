# Recoupable Skills

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

### General — works for anyone

| Skill | What it does |
|-------|-------------|
| [chartmetric](skills/chartmetric) | Query and analyze music data from the Chartmetric API |
| [songwriting](skills/songwriting) | Structured songwriting using the 7 C's method |
| [artist-growth-threshold](skills/artist-growth-threshold) | Identify streaming threshold milestones for artist growth |
| [trend-to-song](skills/trend-to-song) | Turn cultural moments into songs and campaign strategies |

### Platform — requires a [Recoupable](https://recoupable.com) account

These skills integrate with the Recoupable platform. They require a Recoup API key or CLI access.

| Skill | What it does |
|-------|-------------|
| [setup-sandbox](skills/setup-sandbox) | Scaffold the workspace for an account's orgs and artists via the Recoup CLI |
| [artist-workspace](skills/artist-workspace) | Manage artist directories — context, songs, brand, audience |
| [release-management](skills/release-management) | Plan and execute release campaigns |
| [brand-guidelines](skills/brand-guidelines) | Apply Recoupable's brand identity to agent outputs |

## Creating a Skill

Use the [template](template/SKILL.md) to get started. Every skill needs:

1. A `SKILL.md` file with YAML frontmatter (`name` + `description`)
2. A clear description that tells the agent **when** to use it
3. Instructions the agent follows to complete the task

```
skills/
└── my-skill/
    ├── SKILL.md              ← required
    ├── references/           ← optional — docs loaded on-demand
    ├── scripts/              ← optional — executable code
    └── assets/               ← optional — templates, fonts, icons
```

See [contributing.md](contributing.md) for guidelines.

## About

[Recoupable](https://recoupable.com) is an AI-powered music management platform. These skills power the agents that help artists and labels manage their careers.

- **Website**: [recoupable.com](https://recoupable.com)
- **App**: [chat.recoupable.com](https://chat.recoupable.com)
- **Support**: agent@recoupable.com
