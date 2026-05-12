# Recoup Skills

The official marketplace of AI agent **skills** and **plugins** for the music industry.

One repo. Multiple installable plugins. Works with Claude Code, Codex, and Cursor.

## What's in the marketplace

| Plugin | What it is | What you get |
| ------ | ---------- | ------------ |
| [`recoup-skills`](./skills/) | Broad music-industry skills | Artist management, songwriting, analytics, release campaigns, research, content creation, brand |
| [`music-catalog-diligence`](./plugins/music-catalog-diligence/) | Vertical bundle for catalog deals | Royalty normalization, rights diligence, valuation workpapers, IC memos — skills + agents + commands + scripts |

## Install

### Claude Code

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-skills@recoup
/plugin install music-catalog-diligence@recoup
```

### Codex

```bash
codex plugin marketplace add recoupable/skills
codex plugin install recoup-skills@recoup
codex plugin install music-catalog-diligence@recoup
```

### Cursor

Add `recoupable/skills` as a plugin marketplace source. Cursor discovers plugins
via `.cursor-plugin/marketplace.json` at the repo root.

### Manual clone

```bash
git clone https://github.com/recoupable/skills.git recoup-skills
```

## Skills (broad, shared pool)

The `recoup-skills` plugin exposes these skills from `./skills/`:

| Skill | What it does |
| ----- | ------------ |
| [artist-workspace](./skills/artist-workspace) | Manage artist directories — context, songs, brand, audience |
| [chart-metric](./skills/chart-metric) | Query and analyze music data from the Chartmetric API |
| [content-creation](./skills/content-creation) | Create social videos, TikToks, Reels, visual content using AI primitives |
| [create-artist](./skills/create-artist) | 8-step API playbook for onboarding a new artist |
| [getting-started](./skills/getting-started) | Install CLI, get API key, connect via MCP/REST — start here |
| [music-industry-research](./skills/music-industry-research) | Artist analytics, people search, competitive analysis, web intelligence |
| [recoup-api](./skills/recoup-api) | Call the Recoup API from the sandbox — artist data, socials, orgs, reports |
| [release-management](./skills/release-management) | Plan and execute release campaigns |
| [setup-sandbox](./skills/setup-sandbox) | Scaffold the workspace for an account's orgs and artists |
| [song-writing](./skills/song-writing) | Structured songwriting using the 7 C's method |
| [streaming-growth](./skills/streaming-growth) | Grow a new artist past streaming milestones |
| [trend-to-song](./skills/trend-to-song) | Turn cultural moments into songs and campaign strategies |

## Plugins (self-contained vertical bundles)

Each plugin under `./plugins/` is a self-contained bundle with its own skills,
agents, commands, scripts, and templates.

- [`music-catalog-diligence/`](./plugins/music-catalog-diligence/) — review royalties, rights, valuation, and deal materials for music catalog transactions. 9 skills + 5 agents + 6 commands + scripts + templates + evals + fixtures.

## Repository layout

```text
recoupable/skills/
├── .claude-plugin/marketplace.json       ← Claude Code marketplace
├── .agents/plugins/marketplace.json      ← Codex marketplace
├── .cursor-plugin/marketplace.json       ← Cursor marketplace
├── marketplace.source.json               ← Single source of truth (edit this)
│
├── skills/                               ← Broad music skills (recoup-skills plugin)
│   ├── artist-workspace/
│   ├── chart-metric/
│   ├── content-creation/
│   ├── create-artist/
│   ├── getting-started/
│   ├── music-industry-research/
│   ├── recoup-api/
│   ├── release-management/
│   ├── setup-sandbox/
│   ├── song-writing/
│   ├── streaming-growth/
│   └── trend-to-song/
│
├── plugins/                              ← Self-contained vertical plugins
│   └── music-catalog-diligence/
│       ├── .claude-plugin/plugin.json
│       ├── .codex-plugin/plugin.json
│       ├── .cursor-plugin/plugin.json
│       ├── skills/        (9 catalog-specific skills)
│       ├── agents/        (5 specialist reviewers)
│       ├── commands/      (6 slash commands)
│       ├── scripts/       (deterministic normalizers + dashboards)
│       ├── templates/
│       ├── evals/
│       ├── fixtures/
│       └── references/
│
└── scripts/
    ├── generate-marketplaces.py          ← Regenerate the 3 marketplace files
    └── validate-manifests.py             ← CI check: all manifests + skills valid
```

## Maintenance

After editing `marketplace.source.json`:

```bash
python3 scripts/generate-marketplaces.py     # regenerate platform marketplaces
python3 scripts/validate-manifests.py        # full repo validation
```

Both scripts are zero-dependency Python 3.9+ stdlib. CI runs
`scripts/validate-manifests.py` on every PR.

## Contributing

See [contributing.md](./contributing.md).

- **Broad music skill?** Add a folder under `skills/` and list it in
  `marketplace.source.json` under the `recoup-skills` plugin's `skills`
  array.
- **Vertical workflow** (3+ related skills + commands/agents/scripts)? Create
  a new plugin folder under `plugins/{your-plugin}/` and register it as a
  self-contained plugin in `marketplace.source.json`.

## About

[Recoup](https://recoupable.com) is an AI-powered music management platform.
These skills and plugins power the agents that help artists and labels manage
their careers.

- **Website**: [recoupable.com](https://recoupable.com)
- **App**: [chat.recoupable.com](https://chat.recoupable.com)
- **Support**: agent@recoupable.com
- **License**: [Apache-2.0](./LICENSE)
