---
name: recoup-artist-brief
description: A RECURRING, DATED artist monitor that diffs against the last run and writes a markdown file the customer opens. Two scopes — FULL weekly brief (Spotify+TikTok+Instagram+milestones+insights) or a STREAMING spot-check (are streams spiking/dropping right now). Use for "weekly brief", "what's new with [artist] this week", "[artist] weekly update", "how is [artist] doing", "check streaming", "are streams spiking or dropping", "streaming health check", or "did streams jump this week". Reads workspace context, fetches metrics in parallel, diffs vs the previous run; re-running the same day is a no-op. For a one-time overview (not recurring) use recoup-artist-research; for per-song TikTok momentum use recoup-artist-tiktok; to confirm a release went live use recoup-release-monitor.
---

# Artist Monitor (Weekly Brief + Streaming Check)

The recurring artifact a customer opens to see **what changed**. One monitor, two
scopes — they share the same spine (read prior run → snapshot today → diff →
write a dated file), and differ only in **how much they pull and what artifact
they write**:

| Scope | Trigger | Pulls | Writes |
|---|---|---|---|
| **full** (default) | "weekly brief", "what's new", "[artist] update" | Spotify + TikTok + Instagram metrics + milestones + insights (5 endpoints) | `research/brief-{date}.md` |
| **streaming** | "check streaming", "are streams spiking/dropping" | Spotify metrics + playlists + milestones (cause only) | `research/streaming-check-{date}.md` |

Pick **streaming** when the user asks specifically about streams moving; pick
**full** for the comprehensive weekly. This skill exists because one-shot research
dumps don't get re-opened — dated, diffed artifacts do. For a one-time deep sweep
(no delta framing) use `recoup-artist-research`.

The API is backed by **Songstats**; metrics are **current snapshots**, not time
series. The delta comes from diffing today's snapshot against the prior file you
wrote — not a historical backfill.

## Setup

```bash
export RECOUP_API_KEY="recoup_sk_..."   # already set in Recoup sandboxes
export RECOUP_API="https://api.recoupable.com/api"
```

## Workflow

### 1. Resolve workspace + idempotency check

Find the artist's workspace:

```bash
artists/{slug}/RECOUP.md          # preferred — canonical
artists/{slug}/context/artist.md  # legacy fallback
```

Idempotency is **per scope**. If today's artifact for this scope already exists
(`research/brief-$(date +%F).md` for full, `research/streaming-check-$(date +%F).md`
for streaming), **stop** and surface the path — don't re-fetch. No workspace →
ask whether to create one or run output-only.

### 2. Resolve the artist

Most endpoints take `artist={name}`. To disambiguate a shared name, resolve first:

```bash
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.results[0]'
```

Disambiguate by `name`, `avatar`, `site_url` (there is no `match_strength`). If
multiple plausible matches exist, surface the ambiguity rather than guessing.

### 3. Read the prior run (the baseline for the diff)

```bash
# full:
ls -t artists/{slug}/research/brief-*.md | head -1
# streaming:
ls -t artists/{slug}/research/streaming-check-*.md | head -1
```

Extract the prior numbers (full: Spotify monthly listeners, followers, popularity,
TikTok followers, editorial playlists; streaming: monthly listeners, popularity,
playlist reach, editorial playlists). These are the **baseline**.

### 4. Fan out endpoints in parallel (scope-dependent)

**full scope — 5 endpoints:**

```bash
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify"   -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok"    -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=instagram" -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}"               -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/insights?artist={ARTIST}"                 -H "x-api-key: $RECOUP_API_KEY" &
wait
```

**streaming scope — Spotify snapshot + likely-cause feeds (lower credit):**

```bash
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify"                 -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&platform=spotify&status=current" -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}"                             -H "x-api-key: $RECOUP_API_KEY" &
wait
```

A `metrics` call may return `202 { status: "pending", state: "refresh_pending" }`
while the provider refreshes — retry that one call shortly.

### 5. Compute deltas + (streaming) classify

For each numeric metric compute `(current − baseline)` and `% change`. For
milestones, list everything dated **after** the prior run, sorted by
`activity_tier` ascending (lower = more significant) to lead with the biggest.

**streaming scope also classifies the headline move:**

- **Spike** — listeners or playlist reach up materially (≥15% or a large absolute
  jump). Look for a new editorial add or a release in the feed to explain it.
- **Drop** — a material decrease (playlist removal, post-release cooldown).
- **Flat / first reading** — say so plainly; don't manufacture a narrative.

### 6. Write the artifact (template per scope)

**full →** `artists/{slug}/research/brief-$(date +%F).md`

```markdown
# Weekly Brief — {Artist Name}
**Week of {YYYY-MM-DD}** | **Last brief:** {prior date or "first brief"}

## TL;DR
{2–3 sentence delta summary. Specific numbers, not vibes. If nothing moved:
"Quiet week — no significant deltas."}

## What changed this week
| Metric | Last brief | This brief | Δ |
|---|---|---|---|
| Spotify monthly listeners | {prior or "—"} | {monthly_listeners_current} | {±N or "first reading"} |
| Spotify followers | {prior or "—"} | {followers_total} | {±N} |
| Spotify popularity | {prior or "—"} | {popularity_current} | {±N} |
| TikTok followers | {prior or "—"} | {current} | {±N} |
| Editorial playlists | {prior or "—"} | {playlists_editorial_current} | {±N} |

## New activity since last brief
{Milestones dated after the prior brief, biggest first. If none, "—".}

## AI insights this week
{Top 3–5 items from /research/insights, paraphrased — not raw JSON.}

## Watch next week
{1–3 things to look for next brief.}

---
*Generated {ISO timestamp}. Source: Recoup research API.*
```

**streaming →** `artists/{slug}/research/streaming-check-$(date +%F).md` (or
`releases/{slug}/tracking/` during a release)

```markdown
# Streaming Check — {Artist}
**{YYYY-MM-DD}** | Last check: {prior date or "first reading"}

## Verdict
{SPIKE / DROP / FLAT — one line with the headline number and % move.}

## Numbers
| Metric | Last | Now | Δ |
|---|---|---|---|
| Spotify monthly listeners | {prior or "—"} | {monthly_listeners_current} | {±N% or "first reading"} |
| Spotify popularity | {prior or "—"} | {popularity_current} | {±N} |
| Playlist reach | {prior or "—"} | {playlist_reach_current} | {±N} |
| Editorial playlists | {prior or "—"} | {playlists_editorial_current} | {±N} |

## Likely cause
{The new editorial add / release / chart entry from this run that explains the
move — or "no obvious driver in the feed."}

## Next
{1–2 actions, e.g. "ride the spike with paid", "investigate the playlist drop."}
```

### 7. Print a short chat summary

Always print a short summary in chat even when writing the file (full: TL;DR + 3
most-moved metrics; streaming: the Verdict line + headline number). The user
shouldn't have to open the file to see if anything happened.

## What this skill refuses to do

- **No data invention.** Missing metric → `—`. Never substitute a fabricated number.
- **No causation without evidence.** Only name a driver that actually appears in
  `playlists`/`milestones` this run; otherwise "no obvious driver."
- **No silent overwrites.** Same-day, same-scope re-run is a no-op, not a clobber.
- **No deltas on the first run.** First reading shows current values with "first
  reading" in the Δ column.
- **No noise.** If nothing changed, say so; don't pad with filler.

## Reading metrics correctly

`/research/metrics?source=spotify` returns a **current snapshot** under
`stats[0].data` — not a time series:

```jsonc
// .stats[0].data
{
  "monthly_listeners_current": 99477872,
  "followers_total": 112185098,
  "popularity_current": 100,
  "playlists_editorial_current": 568,
  "playlist_reach_current": 993868411
}
```

There is no array to take the last element of. For the delta, parse the prior
artifact's table (parsing your own previous output is more stable than a provider
backfill). TikTok/Instagram `data` keys differ — `jq '.stats[0].data | keys'` once
per source if unsure.

## Endpoint notes

| Endpoint | Source enum or arg |
|---|---|
| `/research/metrics?source=` | `spotify`, `tiktok`, `instagram`, `youtube_channel`, `youtube_artist`, … (16 total) |
| `/research/playlists?platform=spotify&status=current` | current placements (streaming-scope cause) |
| `/research/milestones` | activity feed; sort by `activity_tier` asc |
| `/research/insights` | AI-surfaced observations (full scope) |

For YouTube use `youtube_channel`/`youtube_artist`, not plain `youtube`. There is
no `/research/rank` — use `popularity_current` and `playlist_reach_current` as the
headline magnitude signals.

## Credit awareness

Full scope's 5 endpoints are low-credit (≤5 credits/run); streaming scope is
cheaper (3 low-credit calls). If any call returns
`{ "error": "insufficient_credits" }`, surface the `checkoutUrl` rather than
silently dropping a section.

## Graceful degradation

If `/research/metrics` returns empty `stats` for an emerging artist, don't fall
back to web search — that's `recoup-artist-research`'s job. Write the table with
`—` cells and note: "Thin data — consider `recoup-artist-research` for a deeper
one-shot."

## References

- `references/endpoints.md` — full curl examples
- `references/response-shapes.md` — actual JSON shapes per endpoint
- `recoup-artist-research` — one-shot full sweep (use that for first-time research)
