# Response shapes (what the fields actually are)

Don't guess field names. Chartmetric pass-through responses are richer than the OpenAPI schema enumerates (`additionalProperties: true` everywhere), but these are the fields that exist and matter. If you're looking for a field that isn't here, it probably doesn't exist — dump the raw response once with `jq '.<collection>[0] | keys'` before coding against it.

**jq parsing note:** Some responses (especially `/research/profile`) may contain
control characters in text fields (e.g. bio/description). If `jq` fails with
"Invalid string: control characters", pipe through `tr -d '\000-\011\013\014\016-\037'`
first, or use Python's `json.loads()` which handles them.

## `/research/similar` → `artists[].*`

```jsonc
{
  "id": 3380,                    // Chartmetric artist ID
  "name": "Drake",
  "image_url": "...",
  "code2": "CA",                 // 2-letter country
  "verified": true,
  "band": false,
  "score": 98.74,                // overall match score (0-100)
  "similarity": 0.88,            // audience-config similarity (0-1)
  "rank": 7,                     // global Chartmetric rank
  "career_stage": "superstar",   // undiscovered|developing|mid-level|mainstream|superstar|legendary
  "recent_momentum": "growth",   // decline|gradual decline|steady|growth|explosive growth
  "sp_followers": 109449837,
  "sp_monthly_listeners": 88857078,
  "sp_playlist_count": 3418778,
  "spotify_playlist_total_reach": 905221589,
  "youtube_subscribers": 32000000,
  "youtube_monthly_video_views": 241476550,
  "ins_followers": 141635181,
  "tiktok_followers": 1400000,
  "network_strength": "influential",
  "label": "UMG",
  "primary_genre_smart": { "id": 501121, "name": "hip-hop/rap" },
  "genres": [ { "id": 501121, "name": "hip-hop/rap" }, ... ],
  "normalizedScores": { "sp_followers": 1, "tiktok_followers": 0.36, ... },
  "rank_stats_monthly": [ { "rank": 7, "timestp": "2026-04-17" }, ... ]
}
```

There is **no** `trend` field and **no** `metrics` object. Momentum is `recent_momentum`. Platform counts are top-level (`sp_followers`, `ins_followers`, etc.) — not nested under a wrapper.

## `/research/playlists` → `placements[].*` (NESTED, not flat)

```jsonc
{
  "playlist": {
    "id": 1805667,                // Chartmetric playlist ID
    "playlist_id": "7aa...",      // Spotify base62 ID
    "name": "My Shazam Tracks",
    "curator_name": "Erica Anne Benoit",
    "owner_name": "Erica Anne Benoit",
    "editorial": false,
    "personalized": false,
    "followers": 0,               // ⚠️  often 0 in placements — not a reliable reach signal here
    "position": 20,
    "peak_position": 2,           // better reach proxy than `followers`
    "added_at": "2025-11-11",
    "num_track": 486,
    "image_url": "...",
    "genres": [...], "moods": [...], "activities": [...], "tags": [...]
  },
  "track": {
    "id": 72120853,
    "name": "When You Were Mine",
    "isrc": "GBARL2100707",
    "spotify_popularity": 57,
    "artist_names": ["Joy Crookes"],
    "album_label": ["Speakerbox Recordings"],
    "release_dates": ["2021-08-24"]
    // ...
  }
}
```

So to filter editorial placements in jq: `.placements[] | select(.playlist.editorial == true)`. To rank by true reach, call `/research/playlist?platform=spotify&id={playlist.id}` for the detail record — the placement `followers` field is usually stale/zero.

## `/research/profile` — top-level platform fields are ALWAYS null

**Critical:** The top-level platform fields on `/research/profile` (`sp_followers`,
`sp_monthly_listeners`, `ins_followers`, `tiktok_followers`, etc.) are **always null
for every artist**, including Drake. This is not a coverage issue — the API simply
does not populate these top-level fields.

The real aggregated data lives inside `cm_statistics`:

```jsonc
// ❌ These are ALWAYS null — do not use
profile.sp_followers              // null
profile.sp_monthly_listeners      // null

// ✅ These are populated — use these
profile.cm_statistics.sp_followers           // 572376
profile.cm_statistics.sp_monthly_listeners   // 3019721
profile.cm_statistics.sp_popularity          // 62
profile.cm_statistics.ins_followers           // 409600
profile.cm_statistics.tiktok_followers        // 232200
profile.cm_statistics.ycs_subscribers         // YouTube subscribers
profile.cm_statistics.num_sp_editorial_playlists
profile.cm_statistics.num_sp_playlists
profile.cm_statistics.sp_playlist_total_reach
profile.cm_statistics.sp_editorial_playlist_total_reach
```

If `cm_statistics` fields are also sparse (very new/small artists), fall back:

- Streaming numbers → `/research/metrics?source=spotify`
- `career_stage` / `recent_momentum` → `/research/similar?artist=...` (the artist's own row is the first result and carries both fields)
- Editorial playlist count → `/research/playlists?editorial=true` (trust the actual result set)

**Preflight filter decisions with profile counts.** Before calling `/research/playlists?editorial=true`, check `cm_statistics.num_sp_editorial_playlists`. If it's 0, an empty editorial result isn't a skill or API bug — the artist genuinely has no editorial placements. Drop the filter or widen to `&indie=true&majorCurator=true&popularIndie=true`.

## `/research/milestones` — empty is legit

`{ status: "success", milestones: [] }` is common — even for artists with a real global rank. Milestones are discrete events (chart entries, major playlist adds, award mentions); many artists just haven't had one recently. Don't retry or escalate on empty — fall back to `/research/insights` or `/research/career` for narrative context.
