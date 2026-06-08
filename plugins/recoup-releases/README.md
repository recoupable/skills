# Recoup — Releases

The flagship **workflow bundle**: one command takes an artist + release from
creative brief all the way through post-release monitoring, building a single
release workspace. (See `docs/workflow-plugins.md` for the pattern.)

Most of the time you run one skill — `recoup-release-start` — and let it drive
the whole thing.

## The workflow

```text
/recoup-release-start
  → intake (release facts) + scaffold releases/{artist}/{release}/
  → brief      (recoup-release-marketing-brief)   → brief/
  → campaign   (recoup-release-campaign)           → campaign/
  → master doc (recoup-release-doc)                → RELEASE.md + reports/
  → targeting  (playlist-intelligence → people-outreach, research)  → targeting/
  → arm monitors (new-release-monitor, streaming-check, weekly-brief)
```

## Skills

| Skill | What it does |
| --- | --- |
| `recoup-release-start` | **Orchestrator / front door.** Scaffolds the workspace and runs every stage end-to-end. |
| `recoup-release-marketing-brief` | Creative brief — visualizer directions, content angles, hooks, playlist targets, grounded in audience data. |
| `recoup-release-campaign` | The dated rollout timeline (pre / release-week / post) with channels, assets, owners. |
| `recoup-release-doc` | The master `RELEASE.md` source of truth + generated DSP pitch / press one-sheet. |
| `recoup-release-demo` | Runs the full workflow on a synthetic artist + release to show what it produces. |

## What it produces

```text
releases/{artist-slug}/{release-slug}/
├── RELEASE.md        ← the master doc (open this first)
├── assumptions.yaml  ← the release facts
├── brief/            ← creative directions + content angles
├── campaign/         ← the dated rollout timeline
├── targeting/        ← playlist targets + drafted curator outreach
├── tracking/         ← post-release monitor outputs
└── reports/          ← DSP pitch, press one-sheet
```

The workspace contract is in `recoup-release-start`'s
`references/release-workspace.md`.

## Chained skills (live in other plugins)

The targeting and monitoring stages **call** general-purpose skills that live in
their own plugins — they're not duplicated here:

- `recoup-playlist-intelligence`, `recoup-people-outreach`,
  `recoup-audience-analysis` (recoup-research) — targeting
- `recoup-new-release-monitor`, `recoup-streaming-check`,
  `recoup-weekly-brief` (recoup-research) — post-release monitoring

The shared `releases/{slug}/` workspace is the hand-off surface that keeps a
chained-in skill's output coherent with the bundle.

## How it stays reliable (the bundle internals)

Following the workflow-bundle pattern (`docs/workflow-plugins.md`), the bundle
ships more than skills:

- **Deterministic scripts** (`scripts/`, stdlib Python, tested) for the parts the
  model must not improvise:
  - `build_campaign_timeline.py` — release-date math → exact calendar dates per
    milestone + a DSP-editorial-window warning (vendored into the orchestrator and
    `recoup-release-campaign`).
  - `validate_release.py` — the **completion contract**: checks the workspace has
    `assumptions.yaml` (filled), `RELEASE.md`, a `brief/`, and a `campaign/`;
    exits non-zero if incomplete.
  - Unit tests (`test_*.py`) cover both — edit the scripts safely.
- **A specialist subagent** — `agents/release-readiness-reviewer.md` QCs the plan
  before sign-off (completeness, no fabricated numbers, timeline feasibility,
  honest gaps).
- **A completion hook** — `hooks/hooks.json` (Claude Code) blocks the agent from
  calling a release "ready" until `validate_release.py` passes and gaps are
  disclosed. Other harnesses rely on the orchestrator's own validator gate.
- **A demo fixture** — `fixtures/demo-release/` seeds `recoup-release-demo`.

The split is deliberate: **dates and completeness are deterministic code; the
creative and strategic work stays in the (editable) skills.**

## Requirements

The brief, targeting, and monitor stages call the **Recoup REST API** and require a
`RECOUP_API_KEY` in the environment (read by name, never stored in this repo). The
campaign and master-doc stages are self-contained.

## Install

- **Claude Code:** `/plugin marketplace add recoupable/skills` then `/plugin install recoup-releases@recoup`.
- **Cursor:** add the marketplace, enable **Recoup — Releases**.
- **Cowork:** an enterprise admin connects Cowork to the repo's `marketplace.json`.

## License

[Apache-2.0](./LICENSE).
