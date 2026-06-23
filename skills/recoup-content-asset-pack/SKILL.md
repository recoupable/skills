---
name: recoup-content-asset-pack
description: Generate a whole batch of content assets for one song — a cohesive 15–30-piece clip family (videos, quote cards, a carousel, a visualizer, captions) themed to the audience. Use for "content pack", "30 posts for the launch", or "a bunch of content for [song]". Estimates and confirms cost before spending. Stops at the assets; never posts.
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
