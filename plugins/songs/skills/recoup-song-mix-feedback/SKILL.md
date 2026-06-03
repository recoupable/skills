---
name: recoup-song-mix-feedback
description: Give a technical mix critique of a song from its audio using Recoup's audio language model (Music Flamingo). Use when asked to "critique this mix", "what should I fix in the mix", "is the low end muddy", "give me mix notes", or "review this master". Needs a public audio URL. The model is a critique aid, not a replacement for an engineer or metering.
---

# Song Mix Feedback Reviewer (Music Flamingo)

Give artists and producers a structured mix critique with concrete, prioritized
fixes.

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md`. Read it before calling.

## When to use

- "Critique this mix" / "give me mix notes"
- "Is the low end muddy?" / "is the vocal too harsh?"
- "Review this master"

For arrangement/harmony questions, also pull `music_theory`. For A&R-level song
feedback, that is a separate (future) `recoup-song-ar-reviewer` skill.

## Preset chain

- **Required:** `mix_feedback`
- **Usually add:** `music_theory` when the user also asks about arrangement or
  harmony
- **Optional:** a **custom prompt** for a specific concern, e.g. "Focus on vocal
  harshness and mono compatibility." (custom prompt instead of a preset, still
  with `audio_url`)

## Steps

1. Resolve a **public `audio_url`** (no local file upload).
2. Call `mix_feedback`, or send a custom prompt for a targeted concern.
3. Organize notes by frequency band and translate them into a prioritized
   checklist.

## Output

Mix notes grouped by:

- Low end
- Vocal range / midrange
- High end (air / harshness)
- Stereo image
- Dynamics
- Concrete processing fixes

Plus a **prioritized revision checklist** (what to fix first).

If inside an artist workspace, save to `songs/{song-slug}/analysis/mix-feedback.md`.

## Guardrails

- **The model is a critique aid, not a replacement** for an engineer's ears or
  metering. Frame suggestions as starting points to verify, not gospel.
- Be specific and actionable; avoid vague "make it punchier" notes.
- **Public URL required**; no local file upload. **No `account_id` in the body.**

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas.
