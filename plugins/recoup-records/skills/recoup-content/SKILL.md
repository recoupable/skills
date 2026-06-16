---
name: recoup-content
description: Make any social-ready content asset for an artist — captions, images (cover art, thumbnails, carousels, promos, quote cards), short-form videos, lyric videos, visualizers/Canvas, per-platform reformats, a whole content pack, or a reactive post off a real milestone/trend. Use when the user says "make content for [artist]", "write a caption", "make cover art / a thumbnail / a carousel / a promo / a quote card", "make a TikTok/Reel/short video", "lyric video", "visualizer / Spotify Canvas", "reformat this for TikTok", "content pack / 30 posts for the launch", or "they just hit [X], make something". Picks the mode from the ask; stops at the finished asset (does not post). To find which 5–15s of a song to clip, use recoup-song (hook).
---

# Recoup Content

Every content job an artist needs, behind one door. It **picks a mode from the
ask**, runs that mode's pipeline on one shared backbone, verifies the result, and
writes it back. It stops at the finished asset — it never posts or schedules.

Read the bundled references before generating: `references/workspace-context.md`
(read-context-first + write-back), `references/account-resolver.md` (auth +
`account_id` vs row `id`), `references/research-context.md` (live signals),
`references/content-api.md` (all generation endpoints + the 6 video modes +
async create→poll), `references/song-sourcing.md` (real audio, no placeholders),
and `references/analyze-gate.md` (verify a render before claiming done).

## Mode dispatch (pick one)

| The user wants… | Mode |
|---|---|
| caption / post copy in the artist's voice | **caption** |
| cover art, thumbnail, carousel/photo dump, promo/announcement, quote/lyric card | **image** |
| a finished 9:16 TikTok/Reel/Short of the artist + song | **video** |
| the song's words animated on screen | **lyric-video** |
| a no-text looping background / Spotify Canvas | **visualizer** |
| per-platform cuts of a master video, or polish their own footage | **reformat** |
| a whole batch (15–30 assets) for one song | **pack** |
| react to a real milestone/trend ("they just hit X, make something") | **trend** |

Format request → go straight to that mode. **News/trigger** ("they just hit
1M") → **trend** mode (it finds the real moment, then routes to a format mode).
Unspecified ("make me something for the launch") → ask one question (which
format, or a full pack?), then route. To find the clip-worthy moment first, use
`recoup-song` (hook) and feed the timestamps to **video**.

## Shared backbone (every mode)

1. **Resolve** the artist + workspace (`references/workspace-context.md`); if no
   artist is involved, run **generic mode** from the user's inputs — don't force a
   workspace. Auth + the `account_id`-vs-`id` footgun: `references/account-resolver.md`.
2. **Read context first** (`context/artist.md` voice/aesthetic, `context/audience.md`,
   `context/images/face-guide.png`, `releases/{slug}/RELEASE.md`), API second.
3. **Layer live signals** when they sharpen the asset (song tempo/mood, a real
   milestone) — `references/research-context.md`. Optional; skip in generic mode.
4. **Generate** for the mode (`references/content-api.md`).
5. **Verify with the analyze gate** — you cannot see pixels/motion; analyze the
   render against the mode's checklist and **regenerate on failure**
   (`references/analyze-gate.md`). Never claim an unverified asset is done.
6. **Persist** into the workspace and commit `{what}: {why}`; no workspace →
   return the URL(s).

---

## Mode: caption (text — voice fidelity is the moat)

Diarize the artist's voice into a checkable fingerprint (length/caps/emoji/
punctuation/lexicon + an explicit "avoid" list) from `context/artist.md` +
`context/audience.md`, or fall back to 10–30 real past captions
(`/artists/{ROW_ID}/posts`) as few-shot anchors. Draft `Count` (default 3)
distinct angles **through** the fingerprint. **Verify** each against the
fingerprint + an anti-slop checklist (no "Get ready", "Mark your calendars",
emoji stacks, lines that fit any artist); drop/redraft failures. Never invent a
voice — no context + no posts → ask. Persist to `content/captions/`.

## Mode: image (cover / thumbnail / carousel / promo / quote)

One pipeline, five sub-modes — generate to spec → analyze-gate → persist:

- **cover** — square 1:1, ≥3000px (upscale), brand-defining, **no hooky text**;
  reads at ~120px. → `releases/{slug}/cover.png`.
- **thumbnail** — 16:9, one focal face, ≤5 huge hook words off the face, high
  contrast; draft 3 hook options. → `content/thumbnails/`.
- **carousel** — outline slides first (hook→body→CTA), consistent treatment. →
  `content/carousels/{topic}/`.
- **promo** — **lock exact title/date(s)/CTA first** (a wrong date is the one
  unrecoverable error); date+CTA dominate; 1:1 + 9:16. → `releases/{slug}/announcement-*.png`.
- **quote** — verify the wording (a typo'd lyric card gets screenshotted); large
  kerned high-contrast type. → `content/quote-cards/`.

Mode rules are opposites on purpose (cover forbids the hooky text thumbnail
requires) — pick the sub-mode, then obey its rule. Likeness: seed real faces with
the artist's own reference.

## Mode: video (finished 9:16 short — async pipeline)

The artist's *look* is a **template** (bedroom/stage/outside/album-record-store),
not a separate job. Resolve the artist's **`account_id`** (not row `id` — wrong
one 404s), pick a template (default `artist-caption-bedroom`; list live via
`/content/templates`), fire `POST /content/create`, poll
`/tasks/runs?runId=` every ~10s until `COMPLETED|FAILED|CANCELED|CRASHED`, read
`output.{videoSourceUrl,captionText,…}`. The async path is agent-safe (sync
`/content/video` times out). **Analyze-gate** before claiming success; surface
`runs[0].error` on failure. Real audio only (`references/song-sourcing.md`).

## Mode: lyric-video (the song's words animated)

Transcribe for **word-level timings** (`POST /content/transcribe`, `audio_urls`
is an array → `segments:[{start,end,text}]`); prefer an official lyric sheet for
spelling, transcript for timing. Generate/use an on-brand background, **burn in
synced lyrics** via the edit endpoint, mux the song full-length, analyze-gate
(words readable, on-time, not clipped). Don't reproduce third-party lyrics.

## Mode: visualizer (no-text loop / Spotify Canvas)

Seamless loop, **no text/logos** (Spotify rejects them), 9:16, 3–8s. Match the
song's energy. Use `first-last` with identical start/end frames for a clean wrap.
**Analyze-gate the seam** (no visible cut at the wrap) — a hard cut means it's not
done; regenerate.

## Mode: reformat (per-platform cuts / polish footage)

Edit, don't generate. Master → genuinely **distinct** per-platform cuts (never
identical re-uploads — platforms suppress them): TikTok/Reels/Shorts 9:16 lead
with the hook (use `recoup-song` hook for the in-point), captions clear of UI
safe zones; X/feed 1:1 or 16:9, front-load the payoff. Or polish raw BTS/live
footage (trim, crop, caption). Analyze-gate each cut.

## Mode: pack (15–30-asset clip family for one song)

Orchestrates the modes above. **Estimate + confirm cost before spending**
(`POST /content/estimate`; on `insufficient_credits` surface `checkoutUrl`) — no
silent 30-asset fan-outs. A ~20-asset default: 6–10 **video** clips across looks
(each led by a `recoup-song` hook), 4–6 **image** quote cards, 1 carousel, 1
visualizer, captions per asset. **Theme to the audience** (via `recoup-research`
audience data) — bias looks/copy to where the fans are. Analyze-gate every asset;
assemble a `pack-manifest.md`. Cohesion: a clip *family*, one look + voice.
*Boundary:* legitimate creative volume only — no fake-account farms or
mass-posting; decline the farm, deliver the pack.

## Mode: trend (reactive — news, not a format)

Answers "something happened — what do we make of it?" **Find the real trigger**
(don't invent one): pull `milestones`/`career`/`playlists` from the research feed
(`references/research-context.md`); triage fresh-real vs stale (months old → tell
the user there's no fresh moment, offer evergreen) vs trend-only (use as
direction, keep facts from context). Pick the angle + the carrying format, write
a one-line angle in the artist's voice, then **route to the format mode above**
(image-promo / caption / video) — don't double-run a pipeline. Real or nothing:
every number/date traces to the feed or workspace.

---

## Guardrails (all modes)

- **Verify before delivery.** Presenting an un-analyzed visual/video is the
  failure this skill prevents — run the analyze gate every time.
- **Never fabricate** the voice, a date, a lyric, or a milestone.
- **Real audio only** (`references/song-sourcing.md`).
- **Stop at the asset** — no posting/scheduling.
- **promo dates / quote wording must be exact**; **pack must estimate+confirm**.

## References

- `references/workspace-context.md` · `references/account-resolver.md` ·
  `references/research-context.md` · `references/content-api.md` ·
  `references/song-sourcing.md` · `references/analyze-gate.md`
