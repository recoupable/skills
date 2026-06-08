---
name: recoup-content
description: Entry point for making content for an artist on Recoup — captions, short-form videos, and other social-ready assets. Use when the user says "make content for [artist]", "create a post for [artist]", "I need something for [artist]'s launch", "what can you make for [artist]", or any content request that isn't already specific about the format. Routes to the focused content skill for the job (brand-voice captions, short-form video, …) and enforces the shared rule that every content job reads the artist's workspace context first. Not for posting/publishing — this domain stops at the finished asset.
---

# Recoup Content (router)

The single front door for "make me something for this artist." It does two things:
disambiguate **what** the user wants, then hand off to the focused skill that does that
one job well. If only this skill is installed, run the closest matching workflow inline.

Every content job — whatever the format — shares one backbone: **when an artist is
involved, read their workspace context first, then layer live research signals, before
generating.** Context makes output sound and look like *this* artist; research signals
(the song's real tempo/mood, where it's charting, what just hit a milestone) make it about
what's *actually happening right now*. But both are **optional**: if the user just wants a
generic asset (no artist), run in **generic mode** from their inputs — don't force a
workspace. The three modes (context / API-fallback / generic) are spelled out in each
skill's bundled workspace-context reference; the signals layer is in its research-context
reference.

## Decision tree

Match the user's ask to the one skill that does that job:

**Video / motion**
- **"Make a video / TikTok / Reel / short clip of the artist + their song"** (studio,
  stage, bedroom, etc. — those are *template looks*, not separate jobs) →
  `recoup-short-video`.
- **"Lyric video / words on screen / kinetic typography"** → `recoup-lyric-video`.
- **"Visualizer / Spotify Canvas / looping background"** → `recoup-visualizer`.

**Static graphics**
- **"Album art / cover art / single artwork"** (square, DSP) → `recoup-cover-art`.
- **"YouTube thumbnail / clickable video cover"** (16:9, hook text) → `recoup-thumbnail`.
- **"Quote card / lyric card / typography post"** → `recoup-quote-cards`.
- **"Announcement / release date / pre-save / tour poster"** → `recoup-promo-graphic`.
- **"Carousel / photo dump / multi-image post"** → `recoup-carousel`.

**Text**
- **"Caption / post copy in the artist's voice"** → `recoup-brand-voice-caption`.

**Reactive / timely**
- **"Make something for [milestone] / they just hit X / what's the move right now / make it
  feel current"** → `recoup-trend-jack`. Reacts to a *real* event from the research feed
  (a milestone, a sync, a chart entry) or a current trend, then routes the actual asset to
  the graphic/caption/video skill. Use this when the trigger is "news", not a format.

**Workflow / high-value**
- **"Find the hook / best 15 seconds / what to clip"** → this is *audio analysis*,
  not a content job: use `recoup-song-hook` (in `recoup-song-analysis`) to get the
  timestamps, then feed them to a video skill. Don't clip from a plain transcript.
- **"A whole batch / content pack / week of content / 30 posts"** → `recoup-content-pack`.
- **"Reformat for each platform / resize / caption my own footage / clean up this BTS"** →
  `recoup-content-reformat`.

**Unspecified format** ("make me something for the launch") → ask one clarifying question
(which format, or a full pack?), then route. Don't guess between, say, a video and a
caption — different jobs, different costs.

When a requested job has no dedicated skill yet, say so and offer the closest one rather
than improvising a half-baked version.

## The shared backbone (every content skill follows this)

1. **Resolve the artist + workspace.** Find `artists/{slug}/` and read `RECOUP.md` for the
   canonical IDs. Auth + the `account_id`-vs-`id` distinction are the usual footguns.
2. **Read context first, API second.** `context/artist.md` (voice + aesthetic),
   `context/audience.md` (how fans talk), `context/images/face-guide.png` (reference
   image), `releases/{slug}/RELEASE.md` (release facts). Fall back to the API only when no
   workspace exists.
3. **Layer live research signals.** Pull the song's audio analysis (tempo/energy/mood → it
   drives the edit and template), playlist placements, current per-platform numbers, and any
   fresh milestone — then let them shape concrete choices. Optional and graceful: skip in
   generic mode, degrade if the API is cold. See the research-context reference.
4. **Generate the asset** for the specific job.
5. **Verify before claiming done.** For visual/video output the agent can't see pixels —
   analyze the result, benchmarked against the artist's real top posts when available, rather
   than asserting success.
6. **Write the result back** into the workspace and commit `{what}: {why}`.

Each `recoup-content-*` skill is self-contained and carries its own copies of the shared
references for steps 1–3, so any one of them works on its own.

## Scope boundary

This plugin produces **finished assets + captions**. It does **not** post or schedule to
TikTok/Instagram/YouTube — publishing via connectors is a separate concern. Stop at the
deliverable and hand the user (or a publishing skill) the asset.
