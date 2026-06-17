---
name: recoup-releases
description: Plan and run a music release end-to-end, or do any single stage of it. Modes — plan (one-command full workflow: scaffold workspace → creative brief → dated campaign → master RELEASE.md + deliverables → playlist targeting → post-release monitoring → completion gate), brief (data-grounded creative brief: visualizer directions, content angles, playlist targets), campaign (dated rollout schedule with owners), doc (the master RELEASE.md + DSP pitch + press one-sheet), monitor (confirm the release dropped + launch-day alert), and demo (run the whole thing on synthetic data). Use for "start/plan a release", "release [title]", "creative brief for [release]", "rollout schedule", "RELEASE.md / DSP pitch / one-sheet", "did [artist]'s single drop", or "release demo". Everything lands in releases/{artist}/{release}/.
---

# Recoup Release

The whole release lifecycle behind one skill. **plan** mode runs the full
workflow end-to-end; the other modes are the individual stages, runnable on their
own. Everything reads from and writes to one workspace:
`releases/{artist-slug}/{release-slug}/`.

The workspace schema is in `references/release-workspace.md` (read it first); the
scaffold is in `templates/release-workspace/`. Deterministic helpers ship in
`scripts/` (`build_campaign_timeline.py`, `validate_release.py`). Requires
`RECOUP_API_KEY` for the brief/targeting/monitor stages.

## Mode dispatch

| The user wants… | Mode |
|---|---|
| "start/plan a release", "take [title] start to finish", "run the release" | **plan** (default) |
| "creative brief", "content angles", "what should I plan for [release]" | **brief** |
| "rollout schedule", "campaign", "timeline with dates" | **campaign** |
| "RELEASE.md", "DSP pitch", "press one-sheet", "the master doc" | **doc** |
| "did [artist]'s single drop", "launch alert", "watch for the drop" | **monitor** |
| "release demo", "show me the release workflow" | **demo** |

Format/stage request → that mode. Vague "do the release" → **plan**.

## Mode: plan (the full workflow — don't stop between phases)

Run every phase in order; **do not stop to ask what's next**. Stop only when the
workspace is populated (brief + campaign + RELEASE.md exist) or a hard blocker
hits (no artist, no release facts, no API for a stage).

1. **Intake + scaffold (≤30s).** Confirm release facts in one prompt (artist,
   title, type, date-or-TBD, goal, channels, one-line creative direction, asset
   gaps). Derive `artist-slug`/`release-slug`. Copy `templates/release-workspace/`
   into `releases/{artist-slug}/{release-slug}/` and fill `assumptions.yaml`.
2. **Creative brief** → run **brief** mode; land in `brief/`.
3. **Dated campaign** → compute dates deterministically (never by hand):
   `python3 scripts/build_campaign_timeline.py --release-date {YYYY-MM-DD|TBD} --type {type}`
   (returns every milestone + timing warnings like the ~28-day DSP editorial
   window), then run **campaign** mode; land in `campaign/`.
4. **Master doc + deliverables** → run **doc** mode; pull every fact from
   `assumptions.yaml` and the brief, never from memory.
5. **Playlist targeting (chained)** → call `recoup-research`: **playlists** mode
   (targets + gaps) and **contacts** mode (curator + drafted pitch — draft only,
   never send); if audience is thin, **audience** mode. Land in `targeting/`.
6. **Arm monitoring** → note standing watches: **monitor** mode (drop + launch
   alert) and `recoup-research` **weekly-update** (recurring + streaming spikes).
7. **Review + completion gate (do not skip).** Run
   `python3 scripts/validate_release.py releases/{artist-slug}/{release-slug}` —
   it must return `status: "ok"`; fix anything in `missing[]` and re-run. Then
   dispatch the **release-readiness-reviewer** agent; if `blocked`, resolve or
   disclose in `RELEASE.md` §8 (don't silently rewrite). On Claude Code a Stop
   hook enforces this; elsewhere it's your job.

End with the landing card: workspace path, "open first" list (RELEASE.md, brief/,
campaign/, targeting/, reports/), an honest "what I did NOT do and why" bullet per
gap, and next stages. **Truthfulness over polish** — never claim "ready" while a
stage is missing.

**Release-type emphasis:** single = tight timeline, one hero track; EP/album =
track-by-track narrative, phased singles; sync-focused = lead with `recoup-songs`
pitch mode; catalog-reissue = anniversary hooks + reactivation.

## Mode: brief (the creative brief — structured input, not assets)

Refuse to invent the release — require artist, title, date-or-TBD, type, one-line
creative direction, asset gaps (ask once if missing). Pull in parallel
(`references/endpoints.md`): `audience` (TikTok+IG), `similar`, current
`playlists`. Synthesize to
`brief/brief-$(date +%F).md`: creative direction (verbatim) · narrative thread ·
**3 visualizer directions** (concept/refs/production-bar/why-for-this-artist) ·
**5 content angles** (each a series premise + first 3 pieces) · platform hooks
(each anchored in a concrete audience number — if you can't ground it, drop it) ·
ranked playlist targets (peers' placements this artist isn't on) · geo rollout ·
open decisions. It's a plan, not finished assets — to produce assets use
`recoup-content`. No invented audience numbers; thin data → say so.

## Mode: campaign (the dated rollout schedule)

Compute the timeline deterministically with
`scripts/build_campaign_timeline.py` (never hand-do release-date math), then turn
that timeline + the brief into a phase-by-phase plan (pre-release → release-week →
post-release) with channels, assets, owners, and exact dates counted back from
the release date. Land in `campaign/`. Flag timing risks (e.g. editorial window).

## Mode: doc (the master RELEASE.md + deliverables)

Create/maintain `RELEASE.md` as the single source of truth using
`references/release-template.md` + `references/section-guide.md`, then generate
the **DSP pitch** and **press one-sheet** into `reports/` per
`references/deliverables.md`. Pull every fact from `assumptions.yaml` + the brief.
Copy that needs the house voice → `recoup-content` caption mode. Never fabricate
placements/press — blank + flag in §8.

## Mode: monitor (release-day tracker / launch alert)

Confirm the release actually dropped and build a launch-day alert from the
research API (`references/endpoints.md`). Idempotent + dated; save to
`tracking/`. For ongoing streaming-spike watching, use `recoup-research`
**weekly-update** (streaming scope).

## Mode: demo

Run **plan** mode on a bundled synthetic artist+release so a first-time user sees
the full output fast. Use the demo fixtures; don't require real API data.

## Guardrails

- **No mid-workflow stops** in plan mode — run the next phase anyway.
- **One workspace** — everything under `releases/{artist-slug}/{release-slug}/`.
- **Deterministic dates** — `build_campaign_timeline.py`, never by hand.
- **Completion gate** — `validate_release.py` must say `ok` before "ready".
- **Never fabricate** release facts, numbers, placements, or press — blank + flag.

## References

- `references/release-workspace.md` — the workspace schema/contract.
- `references/endpoints.md` · `references/response-shapes.md` — research API.
- `references/release-template.md` · `references/section-guide.md` ·
  `references/deliverables.md` — the doc + deliverables.
- `scripts/build_campaign_timeline.py` · `scripts/validate_release.py` — ship
  alongside this skill; invoke relatively.
