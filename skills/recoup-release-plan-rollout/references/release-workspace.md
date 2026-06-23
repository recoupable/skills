# Release workspace contract

A release workspace is the operating folder for one release. Every stage of the
release workflow reads from and writes to it, so the stages compose instead of
collide. One release = one workspace.

## Folder structure

```text
releases/{artist-slug}/{release-slug}/
├── RELEASE.md        # the master document (single source of truth)
├── assumptions.yaml  # release facts: artist, title, type, date, creative direction
├── brief/            # creative brief — visualizer directions, content angles, hooks
├── campaign/         # dated rollout timeline (pre / release-week / post)
├── targeting/        # playlist targets + curator outreach drafts
├── tracking/         # post-release monitor outputs (dated)
└── reports/          # deliverables: DSP pitch, press one-sheet, production spec
```

Use lowercase-kebab-case for both slugs (`gatsby-grace`, `blue-slide-park`).

## What writes where

| Stage | Skill | Writes to |
| --- | --- | --- |
| Intake | (orchestrator) | `assumptions.yaml`, scaffolds the tree |
| Creative brief | `recoup-release-plan-rollout` (brief mode) | `brief/` |
| Schedule | `recoup-release-plan-rollout` (campaign mode) | `campaign/` |
| Master doc + deliverables | `recoup-release-plan-rollout` (doc mode) | `RELEASE.md`, `reports/` |
| Targeting | `recoup-research-playlist-targets` → `recoup-research-find-contacts` | `targeting/` |
| Post-release | `recoup-release-track-drop`, `recoup-research-weekly-brief` | `tracking/` |

## Rules

- **`RELEASE.md` is the single source of truth.** Deliverables are generated from
  it, not from prose memory.
- **`assumptions.yaml` holds the facts the agent was told** (date, type, creative
  direction). Assumptions are allowed; hidden assumptions are not.
- **Never fabricate** release facts, performance numbers, playlist placements, or
  press. Leave a section blank and flag it instead.
- **One dated file per run** in `brief/`, `campaign/`, `targeting/`, `tracking/`
  (e.g. `brief/brief-2026-06-06.md`). Re-running the same day is a no-op.
- Chained research skills live in other plugins; they drop their output into this
  workspace so the bundle stays coherent.

## Completion gate

A release isn't "ready" until: `assumptions.yaml` exists, `RELEASE.md` exists with
the project snapshot filled, a `brief/` and a `campaign/` file exist, and any gaps
are listed honestly rather than papered over.
