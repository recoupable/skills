---
name: recoup-artist-brief
description: A RECURRING, DATED weekly artist brief that diffs against the last brief and writes a markdown file the customer opens every week. Use when asked for a "weekly brief", "what's new with [artist] this week", "[artist] weekly update", "how is [artist] doing this week", or to schedule a recurring check-in. Reads workspace context, fetches Spotify + TikTok + Instagram metrics + milestones in parallel, and diffs vs the previous brief; re-running the same day is a no-op. For a one-time overview (not recurring) use recoup-artist-research instead.
---

# Weekly Brief

The recurring artifact a customer opens every Monday. Reads workspace context,
fans 5 endpoints in parallel, **surfaces what changed since the last brief**, and
writes a dated markdown file.

This skill exists because one-shot artist research dumps don't get re-opened.
Dated, diffed briefs do.

The API is backed by **Songstats**; metrics are **current snapshots**, not time
series. The delta comes from diffing today's snapshot against the prior brief
you wrote — not from a historical backfill.

## When to use

- "Weekly brief for {artist}" / "What's new with {artist}"
- "Brief {artist}" / "{artist} update"
- "How is {artist} doing this week" / "Weekly update on {artist}"
- Any scheduled recurring artist check-in

For one-time deep research without the delta framing, use
`recoup-artist-research` instead.

## Setup

```bash
export RECOUP_API_KEY="recoup_sk_..."   # already set in Recoup sandboxes
export RECOUP_API="https://api.recoupable.com/api"
```

## Workflow

### 1. Resolve workspace + idempotency check

Find the artist's workspace folder:

```bash
artists/{slug}/RECOUP.md          # preferred — canonical
artists/{slug}/context/artist.md  # legacy fallback
```

If today's brief already exists at `artists/{slug}/research/brief-$(date +%F).md`,
**stop**. Tell the user "brief already exists for today" and surface the file path.
Do not re-fetch.

If no workspace exists, ask the user whether to create one, or to run the brief
output-only (no file write).

### 2. Resolve the artist

Most endpoints take `artist={name}` directly. If you need an exact entity (e.g.
two artists share a name), resolve a provider ID first:

```bash
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.results[0]'
```

Disambiguate by `name`, `avatar`, and `site_url` (there is no `match_strength`
score anymore). If multiple plausible matches exist, surface the ambiguity to
the user rather than guessing.

### 3. Read the prior brief (for the diff)

```bash
ls -t artists/{slug}/research/brief-*.md | head -1
```

If a prior brief exists, read it and extract the key numbers (Spotify monthly
listeners, Spotify followers, TikTok followers, Spotify popularity, editorial
playlists). These become the **baseline** for the delta section.

### 4. Fan out 5 endpoints in parallel

```bash
# Spotify metrics — listeners, followers, popularity, editorial playlists, reach
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" \
  -H "x-api-key: $RECOUP_API_KEY" &

# TikTok metrics — followers, likes, video counts
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" \
  -H "x-api-key: $RECOUP_API_KEY" &

# Instagram metrics — followers, engagement
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=instagram" \
  -H "x-api-key: $RECOUP_API_KEY" &

# Activity feed — releases, chart moves, playlist adds since last brief
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" &

# AI-surfaced observations for the week
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" &

wait
```

All five run concurrently. Total wall time ≈ slowest single call. A `metrics`
call may return `202` `{ status: "pending", state: "refresh_pending" }` while
the provider refreshes — retry that one call shortly.

### 5. Compute deltas

For each numeric metric, compute `(current - baseline)` and `% change`.
For milestones, list everything dated **after** the prior brief's date. Sort
milestones by `activity_tier` ascending (lower = more significant) to lead with
the biggest events.

### 6. Write the brief

Path: `artists/{slug}/research/brief-$(date +%F).md`

Template:

```markdown
# Weekly Brief — {Artist Name}
**Week of {YYYY-MM-DD}** | **Last brief:** {prior-brief-date or "first brief"}

## TL;DR
{2–3 sentence delta summary. What moved this week. Specific numbers, not vibes.
If nothing moved, say so honestly: "Quiet week — no significant deltas."}

## What changed this week

| Metric | Last brief | This brief | Δ |
|---|---|---|---|
| Spotify monthly listeners | {prior or "—"} | {monthly_listeners_current} | {±N or "first reading"} |
| Spotify followers | {prior or "—"} | {followers_total} | {±N} |
| Spotify popularity | {prior or "—"} | {popularity_current} | {±N} |
| TikTok followers | {prior or "—"} | {current} | {±N} |
| Editorial playlists | {prior or "—"} | {playlists_editorial_current} | {±N} |

## New activity since last brief
{Bullets of milestones dated after the prior brief, biggest first. If none, "—".}

## AI insights this week
{Top 3–5 items from /research/insights, paraphrased — not raw JSON.}

## Watch next week
{1–3 things to look for next brief, derived from what's currently moving.}

---
*Generated {ISO timestamp}. Source: Recoup research API. Re-run with `/recoup-brief {slug}`.*
```

### 7. Print a 200-word chat summary

Even when writing the file, **always print a short summary in the chat**:
TL;DR + 3 most-moved metrics. The user shouldn't have to open the file to see if
anything happened.

## What this skill refuses to do

- **No data invention.** If a metric is missing from `stats[0].data`, write `—`
  in the table. Never substitute a fabricated number.
- **No silent overwrites.** Same-day re-run is a no-op, not a clobber.
- **No deltas on the first brief.** First reading shows current values with
  "first reading" in the Δ column.
- **No noise.** If literally nothing changed (rare but possible), the TL;DR says
  so. Don't pad with filler observations.

## Reading metrics correctly

`/research/metrics?source=spotify` returns a **current snapshot** under
`stats[0].data` — not a time series. Parse the counters directly:

```jsonc
// /research/metrics?artist=X&source=spotify → .stats[0].data
{
  "monthly_listeners_current": 99477872,
  "followers_total": 112185098,
  "popularity_current": 100,
  "playlists_editorial_current": 568,
  "playlist_reach_current": 993868411
}
```

There is no array to take the last element of — these are the current values.
For the delta against last brief, parse the prior brief's table (parsing your
own previous output is more stable than depending on a provider backfill).
TikTok/Instagram `data` keys differ — `jq '.stats[0].data | keys'` once per
source if unsure.

## Endpoint notes

| Endpoint | Source enum or arg |
|---|---|
| `/research/metrics?source=` | `spotify`, `tiktok`, `instagram`, `youtube_channel`, `youtube_artist`, … (16 total) |
| `/research/milestones` | activity feed; sort by `activity_tier` asc |
| `/research/insights` | AI-surfaced observations |

For `/research/metrics?source=youtube`, use `youtube_channel` or
`youtube_artist`, **not plain `youtube`**. There is no `/research/rank` endpoint
— use `popularity_current` and `playlist_reach_current` from `/metrics` as the
headline magnitude signals.

## Credit awareness

The 5 endpoints in step 4 are all low-credit (1 credit or free each).
A full brief costs ≤5 credits per run. If any call returns
`{ "error": "insufficient_credits" }`, surface the `checkoutUrl` to the user
instead of silently dropping the section.

## Graceful degradation

If `/research/metrics` returns empty `stats` for an emerging artist (very thin
provider data), don't fall back to web search — that's the
`recoup-artist-research` skill's job. For the **weekly brief**, just write the
table with `—` cells and a note: "Thin data this week — consider running
`/recoup-research {slug}` for a deeper one-shot."

## References

- `references/endpoints.md` — full curl examples
- `references/response-shapes.md` — actual JSON shapes per endpoint
- `recoup-artist-research` skill — one-shot full sweep (use that, not this, for
  first-time research)
