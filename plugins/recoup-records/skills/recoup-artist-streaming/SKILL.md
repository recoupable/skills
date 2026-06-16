---
name: recoup-artist-streaming
description: Checks an artist's streaming health — flags Spotify/DSP stream spikes or drops by diffing current metrics against the last check. Use when asked to "check streaming", "are streams spiking or dropping", "streaming health check", or "did streams jump this week". Identifies which playlist or release likely drove a move; refuses to fabricate numbers. For TikTok momentum use recoup-artist-tiktok; to confirm a release went live use recoup-release-monitor. Needs the artist name.
---

# Streaming Check

A focused streaming-health read: pull the current snapshot, **diff it against the
last check**, and flag meaningful spikes or drops — then point at the likely
cause (a new editorial add, a release, a chart entry).

Narrower than `recoup-artist-brief` (which is a full multi-metric Monday
artifact) — this is the "are streams moving?" spot-check. For first-time deep
research use `recoup-artist-research`.

The endpoint contract (auth, base URL, params, response shapes, credit costs) is
in `references/endpoints.md` and `references/response-shapes.md`. Read them before
calling. They ship alongside this skill.

## Setup

```bash
export RECOUP_API_KEY="recoup_sk_..."        # already set in Recoup sandboxes
export RECOUP_API="https://api.recoupable.com/api"
```

## Workflow

### 1. Read the prior check (the baseline for the diff)

```bash
ls -t artists/{slug}/research/streaming-check-*.md 2>/dev/null | head -1
```

If one exists, extract its numbers (monthly listeners, popularity, playlist
reach). Metrics are **current snapshots**, not time series — the delta comes from
diffing today's reading against your own last file, not a provider backfill.

### 2. Pull the current snapshot + likely causes (parallel, low-credit)

```bash
# Spotify snapshot — listeners, popularity, editorial playlist count, reach
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY" &
# Current playlist placements — an editorial add is the usual spike driver
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&platform=spotify&status=current" -H "x-api-key: $RECOUP_API_KEY" &
# Activity feed — releases / chart entries that could explain a move
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &
wait
```

A `metrics` call may return `202 { status: "pending", state: "refresh_pending" }`
while the provider refreshes — retry that one call shortly.

### 3. Compute deltas + classify

For each numeric metric compute `(current − baseline)` and `% change`. Classify:

- **Spike** — listeners or playlist reach up materially (e.g. ≥15% or a large
  absolute jump). Look for a new editorial add or a release in the feed to
  explain it.
- **Drop** — a material decrease (playlist removal, post-release cooldown).
- **Flat / first reading** — say so plainly; don't manufacture a narrative.

## Output

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

Save to `artists/{slug}/research/streaming-check-$(date +%F).md` when a workspace
exists (or `releases/{slug}/tracking/` during a release). Otherwise return in chat.
Same-day re-run is a no-op — surface the existing file.

## Guardrails

- **No invented numbers.** Missing metric → `—`. Never substitute a guess.
- **No causation claims without evidence.** Only name a driver that actually
  appears in `playlists`/`milestones` this run; otherwise say "no obvious driver."
- **Snapshots, not history.** The delta is vs your last file, not a backfill.

## References

- `references/endpoints.md` — full curl examples per endpoint, params, credits.
- `references/response-shapes.md` — actual JSON shapes per endpoint.
