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

> **Setup, API access, and artist onboarding** (`recoup-setup`, `recoup-setup-sandbox`, `recoup-artist-workspace`, `recoup-create-artist`, `recoup-api`) now ship in the **Recoup Essentials** plugin below — start there.

## Plugins

Beyond the open skills library above, Recoup ships focused **plugins** — bundles of skills and agents for one workflow. Add the marketplace once, then install the plugins you need:

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-essentials@recoup
```

### Everything in one install

Want the whole platform without managing six plugins? Install **Recoup Records** — a record label in a box — a single bundle of every plugin's skills, agents, and hooks:

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-records@recoup
```

> Pick **one or the other** — install `recoup-records` for everything, *or* the focused plugins below for a smaller surface. Installing both would register the same skills twice. The bundle is generated from the focused plugins by `scripts/build_records_plugin.py`, so it never drifts.

| Plugin | What it does |
|--------|-------------|
| [Recoup Essentials](plugins/recoup-essentials) | Setup, API keys, sandbox scaffolding, artist creation, and direct Recoup API access — **start here** |
| [Recoup Research](plugins/recoup-research) | Music industry research — artist analytics, audience insights, playlist intelligence, competitive analysis, trend detection |
| [Recoup Deals](plugins/recoup-deals) | Music catalog deals — data-room ingestion, royalty normalization, rights checks, and valuation for buy-side, seller-prep, financing, and post-close |
| [Recoup Content](plugins/recoup-content) | Content workflows — draft, edit, and publish social-ready content for artists |
| [Recoup Song Analysis](plugins/recoup-song-analysis) | Song audio analysis — catalog metadata, lyrics, playlist pitches, sync briefs, and mix feedback via Music Flamingo |

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
