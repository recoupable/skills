---
name: recoup-content-make-graphics
description: Make still-image assets for an artist — cover art, thumbnails, carousels, promo/announcement graphics, and quote/lyric cards. Use for "make cover art", "a thumbnail", "a carousel", "a promo graphic", or "a quote card". Picks the format from the ask, generates to spec, and verifies the render before claiming done. Stops at the asset; never posts.
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

# Recoup Content — Make Graphics

One pipeline, five formats. Read the bundled references first:
`references/workspace-context.md`, `references/account-resolver.md`,
`references/research-context.md`, `references/content-api.md` (generation endpoints),
`references/analyze-gate.md` (verify a render before claiming done).

## Backbone

Resolve the artist + workspace, read `context/artist.md` (aesthetic) +
`context/audience.md` first, generate to spec, **analyze-gate** (you can't see
pixels — analyze the render against the format's checklist and regenerate on
failure), then persist + commit.

## Formats (pick one)

- **cover** — square 1:1, ≥3000px, brand-defining, **no hooky text**; reads at
  ~120px. → `releases/{slug}/cover.png`.
- **thumbnail** — 16:9, one focal face, ≤5 huge hook words off the face, high
  contrast; draft 3 hook options. → `content/thumbnails/`.
- **carousel** — outline slides first (hook→body→CTA), consistent treatment. →
  `content/carousels/{topic}/`.
- **promo** — **lock exact title/date(s)/CTA first** (a wrong date is unrecoverable);
  date+CTA dominate; 1:1 + 9:16. → `releases/{slug}/announcement-*.png`.
- **quote** — verify the wording (a typo'd lyric card gets screenshotted); large
  kerned high-contrast type. → `content/quote-cards/`.

Mode rules are opposites on purpose (cover forbids the hooky text thumbnail
requires) — pick the format, then obey its rule. Likeness: seed real faces with the
artist's own reference.

## Guardrails

- **Verify before delivery** — run the analyze gate every time.
- **promo dates / quote wording must be exact.**
- **Stop at the asset** — no posting.

## References

- `references/workspace-context.md` · `references/account-resolver.md` ·
  `references/research-context.md` · `references/content-api.md` ·
  `references/analyze-gate.md`
