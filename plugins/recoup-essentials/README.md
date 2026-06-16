# Recoup Essentials

The starting-point plugin for the [Recoup](https://recoupable.com) platform. Bundles the skills an agent needs to **get onto Recoup and stay productive** — first-run setup, API key issuance, sandbox scaffolding, artist creation, the artist workspace file conventions, and direct Recoup API + connector access.

If you only install one Recoup plugin, install this one first. Every other Recoup plugin (research, deals, content, songs) assumes the account is already set up and the artist workspace already exists — this plugin is what makes that true.

## Install

### Claude Code

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-essentials@recoup
```

### Cursor

1. Cursor → Settings → Plugins → **Add custom plugin**.
2. Paste `https://github.com/recoupable/skills`.
3. Restart Cursor so `.cursor-plugin/plugin.json` loads the skills.

## Getting started

In a fresh chat, just say:

> **Set up Recoup**

The agent picks up `recoup-setup`, which verifies your account, issues an API key, and seeds the workspace. From there, "create an artist" and "what artists do I have" route to the right skills automatically.

## Skills

Loaded automatically by description-matching when the agent recognizes the task:

| Skill | What it does |
| ----- | ------------ |
| `recoup-setup` | **Start here.** First-run setup inside Claude Code — email + PIN verification, API key issuance, org lookup, and memory seeding. |
| `recoup-setup-sandbox` | Scaffold the initial file system (orgs + artists) for a brand-new sandbox. |
| `recoup-artist-workspace` | Work inside artist directories — create them, enumerate them, and edit context, songs, brand, and audience. |
| `recoup-artist-create` | End-to-end 8-call chain to create, identify, and enrich a new artist account from a name. |
| `recoup-api` | Call the Recoupable API for artist data, socials, orgs, research, and documents — plus connector actions (Google Docs / Drive / Sheets, Gmail, TikTok, Instagram). |

These five skills cross-reference each other heavily (setup → sandbox → workspace → artist creation → API), which is why they ship as one plugin rather than standalone skills.

## Required environment

- `RECOUP_API_KEY` (`recoup_sk_…`) — issued by `recoup-setup`, or via `POST /api/agents/signup`. See [Agents](https://developers.recoupable.com/agents).

## Structure

```text
plugins/recoup-essentials/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── .cursor-plugin/plugin.json
├── skills/
│   ├── recoup-setup/SKILL.md
│   ├── recoup-setup-sandbox/SKILL.md
│   ├── recoup-artist-workspace/SKILL.md
│   ├── recoup-artist-create/SKILL.md
│   └── recoup-api/SKILL.md
├── LICENSE
└── README.md
```

## Support

- Email: `agent@recoupable.com`
- Website: <https://recoupable.com>

## License

[Apache-2.0](./LICENSE)
