# Recoup

AI agent skills for the music industry — a record label in a box. One install gives your agent the whole Recoup platform: artist setup & API access, research, catalog deals, content, song analysis, and releases.

## Install

### Claude Code

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-plugin@recoup
```

#### Upgrade an older `recoup-skills` installation

The package identifier changed to `recoup-plugin`. Refreshing the marketplace
does not rename an installed plugin; updating `recoup-skills@recoup` can fail
because that entry is no longer in the current catalog. For a user-scope install:

```bash
claude plugin marketplace update recoup
claude plugin install recoup-plugin@recoup --scope user
claude plugin disable recoup-skills@recoup --scope user
```

Disable the old package after the new installation succeeds, then reopen Claude
Code and follow **Connect Recoup** below. If the old installation used a different
scope, use that scope when disabling it. Disabling retains its cached files for
rollback and avoids loading duplicate skill instructions.

Check `claude plugin list` for the enabled current package and
`claude mcp get plugin:recoup-plugin:recoup` for connection status. A connected
server confirms transport and authentication; verify the actual authorized tools
with a read-only request such as `list_artists` before relying on a workflow.

### Codex and Cursor

Install this repository through the host's plugin marketplace/local-plugin flow.
The Codex manifest references `.mcp.json`; the Cursor manifest references `mcp.json`.
Both configure the same remote Recoup server. No API key is bundled.

### Connect Recoup

After installing, authenticate the plugin's Recoup server in the host's connection
UI (`/mcp` in Claude Code). Review the full `mcp:tools` permission, then verify with
`list_artists`. The host stores and refreshes OAuth credentials. Existing limited
connections need fresh consent and a tool refresh to gain full access.

Use authenticated tool discovery to inspect the business tools authorized in your
host and workspace; credential export is excluded.
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
| recoup-roster-add-artist | Onboard & enrich a new artist (the 8-step onboarding workflow) |
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
| recoup-song-check-credits | Compare writer, producer and performer credits; flag conflicting names, roles and supplied shares |

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
| recoup-release-add-release | Add a supported release link/export and show available details and ordered tracks |
| recoup-release-manage-delivery | Correct existing releases, prepare eligible UGC enrollment and manage distributor transitions with destination readback |
| recoup-release-check-metadata | Compare release records and track exactly which metadata corrections are confirmed |

### catalog — repertoire, contracts, publishing and deals

| Skill | What it does |
|-------|-------------|
| recoup-catalog-import-catalog | Organize a supplied catalog export with row references, counts and unresolved matches |
| recoup-catalog-explain-contract | Explain a supplied music agreement with clause references and concrete obligations |
| recoup-catalog-organize-publishing | Organize compositions, parties, recorded shares, registrations and administration details |
| recoup-catalog-audit-catalog | Audit rights, registrations, identifiers, documents and asset condition with explicit coverage |
| recoup-catalog-reconcile-royalties | Reconcile reported royalties, evidenced entitlements, remittances and receiving-account evidence |
| recoup-catalog-register-catalog | Prepare and carry out authorized registrations, ordinary claims, amendments and matches through verified routes |
| recoup-catalog-resolve-claims | Pursue documented music-rights and royalty exceptions, preserving disposition and financial evidence |
| recoup-catalog-review-deal | Underwrite a deal end to end (data room → IC memo) |
| recoup-catalog-estimate-value | Value a catalog from public data alone (no seller files) |
| recoup-nft-valuation | Measure an artist's onchain NFT earnings & fold them into a valuation |

The new release, catalog, credits, contract and publishing workflows can review supplied
material with the host’s file tools. Saving/importing into Recoup requires the corresponding
supported operation and access; a local worksheet is not a hosted import. The catalog case helpers work locally without an artist roster or provider login.
Service profiles distinguish documented assisted routes from implemented automation;
no provider is advertised as live-verified from fixtures. Hosted case operations
have a separate API/database release dependency. See [catalog coverage](docs/catalog-diligence-coverage.md).

### platform — operate the system

| Skill | What it does |
|-------|-------------|
| recoup-platform-connect-account | Connect with MCP OAuth; REST credential fallback when needed |
| recoup-platform-track-onboarding | Track the applicable company, creator or catalog setup and route to its next useful step |
| recoup-platform-build-os | Build a music-company workspace from available company, catalog, creator or roster context |
| recoup-platform-api-access | Call the Recoup API & external connectors directly |
| recoup-platform-capture-lesson | Capture a reusable lesson (compounding memory) |

### internal — Recoup staff only (gated by the `recoup-internal` keyword)

> OFF by default. These fire **only** when the request explicitly includes `recoup-internal`. They operate Recoup's own engineering and go-to-market systems — never customer-facing work.

| Skill | What it does |
|-------|-------------|
| recoup-internal-dev | Write, maintain & ship GitHub issues end-to-end (tracking issues, docs-first, TDD) |
| recoup-internal-eval-skill-benchmark | Benchmark a skill pack/plugin against the frontier |
| recoup-internal-sales | Daily sales sweep across Stripe/Privy/valuations/Attio/credits/tasks/chats → one ranked follow-up list |
| recoup-internal-funnel-valuation-pipeline | Work the Attio catalog-valuation sales funnel |
| recoup-internal-account-health-report | Account-health snapshot for any Recoup account |
| recoup-internal-marketing | The daily marketing run on our own accounts: workspace canon → socials scrape → topic pick → build → handoff |
| recoup-internal-podcast | One Recoup Podcast episode: recording prep → post-production → covers → Spotify/YouTube → daily shorts |
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

The 65 `recoup-internal-consulting-*` skills cover PMF discovery, client/deal operations, proposals, reporting, content, graphics and video. Use the consulting section of RESOLVER.md to select one. These are public instructions for staff use; the name does not make their contents private.

### PMF finder

Use `recoup-internal-consulting-pmf-finder` to turn an idea or customer evidence into a PULL hypothesis and the next buying-behavior experiment. It covers discovery, commercial commitment, delivery/retention, and the repeatable case-study pattern, with a memo template and timestamped Rob Snyder source guide. Example: “recoup-internal pmf-finder: use these customer calls to identify the weakest demand assumption and our next test.” Keep resulting buyer evidence in the selected private business workspace.

### Mono Business workspace

Mono's Business uses the shared sibling `skills/` checkout. Both starting
directories below refer to the same owning Skills repository:

| Starting directory | Skills repository | Skill authoring path |
| --- | --- | --- |
| Mono root | `skills/` | `skills/skills/<skill-name>/SKILL.md` |
| Business root | `../skills/` | `../skills/skills/<skill-name>/SKILL.md` |

Do not create `business/plugin/` or copy skills into Business. Commit Skills
changes in the Skills repository and Business records in the Business repository,
with separate feature branches and PRs targeting `main`. Follow Mono's existing
coordinator rules for parent references after release; a commit in either
repository does not publish the other.

For another selected workspace, resolve its authoring repository from that
workspace's `AGENTS.md`; do not assume a universal nested plugin layout.
Integration adapters, credentials and active schedules belong to that workspace.
Installing a skill does not configure them or authorize source ingestion. Mono's
Business runs no unattended source-ingestion worker; the separate private sync
coordinator remains outside this workspace.

### Consulting media

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

## Internal MCP thumbnails

`recoup-internal-content-make-thumbnails` creates cinematic animated previews for MCP extension workflow cards. Invoke with the literal `recoup-internal` keyword. It captures the eight-second human-action, physical-transformation, and title-reveal pattern, with scoped generation, visual review, and gallery playback verification. It ships in the full staff package and is excluded from the customer package.

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

The customer directory package uses the blue Recoup icon in
`assets/recoup-customer-icon.png` for its logo and composer icon. The full
marketplace package retains its source icon, making the two distributions
visually distinguishable during installation and review.

### Package identifier migration

The package identifier changed from `recoup-skills` to `recoup-plugin` in 2.4.0.
The display name remains Recoup and the repository remains `recoupable/skills`.
Existing marketplace installations may require installing `recoup-plugin@recoup`
and removing the old entry after verifying the replacement. Uploaded OpenAI drafts
and workspace installations must be checked separately; a GitHub release does not
confirm that those existing records accept an identifier change.

### ChatGPT workspace testing on web and desktop

Direct `.mcp.json` packages can appear as desktop-only in ChatGPT. For workspace
testing, register the remote MCP app in ChatGPT first, then generate a customer
package that references its `asdk_app_...` ID:

```bash
python3 scripts/build_plugin_packages.py --version 2026.1011.1 --out /tmp/recoup-packages --chatgpt-app-id asdk_app_YOUR_REGISTERED_ID
```

This adds `recoup-workspace-<version>.zip` alongside the normal customer and full
ZIPs. It has the same customer skills and blue icon, but uses `.app.json` instead
of direct MCP configuration. Upload it as an update to the workspace plugin and
verify web opening and authentication. Its registered app must be accessible to
the intended workspace users; packaging does not grant access.

Set the repository Actions variable `RECOUP_CHATGPT_APP_ID` to generate this
workspace ZIP on every release. No app ID is hardcoded into public source or the
public submission package. Keep using the customer ZIP for the OpenAI publisher
dashboard, where the submission has its own MCP registration.

When updating an older workspace listing, preserve its package identity using
`--workspace-name recoup-skills` (or set Actions variable
`RECOUP_CHATGPT_WORKSPACE_PACKAGE_NAME`). OpenAI rejects an update that changes
that identity. This affects only the workspace artifact; the public package
remains `recoup-plugin`. The display name stays Recoup in both.

### Claude directory bundle

The release workflow also generates a customer-only Claude plugin on the
`claude-directory` branch. Submit `recoupable/skills`, repository root, tracking
`claude-directory` in Claude's **Plugin bundle** form. This includes the customer
skills and Recoup MCP configuration; it excludes internal skills and staff agents.
The MCP connector has its own separate directory submission.

Merges to `main` regenerate the branch after validation. Configure Claude to
track that branch so it discovers new releases automatically. Anthropic scanning,
review, and publication remain separate from building or pushing the package.
Do not edit the generated branch directly. Its README records source provenance.

Unified artifact shapes, parity checks and the buyer manifest contract: [plugin distribution](references/plugin-distribution.md).
