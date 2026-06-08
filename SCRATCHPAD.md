# SCRATCHPAD — restructuring `recoup-content` into a focused, context-fused skill set

> Brainstorm doc (v2 — corrected after terminology review + 2026 research). Goal: take today's
> single content front-door (`plugins/content/`) and the two standalone skills
> (`skills/short-video`, `skills/content-creation`) and reorganize into a lean skill set that
> compounds **content generation × Recoup artist context**, following the repo's actual plugin
> conventions. Nothing here is built yet.

---

## 0. TL;DR thesis (unchanged — research strengthened it)

**Anyone can call an image/video API. Only Recoup can generate content that already knows the
artist** — catalog, fastest-rising TikTok track, audience cities/languages, brand voice from
past posts, fans' aesthetic, last milestone. The atomic primitives are the floor; **the context
fusion is the moat.** 2026 research backs this hard: the bespoke "trend simulation" play is
*"identify a song's target audience and post where that audience is"* — which needs the exact
audience data we already have.

---

## 1. Terminology + best-practices correction (from review)

Two fixes vs v1 of this doc:

- **Dropped the word "recipes" as a category.** `grep` shows `recipe` is only **prose** in this
  repo (`short-video`, `create-artist` describe themselves as "the canonical recipe"). It is NOT
  structural vocabulary. The repo's real vocabulary is: **skill, plugin, router skill, reference,
  template, fixtures, scripts, standalone vs plugin skill.** These things are just **skills**
  (specifically *output/job skills*) routed by a **router skill** — the pattern every other
  plugin already uses (`recoup-song-analyzer`, `recoup-deal-start`).
- **Stopped over-atomizing.** v1 proposed 8 one-API-call primitive skills. That's "one skill, one
  *call*," not "one skill, one *job*" — it bloats the router and makes descriptions collide.
  `content-creation` already covers the primitives as **building blocks**; keep it, don't shatter
  it.

---

## 2. The organizing rule: how specific is a skill? (one JOB, not one API call)

The load-bearing decision, settled from our **own** codebase. The `songs` plugin is the proof:
**all 6 song skills hit the SAME endpoint** (Music Flamingo `/api/songs/analyze`) — they are not
split by API call. They split by **job**:

| Skill | Trigger | Deliverable | Reader |
|---|---|---|---|
| `recoup-song-metadata` | "tag this song" | catalog metadata | DSPs / catalog systems |
| `recoup-song-lyrics` | "transcribe the lyrics" | lyric sheet | the artist |
| `recoup-song-playlist-pitch` | "pitch this to Spotify" | pitch materials | DSP editors |
| `recoup-song-sync-brief` | "where could this be placed" | sync brief | music supervisors |
| `recoup-song-mix-feedback` | "critique this mix" | mix notes | engineers |
| `recoup-song-analyzer` | "analyze this song" | router | — |

### The rule
> **A skill is one JOB, not one API call.** Carve where three things change together:
> (1) the **trigger phrases** a user would type, (2) the **deliverable/output**, (3) the
> **reader + quality bar**. Split when those differ — *even if the API call is identical.*

### The cost that sets the ceiling
Every skill `description` is **always** in the router's context (progressive disclosure). Too many
→ descriptions collide and routing misfires. Practical ceiling ≈ `research` (11 skills). So: split
by job, but only for **real, recurring, distinctly-phrased** asks.

### Three knobs, in priority order
| Knob | Use for | Example |
|---|---|---|
| **Skill** | A distinct JOB (trigger + deliverable + reader differ) | cover art ≠ quote cards ≠ announcement |
| **`type`/mode param** | Same job, cosmetic variant | thumbnail = a mode of cover-art; caption length |
| **Template** | A *look* within a job (existing API concept) | bedroom vs stage vs album-store, all 9:16 video |

**Answer to "shortform as a skill with template=type?":** No. Template = look, never type. A type
that's a different *job* = its own skill (by the songs precedent). A type that's the *same job* =
a param. **This revises v1's "one `recoup-graphics` skill" — that was too coarse;** cover/quote/
announce/carousel are different jobs → separate skills. Frequency + distinctness is the tiebreaker.

---

## 3. What exists today

| Thing | Location | Role |
|---|---|---|
| `recoup-short-video` | `plugins/recoup-content/skills/recoup-short-video/` | Plugin front door — async end-to-end 9:16 video (renamed from recoup-content-create) |
| `recoup-short-video` (legacy) | `plugins/recoup-content/commands/` | Back-compat command, slated for deletion |
| `short-video` | `skills/short-video/` (standalone) | Per-stage short-form video skill (async + manual) |
| `content-creation` | `skills/content-creation/` (standalone) | Atomic `/api/content/*` building blocks |

Content is dramatically under-split vs `research` (11 skills), `deals` (7), `songs` (6). The whole
domain is "one finished 9:16 video + a primitives doc."

---

## 4. Capability surface we're under-using

### Content endpoints (`/api/content/*`)
image · video (6 modes: prompt/animate/reference/extend/first-last/lipsync) · caption · transcribe
· edit (trim/crop/overlay/mux) · upscale · analyze (the agent's eyes) · templates (list+detail) ·
create (async pipeline + cost estimate)

### Artist context to fuse in (`recoup-api`)
catalog/songs/lyrics/audio-LM · posts/**comments**/**fans** · research (audience demographics,
**listener cities**, **milestones**, charts, per-platform metrics, similar artists) · per-song
TikTok velocity (`recoup-tiktok-per-song`) · connectors (publish to TikTok/IG, Drive, email)

**The gap:** every content skill today takes `artist_account_id` + `template` and stops. None read
posts for voice, demographics for targeting, or TikTok velocity for song choice. That's the opening.

---

## 5. 2026 research findings (what to actually build for)

- **Volume is the game:** consensus is **15–30 assets per song**, batch-created as "clip families."
  → a **content-pack / batch** skill matters more than one-off generation.
- **Hook-first:** 5–15s clips, hook in first 1–3s; 7s loops for catchy hooks. → **hook-finder**.
- **Discovery moved to short-form:** ~47% discover before Spotify; ~84% of 2024 Billboard Global
  200 went viral on TikTok first.
- **Never cross-post identical files:** IG penalizes >70% reused audio/visual + watermarked
  re-uploads. → **per-platform reformat** is a real, distinct job (not copy-paste).
- **BTS/raw is artist-shot, not generated.** Our role there = caption/crop/hook *their* footage →
  belongs in a reformat/polish skill, not a generation skill.
- **Format families that recur:** hook clips · performance · "scene/narrative" (text hook over
  cinematic b-roll + song) · lyric videos · visualizers/Canvas loops · carousels/photo dumps ·
  quote cards/lyric breakdowns · BTS · announcements.

---

## 6. Burner accounts — findings + our defensible slice

**What they are (Billboard, Synnistry, 2026):** networks of faceless, themed accounts (coffee
edits, quote dumps, country memes, fan pages) that drop a song in the background to **simulate**
an organic trend. Warner's Will Morrow coined "burner pages" (~2023). Agencies — **Chaotic Good**
("trend simulation"), **Floodify** — run hundreds-to-thousands of pages, 5,000–15,000 videos/day.
There's a ban-evasion infra layer (LTE proxies, anti-detect browsers, account warming) and a real
ethical/ToS line (soft chart manipulation, fake authenticity).

**The valuable, defensible insight:** the *bespoke* version targets by audience — *"an R&B ballad
works on the coffee-cup page, not the truck page."* That targeting needs audience demographics —
**which we have and competitors don't.**

**What we build (creative half):**
- ✅ High-volume, **themed, audience-matched content packs** — one song rendered as
  coffee-aesthetic / quote-dump / POV-scene / etc., matched to where the song's audience actually
  is (`recoup-content-pack` + `recoup-audience-tuned-content`).
- ✅ Power the legitimate pages an artist/marketer already runs.

**What we do NOT build (the boundary — note it in the skill body):**
- ❌ Mass fake-account creation, proxy/anti-detect ban-evasion, 10k-posts/day automation. ToS-
  violating, ban-risky for our users, bad look. We supply the *creative volume + targeting*, not
  the account farm.

---

## 7. Proposed structure (job-grained, per the §2 rule)

```
plugins/content/   (prefixed recoup-content-*; API/context-aware)
│
├── recoup-content                  ← NEW router (entry point; disambiguates + dispatches)
│
├── OUTPUT SKILLS (one per JOB; looks via TEMPLATES; cosmetic variants via params)
│   ├── recoup-short-video          hook / performance / scene-narrative (looks = templates)
│   │                               (today's short-video; keep portable copy standalone)
│   ├── recoup-lyric-video          transcribe-driven timed text
│   ├── recoup-cover-art            square DSP/release art (brand-defining, no clickbait)
│   ├── recoup-thumbnail            YouTube/video CTR art (face + hook text) — DIFFERENT job
│   ├── recoup-quote-cards          lyric → shareable cards
│   ├── recoup-promo-graphic        release / tour / pre-save graphic (+ countdown variants)
│   ├── recoup-carousel             IG multi-image / photo dump (distinct output: N images)
│   ├── recoup-visualizer           audio-reactive loop + Spotify Canvas 8s
│   └── recoup-content-reformat     one master → per-platform cuts; also caption/crop the
│                                   artist's OWN BTS footage (edit pipeline)
│
├── CONTEXT-FUSED SKILLS (the moat — content × artist data)
│   ├── recoup-brand-voice-caption  captions that sound like THIS artist (from post history) ⭐
│   ├── recoup-audience-tuned-content style/lang/format from demographics + cities ⭐
│   ├── recoup-song-hook            find the 15s hook via Music Flamingo (lives in
│   │                               recoup-song-analysis — it's audio analysis, not content) ⭐
│   ├── recoup-trend-jack           fastest-rising TikTok track → auto edits (wires
│   │                               tiktok-per-song → content) ⭐
│   └── recoup-content-pack         15–30 assets/song; themed + audience-matched volume
│                                   (the defensible burner-aware play) ⭐
│
└── BUILDING BLOCKS stay in standalone `content-creation` (primitives) — do NOT shatter
```

`recoup-content` = router · output skills = finished artifacts (carved by job) · context-fused =
the moat · `content-creation` = primitives (portable npx layer) · `short-video` stays standalone
as the portable short-form skill (plugin references shared patterns via vendored refs).

**Publishing is OUT of this plugin** — posting to TikTok/IG via connectors will be a **separate
plugin**. This plugin stops at "finished asset + caption."

**Frequency tiering (build the high-freq first):**
- Tier 1 (every release, do first): short-video (exists), cover-art, brand-voice-caption,
  hook-finder, content-pack.
- Tier 2: quote-cards, announcement, lyric-video, audience-tuned-content, trend-jack.
- Tier 3: carousel, visualizer, content-reformat, thumbnail.

---

## 8. Cross-cutting concerns (every content skill respects)

0. **Artist-workspace-native (the deepest context fusion).** Read context from the workspace
   first; the API is the fallback (mirrors `recoup-api`'s "filesystem is authoritative" rule):
   - `context/artist.md` → brand voice + aesthetic (captions, image style) — *the source of truth*
   - `context/audience.md` → who fans are + how they talk (audience-tuned, brand-voice-caption)
   - `context/images/face-guide.png` → reference image for image/video gen (`$REFERENCE_IMAGE_URL`)
   - `releases/{slug}/RELEASE.md` → release context (announcements, packs)
   - `songs/{slug}/*.mp3` → audio (already in `song-sourcing.md`)
   - **Write outputs BACK** into the workspace (e.g. `artists/{slug}/content/…` or the release
     folder) and commit `{what}: {why}`. Fallback to `GET artist posts/socials` only when no
     workspace context exists. → vendored `workspace-context.md`.
1. **Async or die.** `POST /video` & `/create` take 60–180s; agent shells cap ~30–60s. Use
   create→poll `/tasks/runs`. → vendored `async-pipeline.md`.
2. **`account_id` ≠ `id`** (the 404 footgun). → vendored `account-resolver.md`.
3. **Don't fake the song.** `short-video/references/song-sourcing.md` already nails it (sandbox →
   YouTube ask → user). Promote to canonical, vendor into audio skills.
4. **`analyze` before "done."** Agent can't see pixels — run analyze, don't claim success on a
   glitchy/empty render. (Pair with the README's planned `Stop` hook for non-zero `.mp4`.)
5. **Credit awareness.** `recoup-content-pack` (12-track × 20 assets) must cost-estimate +
   confirm before fanning out, like `recoup-tiktok-per-song` warns before 100 calls.
6. **Likeness limits.** Veo 422s on celebrity likeness; templates carry refs to avoid it.

---

## 9. Build approach (exemplar-first, then replicate — NOT a 15-file dump)

Don't mass-generate every skill at once (unreviewable; violates KISS/YAGNI). Establish the pattern
on one, review, replicate.

**Step 1 — pattern (do now):**
1. `recoup-content` router.
2. `recoup-brand-voice-caption` ⭐ as the exemplar (clearest "content × context" proof).
3. Vendored shared refs: `async-pipeline.md`, `account-resolver.md`, `song-sourcing.md`
   (promote from short-video), `analyze-gate.md`, `credit-estimate.md`.

**Step 2 — replicate Tier 1:** cover-art, hook-finder, content-pack (+ short-video already exists).

**Step 3 — Tier 2 → Tier 3** per §7 tiering.

Each new skill: three plugin manifests untouched (skills auto-discovered), update both marketplace
catalogs only if versioning, bump plugin `version`, run the 3 validation gates, update README +
AGENTS tables.

Rationale: generic format skills are commodity; the context-fused five are why someone picks
Recoup over a raw image API. Prove the moat first.

---

## 10. Decisions (resolved) + remaining questions

**Resolved:**
- ✅ **Grain = one JOB, not one API call** (§2; songs precedent).
- ✅ **Scope = full** (Tiers 1–3 over time), built **exemplar-first** (§9).
- ✅ **Publishing = separate plugin** (this plugin stops at asset + caption).
- ✅ **Graphics split by job** (cover/quote/announce/carousel separate; thumbnail = mode of cover).
- ✅ **Placement:** new skills in `plugins/content/` (prefixed); `short-video` + `content-creation`
  stay standalone as the portable layer.
- ✅ **Burner boundary:** ship themed + audience-matched volume packs; NO account-farming/ban-evasion.

**Resolved (this round):**
- ✅ **Brand-voice source = `context/artist.md`** (+ `context/audience.md`) from the artist
  workspace — the maintained source of truth. `GET artist posts/socials` is the fallback.
- ✅ **Content plugin is artist-workspace-native** (§8.0): read `context/`, `face-guide.png`,
  `releases/`, `songs/`; write outputs back + commit `{what}: {why}`.
- ✅ **Thumbnail = its own skill** (≠ cover art): YouTube/video CTR art vs square DSP release art.

**Built (FULL taxonomy shipped — 13 skills, v0.5.0):**
- ✅ Router `recoup-content` + Video (`recoup-short-video` w/ template looks studio/stage/
  bedroom/album-record-store, `recoup-lyric-video`, `recoup-visualizer`/Canvas) + Graphics
  (`recoup-cover-art`, `recoup-thumbnail`, `recoup-quote-cards`, `recoup-promo-graphic`,
  `recoup-carousel`) + Text (`recoup-brand-voice-caption`) + Workflow (`recoup-content-pack`,
  `recoup-content-reformat`).
- ✅ v0.6.0: moved hook-finding OUT of content → `recoup-song-hook` in `recoup-song-analysis`
  (v0.2.0), Flamingo-powered (sync_brief_match + music_theory + lyric_transcription), not
  `/content/transcribe`. It's audio analysis; content skills consume the timestamps.
- ✅ Canonical refs: `content-api.md`, `account-resolver.md`, `workspace-context.md` (3 modes
  incl. generic/no-context), `song-sourcing.md`, `analyze-gate.md` — vendored (131 copies).
- ✅ studio/stage/bedroom = TEMPLATE looks (one video skill); album art / Canvas / lyric video
  / thumbnail = distinct jobs; every skill runs context / API-fallback / generic mode.
- ✅ 3 gates pass (portability 48, vendored 131/31, manifests parity). README/PROGRESS updated.
- Next: `recoup-audience-tuned-content`, `recoup-trend-jack`; publishing as a separate plugin.

**Built (Step 1 — exemplar pattern, shipped earlier):**
- ✅ `plugins/recoup-content/skills/recoup-content/` — router.
- ✅ `plugins/recoup-content/skills/recoup-brand-voice-caption/` — exemplar (workspace-native:
  reads `context/artist.md`/`audience.md`, falls back to `GET /api/artists/{id}/posts`,
  writes back to `content/captions/`).
- ✅ Canonical shared refs `plugins/recoup-content/references/{workspace-context,account-resolver}.md`
  vendored into the exemplar; registered in `scripts/vendored.json`.
- ✅ Plugin bumped 0.3.0 → 0.4.0 (3 manifests + both catalogs); README updated; 3 gates pass.
- Note: deferred `async-pipeline.md` / `song-sourcing.md` / `analyze-gate.md` / `credit-estimate.md`
  to build JIT with the skills that consume them (YAGNI) rather than as orphan canonicals.

**Next (Step 2 — replicate Tier 1):** `recoup-cover-art`,
`recoup-content-pack` off this same pattern.
```

---

# Songstats data-utilization audit (2026-06-07)

**Question:** are we limiting our possibilities out of naivety vs what Songstats offers?
**Verdict:** yes — we surface ~⅓ of the Songstats surface, and several gaps are
self-inflicted (we removed cities/charts/venues/festivals/radio and replaced them
with weaker `web`/`deep` fallbacks that Songstats serves natively + cheaper).

Sources: https://docs.songstats.com/ · SDK https://github.com/Songstats/songstats-python-sdk
· https://lab.songstats.com/songstats-enterprise-api-update-april-2025-1d205cd16ade

## Songstats surface (from their SDK)
- Entities **artists / collaborators / labels**, each: `info`, `stats`,
  **`historic_stats`** (daily time-series), `audience`, **`audience/details`**
  (per-country), `catalog`, `activities`, `top_tracks`, `top_playlists`,
  **`top_curators`**, **`top_commentors`**, `songshare`.
- **tracks**: `info`, `stats`, `historic_stats`, `activities`, **`comments`**,
  **`locations`** (geo), `songshare`.
- **`artists/events`** (touring: venue/city/lat-lng, past+upcoming), **Radiostats**
  (40k+ stations + SiriusXM), DJ/electronic (1001Tracklists/Beatport/Traxsource),
  distributor info, songwriter/producer credits, `sources`/`definitions`. 18 platforms.

## Our `/api/research/*` (from OpenAPI) — 20 endpoints
search, lookup, profile, metrics, audience, similar, playlists, tracks, albums,
track, track/playlists, career/insights/milestones (1 feed, 3 views), urls,
+ our web layer (web/deep/enrich/extract/people).

## Gap table (prioritized)
| # | Songstats has | We expose | Impact |
|---|---|---|---|
| 1 | `historic_stats` time-series (all entities) | `metrics` = current snapshot only | 🔴 no native trend/growth/momentum |
| 2 | Labels (info/stats/historic/catalog/audience) | `search?type=labels` only | 🔴 "Label Profiles" pitched by Songstats; deals/catalog relevance |
| 3 | Collaborators entity + track credits | none | 🔴 songwriter/producer/publishing → recoup-deals |
| 4 | `artists/events` touring | removed venues/festivals → web fallback | 🟠 native structured touring exists |
| 5 | `tracks/locations` + `audience/details?country_code` | removed cities; audience=overall only | 🟠 geo sent to web/deep needlessly |
| 6 | `top_curators` / `top_commentors` | `playlists` only | 🟠 "who's championing this artist" lost |
| 7 | DJ/electronic + Radiostats spins + `comments` | none | 🟡 whole verticals dropped |

## Smoking gun — `/metrics?source=` enum is stale Chartmetric-era + mismatched
Verified live (artist=Drake, 3-retry):
- **Return data (10):** spotify, instagram, tiktok, twitter, facebook,
  youtube_channel, youtube_artist, soundcloud, deezer, bandsintown
- **Accepted but empty (6):** twitch, line, melon, wikipedia (inert — not Songstats
  sources), radio, sxm (only radio-active artists)
- **Songstats provides but our /metrics REJECTS (`status:error`, 9):** apple_music,
  amazon, shazam, itunes, tidal, beatport, traxsource, 1001tracklists, songkick —
  yet apple_music/shazam/itunes already appear in our `career`/`milestones` feed.
  → data arrives; metrics endpoint won't serve it.

## Where fixes live (2 layers)
- **api submodule (most value):** expose historic_stats, label detail,
  collaborators/credits, events, locations, audience/details, top_curators;
  fix metrics source enum (drop twitch/line/melon/wikipedia; add apple_music/
  amazon/shazam/tidal/beatport/traxsource/itunes).
- **skills (now, safe):** document verified source behavior + provider-gap note
  so agents stop wasting calls on inert sources and stop routing geo/touring to web.

## Done in skills repo (2026-06-07)
- ✅ Corrected "Platform sources" in recoup-research/references/endpoints.md
  (canonical) → re-synced vendored copies; mirrored into music-industry-research.
- ✅ recoup-content "make it better" (do it all), v0.8.0 — all 3 gates green:
  - P0 `references/research-context.md` backbone (signals between context & generation),
    vendored into 11 skills + recoup-trend-jack.
  - P1 audio→edit mapping (content-api template auto-select; BPM/energy/valence → cuts/look/tone).
  - P2/P5 new `recoup-trend-jack` skill (react to real milestone/trend, route to format skill).
  - P3 analyze-gate benchmarks vs the artist's real top posts.
  - P4 hooks/ (SessionStart env advice + Stop analyze-gate enforcement).
  - router backbone → 6 steps; README + manifests + marketplaces updated.

