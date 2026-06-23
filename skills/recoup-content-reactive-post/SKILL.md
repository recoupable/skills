---
name: recoup-content-reactive-post
description: Turn a real milestone or trend into a timely post — finds the real moment (a chart entry, a streaming milestone, a fresh trend), picks an angle in the artist's voice, then routes to the right format. Use for "they just hit 1M, make something", "react to this trend", or "make something timely". Real moments only; never invents a milestone. The underlying data comes from recoup-research-artist-overview.
hooks:
  Stop:
    - hooks:
        - type: prompt
          timeout: 30
          prompt: |
            You are the analyze-gate reviewer for the recoup-content-* skill. The main agent is about to stop. Decide whether to block.

            The rule: the agent must NOT claim a visual or video asset is finished — 'ready', 'done', 'here's your video/image/thumbnail/clip', 'final', 'good to go', or any equivalent — unless an analyze-gate result for THAT asset appears in the conversation. The analyze gate is a POST to /api/content/analyze (or an equivalent visual inspection of the rendered output) whose result the agent reviewed. A render returning the right size/format/duration is NOT evidence the content is good; the agent cannot see pixels without analyzing.

            Decide:

            1. If the agent produced or is presenting a generated IMAGE or VIDEO asset AND is claiming it is finished/ready AND there is no analyze-gate pass (or explicit visual inspection) for that asset in the conversation, block:
            {"decision": "block", "reason": "visual/video asset presented as ready without an analyze-gate pass", "systemMessage": "Run POST /api/content/analyze on the rendered asset (see the analyze-gate reference) and review the result before claiming it's ready. If it fails, regenerate and re-analyze; if borderline, surface the analysis to the user instead of asserting success."}

            2. Otherwise approve:
            {"decision": "approve"}

            Default to approve for: text-only output (captions, copy, plans), generic chat or exploration, partial work where the agent is not claiming an asset is finished, jobs that produced no rendered pixels, and cases where an analyze-gate pass IS present. Be strict only when a generated image/video is being handed off as done with no verification.
---

# Recoup Content — Reactive Post

Answers "something happened — what do we make of it?" Read the bundled references
first: `references/workspace-context.md`, `references/account-resolver.md`,
`references/research-context.md`, `references/analyze-gate.md`.

## Procedure

**Find the real trigger** (don't invent one): pull `milestones`/`career`/`playlists`
from the research feed (`references/research-context.md`); triage fresh-real vs stale
(months old → tell the user there's no fresh moment, offer evergreen) vs trend-only
(use as direction, keep facts from context). Pick the angle + the carrying format,
write a one-line angle in the artist's voice, then **route to the format**:
recoup-content-make-graphics (promo) / recoup-content-write-caption /
recoup-content-make-video — don't double-run a pipeline. Real or nothing: every
number/date traces to the feed or workspace.

## Guardrails

- **Never fabricate** a milestone, date, or number — it traces to the feed or workspace.
- **Stale ≠ fresh** — months-old isn't a moment; say so and offer evergreen.
- **Stop at the asset** (via the routed format skill) — no posting.

## References

- `references/workspace-context.md` · `references/account-resolver.md` ·
  `references/research-context.md` · `references/analyze-gate.md`
