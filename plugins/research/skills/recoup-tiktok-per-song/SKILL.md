---
name: recoup-tiktok-per-song
description: Produces a per-track TikTok velocity table for an artist's catalog by fetching every track and pulling per-song TikTok counts (uses, views) where the API has them — and explicitly printing "no data" for tracks where it doesn't. Use when asked "which of {artist}'s songs are blowing up on TikTok", "TikTok for {artist}", "{artist} per-song TikTok", "TT velocity {artist}", "which {artist} tracks are viral", or any per-song social signal request. This skill exists because ~2/3 of customer asks are per-song TikTok and the #1 source of bad results today is fabricated TikTok counts. The skill REFUSES to invent a number for tracks without data.
---

# TikTok Per-Song

The single highest-frequency customer ask in the company (~2/3 of Recoup
research requests). Also the #1 source of bad results today, because agents
fabricate per-song TikTok counts by substituting artist-level numbers.

**This skill exists to make that failure mode impossible.** For every track,
either the API has per-song TikTok data and we report it, or it doesn't and we
say "no data" — never a fabricated number.

## When to use

- "TikTok for {artist}" / "TT for {artist}"
- "Which {artist} songs are blowing up on TikTok"
- "{artist} per-song TikTok" / "per-track TT for {artist}"
- "Which tracks of {artist} are going viral"
- "TikTok velocity for {artist}"

For artist-level TikTok numbers (follower count, total posts), use
`recoup-artist-research` or `recoup-weekly-brief` instead.

## Setup

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Workflow

### 1. Resolve artist + workspace

Prefer `cmArtistId` from `artists/{slug}/RECOUP.md` if present. Otherwise:

```bash
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists&beta=true" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.results[0]'
```

Refuse to proceed if `match_strength < 1` — surface the ambiguity.

### 2. Get the catalog

```bash
curl -s "$RECOUP_API/research/tracks?artist={ARTIST}" \
  -H "x-api-key: $RECOUP_API_KEY" | jq '.tracks'
```

Each track object includes a Chartmetric track ID (`cm_track_id` or similar —
see `references/response-shapes.md` for the exact field name).

If the catalog is empty or the API errors, **stop** and report it. Do not
attempt to enumerate tracks from artist-level data.

### 3. For each track, fetch per-track detail

Fan out in parallel (use `&` and `wait`, or `xargs -P`):

```bash
curl -s "$RECOUP_API/research/track?id={CM_TRACK_ID}" \
  -H "x-api-key: $RECOUP_API_KEY" | jq
```

The per-track response **may or may not** include TikTok signal. Look for these
fields (exact names confirmed via `references/response-shapes.md`):

- `tt_uses` — TikTok creation count using this sound
- `tt_views` — TikTok views attributed to this sound
- `tt_velocity` — change in uses over a recent window
- `tiktok_top_videos` — top TT videos by view count

If **any** of these are present and non-null, the track has data.
If **all** are missing or null, the track has **no data**.

### 4. Build the table

Sort by TikTok velocity descending. For tracks without per-song data, list them
at the bottom in a separate group.

```markdown
# TikTok Per-Song — {Artist Name}
**Generated {YYYY-MM-DD}** | **Catalog size:** {N} tracks | **Tracks with TT data:** {M}

## Tracks with TikTok signal (sorted by velocity)

| Track | TT uses | TT views | Velocity | Notes |
|---|---|---|---|---|
| {title} | {tt_uses} | {tt_views} | {tt_velocity or "—"} | {1-line context if signal in `tiktok_top_videos`} |
| ... | ... | ... | ... | ... |

## Tracks without per-song TikTok data ({K} tracks)

The Recoup API does not have per-song TikTok signal for these. Reasons can
include: track too new, track too old, low TT presence, Chartmetric coverage
gap. **Do not assume zero TT activity** — assume *unknown* TT activity.

- {title 1}
- {title 2}
- ...

---
*Generated {ISO timestamp}. Source: Recoup research API per-track endpoint. For
artist-level TikTok numbers, run `/recoup-brief {slug}`.*
```

### 5. Save (if workspace exists)

Path: `artists/{slug}/research/tiktok-per-song-$(date +%F).md`

Same-day re-run is a no-op (file exists → tell the user).

## The hard rule

**If `tt_uses`, `tt_views`, `tt_velocity`, and `tiktok_top_videos` are ALL
absent or null for a track, that track goes in the "no data" group.**

Forbidden behaviors:

- ❌ Estimating per-song TT counts from artist-level `tiktok_followers`
- ❌ Filling cells with `~10K` or `est. {N}` or `low signal`
- ❌ Dropping the no-data tracks silently to make the output look better
- ❌ Inferring "high TT activity" from streaming data
- ❌ Writing a confident-looking number when only one of four TT fields is null

The honest table is the product. A 40-track catalog where 6 have data and 34
don't → the report shows 6 tracks ranked and lists the other 34 by name with no
fake numbers. **That is the right answer.**

## Output for tracks with TT data

When per-song data exists, show:

- `tt_uses` formatted with commas (e.g., `127,432`)
- `tt_views` formatted with K/M shorthand for >10K (e.g., `2.3M`)
- `tt_velocity` as a signed delta over the API's window (e.g., `+18%`)
- Notes column: brief context from `tiktok_top_videos[0]` if present
  (e.g., `"Top video: 4.2M views, posted by @creatorname"`)

## When the catalog endpoint fails

If `/research/tracks` returns empty for an artist that clearly has releases
(known from `/research/profile`), it usually means Chartmetric hasn't ingested
the catalog. Fallback options:

1. Try `/research/albums?artist=...` to enumerate releases, then per-album
   tracks
2. If still empty, tell the user honestly: "Catalog not ingested in
   Chartmetric. Cannot produce per-song view. Try `/recoup-brief` for
   artist-level signal."

**Do not** make up a track list from web search or guess track names. The
catalog endpoint being empty is a real signal about data availability.

## Endpoint notes

| Endpoint | What it returns |
|---|---|
| `/research/tracks?artist=` | Track list w/ Chartmetric IDs |
| `/research/track?id=` | Per-track detail (may include TT fields) |
| `/research/track/playlists?id=` | Playlists hosting this track (5 credits) |
| `/research/albums?artist=` | Album list (fallback for catalog) |

`/research/track/playlists` is expensive (5 credits) and only relevant for
playlist-pitching workflows — skip it for the TikTok view.

## Credit awareness

- `/research/tracks` — typically 1 credit
- `/research/track?id=` — typically 1 credit per call
- A 40-track catalog → ~41 calls → ~41 credits

For very large catalogs (Wiz Khalifa, Mac Miller-tier), warn the user before
fanning out 100+ track calls. Offer to cap at the top 25 tracks by
streaming/recency.

## References

- `references/endpoints.md` — full curl examples
- `references/response-shapes.md` — exact `/research/track` JSON shape including
  TT field names
- `recoup-artist-research` — for artist-level TikTok numbers
- `recoup-weekly-brief` — for weekly TT follower deltas
