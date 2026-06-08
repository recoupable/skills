---
name: recoup-song-hook
description: Find a song's most clip-worthy moments — the 5–15s hook to lead short-form with — by analyzing its audio with Recoup's audio language model (Music Flamingo). Use when asked "find the hook", "what part should I clip", "best 15 seconds", "which moment for TikTok/Reels", "where's the drop", or "what section will go viral". Returns ranked windows with timestamps and why each stops the scroll, for a video skill to clip. Needs a public audio URL.
---

# Song Hook Finder (Music Flamingo)

Short-form lives or dies on the first 1–3 seconds. This skill finds the **moments**
of a song most likely to stop the scroll — the drop, the chorus/title line, the
peak — from the song's actual audio structure and energy, and hands back exact
timestamps any video skill can lead with.

This is **audio analysis**, so it runs on Music Flamingo (the same model as the
other `recoup-song-*` skills) — not on a plain transcript. A transcript gives you
word timings but no idea where the energy peaks or the drop lands; Flamingo's
structure + energy output is what makes a *hook* a hook.

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md`. Read it before calling.

## When to use

- "Find the hook" / "what part should I clip?" / "best 15 seconds"
- "Which moment for TikTok/Reels/Shorts?" / "where's the drop?"
- "What section will go viral?"

To then *build* the clip, hand the timestamps to a content skill
(`recoup-short-video`, `recoup-content-pack`, `recoup-content-reformat`).

## Preset chain

- **Required:** `sync_brief_match` — gives the energy curve, emotional arc, and
  timestamped sync moments (the standout windows).
- **Add:** `music_theory` — sections + duration, so a window snaps to a real
  boundary (intro / verse / chorus / drop) instead of an arbitrary cut.
- **Usually add:** `lyric_transcription` — the most quotable line to caption the
  hook with.

## Steps

1. Resolve a **public `audio_url`** (no local file upload).
2. Call `sync_brief_match`; add `music_theory` for section boundaries and
   `lyric_transcription` for the quotable line.
3. Cross-reference: align the highest-energy sync moments with section starts and
   the most quotable lyric. The best hook is usually where energy + section change
   + a memorable line coincide.
4. Return **ranked candidates** (below).

## Output

Top 3 windows, each with:

- `start`–`end` — target **5–15s** (≈7s if it needs to loop).
- Moment type — drop, chorus/title line, beat switch, emotional peak.
- The quotable line in that window, if any.
- One line: **why this stops the scroll**.

Recommend one. If inside an artist workspace, save to
`songs/{song-slug}/analysis/hooks.md`.

## Guardrails

- **Timestamps come from the analysis, not vibes** — they feed real edits.
- **5–15s windows.** A 40s "hook" isn't a hook.
- **Public URL required**; no local file upload. **No `account_id` in the body.**

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas.
