---
name: recoup-song-hook
description: Find a song's most clip-worthy 5–15s moments — the hook to lead short-form video with — from its audio using Recoup's audio language model (Music Flamingo). Use when asked to "find the hook", "best 15 seconds", "what part should I clip", "where's the drop", "which moment for TikTok/Reels", or "what section will go viral". Returns ranked timestamps to clip; it does NOT produce a finished video (hand the timestamps to recoup-content-video for that). Needs a public audio URL.
---

# Song Hook Finder (Music Flamingo)

Short-form lives or dies on the first 1–3 seconds. This skill finds the **moments**
of a song most likely to stop the scroll — the drop, the chorus/title line, the
peak — from the song's actual audio structure and energy, and hands back exact
timestamps a video skill can lead with.

This is **audio analysis**, so it runs on Music Flamingo (the same model as the
other `recoup-song-*` skills) — a transcript gives word timings but no idea where
the energy peaks; Flamingo's structure + energy output is what makes a *hook*.

The endpoint contract (auth, base URL, request/response, presets, call patterns,
gotchas) is in `references/flamingo-api.md`. Read it before calling.

## Preset chain

- **Required:** `sync_brief_match` — energy curve, emotional arc, timestamped moments.
- **Add:** `music_theory` — sections + duration, so a window snaps to a real
  boundary (intro / verse / chorus / drop) instead of an arbitrary cut.
- **Usually add:** `lyric_transcription` — the most quotable line to caption with.

## Steps

1. Resolve a **public `audio_url`** (no local file upload).
2. Call `sync_brief_match`; add `music_theory` for section boundaries and
   `lyric_transcription` for the quotable line.
3. Align the highest-energy moments with section starts and the most quotable
   lyric — the best hook is where energy + section change + a memorable line coincide.
4. Return **ranked candidates**.

## Output

Top 3 windows, each with:

- `start`–`end` — target **5–15s** (≈7s if it needs to loop).
- Moment type — drop, chorus/title line, beat switch, emotional peak.
- The quotable line in that window, if any.
- One line: **why this stops the scroll**.

Recommend one. To build the clip, hand the timestamps to a content skill
(`recoup-content-video`, `recoup-content-pack`, `recoup-content-reformat`). If
inside an artist workspace, save to `songs/{song-slug}/analysis/hooks.md`.

## Guardrails

- **Timestamps come from the analysis, not vibes** — they feed real edits.
- **5–15s windows.** A 40s "hook" isn't a hook.
- **Public URL required**; no local file upload. **No `account_id` in the body.**

## Reference

- `references/flamingo-api.md` — auth, base URL, request/response, preset table,
  call patterns, gotchas.
