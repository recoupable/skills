# Skill Rename Proposal — v2 (after your notes)

> **⚠️ Superseded by v3 (`skill-rename-proposal-v3.md`).** v2 below explored
> deliverable-led freeform names; the direction we landed on is the uniform
> `recoup-[domain]-[verb]-[noun]` convention in v3. Kept here for history.

> **What changed from v1:** your notes said my abstract names ("overview",
> "insights", "monitor", "placement", "launch") didn't tell you *what you get* or
> *about whom*. v2 follows three rules pulled from your own notes:
>
> 1. **Name the tool / deliverable** (you liked `graphic-designer`,
>    `short-video-generator`, `songwriting-helper`, `release-planner`).
> 2. **Name the subject** (whose songs, whose brand, pack of what).
> 3. **No jargon** (no "placement", "launch", "monitor", "intelligence").
>
> **How to respond now — just talk to me in chat.** Say "apply" if v2 looks good,
> or name any you still don't like. No table-editing needed.

Legend: ★ = your suggested name · ✅ = you already approved in v1 · 🔀 = a
merge/fold decision I need from you.

---

## Foundation / setup

| Current | v2 name | What you get | Note |
|---|---|---|---|
| `recoup-setup` | `recoup-connect-account` | connect your real account (email/PIN, key) | you said "login"; connect = first-run. Or `recoup-login` |
| `recoup-setup-sandbox` | `recoup-build-workspace` ✅ | scaffold your **whole account's** folders | (vs artist-workspace = one artist — now folded, see below) |
| `recoup-api` | `recoup-api` | raw platform/connector access (dev utility) | keep |
| `recoup-artist-create` | `recoup-create-artist` ★ | add a new artist **and** set up their folder | 🔀 folds in `artist-workspace` |
| `recoup-artist-workspace` | → **folded into `recoup-create-artist`** | — | 🔀 you asked "can this be folded?" — yes (rec) |

## Artist research & insight

| Current | v2 name | What you get | Note |
|---|---|---|---|
| `recoup-artist-research` | `recoup-research-an-artist` | a full research report on one artist | "what do I get" → a research report |
| `recoup-artist-audience` | `recoup-fanbase-report` | who/where the fans are + where to grow | "what do I get" → a fanbase report |
| `recoup-artist-competition` | `recoup-competitive-analysis` ✅ | how they stack up, collabs, release timing | approved |
| `recoup-artist-scout` | `recoup-discover-artists` ✅ | find emerging/unsigned talent | approved |
| `recoup-artist-playlists` | `recoup-playlist-targets` | which playlists to chase + gaps | "what do I get" → target playlists |
| `recoup-artist-outreach` | `recoup-find-contacts` | managers/A&R/press + drafted outreach | you said "just find?" → shorter |
| `recoup-artist-tiktok` | `recoup-artist-tiktok-songs` | which of **this artist's** songs pop on TikTok | "whose?" → keeps "artist" |
| `recoup-web-intelligence` | `recoup-research-anything` | research any topic OR look up any company/person/label | "artists?" → no, deliberately general |

## Tracking over time

| Current | v2 name | What you get | Note |
|---|---|---|---|
| `recoup-artist-brief` | `recoup-weekly-artist-update` | a weekly "what changed" update (+ streaming spikes) | "monitor what?" → a weekly update |
| `recoup-release-monitor` | `recoup-release-day-tracker` | confirms the release dropped + alerts you | killed "launch" jargon |

## Song (needs the audio) + songwriting

| Current | v2 name | What you get | Note |
|---|---|---|---|
| `recoup-song-analyze` | `recoup-analyze-song` ✅ | BPM/key/genre/mood, lyrics, mix critique | approved |
| `recoup-song-hook` | `recoup-find-song-hook` | the best 5–15s of a song to clip | "hook of what?" → a song |
| `recoup-song-pitch-kit` | `recoup-pitch-this-song` | a playlist pitch + sync brief | killed "placement" jargon |
| `recoup-songwriting` | `recoup-songwriting-helper` ★ | write/evaluate lyrics & concepts | your suggestion |

## Content

| Current | v2 name | What you get | Note |
|---|---|---|---|
| `recoup-content` | `recoup-create-content` ★ | front door — figures out what to make | stays the router (not a blob) |
| `recoup-content-caption` | `recoup-artist-voice-caption` | a caption that sounds like the artist | "whose brand?" → the artist's |
| `recoup-content-image` | `recoup-graphic-designer` ★ | cover art / thumbnail / carousel / promo / quote | your suggestion |
| `recoup-content-video` | `recoup-short-video-generator` ★ | finished 9:16 TikTok/Reel | your suggestion |
| `recoup-content-lyric-video` | `recoup-lyric-video-maker` | the song's words animated to the audio | 🔀 keep, or merge w/ visualizer? |
| `recoup-content-visualizer` | `recoup-visualizer-maker` | no-text looping background (Spotify Canvas) | 🔀 keep, or merge w/ lyric-video? |
| `recoup-content-pack` | `recoup-song-content-pack` | 15–30 posts/clips for **one song** | "pack of what?" → a song's content |
| `recoup-content-reformat` | `recoup-reformat-video` ✅ | per-platform cuts / polish your footage | approved |
| `recoup-content-trend` | `recoup-make-timely-content` | turn a real milestone/trend into a post | "no idea what this is" → timely content |

## Deals *(all approved in v1 — kept)*

| Current | v2 name | What you get |
|---|---|---|
| `recoup-deal-start` | `recoup-full-deal-review` ✅ | one-command end-to-end catalog review |
| `recoup-deal-ingest` | `recoup-catalog-data-cleanup` ✅ | normalize a messy data room |
| `recoup-deal-value` | `recoup-deal-valuation` ✅ | value the catalog (with seller files) |
| `recoup-catalog-value` | `recoup-catalog-estimate` ✅ | value from public data only (no files) |
| `recoup-deal-dashboard` | `recoup-deal-dashboard` ✅ | the executive DASHBOARD.html |
| `recoup-deal-report` | `recoup-deal-report` ✅ | IC memo / financing pack → PDF |
| `recoup-deal-demo` | `recoup-deal-demo` ✅ | sample deal in ~60s |

## Releases

| Current | v2 name | What you get | Note |
|---|---|---|---|
| `recoup-release-start` | `recoup-release-planner` ★ | one-command end-to-end release | your suggestion |
| `recoup-release-brief` | `recoup-release-creative-brief` | pre-release concepts/angles/targets | the creative starting point |
| `recoup-release-campaign` | `recoup-release-calendar` | the dated rollout schedule | concrete: a calendar |
| `recoup-release-doc` | `recoup-release-master-doc` | the source-of-truth doc + DSP pitch/one-sheet | the master document |
| `recoup-release-demo` | `recoup-demo-release` ★ | sample release flow | 🔀 your reorder (or keep `*-demo` to match deal-demo) |

## Cross-cutting

| Current | v2 name | What you get | Note |
|---|---|---|---|
| `recoup-learn` | `recoup-remember-this` ✅ | save a lesson so the next run is cheaper | approved |

---

## Decisions I need (the 🔀 rows)

1. **Fold `artist-workspace` into `create-artist`?** (rec: yes — removes a skill)
2. **lyric-video + visualizer:** keep as two clear skills (rec) **or** merge into one
   `recoup-motion-video` with two modes (lyric / no-text loop)?
3. **demo naming:** `recoup-demo-release` + `recoup-demo-deal` (your reorder, consistent)
   **or** keep `recoup-release-demo` + `recoup-deal-demo`?

## Count

41 skills → **40** if we fold `artist-workspace`. Tell me "apply" (with your calls
on 1–3) and I'll `git mv` everything, update `RESOLVER.md`, `resolver-eval.jsonl`,
all cross-references and the agents, then re-run the gates.
