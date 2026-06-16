# Recoup Content

Agent plugin for content workflows on the [Recoup](https://recoupable.com) platform. Lets AI agents draft, edit, and publish content for artists — short-form music videos, captions, images, and the supporting building blocks.

Built around the `/api/content/*` endpoints and the `recoup content` CLI. Driven by a single front-door skill — `recoup-content-video` (invoke with `/recoup-content-video`) — that produces a finished 9:16 social-ready clip from an artist + song.

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
3. Restart Cursor so `.cursor-plugin/plugin.json` loads the skills.

## Getting started

After install, set your Recoup API key in the shell:

```bash
export RECOUP_API_KEY="recoup_sk_..."   # see https://developers.recoupable.com/agents
```

Then in a new chat:

> **Make a TikTok for Mari Vega**

Or invoke the anchor command directly:

```text
/recoup-content-video
```

The agent picks up the `recoup-content-video` skill, resolves the artist's `account_id`, fires the async pipeline, polls until the render finishes, and lands you on the final video URL + caption.

> **Skills, not commands.** This plugin ships **skills only** — no `commands/`
> files. Each skill auto-registers its own `/skill-name` slash entry, so
> `/recoup-content-video` is the skill itself. (See the repo's AGENTS.md
> "No slash-commands".)

## Skills

Loaded automatically by description-matching when the agent recognizes the task. Start at
the router, which dispatches to the right job:

| Skill | Job |
| ----- | --- |
| `recoup-content` | **Router / entry point.** Disambiguates "make content for [artist]" and hands off to the right skill below. |
| **Video / motion** | |
| `recoup-content-video` | Featuring-artist short-form video (TikTok/Reel/Short) + caption. Looks (studio / stage / bedroom / album-record-store) are **templates**, not separate skills. Async create→poll. |
| `recoup-content-lyric-video` | Lyrics on screen, timed to the audio, over a visual. |
| `recoup-content-visualizer` | Seamless looping visualizer / Spotify Canvas (8s, 9:16, no text). |
| **Static graphics** | |
| `recoup-content-cover-art` | Square DSP release artwork (single / EP / album). |
| `recoup-content-thumbnail` | 16:9 YouTube/video thumbnail (focal face + hook text). |
| `recoup-content-graphic` | Still-image posts — carousel/photo dump, date/announcement promo (release-date / pre-save / out-now / tour poster), and lyric/quote cards. Three modes in one skill. |
| **Text** | |
| `recoup-content-caption` | Captions that sound like *this* artist (voice from the workspace, fallback to real posts). |
| **Reactive / timely** | |
| `recoup-content-trend` | Turn a *real* trigger — a fresh milestone, sync, chart entry, or current trend from the research feed — into content, then route the asset to the right skill below. |
| **Workflow / high-value** | |
| `recoup-content-pack` | Batch 15–30-asset "clip family" for a release; audience-themed; cost-gated. |
| `recoup-content-reformat` | One master → distinct per-platform cuts; polish the artist's own footage. |

> **Finding the hook** ("best 15 seconds to clip") is *audio analysis*, not a content
> job — it lives in the `recoup-song-analysis` plugin as `recoup-song-hook` (powered by
> Music Flamingo's structure + energy output). Use it to get timestamps, then feed them
> to the video skills above.

Every skill is **artist-workspace-native but context-optional** — it reads the artist's own
context (`context/artist.md`, `context/audience.md`, `context/images/face-guide.png`,
`releases/`) when a workspace exists, falls back to the API when it doesn't, and runs in
**generic mode** from the user's inputs when no artist is involved. Finished assets are
written back into the workspace.

The shared building blocks live in `references/` at the plugin root and are vendored
(byte-identical) into each skill that needs them: `content-api.md` (endpoints, video modes,
templates, async), `account-resolver.md` (auth + IDs), `workspace-context.md` (the three
modes), `research-context.md` (live signals — audio analysis, placements, milestones, the
performance loop), `song-sourcing.md` (audio), and `analyze-gate.md` (verify before "done").

Every artist-grounded skill now runs the same expanded backbone: **resolve → read workspace
context → layer live research signals → generate → analyze (benchmarked against the artist's
real top posts) → write back.** Research is optional and degrades gracefully (skipped in
generic mode, never blocks on a cold API), but when an artist is named it's the default.

For granular control, this plugin's skill points at two skills in the **Recoupable skills library** (installed alongside it from `recoupable/skills`):

- `short-video` — the per-stage recipe. Two paths: async pipeline (preferred for agents) and a manual five-step recipe in its bundled `references/short-video-manual.md`.
- `content-creation` — atomic `/api/content/*` primitives (image, video with 6 modes including lipsync, caption, transcribe, edit, upscale, analyze) for one capability in isolation.

`recoup-content-video` (this plugin) is the **front door**; the library's `short-video` is the **recipe**; `content-creation` is the **building blocks**. The recipe and building blocks live in the library so they stay valuable independently of this plugin.

## Required environment

- `RECOUP_API_KEY` (`recoup_sk_…`) — obtain via `POST /api/agents/signup`. See [Agents](https://developers.recoupable.com/agents).
- For the `short-video` skill's manual compose step: `ffmpeg` on PATH.

## Structure

```text
plugins/recoup-content/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── .cursor-plugin/plugin.json
├── hooks/                                # SessionStart env check + Stop analyze-gate
│   ├── hooks.json
│   └── check-env.sh
├── references/                           # canonical shared refs (vendored into skills)
│   ├── content-api.md
│   ├── account-resolver.md
│   ├── workspace-context.md
│   ├── research-context.md
│   ├── song-sourcing.md
│   └── analyze-gate.md
├── skills/                               # each carries its own vendored references/
│   ├── recoup-content/                   # router / entry point
│   ├── recoup-content-video/             # featuring-artist short-form video (template looks)
│   ├── recoup-content-lyric-video/
│   ├── recoup-content-visualizer/        # visualizer / Spotify Canvas
│   ├── recoup-content-cover-art/
│   ├── recoup-content-thumbnail/
│   ├── recoup-content-graphic/           # carousel + promo + quote modes
│   ├── recoup-content-caption/
│   ├── recoup-content-trend/             # reactive content from a real milestone/trend
│   ├── recoup-content-pack/
│   └── recoup-content-reformat/
├── LICENSE
└── README.md
```

The per-stage `short-video` and atomic `content-creation` skills live in the Recoupable skills library (`skills/short-video/`, `skills/content-creation/`), not in this plugin.

## Roadmap

- `/recoup-content-templates` — browse and inspect content templates without running a full pipeline.
- `/recoup-content-demo` — bundled fixture so first-install users see output before pointing the plugin at a real account.
- `recoup-audience-tuned-content` — a dedicated skill that tunes phrasing/hashtags to `recoup-research` audience data (the shared `research-context.md` backbone already wires the signals in for every skill).
- A separate plugin for Recoup-surface publishing (this plugin stops at the finished asset).

### Shipped recently

- `hooks/` — a `SessionStart` hook that advises on missing `RECOUP_API_KEY`/`ffmpeg`, and a `Stop` hook that enforces the analyze gate (no "asset ready" claim without an analyze-gate pass).
- `recoup-content-trend` — reactive content from a real milestone/trend in the research feed.
- `references/research-context.md` — live research signals (audio analysis → edit, placements, milestones, the performance loop) wired into every artist-grounded skill's backbone.

## Support

- Email: `support@recoupable.com`
- Website: <https://recoupable.com>

## License

[Apache-2.0](./LICENSE)
