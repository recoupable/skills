# Changelog

All notable changes to the Recoup Skills marketplace are documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and the marketplace as a whole uses [Semantic Versioning](https://semver.org/).
Individual plugins listed in `marketplace.source.json` carry their own versions.

## [1.0.0] — 2026-05-10

### Added

- **Unified marketplace.** This repo is now both a skill collection AND a plugin marketplace. Adds three platform marketplace files at the repo root:
  - `.claude-plugin/marketplace.json` (Claude Code)
  - `.agents/plugins/marketplace.json` (Codex)
  - `.cursor-plugin/marketplace.json` (Cursor)
- **`marketplace.source.json`** — single source of truth for the marketplace catalog. All three platform marketplace files are generated from this file.
- **`scripts/generate-marketplaces.py`** — zero-dependency Python script that regenerates the three platform marketplace files. Supports `--check` for CI.
- **`scripts/validate-manifests.py`** — zero-dependency Python validator that verifies marketplace parity, plugin source paths, skill frontmatter, and plugin manifests.
- **`plugins/music-catalog-diligence/`** — merged in via `git subtree` (full history preserved) from the legacy standalone `recoupable/music-catalog-diligence` repo. 9 catalog skills + 5 agents + 6 commands + scripts/templates/evals/fixtures.
- **`skills/create-artist/`** — already on `main`; included in the new marketplace listing.

### Plugins shipping in 1.0.0

| Plugin | Version | Type | Source |
| ------ | ------- | ---- | ------ |
| `recoup-skills` | 1.0.0 | virtual (over `./skills/*`) | `./` |
| `music-catalog-diligence` | 0.1.0 | self-contained | `./plugins/music-catalog-diligence` |

### Changed

- **`README.md`** and **`AGENTS.md`** rewritten to describe the marketplace + plugin model.
- **`contributing.md`** rewritten with separate flows for adding a broad skill vs. a vertical plugin, and a release checklist.

### Removed

- Legacy root `.claude-plugin/plugin.json` — superseded by the `recoup-skills` virtual plugin entry in the marketplace.
- Legacy root `.codex-plugin/plugin.json` — same.

### Migration notes

- Users who previously cloned this repo and pointed agents at `skills/` directly will continue to work; no skill paths changed.
- Users of the legacy `recoupable/plugins` registry repo or the standalone `recoupable/music-catalog-diligence` repo should switch their marketplace to `recoupable/skills` once this branch is merged.
- The legacy repos can be archived after consumers are migrated.
