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

Add `recoupable/skills` as a plugin marketplace source. Cursor discovers plugins via `.cursor-plugin/marketplace.json` at the repo root.

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

Each plugin under `./plugins/` is a self-contained bundle with its own skills, agents, commands, scripts, and templates.

- [`music-catalog-diligence/`](./plugins/music-catalog-diligence/) — review royalties, rights, valuation, and deal materials for music catalog transactions. 9 skills + 5 agents + 6 commands + scripts + templates + evals + fixtures.

## Maintenance

After editing `marketplace.source.json`:

```bash
python3 scripts/generate-marketplaces.py     # regenerate platform marketplaces
python3 scripts/validate-manifests.py        # full repo validation
```

Both scripts are zero-dependency Python 3.9+ stdlib. CI runs `scripts/validate-manifests.py` on every PR.

For repo layout, skill format, and contribution rules, see [`AGENTS.md`](./AGENTS.md) and [`contributing.md`](./contributing.md).

## About

[Recoup](https://recoupable.com) is an AI-powered music management platform.

- **App**: [chat.recoupable.com](https://chat.recoupable.com)
- **Support**: agent@recoupable.com
- **License**: [Apache-2.0](./LICENSE)
