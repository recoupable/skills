---
name: recoup-trend-detection
description: A&R discovery, emerging-artist scouting, and viral song analysis via the Recoup research API. Use when asked to find emerging artists, discover new talent, scout a genre or scene, or understand why a song went viral. Triggers on "find emerging artists", "A&R scouting", "discover artists", "why did this go viral", "viral song", "trending", "emerging [genre]", "breakout artists", "who's next in [genre]".
---

# Trend Detection

A&R discovery and viral song analysis through the Recoup research API. Find
emerging artists before they blow up and understand what's driving virality.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

> **How discovery works now:** the filter-based `discover`, `charts`, and
> `genres` endpoints were removed in the Songstats migration. Discovery now
> starts from a known **anchor artist** and fans out through `/research/similar`
> (weighted by `musicality`/`genre`), validated with `/research/metrics`. Use
> `/research/web` and `/research/deep` to find anchors or scan a scene.

## Decision tree

- **"Find emerging [genre] artists"** → A&R Discovery workflow (anchor → similar → metrics)
- **"Who's blowing up in [scene]?"** → `POST /research/web` to surface names, then validate each
- **"Why did [song] go viral?"** → Viral Song Autopsy workflow
- **"Find TikTok breakouts"** → TikTok-Driven Scouting workflow

## A&R Discovery

Find emerging artists before they blow up:

```bash
# 1. Pick an anchor — a known artist in the target sound. Resolve it, or scout names via web.
curl -s "$RECOUP_API/research?q={ANCHOR_ARTIST}&type=artists" -H "x-api-key: $RECOUP_API_KEY"
# (or) surface candidate names from the web:
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"emerging {GENRE} artists to watch 2026","max_results":15}'

# 2. Fan out to sonic look-alikes — musicality=high surfaces smaller, undiscovered acts
curl -s "$RECOUP_API/research/similar?artist={ANCHOR_ARTIST}&musicality=high&genre=high&limit=50" \
  -H "x-api-key: $RECOUP_API_KEY"

# 3. For each candidate, validate trajectory on two platforms (similar has no metrics — size them here)
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"

# 4. Editorial pickup = label interest signal (read playlists_editorial_current from metrics, or list placements)
curl -s "$RECOUP_API/research/playlists?artist={candidate}&status=current" -H "x-api-key: $RECOUP_API_KEY"

# 5. AI-generated insights
curl -s "$RECOUP_API/research/insights?artist={candidate}" -H "x-api-key: $RECOUP_API_KEY"
```

**Synthesize:** Emerging artists with a similar sound but a smaller audience.
Since `/similar` returns no stage or score, rank candidates yourself from the
`/metrics` snapshot — lower `monthly_listeners_current` with rising
`playlists_editorial_current` is the breakout window.

## Viral Song Autopsy

Why did this song go viral? Can we replicate it?

```bash
# 1. Resolve + fetch track details (genres, audio analysis, collaborators)
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks" -H "x-api-key: $RECOUP_API_KEY"   # get track id
curl -s "$RECOUP_API/research/track?id={track_id}" -H "x-api-key: $RECOUP_API_KEY"

# 2. Artist metrics snapshots
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"

# 3. Playlist timeline for this track (5 credits)
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&status=current" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&status=past&since=2025-01-01" -H "x-api-key: $RECOUP_API_KEY"

# 4. Activity feed — chart entries, big playlist adds
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 5. AI insights
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY"

# 6. Cultural context via web search (per-song TikTok counts aren't in the API)
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"{TRACK_NAME} {ARTIST} viral TikTok moment\",\"max_results\":10}"
```

**Synthesize:** Timeline of the viral moment — which playlists amplified it (from
`track/playlists`), what the audio analysis suggests about its hook, which
audience drove sharing. Compare with similar artists' trajectories to judge
replicability. The per-song TikTok *numbers* aren't in the API — pull that
narrative from web/deep research, never a fabricated count.

## TikTok-Driven Scouting

Find tracks blowing up on TikTok and the indie artists behind them:

```bash
# 1. Surface candidate songs/artists from the web (no charts/discover endpoint)
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"songs blowing up on TikTok {GENRE} 2026","max_results":15}'

# 2. Validate each candidate's pipeline
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=tiktok" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=spotify" -H "x-api-key: $RECOUP_API_KEY"

# 3. Check editorial pickup for the breakout track
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks" -H "x-api-key: $RECOUP_API_KEY"   # get track id
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&editorial=true&indie=true&majorCurator=true&popularIndie=true" -H "x-api-key: $RECOUP_API_KEY"

# 4. Deep cited narrative on the trend itself
curl -s -X POST "$RECOUP_API/research/deep" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"why is {TRACK} going viral on TikTok and who is driving it"}'
```

## Ranking candidates (no filter endpoint — do it client-side)

Because there's no `/discover` endpoint to pre-filter by listener range or growth,
gather candidates from `/similar` and `/web`, then rank them yourself on the
`/metrics` snapshot:

- **Listener band:** keep candidates whose `monthly_listeners_current` sits in
  your target range (e.g. 50K–200K for emerging acts).
- **Editorial signal:** rising `playlists_editorial_current` on a small artist =
  label interest before it's obvious.
- **Cross-platform:** strong TikTok (`/metrics?source=tiktok`) + thin Spotify =
  an unconverted breakout worth catching early.
- **Sound fit:** confirm with `/research/track` audio analysis and genres.

## Critical gotchas

- **No `discover`, `charts`, or `genres` endpoints.** Discovery = anchor artist +
  `/similar` + `/web`. Filtering by listener range / growth happens client-side
  on the `/metrics` snapshot, not via query params.
- **`/research/similar` has no `career_stage` or score.** Size and rank each
  candidate with `/research/metrics`.
- **`/research/milestones` empty is legit** — even for ranked artists. Fall back
  to `/insights` or `/career`.
- **`/research/metrics` uses `youtube_channel` / `youtube_artist`**, not plain
  `youtube`; may return `202` `refresh_pending` (retry shortly).
- **Per-song TikTok counts don't exist in the API.** Get viral narrative from
  `/web` and `/deep` — never invent a number.

## References

- **`references/endpoints.md`** — endpoint params, source enums, latency
- **`references/workflows.md`** — Workflows 4 (A&R Discovery), 7 (Viral Autopsy), Example C (TikTok scouting)
