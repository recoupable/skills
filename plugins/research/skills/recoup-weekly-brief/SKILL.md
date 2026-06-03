---
name: recoup-weekly-brief
description: Generates a dated, delta-focused weekly brief for an artist by reading the workspace context file, fetching streaming + TikTok + rank + milestones + insights from the Recoup research API in parallel, and diffing against the previous brief. Use when asked for a "weekly brief", "what's new with [artist]", "brief [artist]", "[artist] update", "how is [artist] doing this week", "weekly update on [artist]", or when scheduling a recurring artist check-in. Outputs a markdown file under `artists/{slug}/research/brief-YYYY-MM-DD.md` so customers have a recurring artifact they actually open. Re-running on the same day is a no-op.
---

# Weekly Brief

The recurring artifact a customer opens every Monday. Reads workspace context,
fans 5 endpoints in parallel, **surfaces what changed since the last brief**, and
writes a dated markdown file.

This skill exists because one-shot artist research dumps don't get re-opened.
Dated, diffed briefs do.

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

### 2. Resolve the artist ID

Prefer `cmArtistId` from `RECOUP.md` frontmatter when present. Otherwise:

```bash
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists&beta=true" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

Use the top result if `match_strength >= 1`. Refuse to proceed on sub-1 matches
— surface the ambiguity instead.

### 3. Read the prior brief (for the diff)

```bash
ls -t artists/{slug}/research/brief-*.md | head -1
```

If a prior brief exists, read it and extract the key numbers (Spotify monthly
listeners, TikTok followers, rank, playlist count). These become the
**baseline** for the delta section.

### 4. Fan out 5 endpoints in parallel

```bash
# Spotify metrics — current followers, listeners, popularity
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" \
  -H "x-api-key: $RECOUP_API_KEY" &

# TikTok metrics — current followers, posts, views
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" \
  -H "x-api-key: $RECOUP_API_KEY" &

# Global rank (single int)
curl -s "$RECOUP_API/research/rank?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" &

# Activity feed — releases, chart moves, milestones since last brief
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" &

# AI-surfaced observations for the week
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" &

wait
```

All five run concurrently. Total wall time ≈ slowest single call (typically
1–3s), not 5× that.

### 5. Compute deltas

For each numeric metric, compute `(current - baseline)` and `% change`.
For milestones, list everything dated **after** the prior brief's date.

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
| Spotify monthly listeners | {prior or "—"} | {current} | {±N or "first reading"} |
| Spotify followers | {prior or "—"} | {current} | {±N} |
| TikTok followers | {prior or "—"} | {current} | {±N} |
| Global rank | {prior or "—"} | {current} | {±N} |
| Editorial playlists | {prior or "—"} | {current} | {±N} |

## New activity since last brief
{Bullets of milestones dated after the prior brief. If none, "—".}

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

- **No data invention.** If `cm_statistics.sp_monthly_listeners` is null, write `—` in
  the table. Never substitute a fabricated number.
- **No silent overwrites.** Same-day re-run is a no-op, not a clobber.
- **No deltas on the first brief.** First reading shows current values with
  "first reading" in the Δ column.
- **No noise.** If literally nothing changed (rare but possible), the TL;DR says
  so. Don't pad with filler observations.

## Reading metrics correctly

The `cm_statistics` object on profile is **NOT** what `/research/metrics`
returns. `/research/metrics?source=spotify` returns a time-series object whose
latest data point is the current value. Parse:

```jsonc
// /research/metrics?artist=X&source=spotify response
{
  "metrics": {
    "followers":         [{ "timestp": "...", "value": N }, ...],
    "monthly_listeners": [{ "timestp": "...", "value": N }, ...],
    "popularity":        [{ "timestp": "...", "value": N }, ...]
  }
}
```

Take the last entry of each array for the current value. For the delta against
last brief, parse the prior brief's table (not the time-series — parsing your
own previous output is more stable than depending on Chartmetric's historical
backfill).

## Endpoint notes

| Endpoint | Source enum or arg |
|---|---|
| `/research/metrics?source=` | `spotify`, `tiktok`, `instagram`, `youtube_channel`, `youtube_artist` |
| `/research/rank` | returns a single integer or `null` |
| `/research/milestones` | activity feed, sorted by date desc |
| `/research/insights` | AI-surfaced observations |

For `/research/metrics?source=youtube`, use `youtube_channel` or
`youtube_artist`, **not plain `youtube`**.

## Credit awareness

The 5 endpoints in step 4 are all low-credit (1 credit or free each).
A full brief costs ≤5 credits per run. If any call returns
`{ "error": "insufficient_credits" }`, surface the `checkoutUrl` to the user
instead of silently dropping the section.

## Graceful degradation

If `/research/metrics` returns empty for an emerging artist (very thin
Chartmetric data), don't fall back to web search — that's the
`recoup-artist-research` skill's job. For the **weekly brief**, just write the
table with `—` cells and a note: "Thin data this week — consider running
`/recoup-research {slug}` for a deeper one-shot."

## References

- `references/endpoints.md` — full curl examples
- `references/response-shapes.md` — actual JSON shapes per endpoint
- `recoup-artist-research` skill — one-shot full sweep (use that, not this, for
  first-time research)
