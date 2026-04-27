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

| Skill | What it does |
|-------|-------------|
| [getting-started](skills/getting-started) | Install CLI, get API key, connect via MCP/REST — start here |
| [artist-workspace](skills/artist-workspace) | Manage artist directories — context, songs, brand, audience |
| [streaming-growth](skills/streaming-growth) | Grow a new artist past streaming milestones that unlock platform tools |
| [chart-metric](skills/chart-metric) | Query and analyze music data from the Chartmetric API |
| [content-creation](skills/content-creation) | Create social videos, TikToks, Reels, and visual content using AI primitives |
| [music-industry-research](skills/music-industry-research) | Music industry research — artist analytics, people search, competitive analysis, web intelligence |
| [recoup-api](skills/recoup-api) | Call the Recoupable API from the sandbox — artist data, socials, orgs, reports |
| [release-management](skills/release-management) | Plan and execute release campaigns |
| [setup-sandbox](skills/setup-sandbox) | Scaffold the workspace for an account's orgs and artists |
| [song-writing](skills/song-writing) | Structured songwriting using the 7 C's method |
| [trend-to-song](skills/trend-to-song) | Turn cultural moments into songs and campaign strategies |

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
    └── assets/               ← optional — templates, fonts, icons
```

See [contributing.md](contributing.md) for guidelines.

## About

[Recoupable](https://recoupable.com) is an AI-powered music management platform. These skills power the agents that help artists and labels manage their careers.

- **Website**: [recoupable.com](https://recoupable.com)
- **App**: [chat.recoupable.com](https://chat.recoupable.com)
- **Support**: agent@recoupable.com
