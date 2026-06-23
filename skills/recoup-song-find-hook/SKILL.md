---
name: recoup-song-find-hook
description: Find the most clip-worthy 5–15 seconds of a song to lead short-form content with — the moment where energy, a section change, and a quotable line coincide. Use for "find the hook", "best 15 seconds to clip", "what to clip", or "where's the drop". Requires a public audio URL. Hand the timestamps to recoup-content-make-video to build the clip.
---

# Recoup Song — Find Hook

Find the moments most likely to stop the scroll, for short-form. Uses Music
Flamingo — the endpoint contract is in `references/flamingo-api.md` (read first).
Needs a **public `audio_url`**; never put `account_id` in the body.

## Procedure

Run `sync_brief_match` (energy curve + timestamped moments) + `music_theory` (so a
window snaps to a real section boundary, not an arbitrary cut) + `lyric_transcription`
(the quotable line). The best hook is where **energy + section change + a quotable
line** coincide.

Return **3 ranked windows**, each with `start`–`end` (target 5–15s; ≈7s if it must
loop), the moment type (drop/chorus/beat-switch/peak), the quotable line, and one
line on why it stops the scroll. Timestamps come from the analysis, not vibes — they
feed real edits; hand them to recoup-content-make-video. Save to
`songs/{song-slug}/analysis/hooks.md`.

## Guardrails

- **Audio-grounded only** — windows come from the analysis, never guessed.
- **Hook windows are 5–15s** — a 40s "hook" isn't a hook.
- **Public URL required**; no `account_id` in the body.

## References

- `references/flamingo-api.md` — presets + call patterns.
