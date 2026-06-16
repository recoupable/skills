# RESOLVER — recoup-records skill dispatcher

> **This is the dispatcher, not an implementation.** It maps a user's intent to
> the one skill that owns it. **Read the matched skill's `SKILL.md` before
> acting.** If two skills could match, read both, then pick the narrower one.
> When nothing fits, say so plainly and offer the closest skill — do not
> improvise a half-version of a job a skill already owns.
>
> Why this file exists: `recoup-records` bundles **43 skills** — past the point
> where description-only auto-matching routes cleanly. This table is the single
> place routing decisions are made once, so skills don't drift or go "dark"
> (built but unreachable). It is verified by `scripts/check_resolvable.py`
> (every skill is reachable from here; every row points at a real skill) and by
> `tests/resolver-eval.jsonl` (the right skill fires for real phrasings; the
> wrong ones don't).

## How to route

1. Find the **domain** below that matches the request.
2. Within it, match the **intent** to a single skill.
3. Open that skill's `SKILL.md`. Follow it.
4. If the request spans domains (e.g. "research the artist then make content"),
   route to each in sequence, or to the domain's **workflow** skill if one owns
   the whole arc (`recoup-deal-start`, `recoup-release-start`).

---

## Domain 1 — Setup & account (start here if unconfigured)

| Intent | Skill |
|---|---|
| First-run setup, verify email/PIN, issue + persist an API key | `recoup-setup` |
| Scaffold the initial sandbox file system from the account's orgs/artists | `recoup-setup-sandbox` |
| Call the Recoupable API / connectors directly (artists, socials, docs, research) | `recoup-api` |
| Create / onboard / identify / enrich a **new artist** account | `recoup-artist-create` |
| Work *inside* an artist directory — scaffold, enumerate, edit the workspace | `recoup-artist-workspace` |
| Capture a solved problem / "remember this" / "that worked" into the learnings store | `recoup-learn` |

- `recoup-artist-create` (the playbook for *bringing an artist into existence*)
  vs `recoup-artist-workspace` (the rules for *operating in* an artist's folder):
  create first, then operate. They cross-reference.

## Domain 2 — Research & A&R (on-demand, pull live data, answer now)

| Intent | Skill |
|---|---|
| Comprehensive one-time sweep / "research [artist]" / "tell me about [artist]" | `recoup-artist-research` |
| Audience demographics, geography, market expansion, tour routing, TikTok→Spotify funnel | `recoup-artist-audience` |
| Compare artists, competitive positioning, find collaborators, time a release vs peers | `recoup-artist-competition` |
| Discover **emerging/unsigned** artists you don't track; why a song went viral | `recoup-artist-scout` |
| Catalog-wide playlist strategy — targets, gaps, editorial vs algorithmic coverage | `recoup-artist-playlists` |
| Find managers / A&R / press contacts; draft outreach; enrich CRM | `recoup-artist-outreach` |
| Per-song **TikTok signal** view for one artist ("which songs are blowing up") | `recoup-artist-tiktok` |
| Web/deep research, URL extraction, entity enrichment when structured data is thin | `recoup-web-research` |

- `recoup-artist-research` is the **broad sweep**; the others are **focused
  lenses** on one facet. Start broad only when the ask is broad; otherwise route
  straight to the lens.
- Structured (Songstats-backed) data → the `recoup-artist-*` skills. No structured
  data / need narrative from the open web → `recoup-web-research`.
- Playlist **strategy across a catalog** → `recoup-artist-playlists`. Playlist
  **pitch for one song from its audio** → `recoup-song-pitch-kit` (Domain 4).

## Domain 3 — Monitors (scheduled / recurring; diff vs last run; save an artifact)

| Intent | Skill |
|---|---|
| Recurring **dated weekly brief** that diffs against last week and writes a file | `recoup-artist-brief` |
| Streaming health check — flag Spotify/DSP spikes or drops vs last check | `recoup-artist-streaming` |
| Confirm a release actually dropped; build a launch-day alert | `recoup-release-monitor` |

- These are the **scheduled twins** of on-demand research skills. "Analyze the
  audience now" → `recoup-artist-audience`; "watch [artist] every week" →
  `recoup-artist-brief`. State the modality (ask-now vs runs-on-a-cadence) when
  disambiguating.

## Domain 4 — Song audio analysis (needs an audio file; Music Flamingo)

| Intent | Skill |
|---|---|
| Analyze a track from audio — full report, catalog metadata (BPM/key/genre/mood), lyric sheet, mix critique | `recoup-song-analyze` |
| Find the most clip-worthy **5–15s hook** to lead short-form with | `recoup-song-hook` |
| Turn one song's audio into a **playlist pitch + sync brief** | `recoup-song-pitch-kit` |
| Write/evaluate **lyrics & song concepts** (no audio needed) | `recoup-songwriting` |

- These need the **audio**. "What playlists should the catalog target" (no audio,
  research data) → `recoup-artist-playlists` (Domain 2), NOT `recoup-song-pitch-kit`.
- `recoup-song-hook` produces timestamps → feed them to a video skill (Domain 5).
  Don't clip from a plain transcript.

## Domain 5 — Content creation (stops at the finished asset; never posts)

**Router:** `recoup-content` — the front door for "make me something for this
artist." Route through it when the format is unspecified; otherwise go direct:

| Intent | Skill |
|---|---|
| Unspecified format — "make me something for [artist]" (disambiguates, then routes) | `recoup-content` |
| Caption / post copy in the artist's voice | `recoup-content-caption` |
| Finished 9:16 short-form music video (TikTok/Reel/Short) | `recoup-content-video` |
| Lyric video — whole song's words animated, timed to audio, over motion | `recoup-content-lyric-video` |
| Looping visualizer / Spotify Canvas — short, seamless, no-text loop | `recoup-content-visualizer` |
| Square DSP cover art (single/EP/album) | `recoup-content-cover-art` |
| 16:9 YouTube thumbnail with focal face + hook text | `recoup-content-thumbnail` |
| Still graphic — carousel/photo dump, announcement/promo, or single lyric/quote card | `recoup-content-graphic` |
| React to a **real timely trigger** (milestone, sync, chart entry) or current trend | `recoup-content-trend` |
| Batch "clip family" — 15–30 assets for one song's push | `recoup-content-pack` |
| Reformat a master video per platform, or polish the artist's own footage | `recoup-content-reformat` |

- Motion jobs are distinct: **video** (artist + song clip) vs **lyric-video**
  (words on screen) vs **visualizer** (no-text loop). Match the described output.
- Still images: **cover-art** (square DSP) vs **thumbnail** (16:9 + hook) vs
  **graphic** (carousel / promo / quote-card modes). Match aspect + purpose.
- `recoup-content-trend` reacts to **news/a trigger**, then routes the actual
  asset to a graphic/caption/video skill. Use it when the trigger is an event,
  not a format.
- Need the hook to clip first? → `recoup-song-hook` (Domain 4), then a video skill.

## Domain 6 — Catalog deals (workflow bundle; immutable source; completion-gated)

**Workflow front door:** `recoup-deal-start` — one command, end-to-end. Single
stages below are runnable on their own for power users.

| Intent | Skill |
|---|---|
| Full end-to-end deal review (ingest → value → dashboard → report) | `recoup-deal-start` |
| 60-second demo on the bundled synthetic catalog | `recoup-deal-demo` |
| Ingest/normalize a data room, royalty statements, rights files, metadata | `recoup-deal-ingest` |
| Value the catalog (NPS/NLS, concentration, decay, scenarios) | `recoup-deal-value` |
| Build/refresh/QC the customer-facing `DASHBOARD.html` | `recoup-deal-dashboard` |
| Assemble IC memo / seller cleanup / financing pack → shareable PDF | `recoup-deal-report` |
| Value a catalog/album/recording from **public data alone** (no seller files) | `recoup-catalog-value` |

- `recoup-deal-value` requires **ingested seller files** (a real deal workspace);
  `recoup-catalog-value` estimates from **public/streaming data only** (no data
  room). Pick by what inputs exist.

## Domain 7 — Releases (workflow bundle; RELEASE.md workspace; completion-gated)

**Workflow front door:** `recoup-release-start` — one command, end-to-end.

| Intent | Skill |
|---|---|
| Full end-to-end release workflow | `recoup-release-start` |
| Demo the release workflow on a synthetic artist+release | `recoup-release-demo` |
| Data-grounded pre-release **creative brief** (concepts, angles, playlist targets) | `recoup-release-brief` |
| The master `RELEASE.md` doc + deliverables (DSP pitch, press one-sheet, spec) | `recoup-release-doc` |
| Dated **rollout schedule** (pre/release-week/post timeline, channels, owners) | `recoup-release-campaign` |
| Confirm the release dropped; launch-day alert | `recoup-release-monitor` |

- `recoup-release-brief` (the *creative direction* artifact) vs
  `recoup-release-campaign` (the *dated schedule* artifact) vs `recoup-release-doc`
  (the *source-of-truth document*). Three different artifacts — match the noun the
  user asks for.

---

## Cross-domain disambiguation (the pairs people confuse)

- **Playlist work:** catalog strategy → `recoup-artist-playlists`; single-song
  pitch from audio → `recoup-song-pitch-kit`.
- **Valuation:** with seller files → `recoup-deal-value`; public data only →
  `recoup-catalog-value`.
- **"Make something for a milestone":** the *reaction/angle* → `recoup-content-trend`;
  the underlying *event data* → a Domain 2/3 research skill.
- **Briefs:** weekly performance brief → `recoup-artist-brief`; pre-release creative
  brief → `recoup-release-brief`. Different artifacts, different domains.
- **"Research then act":** route research (Domain 2) first, then content (5) or a
  workflow (6/7). The workflow front doors already chain what they need.
