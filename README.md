# Recoup

AI agent skills for the music industry — a record label in a box. One install gives your agent the whole Recoup platform: artist setup & API access, research, catalog deals, content, song analysis, and releases.

## Install

### Claude Code

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-skills@recoup
```

### Codex and Cursor

Install this repository through the host's plugin marketplace/local-plugin flow.
The Codex manifest references `.mcp.json`; the Cursor manifest references `mcp.json`.
Both configure the same remote Recoup server. No API key is bundled.

### Connect Recoup

After installing, authenticate the plugin's Recoup server in the host's connection
UI (`/mcp` in Claude Code). Review the full `mcp:tools` permission, then verify with
`list_artists`. The host stores and refreshes OAuth credentials. Existing limited
connections need fresh consent and a tool refresh to gain full access.

The MCP catalog currently offers 51 business tools; credential export is excluded.
REST-only endpoints and scripts still need separate REST credentials. Installing
skills alone does not make every API endpoint an MCP tool.

### npx (skills only)

```bash
npx skills add recoupable/skills
```

This installs skill instructions only. Configure `https://api.recoupable.dev/mcp`
separately in the host to use OAuth tools.

### Manual

Clone the repo and load it as a plugin — the repo root is the plugin, with every skill under `skills/`:

```bash
git clone https://github.com/recoupable/skills.git
```

## Skills

Every skill is named `recoup-[domain]-[verb]-[noun]`, so the `/` list clusters by domain.

### roster — your artists

| Skill | What it does |
|-------|-------------|
| recoup-roster-add-artist | Onboard & enrich a new artist (the 8-call setup chain) |
| recoup-roster-list-artists | See who's on your roster |
| recoup-roster-onboard | Bootstrap an empty org's whole roster (bulk-onboard via parallel subagents) |
| recoup-roster-manage-artist | Work inside one artist's folder — context, brand, songs, releases |

### research — industry intelligence

| Skill | What it does |
|-------|-------------|
| recoup-research-artist-overview | Full research sweep on one artist |
| recoup-research-find-talent | A&R scouting for emerging/unsigned artists |
| recoup-research-playlist-targets | Catalog-wide playlist strategy & placement gaps |
| recoup-research-find-contacts | Find managers/A&R/press + draft outreach |
| recoup-research-weekly-brief | The recurring "what changed this week" update |
| recoup-research-the-web | Open-web search, deep research, entity enrichment |

### song — creation and audio analysis

| Skill | What it does |
|-------|-------------|
| recoup-song | Original song through Recoup: approved idea, genre, lyrics/prompt, then API call |
| recoup-song-analyze-audio | Understand a song from its audio (BPM/key/genre, lyrics, mix) |
| recoup-song-find-hook | Find the most clip-worthy 5–15 seconds |
| recoup-song-placement-pitch | Playlist/editorial pitch + sync brief from the audio |

### content — media assets

| Skill | What it does |
|-------|-------------|
| recoup-content-build-sites | Design and build interactive sites using 60 curated digital experience references |
| recoup-content-connect-fans | Configure paid Spotify fan connection, site attribution and private fan retrieval |
| recoup-content-write-caption | Captions in the artist's own voice |
| recoup-content-make-graphics | Cover art, thumbnails, carousels, promo/quote cards |
| recoup-music-video | Narrative music video: approved song, bible, audition, references, motion and verified edit |
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
| recoup-nft-valuation | Measure an artist's onchain NFT earnings & fold them into a valuation |

### platform — operate the system

| Skill | What it does |
|-------|-------------|
| recoup-platform-connect-account | Connect with MCP OAuth; REST credential fallback when needed |
| recoup-platform-track-onboarding | Score an account against the activation funnel; route to the next step |
| recoup-platform-build-os | Build the org's self-managing music-company OS (folders + brain + janitor + plugin), seeded from your live roster |
| recoup-platform-api-access | Call the Recoup API & external connectors directly |
| recoup-platform-capture-lesson | Capture a reusable lesson (compounding memory) |

### internal — Recoup staff only (gated by the `recoup-internal` keyword)

> OFF by default. These fire **only** when the request explicitly includes `recoup-internal`. They operate Recoup's own engineering and go-to-market systems — never customer-facing work.

| Skill | What it does |
|-------|-------------|
| recoup-internal-dev-issue-tracker | Write & maintain high-signal GitHub tracking issues |
| recoup-internal-dev-ship-issue | Deliver a tracked issue end-to-end (docs-first, TDD) |
| recoup-internal-eval-skill-benchmark | Benchmark a skill pack/plugin against the frontier |
| recoup-internal-sales | Daily sales sweep across Stripe/Privy/valuations/Attio/credits/tasks/chats → one ranked follow-up list |
| recoup-internal-funnel-valuation-pipeline | Work the Attio catalog-valuation sales funnel |
| recoup-internal-account-health-report | Account-health snapshot for any Recoup account |
| recoup-internal-marketing | The daily marketing run on our own accounts: workspace canon → socials scrape → topic pick → build → handoff |
| recoup-internal-social-ship-posts | Draft, publish & measure LinkedIn/X posts |

## What else ships

Beyond the skills, the plugin bundles shared components at the repo root:

- **`agents/`** — specialized subagents (deal QC, market scout, royalty audit, rights chain, valuation sensitivity, metadata reconciler, release readiness, research analyst)
- **`.mcp.json` / `mcp.json`** — the remote Recoup MCP connection
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

[Recoup](https://recoupable.com) is an AI-powered music platform. These skills power the agents that help artists and labels manage their careers.

- **Website**: [recoupable.com](https://recoupable.com)
- **Support**: support@recoupable.com

## Internal consulting workflows

The 63 `recoup-internal-consulting-*` skills cover client/deal operations, proposals, reporting, content, graphics and video. Use the consulting section of RESOLVER.md to select one. These are public instructions for staff use; the name does not make their contents private.

Business installs this same repository at `plugin/` as a pinned Git submodule. Consult its workspace rules before accessing data. Integration adapters, credentials and active schedules belong to the selected workspace; installing these skills does not configure them.

Media skills bundle the Recoup Sky identity, DM Sans, IBM Plex Mono, exact logos and approved Finals references. Video engines and modes are supporting GUIDE.md files under the HyperFrames skill. Third-party assets retain their notices; personal-use replica and Virgil font binaries are excluded.

### Catalog Stop-hook removal (2.1.1)

Catalog review uses explicit readiness and dashboard validators, with no catalog
Stop hook. Update to 2.1.1 and start a new session to unload a previously active
skill hook. If the reviewer identifies itself as `recoup-catalogs-plugin`, update
that separate plugin to 0.3.1 too (or disable it if you use this consolidated
package). Organization-managed installs require the administrator to publish the
update. Completion requirements remain in place; version 2.2.0 also removes the source-file hook.


### Hook-free MCP release (2.2.0)

Removed both plugin-wide lifecycle hooks and all six skill-local Stop hooks.
Visual inspection, release validators, and immutable-source instructions remain
explicit workflow steps.
Update/reinstall the plugin and start a new session to unload cached hooks; an
organization-managed install needs its administrator to distribute the update.

Connection setup prefers MCP OAuth and no longer edits global agent instructions.
Missing API-key environment variables do not imply a disconnected MCP account.

### OpenAI public directory

This package includes the remote MCP endpoint in its initial submission and has
no lifecycle hooks or registered-app references. Those packaging choices follow
[OpenAI's submission requirements](https://developers.openai.com/plugins/deploy/submission).
They do not establish directory approval. Domain verification, OAuth/tool scan,
review-account setup, live test cases, and the review walkthrough still need to
be completed in the publisher portal. Include MCP in the initial submission;
OpenAI currently does not support adding it to an existing skills-only listing.

Run the five validation gates in AGENTS.md before release. Also verify plugin
installation, browser consent, tool discovery, a read, refresh and revocation in
each supported host. JSON validation is not proof of a working host connection.

## Internal motion design

`recoup-internal-content-design-motion` creates feature-announcement films, product demos and marketing motion graphics. Invoke with the literal `recoup-internal` keyword. It includes original motion kernels, executable tests, image/video asset production, and a bundled independent gauntlet review loop against inspected references; it is not the customer release-pack generator. Private assets stay in the selected project workspace.

## Automatic plugin packages

Every merge to `main` validates and publishes a GitHub release with two ZIPs built
from the same commit. No separate skill copies or manually maintained skill list
are needed:

- **Customer:** every skill except `recoup-internal-*`, its bundled support files,
  the Codex manifest, assets and MCP configuration. Use this ZIP for OpenAI.
- **Full:** all customer and staff skills plus the repository's shared components
  and manifests. Internal naming describes audience, not repository privacy.

New customer skills are included automatically. Staff skills must use the
`recoup-internal-` prefix. Customer files must not refer to excluded internal
skills; PR validation rejects those dependencies.

The workflow stamps `YYYY.MMDD.run-number` versions into packaged manifests only
(the middle number has no leading zero). Source manifests remain synchronized
under the existing validation rules. Each release includes SHA-256 checksums,
skill inventories, the source commit and OpenAI submission instructions. Failed
uploads resume in a draft release before publication; published releases are
retained unchanged.

GitHub release publication is automatic. OpenAI directory updates still require
uploading the customer ZIP, completing checks, review and publication in the
publisher portal. This workflow does not promise automatic refresh of existing
GitHub marketplace installations. It does not change the live MCP deployment.

To build locally after staging new files:

```bash
python3 -m unittest discover -s tests -p test_plugin_packages.py
python3 scripts/build_plugin_packages.py --version 2026.1008.1 --out /tmp/recoup-packages
```

The builder reads tracked files, so untracked files are never silently shipped.

### Platform-specific listing copy

Claude and Cursor manifests name their respective hosts. Shared source metadata
uses “A record label powered by agents.” The package builder sets the Codex-format
manifest subtitle to “A record label inside ChatGPT” in the customer directory ZIP
and “A record label inside Codex” in the full ZIP. These are build-time labels,
not runtime host detection; direct repository installs use the source metadata.
The long product description and skills remain shared.
