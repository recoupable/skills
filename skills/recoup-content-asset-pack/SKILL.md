---
name: recoup-content-asset-pack
description: Generate a whole batch of content assets for one song — a cohesive 15–30-piece clip family (videos, quote cards, a carousel, a visualizer, captions) themed to the audience. Use for "content pack", "30 posts for the launch", or "a bunch of content for [song]". Estimates and confirms cost before spending. Stops at the assets; never posts.
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

# Recoup Content — Asset Pack

Orchestrates the other content modes into one cohesive batch for a song. Read the
bundled references first: `references/workspace-context.md`,
`references/account-resolver.md`, `references/research-context.md`,
`references/content-api.md`, `references/song-sourcing.md`,
`references/analyze-gate.md`.

## Procedure

**Estimate + confirm cost before spending** (`POST /content/estimate`; on
`insufficient_credits` surface `checkoutUrl`) — no silent 30-asset fan-outs. A
~20-asset default: 6–10 video clips across looks (each led by a recoup-song-find-hook
hook), 4–6 quote cards, 1 carousel, 1 visualizer, captions per asset. **Theme to the
audience** (via recoup-research-artist-overview audience data) — bias looks/copy to
where the fans are. Analyze-gate every asset; assemble a `pack-manifest.md`.
Cohesion: a clip *family*, one look + voice.

*Boundary:* legitimate creative volume only — no fake-account farms or mass-posting;
decline the farm, deliver the pack.

## Guardrails

- **Estimate + confirm** before spending; surface `checkoutUrl` on insufficient credits.
- **Analyze-gate every asset.**
- **Stop at the assets** — no posting/scheduling.

## References

- `references/workspace-context.md` · `references/account-resolver.md` ·
  `references/research-context.md` · `references/content-api.md` ·
  `references/song-sourcing.md` · `references/analyze-gate.md`
