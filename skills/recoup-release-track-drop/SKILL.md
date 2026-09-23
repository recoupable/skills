---
name: recoup-release-track-drop
description: Confirm a release actually dropped and build a launch-day alert — checks whether the single/album went live and surfaces the first-day signals. Use for "did [artist]'s single drop", "launch alert", or "watch for the drop". Idempotent and dated; saves to the release workspace. For ongoing weekly streaming-spike watching use recoup-research-weekly-brief.
---

# Recoup Release — Track Drop

Confirm the release dropped and build a launch-day alert from the research API.
Idempotent + dated; save to `releases/{artist-slug}/{release-slug}/tracking/`.

## Procedure

Check whether the release is live (`GET /spotify/artist/albums?id=` for the title,
then `GET /spotify/album` for its tracks), then pull launch-day signals: a `current`
measurement job on the album → `GET /research/playcounts?spotify_album_id=` for
first-day play counts, `GET /artists/{id}/socials` for follower counts, and one
`POST /research/web` for press or playlist mentions. Classify the launch (live yet?
early streaming? any coverage?) and write a dated tracking file + a short chat
summary. If it isn't live yet, say so — don't fabricate.

For ongoing streaming-spike watching across the catalog, use
recoup-research-weekly-brief (streaming scope).

## Guardrails

- **Idempotent + dated** — re-runs surface the existing file rather than duplicate.
- **Never fabricate** a drop, placement, or number.

## References

- `references/response-shapes.md` — measurement-store and web research shapes.
