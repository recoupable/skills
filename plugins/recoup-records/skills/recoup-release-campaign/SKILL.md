---
name: recoup-release-campaign
description: >
  ARTIFACT: a dated rollout SCHEDULE (pre-release → release-week → post-release
  timeline with channels, assets, owners, dates counted back from the release
  date). Use for "plan the rollout for [single/EP/album]", "build a release
  campaign", "what's the schedule for release week", "give me a pre-release plan".
  This is one of three release skills — for CREATIVE DIRECTIONS use
  recoup-release-brief; for the master DOC + DSP pitch use
  recoup-release-doc; this one is the SCHEDULE. For "where do I even start" use
  recoup-release-start; for copy tone use recoup-content-caption.
license: Proprietary
metadata:
  owner: agent@recoupable.com
  status: draft
  user-invocable: true
---

# Recoup Release Campaign

Build an executable, dated marketing campaign for a music release. The output is
a timeline a human can run, not a vibe — every line has a date (or relative
offset), a channel, an asset, and an owner.

## Required inputs

- **Artist** and **release** (title, format: single / EP / album / video).
- **Release date** (or "TBD" — then plan in relative offsets).
- **Goal metric** (streams, saves, playlist adds, ticket sales, press).
- **Channels available** (IG, TikTok, X, YouTube, email list, DSP pitching,
  press/PR) and whether there's paid budget.

Ask for any of these that are missing before producing the timeline. Never
invent performance numbers, playlist placements, or press commitments.

## Workflow

1. **Anchor on the release date — compute dates deterministically, don't do the
   math by hand:**

```text
python3 scripts/build_campaign_timeline.py --release-date {YYYY-MM-DD|TBD} --type {type}
```

   This returns every milestone as an offset (`R-21`, `R+7`) *and* its exact
   calendar date, plus timing warnings (e.g. the ~28-day DSP editorial window).
   Build your plan on those dates. (Script ships with this skill.)
2. **Build the three phases:**
   - **Pre-release (≈ R-28 → R-1):** announce, build anticipation, secure DSP
     pitch (note the ~4-week lead editorial playlists need), tease clips, open
     pre-save, line up press/feature placements.
   - **Release week (R-0 → R+6):** drop-day push across all channels, pin the
     pre-save→stream conversion, coordinate artist posting, send the email blast,
     activate any paid support, capture day-one reactions.
   - **Post-release (R+7 → R+28):** sustain with follow-up content, chase
     playlist/press momentum, repurpose top-performing clips, report results
     against the goal metric.
3. **For each milestone, specify:** date/offset · channel · asset needed · owner
   · the one outcome it drives.
4. **List the asset checklist** the campaign depends on (cover art, vertical
   clips, lyric/visualizer, EPK/one-sheet, pre-save link, email copy) and flag
   which are missing.
5. **Close with a measurement plan:** what to check at R+7 and R+28 against the
   stated goal metric, and the trigger for doubling down vs cutting.

## Output format

A phase-grouped table or checklist (offset → action → channel → asset → owner),
followed by the asset checklist and the measurement plan. Keep it scannable.

When run inside a release workspace, save to
`releases/{artist-slug}/{release-slug}/campaign/campaign-$(date +%F).md`
(the `campaign/` folder of the shared workspace). Re-running the same day is a
no-op.

## Edge cases

- **DSP editorial lead time:** if the release is under ~3 weeks out, flag that
  the pitch window for editorial playlists is tight or closed.
- **No paid budget:** weight the plan toward organic + artist-driven content and
  say so; don't assume ad spend.
- **Catalog / re-release:** lean on the existing audience and anniversary hooks
  rather than a "new artist" discovery push.

## Quality bar

The #1 failure mode is a **timeline with no owners or no dates** — that's a wish
list, not a campaign. Every line is actionable and assigned. If the user can't
hand a row to a person and have them execute it, tighten it.

## When to escalate

If the campaign needs historical data or fan insights you don't have, ask for
them or mark the gap. If the request is broader than one release (full artist
strategy), route back to `recoup-release-start`.
