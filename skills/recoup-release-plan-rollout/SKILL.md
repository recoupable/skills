---
name: recoup-release-plan-rollout
description: 'Plan and run a music release end to end — scaffold the workspace, write the creative brief, build the dated rollout schedule, produce the master RELEASE.md + DSP pitch + one-sheet, target playlists, and arm monitoring. Use for "start/plan a release", "take [title] start to finish", "creative brief", "rollout schedule", or "RELEASE.md / DSP pitch / one-sheet". Modes: plan (default, full workflow), brief, campaign, doc. Everything lands in releases/{artist}/{release}/. To confirm the drop afterward use recoup-release-track-drop.'
hooks:
  Stop:
    - hooks:
        - type: prompt
          timeout: 30
          prompt: |
            You are the completion-gate reviewer for the recoup-release-plan-rollout skill. The main agent is about to stop. Decide whether to block.

            Look for a COMPLETION CLAIM: the agent saying a release is 'ready', 'done', 'complete', 'set', 'good to go', 'ready to ship', or presenting a final release recap / landing card for a release workspace under releases/{artist-slug}/{release-slug}/.

            If NO completion claim is present, approve: {"decision": "approve"}. Ordinary chat, exploration, partial work, and single-stage runs (just the brief, just the campaign, just the doc) are all fine to stop on.

            If a completion claim IS present, verify each item. Treat anything not visibly satisfied in the conversation as unmet:
              a. python3 scripts/validate_release.py releases/{artist-slug}/{release-slug} was run during this session and returned status "ok" (look for the JSON with status=ok). Per the release-workspace contract, a release is not ready while the validator reports missing items.
              b. assumptions.yaml, RELEASE.md, a brief/ file, and a campaign/ file all exist in the workspace (this is what the validator checks).
              c. No fabricated numbers: any streaming counts, chart positions, playlist placements, or press are sourced or labeled as assumptions — not invented. Open gaps are listed in RELEASE.md section 8, not hidden.

            If any item is unmet, block:
            {"decision": "block", "reason": "<short list of unmet items>", "systemMessage": "Don't call the release ready yet. Run python3 scripts/validate_release.py on the workspace and resolve its missing[] items, dispatch the release-readiness-reviewer agent, and disclose any gaps in RELEASE.md section 8 before declaring ready."}

            If all items are satisfied, approve: {"decision": "approve"}.
---

# Recoup Release — Plan Rollout

The whole release lifecycle. **plan** runs the full workflow end to end; brief /
campaign / doc are the individual stages, runnable alone. Everything reads from and
writes to `releases/{artist-slug}/{release-slug}/`. The workspace schema is in
`references/release-workspace.md` (read it first); the scaffold is in
`templates/release-workspace/`. Deterministic helpers ship in `scripts/`
(`build_campaign_timeline.py`, `validate_release.py`). Requires `RECOUP_API_KEY` for
the brief/targeting stages.

## Mode: plan (the full workflow — don't stop between phases)

Run every phase in order; **do not stop to ask what's next**. Stop only when the
workspace is populated (brief + campaign + RELEASE.md exist) or a hard blocker hits.

1. **Intake + scaffold (≤30s).** Confirm release facts in one prompt (artist, title,
   type, date-or-TBD, goal, channels, one-line creative direction, asset gaps). Derive
   slugs. Copy `templates/release-workspace/` into the workspace and fill
   `assumptions.yaml`.
2. **Creative brief** → run **brief** mode; land in `brief/`.
3. **Dated campaign** → compute dates deterministically:
   `python3 scripts/build_campaign_timeline.py --release-date {YYYY-MM-DD|TBD} --type {type}`
   (returns every milestone + timing warnings like the ~28-day DSP editorial window),
   then run **campaign** mode; land in `campaign/`.
4. **Master doc + deliverables** → run **doc** mode; pull every fact from
   `assumptions.yaml` + the brief, never from memory.
5. **Playlist targeting (chained)** → call recoup-research-playlist-targets (targets +
   gaps) and recoup-research-find-contacts (curator + drafted pitch — draft only); if
   audience is thin, recoup-research-artist-overview (audience). Land in `targeting/`.
6. **Arm monitoring** → note standing watches: recoup-release-track-drop (drop +
   launch alert) and recoup-research-weekly-brief (recurring + streaming spikes).
7. **Review + completion gate (do not skip).** Run
   `python3 scripts/validate_release.py releases/{artist-slug}/{release-slug}` — it
   must return `status: "ok"`; fix anything in `missing[]` and re-run, then dispatch
   the release-readiness-reviewer agent. On Claude Code a Stop hook enforces this;
   elsewhere it's your job.

End with the landing card: workspace path, "open first" list (RELEASE.md, brief/,
campaign/, targeting/, reports/), an honest "what I did NOT do and why" bullet per
gap, and next stages. **Truthfulness over polish** — never claim "ready" while a
stage is missing.

## Mode: brief (the creative brief)

Require artist, title, date-or-TBD, type, one-line creative direction, asset gaps
(ask once if missing). Pull in parallel (`references/endpoints.md`): `audience`
(TikTok+IG), `similar`, current `playlists`. Synthesize to `brief/brief-$(date +%F).md`:
creative direction (verbatim) · narrative thread · **3 visualizer directions** ·
**5 content angles** · platform hooks (each anchored in a concrete audience number) ·
ranked playlist targets · geo rollout · open decisions. It's a plan, not assets — to
produce assets use the recoup-content-* skills. No invented audience numbers.

## Mode: campaign (the dated rollout schedule)

Compute the timeline with `scripts/build_campaign_timeline.py` (never hand-do
release-date math), then turn it + the brief into a phase-by-phase plan (pre-release →
release-week → post-release) with channels, assets, owners, and exact dates counted
back from the release date. Land in `campaign/`. Flag timing risks.

## Mode: doc (the master RELEASE.md + deliverables)

Create/maintain `RELEASE.md` as the single source of truth using
`references/release-template.md` + `references/section-guide.md`, then generate the
DSP pitch and press one-sheet into `reports/` per `references/deliverables.md`. Pull
every fact from `assumptions.yaml` + the brief. Copy that needs the house voice →
recoup-content-write-caption. Never fabricate placements/press — blank + flag in §8.

## Guardrails

- **No mid-workflow stops** in plan mode — run the next phase anyway.
- **One workspace** — everything under `releases/{artist-slug}/{release-slug}/`.
- **Deterministic dates** — `build_campaign_timeline.py`, never by hand.
- **Completion gate** — `validate_release.py` must say `ok` before "ready".
- **Never fabricate** release facts, numbers, placements, or press — blank + flag.

## References

- `references/release-workspace.md` · `references/endpoints.md` ·
  `references/response-shapes.md` · `references/release-template.md` ·
  `references/section-guide.md` · `references/deliverables.md`
- `scripts/build_campaign_timeline.py` · `scripts/validate_release.py` — ship
  alongside this skill; invoke relatively.
