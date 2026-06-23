# Recoup Skills

AI agent skills for the music industry — a record label in a box. One install gives your agent the whole Recoup platform: artist setup & API access, research, catalog deals, content, song analysis, and releases.

## Install

### Claude Code / agents marketplace

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-skills@recoup
```

### npx (any harness)

```bash
npx skills add recoupable/skills
```

### Manual

Clone and point your agent at the `skills/` directory:

```bash
git clone https://github.com/recoupable/skills.git
```

> **One plugin, everything included.** As of v2 this repo ships as a **single flat plugin** rooted at the repo root — there are no separate "records" or "internal" installs anymore. Adding the marketplace (or `npx skills add recoupable/skills`) installs every skill in `skills/`. The agent picks the right one via [`RESOLVER.md`](RESOLVER.md).

## Skills

Every skill is named `recoup-[domain]-[verb]-[noun]`, so the `/` list clusters by domain.

### roster — your artists

| Skill | What it does |
|-------|-------------|
| recoup-roster-add-artist | Onboard & enrich a new artist (the 8-call setup chain) |
| recoup-roster-list-artists | See who's on your roster |
| recoup-roster-manage-artist | Work inside one artist's folder — context, brand, songs, releases |

### research — intelligence

| Skill | What it does |
|-------|-------------|
| recoup-research-artist-overview | Full research sweep on one artist |
| recoup-research-find-talent | A&R scouting for emerging/unsigned artists |
| recoup-research-playlist-targets | Catalog-wide playlist strategy & placement gaps |
| recoup-research-find-contacts | Find managers/A&R/press + draft outreach |
| recoup-research-weekly-brief | The recurring "what changed this week" update |
| recoup-research-the-web | Open-web search, deep research, entity enrichment |

### song — single-song audio

| Skill | What it does |
|-------|-------------|
| recoup-song-analyze-audio | Understand a song from its audio (BPM/key/genre, lyrics, mix) |
| recoup-song-find-hook | Find the most clip-worthy 5–15 seconds |
| recoup-song-placement-pitch | Playlist/editorial pitch + sync brief from the audio |

### content — assets

| Skill | What it does |
|-------|-------------|
| recoup-content-write-caption | Captions in the artist's own voice |
| recoup-content-make-graphics | Cover art, thumbnails, carousels, promo/quote cards |
| recoup-content-make-video | Short-form video, lyric videos, visualizers, reformats |
| recoup-content-asset-pack | A whole 15–30-piece clip family for one song |
| recoup-content-reactive-post | Turn a real milestone/trend into a timely post |

### release — release workflow

| Skill | What it does |
|-------|-------------|
| recoup-release-plan-rollout | Plan & run a release end to end |
| recoup-release-track-drop | Confirm a drop & build a launch-day alert |

### catalog — catalog deals

| Skill | What it does |
|-------|-------------|
| recoup-catalog-review-deal | Underwrite a deal end to end (data room → IC memo) |
| recoup-catalog-estimate-value | Value a catalog from public data alone (no seller files) |

### platform — operate the system

| Skill | What it does |
|-------|-------------|
| recoup-platform-connect-account | First-run setup: verify email, mint an API key |
| recoup-platform-build-workspace | Scaffold your orgs/artists folder tree |
| recoup-platform-api-access | Call the Recoup API & external connectors directly |
| recoup-platform-capture-lesson | Capture a reusable lesson (compounding memory) |

### internal — Recoup staff only (gated by the `recoup-internal` keyword)

> OFF by default. These fire **only** when the request explicitly includes `recoup-internal`. They operate Recoup's own engineering and go-to-market systems — never customer-facing work.

| Skill | What it does |
|-------|-------------|
| recoup-internal-dev-issue-tracker | Write & maintain high-signal GitHub tracking issues |
| recoup-internal-dev-ship-issue | Deliver a tracked issue end-to-end (docs-first, TDD) |
| recoup-internal-eval-skill-benchmark | Benchmark a skill pack/plugin against the frontier |
| recoup-internal-funnel-valuation-pipeline | Work the Attio catalog-valuation sales funnel |
| recoup-internal-account-health-report | Account-health snapshot for any Recoup account |
| recoup-internal-social-ship-posts | Draft, publish & measure LinkedIn/X posts |

## What else ships

Beyond the skills, the plugin bundles shared components at the repo root:

- **`agents/`** — specialized subagents (deal QC, market scout, royalty audit, rights chain, valuation sensitivity, metadata reconciler, release readiness, research analyst)
- **`hooks/`** — completion-gate and environment-check hooks
- **`references/`, `templates/`, `fixtures/`** — shared docs, workspace scaffolds, and golden/demo data
- **`RESOLVER.md`** — the routing table the agent uses to pick a skill
- **`scripts/`** — repo validators (portability, vendoring, manifests, resolver reachability + eval)

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

Add a route for the new skill in [`RESOLVER.md`](RESOLVER.md) and a fixture in `resolver-eval.jsonl` — CI fails on unreachable skills. See [contributing.md](contributing.md) for guidelines.

## About

[Recoup](https://recoupable.com) is an AI-powered music management platform. These skills power the agents that help artists and labels manage their careers.

- **Website**: [recoupable.com](https://recoupable.com)
- **App**: [chat.recoupable.com](https://chat.recoupable.com)
- **Support**: support@recoupable.com
