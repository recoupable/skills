---
name: recoup-internal-podcast
description: 'INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke ONLY when the request explicitly includes "recoup-internal". Never use for customer-facing or artist requests. The Recoup Podcast episode, from the studio to the shorts: recording prep (the day-before camera test, what not to run during the take), post-production from the raw Restream files to an edited news-desk episode (transcripts, cut list, chapter graphics, cold open and intro, enhanced audio, assembly, captions), packaging (title, description, covers, guest photo), publishing on Spotify and YouTube, and one vertical short a day from release. Use for "edit the podcast episode", "produce <guest>''s episode from the raw files", "render the chapters", "make the podcast thumbnail", "publish the podcast to Spotify and YouTube", "cut the shorts", "prep tomorrow''s recording". Guest invites, nudges, booking, consent and the guest emails are recoup-internal-sales; deciding what our social accounts post today is recoup-internal-marketing.'
---

# Recoup Internal — Podcast

One Recoup Podcast episode, from the studio to the last short. The other two skills hand off to this one:

| Before | This skill | After |
|---|---|---|
| `recoup-internal-sales`: invite, nudges, booking and the timeline PDF, guest brief, same-day CRM close-out | recording prep → post-production → packaging → publish → shorts | `recoup-internal-sales`: live links to the guest, wrap-up and day-7 emails. `recoup-internal-marketing`: which short goes out today, measured against the funnel |

The podcast is the top of the agency sales funnel, so every public piece is also sales copy for a firm that
charges for builds (`references/podcast-packaging.md`).

## The run

| Phase | Reference | Gate before the next phase |
|---|---|---|
| 1. Recording prep | `references/recording-prep.md` | Host camera test at ~30 fps, or the low-fps plan agreed |
| 2. Post-production | `references/podcast-episode.md` steps 0-12 | Owner approves the analysis, the audio rough cut, the prototype, each chapter and the assembled episode |
| 3. Packaging | `references/podcast-packaging.md`, episode steps 13 and 15 | Owner approves title, description and both covers; the guest approves their cover photo |
| 4. Publish | `references/podcast-episode.md` steps 14 and 16 (episode page) | Owner makes the Publish or Schedule click; every field re-read from the platform; the episode page merges after the release minute |
| 5. Shorts | `references/podcast-shorts.md` | Clips table approved, then one prototype short (real references on screen; three directions when the look changes), then the rest |
| 6. Hand back | `references/podcast-episode.md` step 18 | Sales sends the live links |

**Where it runs:** read `~/.config/recoup/podcast-sandbox.json` before post-production. `"default": "sandbox"`
means every re-cut, build and render runs on Vercel Sandbox through `scripts/podcast/sandbox/studio.mjs`
(`references/podcast-sandbox.md`); no file means the local commands in the references.

Scripts ship alongside this skill: `scripts/podcast/` (run as `python3 scripts/podcast/<name>.py <project>`),
`scripts/podcast/shorts/`, templates in `templates/podcast/`, fonts and logos in `brand/`. One project
folder per episode, outside this skill (layout in `references/podcast-episode.md`). Private show assets (the
lockup PNG, the intro sting, the blue-sweep background) live in the operator's workspace and are passed in.

## Guardrails

- **Booking and joining the recording is the guest's consent;** a guest who withdraws before publication is not published. The sales guest pipeline owns the guest side.
- **Every stage is shown to the owner and approved before the next one.** Record each decision with who and
  when in the episode's `edit/ANALYSIS.md`; never re-ask an approved decision.
- **Nothing goes public without the owner's explicit go-ahead,** and the owner makes the final click.
- **Run scripts from a skills worktree of your own** on `origin/main`; parallel sessions switch or delete
  shared checkouts mid-render.
- **Sandbox default means sandbox only.** With `"default": "sandbox"`, never run `cut.py`, `build.py`,
  `build_hy.py`, `render.sh` or `hyperframes render` on the laptop, not even a quick re-cut; ask the owner first.
- **Nothing heavy during a live recording:** no local renders (and locally, one chapter at a time), no
  media uploads to the sandbox drive (they compete with Restream for the connection).
- **No em dashes in published copy** (titles, descriptions, cards, captions).
- **Motion follows huashu-art-motion** (installed skill) in the full episode and the shorts: real captures on
  screen, highlighter on the spoken line, numbers grown on the word. No more than 15 s of cameras only.
- **Real facts on cards only.** Every figure and claim on a card is checked against the transcript and the
  source; the recorder's mishearings and the guest's on-tape corrections are listed before cards are written.

## References

- `references/recording-prep.md` — the day-before studio test (frame-rate check, the phone-camera fallback), what not to run during the take, the dropout scan after
- `references/podcast-episode.md` — raw Restream files to scheduled episode: the news-desk format, project layout, the ordered run with approval gates, enhancing only what the cut plays, assembly, publish traps
- `references/podcast-packaging.md` — premium episode copy (title shape, description, cold open, back catalog), the cover spec, guest photo sourcing, Spotify for Creators edits
- `references/podcast-sandbox.md` — the optional Vercel Sandbox path: which operators use it, what stays local, one-time setup, media upload, build/run jobs, gotchas
- `references/podcast-shorts.md` — vertical shorts: the clips table gate, the hybrid format, beat design, build/snapshot/render, per-platform captions and UTMs
