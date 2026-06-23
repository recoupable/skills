---
name: recoup-content-write-caption
description: Write social captions in an artist's own voice — diarized from their context and past posts, checked against an anti-slop fingerprint. Use for "write a caption for [artist]", "post copy", or "what should they post". Stops at the text; never posts. To make the visual it goes with, use recoup-content-make-graphics or recoup-content-make-video.
---

# Recoup Content — Write Caption

Voice fidelity is the moat. Read the bundled references first:
`references/workspace-context.md` (read-context-first + write-back),
`references/account-resolver.md` (auth + account_id vs row id),
`references/research-context.md` (live signals).

## Procedure

Diarize the artist's voice into a checkable fingerprint (length/caps/emoji/
punctuation/lexicon + an explicit "avoid" list) from `context/artist.md` +
`context/audience.md`, or fall back to 10–30 real past captions
(`/artists/{ROW_ID}/posts`) as few-shot anchors. Draft `Count` (default 3) distinct
angles **through** the fingerprint. **Verify** each against the fingerprint + an
anti-slop checklist (no "Get ready", "Mark your calendars", emoji stacks, lines that
fit any artist); drop/redraft failures. Never invent a voice — no context + no posts
→ ask. Persist to `content/captions/`.

## Guardrails

- **Never fabricate the voice** — diarize from real context/posts or ask.
- **Stop at the text** — no posting/scheduling.

## References

- `references/workspace-context.md` · `references/account-resolver.md` ·
  `references/research-context.md`
