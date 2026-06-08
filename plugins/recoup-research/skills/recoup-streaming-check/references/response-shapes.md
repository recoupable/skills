# Response shapes (what the fields actually are)

Don't guess field names. The research API is backed by **Songstats**, and
responses carry `additionalProperties: true` (extra fields may pass through),
but these are the fields that exist and matter. If you're looking for a field
that isn't here, it probably doesn't exist — dump the raw response once with
`jq '.<collection>[0] | keys'` before coding against it.

**IDs are short alphanumeric strings** (`wjcgfd9i`, `1ik97vot`), not numeric
Chartmetric IDs. **`career_stage`, `recent_momentum`, `match_strength`,
`cm_statistics`, and `peak_position` no longer exist** anywhere in the API.

**jq parsing note:** Some responses (especially `/research/profile`) may contain
control characters in text fields (e.g. bio). If `jq` fails with
"Invalid string: control characters", pipe through `tr -d '\000-\011\013\014\016-\037'`
first, or use Python's `json.loads()` which handles them.

## `/research` (search) → `results[].*`

```jsonc
{
  "id": "wjcgfd9i",                  // provider-neutral ID → pass to detail endpoints
  "songstats_artist_id": "wjcgfd9i", // (type=tracks → songstats_track_id)
  "name": "Drake",
  "avatar": "https://i.scdn.co/image/...",
  "site_url": "https://songstats.com/artist/wjcgfd9i/drake"
  // type=tracks also: release_date, is_remix, artists[], labels[]
}
```

There is **no** `match_strength` and no relevance score. Disambiguate by `name`,
`avatar`, `site_url`, and (tracks) `release_date` / `artists[]`.

## `/research/profile` and `/research/lookup` → `artist_info.*`

Both return the same `artist_info` object. **There are no follower/listener
counts on profile** — those come from `/research/metrics`.

```jsonc
{
  "status": "success",
  "result": "success",
  "message": "Data Retrieved.",
  "artist_info": {
    "name": "Drake",
    "avatar": "https://i.scdn.co/image/...",
    "site_url": "https://songstats.com/artist/...",
    "country": "US",                  // ISO code, may be null
    "bio": "A year or so after...",   // may be null
    "genres": ["Rap", "Hip Hop", "Pop Rap"],
    "links": [
      { "source": "spotify", "external_id": "3TVXtAsR1Inumwj472S9r4",
        "url": "https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" }
      // beatport, traxsource, apple_music, etc.
    ],
    "related_artists": [
      { "songstats_artist_id": "0rtly9qv", "name": "Tory Lanez",
        "avatar": "...", "site_url": "..." }
    ]
  }
}
```

## `/research/metrics` → `stats[].data` (CURRENT snapshot, not a time series)

`/research/metrics?source=spotify` returns **current snapshot counters**, not a
historical time series. This is where follower/listener/playlist numbers live.

```jsonc
{
  "status": "success",
  "source_ids": ["spotify"],
  "artist_info": { "songstats_artist_id": "wjcgfd9i", "name": "Drake", "avatar": "...", "site_url": "..." },
  "stats": [
    {
      "source": "spotify",
      "data": {
        "monthly_listeners_current": 99477872,
        "followers_total": 112185098,
        "popularity_current": 100,
        "streams_total": 137929083971,
        "playlists_current": 176085,
        "playlists_total": 214818,
        "playlists_editorial_current": 568,
        "playlists_editorial_total": 2102,
        "playlist_reach_current": 993868411,
        "playlist_reach_total": 1939843597,
        "charts_current": 179,
        "charts_total": 341,
        "charted_tracks_current": 66,
        "charted_tracks_total": 399,
        "charted_cities_total": 135,
        "charted_countries_total": 74
      }
    }
  ]
}
```

The `data` keys vary by `source`. For TikTok you'll see follower/like/video
counts; for instagram follower/engagement counts; etc. Always `jq
'.stats[0].data | keys'` once for an unfamiliar source. A `202`
`{ status: "pending", state: "refresh_pending" }` means retry shortly.

## `/research/similar` → `artists[].*` (flat list, no scores)

```jsonc
{
  "status": "success",
  "artists": [
    { "id": "0rtly9qv", "songstats_artist_id": "0rtly9qv",
      "name": "Tory Lanez", "avatar": "...", "site_url": "..." }
  ]
}
```

**No similarity score, no `career_stage`, no `recent_momentum`, no platform
counts.** It's a ranked-by-relevance list of artist references. To judge a
peer's size/stage, call `/research/metrics` on that peer. Weight the match with
`audience`, `genre`, `mood`, `musicality` (each `high|medium|low`, default
`medium`).

## `/research/playlists` → `placements[].*` (FLAT, not nested)

```jsonc
{
  "status": "success",
  "placements": [
    {
      "playlist_id": "37i9dQZF1DXcBWIGoYBM5M",  // platform playlist ID
      "playlist_name": "Today's Top Hits",
      "external_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
      "followers_total": "34.3M",                // human-readable STRING
      "image_url": "https://i.scdn.co/image/..."
    }
  ]
}
```

`followers_total` is a formatted string (`"34.3M"`), not an integer. The shape
is flat — there is no nested `playlist`/`track` wrapper and no `editorial`
boolean on artist-level placements.

## `/research/track/playlists` → `placements[]`

`{ status, placements: [...] }`. Placement shape varies by platform; each entry
is the provider's raw playlist object. `jq '.placements[0] | keys'` once.

## `/research/tracks` → `tracks[]` and `/research/albums` → `albums[]` (catalog items)

```jsonc
{
  "songstats_track_id": "p8or4a5h",          // tracks; albums omit this
  "title": "Janice STFU (HILLS Remix)",
  "avatar": "https://data.songstats.com/images/...",
  "release_date": "2026-05-29",               // may be null
  "site_url": "https://songstats.com/track/...",
  "isrcs": [],
  "artists": [{ "name": "Drake", "songstats_artist_id": "wjcgfd9i" }]
}
```

The catalog is **unfiltered** — high-catalog artists include remixes and
feature appearances. There is **no per-track popularity, stream, or TikTok
count** in this list.

## `/research/track` → `track_info` + `audio_analysis`

```jsonc
{
  "status": "success",
  "track_info": {
    "title": "...", "avatar": "...", "site_url": "...",
    "release_date": "2024-02-25",
    "artists": [{ "name": "..." }],
    "is_remix": false,
    "collaborators": [{ "name": "...", "roles": ["producer"] }],
    "labels": [ /* objects */ ],
    "distributors": [{ "name": "..." }],
    "genres": ["..."],
    "links": [{ "source": "spotify", "external_id": "...", "url": "...", "isrc": "..." }]
  },
  "audio_analysis": [
    { "key": "acousticness", "value": "0.12" },
    { "key": "tempo", "value": "134" }
    // ~13 audio features as key/value strings
  ]
}
```

**There are NO TikTok fields** (`tt_uses`, `tt_views`, etc.) on track detail —
the API does not expose per-song TikTok counts. Don't look for them.

## `/research/career`, `/research/insights`, `/research/milestones` → activity feeds

All three return an array of the same `activity` shape, keyed `career`,
`insights`, and `milestones` respectively.

```jsonc
{
  "status": "success",
  "milestones": [
    {
      "source": "spotify",
      "activity_text": "Added to Today's Top Hits",
      "activity_type": "playlist",          // e.g. playlist, chart
      "activity_date": "2026-06-04",
      "activity_url": "...",                 // may be null
      "activity_avatar": "...",              // may be null
      "activity_tier": 1,                    // importance: lower = more significant
      "track_info": { "title": "...", "release_date": "...", "artists": [{ "name": "..." }] }
    }
  ]
}
```

Importance is `activity_tier` (an integer, lower = bigger) — **not** a star
rating. An empty array (`{ status: "success", milestones: [] }`) is legitimate;
many artists simply have no recent discrete events. Don't retry or escalate on
empty — fall back to `/research/insights` or `/research/career`.

## `/research/audience` → `audience[]`

```jsonc
{ "status": "success", "audience": [ /* per-platform demographic objects */ ],
  "artist_info": { ... }, "source_ids": ["tiktok"] }
```

`audience` is frequently `[]` for an artist/platform the provider has no data
for. Empty is not an error — fall back to another platform or to cities-via-web
research.

## `/research/urls` → `urls[]`

```jsonc
{ "status": "success",
  "urls": [ { "domain": "spotify", "url": "https://open.spotify.com/artist/..." },
            { "domain": "instagram", "url": "..." } ] }
```

Each entry is a `{ domain, url }` pair (it also includes pseudo-entries like
`avatar` and `site_url`).

## POST responses

- `/research/web` → `{ status, results: [{ title, url, snippet, date, last_updated }], formatted }`
- `/research/deep` → `{ status, content (markdown), citations: [url, ...] }`
- `/research/people` → `{ status, results: [{ title, url, id, publishedDate, author, highlights[], summary }] }`
- `/research/extract` → `{ status, results: [{ url, title, publish_date, excerpts[], full_content }], errors[] }`
- `/research/enrich` → `{ status, output: { ...your schema... }, citations: [{ url, title, field }] }`

## Error shape (all endpoints)

```jsonc
{ "status": "error", "error": "Missing required parameter: artist" }
```

`501` with `Request failed with status 501` means the configured data source
doesn't support that endpoint/shape — treat it like "no data" and degrade
gracefully.
