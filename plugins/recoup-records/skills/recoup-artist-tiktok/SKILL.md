---
name: recoup-artist-tiktok
description: Answers "which of {artist}'s songs are blowing up on TikTok" honestly. The research API (Songstats-backed) does NOT expose per-song TikTok counts, so this skill builds a per-song TikTok SIGNAL view from the data that does exist — track-level activity feeds, web/deep research with citations, and artist-level TikTok context — and refuses to fabricate per-track uses/views. Use when asked "which of {artist}'s songs are blowing up on TikTok", "TikTok for {artist}", "{artist} per-song TikTok", "TT velocity {artist}", or any per-song TikTok signal request. TikTok only — for general streaming health use recoup-artist-brief (streaming scope). This skill exists because per-song TikTok is the #1 customer ask and the #1 source of fabricated numbers.
---

# TikTok Per-Song

The single highest-frequency customer ask in the company (~2/3 of Recoup
research requests). Also the #1 source of bad results, because agents fabricate
per-song TikTok counts by substituting artist-level numbers.

**This skill exists to make that failure mode impossible.**

## Read this first — what the API can and can't do

The research API is backed by **Songstats**. Its track-detail endpoint
(`/research/track`) returns title, release date, collaborators, labels, genres,
and audio analysis — **but NO per-song TikTok fields.** There is no `tt_uses`,
`tt_views`, `tt_velocity`, or `tiktok_top_videos`. Those fields do not exist.

So you **cannot** produce a precise per-track TikTok uses/views table from the
structured API. Pretending otherwise is exactly the hallucination this skill
prevents. What you CAN do, honestly:

1. **Track-level activity feeds** — `/research/milestones` and `/research/career`
   return events with `activity_type` and a `track_info` object. TikTok/sound
   events tied to a specific track are real per-song signal.
2. **Web + deep research (cited)** — `POST /research/web` and `/research/deep`
   surface which songs are trending on TikTok, with citations. Any number you
   report MUST carry its source link.
3. **Artist-level TikTok context** — `/research/metrics?source=tiktok` for the
   artist's overall TikTok scale (clearly labeled as artist-level, never
   attributed to a single song).

The deliverable is a **per-song TikTok signal view**, not a fabricated counts
table.

## When to use

- "TikTok for {artist}" / "TT for {artist}"
- "Which {artist} songs are blowing up on TikTok"
- "{artist} per-song TikTok" / "per-track TT for {artist}"
- "Which tracks of {artist} are going viral"
- "TikTok velocity for {artist}"

For artist-level TikTok numbers only (follower count, total videos), use
`recoup-artist-research` or `recoup-artist-brief` instead.

## Setup

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Workflow

### 1. Resolve artist + workspace

Most endpoints take `artist={name}` directly. Resolve a provider ID if you need
an exact entity:

```bash
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.results[0]'
```

Disambiguate by `name`, `avatar`, `site_url` (there's no `match_strength` score).
Surface ambiguity to the user rather than guessing.

### 2. Get the catalog (so we know which songs exist)

```bash
curl -s "$RECOUP_API/research/tracks?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.tracks'
```

Each track has a `songstats_track_id`, `title`, `release_date`, and `artists[]`
(see `references/response-shapes.md`). This is the canonical song list — do NOT
invent track names from web search.

### 3. Pull per-song TikTok SIGNAL (not counts)

Fan out in parallel:

```bash
# Track-level activity events (filter to TikTok/sound activity, keyed by track_info)
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/career?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &

# AI insights — often names the specific viral song
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &

# Artist-level TikTok scale (context only, never per-song)
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY" &

wait

# Cited web research on which songs are trending on TikTok (the real per-song source)
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"which {ARTIST} songs are going viral on TikTok 2026","max_results":10}'

# For a deeper cited report on one breakout song:
curl -s -X POST "$RECOUP_API/research/deep" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} {TRACK} TikTok virality: sound uses, creator videos, timeline"}'
```

In the activity feeds, an entry's `track_info.title` maps the event to a song;
`activity_type` and `activity_text` tell you what happened. Sort by
`activity_tier` ascending (lower = more significant).

### 4. Build the per-song signal table

```markdown
# TikTok Per-Song Signal — {Artist Name}
**Generated {YYYY-MM-DD}** | **Catalog size:** {N} tracks

> The research API does not expose per-song TikTok uses/view counts. This is a
> SIGNAL view built from track-level activity events and cited web research.
> Numbers appear only where a cited source provides them.

## Songs with TikTok signal

| Track | Signal | Source | Detail |
|---|---|---|---|
| {title} | {activity event / web-cited trend} | {milestones \| web: domain} | {what the source says — cite link for any number} |
| ... | ... | ... | ... |

## Artist-level TikTok context (NOT per-song)
- Followers: {from /metrics?source=tiktok} · {other artist-level counters}
- *These are whole-account numbers and must never be attributed to one song.*

## Songs with no TikTok signal ({K} tracks)
No activity-feed event or cited web result tied these to TikTok. **Unknown**
TikTok activity — not zero.

- {title 1}
- {title 2}
- ...

---
*Generated {ISO timestamp}. Per-song counts are not available from the structured
API; web-sourced figures are cited inline. For artist-level TikTok numbers, run
`/recoup-brief {slug}`.*
```

### 5. Save (if workspace exists)

Path: `artists/{slug}/research/tiktok-per-song-$(date +%F).md`

Same-day re-run is a no-op (file exists → tell the user).

## The hard rule

**Never write a per-song TikTok uses/views number that the structured API didn't
give you (it can't) and that a citation doesn't support.**

Forbidden behaviors:

- ❌ Estimating per-song TT counts from artist-level TikTok followers
- ❌ Filling cells with `~10K`, `est. {N}`, or `low signal`
- ❌ Dropping no-signal tracks silently to make output look fuller
- ❌ Inferring "high TT activity" from streaming or playlist data
- ❌ Reporting a web-sourced number without its citation link

The honest signal view is the product. A 40-track catalog where 3 songs have a
cited TikTok trend and 37 don't → the report shows those 3 with sources and
lists the other 37 by name with no fake numbers. **That is the right answer.**

## When the catalog endpoint is empty

If `/research/tracks` returns empty for an artist that clearly has releases
(known from `/research/profile`), the catalog isn't ingested. Fallback:

1. Resolve the provider artist ID via search, then try
   `/research/albums?artist_id={id}` to enumerate releases.
2. If still empty, say so honestly: "Catalog not ingested. Cannot produce a
   per-song view. Try `/recoup-brief` for artist-level signal, or I can run web
   research on specific song titles you name."

**Do not** invent a track list from web search.

## Endpoint notes

| Endpoint | What it returns |
|---|---|
| `/research/tracks?artist=` | Catalog (song list with provider IDs) |
| `/research/milestones?artist=` | Activity feed, events keyed by `track_info` |
| `/research/career?artist=` | Activity feed (same shape) |
| `/research/insights?artist=` | AI observations (often names the viral song) |
| `/research/metrics?artist=&source=tiktok` | Artist-level TikTok scale (context only) |
| `POST /research/web` / `/research/deep` | Cited per-song TikTok trend research |
| `/research/track?id=` | Track metadata + audio analysis (NO TikTok fields) |

## Credit awareness

- `/research/tracks`, `/research/milestones`, `/research/career`,
  `/research/insights`, `/research/metrics` — typically 1 credit each
- `POST /research/web` — low credit; `/research/deep` — higher (and ~2+ min)
- `/research/track?id=` — ~5 credits (skip it for the TikTok view; it has no TT
  data anyway)

This skill is cheap by default (~5 credits) because it relies on artist-level
feeds + web research, not a per-track fan-out. Reserve `/research/deep` for a
single confirmed breakout song.

## References

- `references/endpoints.md` — full curl examples
- `references/response-shapes.md` — `/research/track` shape (confirms no TT fields)
- `recoup-artist-research` — for artist-level TikTok numbers
- `recoup-artist-brief` — for weekly TikTok follower deltas
