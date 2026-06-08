---
name: recoup-release-start
description: >
  One-command, end-to-end release workflow. Use whenever the user says "start a
  release", "plan the release for [artist]", "let's release [title]", "run the
  release for [artist]", "take this release from start to finish", or types
  /recoup-release-start. Scaffolds the release workspace, then drives the whole
  lifecycle without stopping between phases — creative brief → dated campaign →
  master RELEASE.md + deliverables → playlist targeting → post-release monitoring
  — and lands the user on a populated `releases/{artist}/{release}/` workspace. The
  default front door for releases. For a single piece (just the schedule, just the
  brief), run that stage skill directly.
license: Proprietary
metadata:
  owner: agent@recoupable.com
  status: draft
  user-invocable: true
---

# Release Start — full release workflow

The **default starting point** for any release. It runs every stage in order and
ends with a populated release workspace the user can open. **Do not stop and ask
what to do next between phases.** Run all phases. Stop only when the workspace is
populated (brief + campaign + RELEASE.md exist) or a hard blocker prevents
proceeding (no artist identified, no release facts, no API access for a stage).

The workspace schema this builds is in `references/release-workspace.md` — read it
first. The scaffold lives in `templates/release-workspace/`.

Requires the Recoup REST API (the brief, targeting, and monitor stages call it),
authenticated with `RECOUP_API_KEY` from the environment.

## Phase 1 — Intake + scaffold (≤30s)

1. Confirm the **release facts** (ask once, in one structured prompt, if missing):
   artist, release title, type (single/EP/album/…), release date (or TBD), goal
   metric, channels, creative direction (one line), known asset gaps. The brief
   refuses to proceed without title + date-or-TBD + creative direction.
2. Derive `artist-slug` and `release-slug` (lowercase-kebab).
3. Copy `templates/release-workspace/` into
   `releases/{artist-slug}/{release-slug}/` and fill `assumptions.yaml` with the
   facts from step 1.

Print one line: **"Release workspace at releases/{artist-slug}/{release-slug}/.
Starting the brief."**

## Phase 2 — Creative brief

Run **`recoup-release-marketing-brief`** for this artist + release. It pulls
audience data and produces visualizer directions, content angles, platform hooks,
and ranked playlist targets. Land its output in `brief/`.

## Phase 3 — Dated campaign

**Compute the dates deterministically — never do release-date math by hand:**

```text
python3 scripts/build_campaign_timeline.py --release-date {YYYY-MM-DD|TBD} --type {type}
```

This returns every milestone with its exact calendar date and any timing
warnings (e.g. the ~28-day DSP editorial window). Then run
**`recoup-release-campaign`** to turn that timeline + the brief into the
phase-by-phase plan with owners. Land it in `campaign/`.

## Phase 4 — Master doc + deliverables

Run **`recoup-release-doc`** to create/update `RELEASE.md` as the single source
of truth, then generate the DSP pitch and press one-sheet into `reports/`. Pull
every fact from `assumptions.yaml` and the brief — never from memory.

## Phase 5 — Playlist targeting (chained research)

These skills live in the research plugin; call them and land their output in
`targeting/`:

1. **`recoup-playlist-intelligence`** → which playlists to target (gap vs. peers).
2. **`recoup-people-outreach`** → the curator behind each top target + a drafted pitch (draft only — never send).

If the artist's audience picture is thin, also run
**`recoup-audience-analysis`** to ground the targeting.

## Phase 6 — Arm post-release monitoring

Set up the standing watches so the release keeps producing value after drop day:

- **`recoup-new-release-monitor`** — confirms the drop and builds a launch alert.
- **`recoup-streaming-check`** — watches for streaming spikes.
- **`recoup-weekly-brief`** — the recurring tracker.

Note these in the workspace so the team knows what's running.

## Phase 7 — Review + completion gate (do not skip)

The release is **not** ready until it passes the deterministic gate and the
specialist review:

1. Run the validator — it must return `status: "ok"`:

```text
python3 scripts/validate_release.py releases/{artist-slug}/{release-slug}
```

   If it reports anything in `missing[]`, fix those (write the missing brief /
   campaign / `RELEASE.md` section) and re-run. Do not claim "ready" while it
   reports `incomplete`.
2. Dispatch the **`release-readiness-reviewer`** agent. If it returns
   `overall_status: "blocked"`, surface the blockers and resolve them (or disclose
   them in `RELEASE.md` section 8) — do not silently rewrite over them.

On Claude Code, a Stop hook enforces this gate automatically; on other harnesses
it's your responsibility to run the validator before the recap.

## Final recap (the landing card)

End with this shape, populated from the actual run:

```text
✅ Release workspace ready.

  releases/{artist-slug}/{release-slug}/

Open first:
  RELEASE.md            — the master doc
  brief/                — creative directions + content angles
  campaign/             — the dated rollout timeline
  targeting/            — playlist targets + drafted outreach
  reports/              — DSP pitch + press one-sheet

What I did NOT do (and why):
  <one honest bullet per gap, e.g. "skipped targeting — artist not in Chartmetric yet">

Next:
  /recoup-release-campaign  — refine the timeline
  /recoup-release-doc       — refine the master doc + deliverables
```

## Rules

- **Truthfulness over polish.** If a stage was thin or skipped, say so in the recap.
  Never claim a release is "ready" while `RELEASE.md` or the brief is missing.
- **No mid-workflow stops.** If you finish Phase 2 and feel unsure about Phase 3,
  run Phase 3 anyway. The user can stop you with a follow-up.
- **One workspace.** Everything lands under `releases/{artist-slug}/{release-slug}/`.
- **Never fabricate** release facts, numbers, placements, or press. Blank + flag.
- **Copy that needs the house voice** → run it through `recoup-brand-voice-caption`.

## Release-type modes

The same workflow runs for every release; the type only shifts emphasis:

| Type | Emphasis |
| --- | --- |
| single | tight timeline, one hero track, fast playlist push |
| EP / album | track-by-track narrative, phased singles, deeper press |
| sync-focused | lead with `recoup-song-sync-brief` placements |
| catalog-reissue | anniversary hooks + existing-audience reactivation, lighter discovery |

## Power-user escape hatches

Run a single stage directly: `recoup-release-marketing-brief` (creative),
`recoup-release-campaign` (schedule), `recoup-release-doc` (master doc). Most
users should run this orchestrator and let it drive the whole thing.
