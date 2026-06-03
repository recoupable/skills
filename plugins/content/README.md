# Recoup Content Plugin

Agent plugin for content workflows on the [Recoup](https://recoupable.com) platform. Lets AI agents draft, edit, and publish content for artists — short-form music videos, captions, images, and the supporting building blocks.

Built around the `/api/content/*` endpoints and the `recoup content` CLI. Driven by a single front-door command — `/recoup-content-create` — that produces a finished 9:16 social-ready clip from an artist + song.

## Install

### Claude Code (CLI)

```bash
claude plugin install https://github.com/recoupable/recoup-content
```

### Claude Cowork

1. Open the plugin marketplace (puzzle-piece icon in the sidebar).
2. Click **Add custom plugin** and paste:
   `https://github.com/recoupable/recoup-content`
3. Approve the requested tool permissions (`Read`, `Write` — needed to write the workspace and final `.mp4`).
4. Restart the Cowork session so manifests load.

### Cursor

1. Cursor → Settings → Plugins → **Add custom plugin**.
2. Paste the GitHub URL above.
3. Restart Cursor so `.cursor-plugin/plugin.json` loads commands and skills.

## Getting started

After install, set your Recoup API key in the shell:

```bash
export RECOUP_API_KEY="recoup_sk_..."   # see https://developers.recoupable.com/agents
```

Then in a new chat:

> **Make a TikTok for Mari Vega**

Or invoke the anchor command directly:

```text
/recoup-content-create
```

The agent picks up the `recoup-content-create` skill, resolves the artist's `account_id`, fires the async pipeline, polls until the render finishes, and lands you on the final video URL + caption.

## Commands

| Command | When to use it |
| ------- | -------------- |
| `/recoup-content-create` | **Default.** End-to-end async run from artist name to finished video + caption. The front door for first installs and "make me a video" requests. |

> **v0.3.0 spec migration:** `/recoup-content-create` was migrated from `commands/recoup-content-create.md` to `skills/recoup-content-create/SKILL.md` per Anthropic's newer skills-not-commands convention (the official `claude-plugins-official` example-plugin declares the `commands/*.md` layout legacy). Both files exist in this release for back-compat; the legacy command file will be removed in a future version.

More command coverage (templates browse, single-step overrides, demo workspace) is on the roadmap.

## Skills

Loaded automatically by description-matching when the agent recognizes the task:

| Skill | What it does |
| ----- | ------------ |
| `recoup-content-create` | **Default front door.** Self-contained async run — resolves the artist's `account_id`, fires `POST /api/content/create`, polls `/api/tasks/runs` until terminal, and lands you on the final video URL + caption. |

For granular control, this plugin's skill points at two skills in the **Recoupable skills library** (installed alongside it from `recoupable/skills`):

- `short-video` — the per-stage recipe. Two paths: async pipeline (preferred for agents) and a manual five-step recipe in its bundled `references/short-video-manual.md`.
- `content-creation` — atomic `/api/content/*` primitives (image, video with 6 modes including lipsync, caption, transcribe, edit, upscale, analyze) for one capability in isolation.

`recoup-content-create` is the **front door**; `short-video` is the **recipe**; `content-creation` is the **building blocks**. The recipe and building blocks live in the library so they stay valuable independently of this plugin.

## Required environment

- `RECOUP_API_KEY` (`recoup_sk_…`) — obtain via `POST /api/agents/signup`. See [Agents](https://developers.recoupable.com/agents).
- For the `short-video` skill's manual compose step: `ffmpeg` on PATH.

## Structure

```text
plugins/content/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── .cursor-plugin/plugin.json
├── commands/
│   └── recoup-content-create.md      # legacy front-door command (back-compat)
├── skills/
│   └── recoup-content-create/SKILL.md  # self-contained async front door
├── LICENSE
└── README.md
```

The per-stage `short-video` and atomic `content-creation` skills live in the Recoupable skills library (`skills/short-video/`, `skills/content-creation/`), not in this plugin.

## Roadmap

- `/recoup-content-templates` — browse and inspect content templates without running a full pipeline.
- `/recoup-content-demo` — bundled fixture so first-install users see output before pointing the plugin at a real account.
- `hooks/` — a `SessionStart` hook that validates `RECOUP_API_KEY` and `ffmpeg` presence, and a `Stop` hook that prevents the agent from claiming "video ready" without a non-zero-byte `.mp4`.
- More skills covering artist-brand-voice editing and Recoup-surface publishing.

## Support

- Email: `support@recoupable.com`
- Website: <https://recoupable.com>

## License

[Apache-2.0](./LICENSE)
