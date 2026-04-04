# Chartmetric API - Parameter Guide

All parameters below have been **tested and verified working**.

---

## Search Endpoints

### Universal Search ✅
```
GET /api/search?q=Drake&type=artists
GET /api/search?q=One%20Dance&type=tracks
GET /api/search?q=Views&type=albums
```
- `q`: Search query
- `type`: `artists` | `tracks` | `albums`

---

## Artist Endpoints

### Artist Metadata ✅
```
GET /api/artist/:id
```
- No params required

### Artist by Spotify ID ✅
```
GET /api/artist/spotify/:spotify_id/get-ids
```
- Returns Chartmetric ID for the artist

### Artist Stats ✅
```
GET /api/artist/:id/stat/:source
```
- **Valid sources:**
  - `spotify` ✅
  - `instagram` ✅
  - `tiktok` ✅
  - `twitter` ✅
  - `facebook` ✅
  - `youtube_channel` ✅
  - `youtube_artist` ✅
  - `soundcloud` ✅
  - `deezer` ✅
  - `twitch` ✅
  - `line` ✅
  - `melon` ✅
  - `wikipedia` ✅
  - `bandsintown` ✅
  - ~~`bilibili`~~ ❌ (doesn't exist)
  - ~~`snap`~~ ❌ (doesn't exist)

### Artist Where People Listen ✅
```
GET /api/artist/:id/where-people-listen
```
- Returns top cities by Spotify monthly listeners

### Artist URLs ✅
```
GET /api/artist/:id/urls
```
- Returns social and streaming URLs

### Artist Albums ✅
```
GET /api/artist/:id/albums
```
- Returns all albums

### Artist Tracks ✅
```
GET /api/artist/:id/tracks
```
- Returns all tracks

### Artist Top Tracks ✅
```
GET /api/artist/:id/top-tracks/tiktok
```
- **Only `tiktok` works**
- ~~`cm`~~ and ~~`youtubeforartist`~~ return "Domain does not exist"

### Artist Charts ✅
```
GET /api/artist/:id/:type/charts
```
- **Working types:**
  - `shazam` ✅
  - `itunes_top` ✅
  - `itunes_albums` ✅
  - `youtube` ✅
  - `youtube_tracks` ✅
  - `youtube_videos` ✅
  - `youtube_trends` ✅
  
- **NOT working (return "Streaming type does not exist"):**
  - ~~`spotify_viral_daily`~~
  - ~~`spotify_top_daily`~~
  - ~~`applemusic_top`~~
  - ~~`beatport`~~
  - ~~`amazon`~~

### ANR by Playlists ✅
```
GET /api/artist/anr/by/playlists?sortBy=followers_total_reach_diff_week_percent
```
- `sortBy` is REQUIRED
- DO NOT include `streamingType` (not allowed)

---

## Track Endpoints

### Track Metadata ✅
```
GET /api/track/:id
```
- Use Chartmetric track ID (not Spotify ID)

### Track by Spotify ID ✅
```
GET /api/track/spotify/:spotify_id/get-ids
```
- Returns Chartmetric ID for the track

---

## Album Endpoints

### Album Metadata ✅
```
GET /api/album/:id
```
- Use Chartmetric album ID

### Album Tracks ✅
```
GET /api/album/:id/tracks
```

### Album by Spotify ID ✅
```
GET /api/album/spotify/:spotify_id/get-ids
```
- Returns list with `cm_album` IDs

---

## Chart Endpoints

### Spotify Charts ✅
```
GET /api/charts/spotify?latest=true&country_code=US&interval=daily&type=plays
```
| Param | Required | Values |
|-------|----------|--------|
| `country_code` | ✅ | `US`, `GB`, `DE`, etc. |
| `interval` | ✅ | `daily`, `weekly` |
| `type` | ✅ | `plays`, `popularity`, `playlist_count`, `playlist_reach`, `viral`, `regional` |
| `latest` | optional | `true` |
| `date` | optional | `2026-01-01` |

### Apple Music Charts ✅
```
GET /api/charts/applemusic/tracks?latest=true&country_code=US&type=top
GET /api/charts/applemusic/albums?latest=true&country_code=US
```
| Param | Required | Values |
|-------|----------|--------|
| `country_code` | ✅ | `US`, `GB`, etc. |
| `type` (tracks only) | ✅ | `top`, `daily`, `city` |

### iTunes Charts ✅
```
GET /api/charts/itunes/tracks?latest=true&country_code=US
GET /api/charts/itunes/albums?latest=true&country_code=US
```
| Param | Required | Values |
|-------|----------|--------|
| `country_code` | ✅ | `US`, `GB`, etc. |
| `genre` | optional | `pop`, `hip-hop`, etc. |

### YouTube Charts ✅
```
GET /api/charts/youtube/videos?latest=true&country_code=US
```
| Param | Required | Values |
|-------|----------|--------|
| `country_code` | ✅ | `US`, `GB`, etc. |

### TikTok Charts ✅
```
GET /api/charts/tiktok/tracks?latest=true
```
| Param | Required | Values |
|-------|----------|--------|
| `latest` | optional | `true` |
| ~~`country_code`~~ | ❌ | NOT ALLOWED |

### Shazam Charts ✅
```
GET /api/charts/shazam?latest=true&country_code=US
```

### Deezer Charts ✅
```
GET /api/charts/deezer?latest=true&country_code=US
```

### Amazon Charts ✅
```
GET /api/charts/amazon/tracks?latest=true&genre=pop&type=popular_track
```
| Param | Required | Values |
|-------|----------|--------|
| `type` | ✅ | `popular_track`, `new_track` |
| `genre` | ✅ | `pop`, `hip-hop`, `All Genres`, etc. |
| ~~`country_code`~~ | ❌ | NOT ALLOWED |

### SoundCloud Charts ✅
```
GET /api/charts/soundcloud?latest=true&country_code=US&kind=top&genre=all-music
```
| Param | Required | Values |
|-------|----------|--------|
| `country_code` | ✅ | `US`, `GLOBAL`, etc. |
| `kind` | ✅ | `top`, `trending` |
| `genre` | ✅ | `all-music`, specific genres |

### Melon Charts (Korea) ✅
```
GET /api/charts/melon/track/general?duration=daily&genre=All%20Genres
```
| Param | Required | Values |
|-------|----------|--------|
| `duration` | ✅ | `daily` |
| `genre` | ✅ | `All Genres`, `pop`, `k-pop`, `hot` |

### Hanteo Charts (Korea) ✅
```
GET /api/charts/hanteo/album/music?duration=daily&latest=true
```
| Param | Required | Values |
|-------|----------|--------|
| `duration` | ✅ | `daily` |
| Chart type in path | ✅ | `music` |

### Chart Dates ✅
```
GET /api/charts/spotify_tracks/dates?fromDaysAgo=28
```
| Param | Required | Values |
|-------|----------|--------|
| `fromDaysAgo` | ✅ | Max 28 |

### Chart Genres ✅
```
GET /api/charts/genres/apple_music
GET /api/charts/genres/shazam_genre
```
- Valid platforms: `amazon`, `apple_music`, `beatport`, `itunes`, `shazam_genre`, `soundcloud`, etc.

---

## Other Endpoints

### Genre List ✅
```
GET /api/genre
```
- No params required

---

## Artist Playlists ✅

```
GET /api/artist/:id/:platform/:status/playlists
```

### Path Parameters

| Param | Required | Values |
|-------|----------|--------|
| `id` | ✅ | Chartmetric artist ID |
| `platform` | ✅ | `spotify`, `applemusic`, `deezer`, `amazon`, `youtube` |
| `status` | ✅ | `current`, `past` |

### Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `since` | date | Start date (YYYY-MM-DD) |
| `until` | date | End date (YYYY-MM-DD) |
| `limit` | integer | Results per page (default: 50) |
| `offset` | integer | Pagination offset |
| `sortColumn` | string | Sort by (see table below) |

**Note:** API defaults to descending sort order. Use `--asc` flag in script for ascending.

### Valid sortColumn by Platform & Status

| Platform | Status | Valid sortColumn Values |
|----------|--------|------------------------|
| amazon | current | `added_at` (default), `countries`, `name`, `peak_position`, `track` |
| applemusic | current | `added_at` (default), `name`, `peak_position`, `position`, `track` |
| applemusic | past | `added_at`, `name`, `peak_position`, `position`, `removed_at` (default), `track` |
| deezer | current | `added_at` (default), `fdiff_month`, `followers`, `name`, `peak_position`, `track` |
| deezer | past | `added_at`, `fdiff_month`, `followers`, `name`, `peak_position`, `removed_at` (default), `track` |
| spotify | current | `added_at`, `code2`, `fdiff_month`, `followers` (default), `name`, `peak_position`, `position`, `track` |
| spotify | past | `added_at`, `code2`, `fdiff_month`, `followers` (default), `name`, `peak_position`, `position`, `removed_at`, `track` |
| youtube | current | `added_at` (default), `name`, `peak_position`, `track`, `vdiff_month`, `views` |
| youtube | past | `added_at`, `name`, `peak_position`, `removed_at` (default), `track`, `vdiff_month`, `views` |

### Playlist Type Filters (Platform-Specific)

| Filter | spotify | applemusic | deezer | amazon |
|--------|---------|------------|--------|--------|
| `editorial` | ✅ | ✅ | ✅ | |
| `editorialBrand` | | ✅ | | |
| `personalized` | ✅ | | | |
| `deezerPartner` | | | ✅ | |
| `chart` | ✅ | ✅ | ✅ | |
| `thisIs` | ✅ | | | |
| `hundredPercent` | | | ✅ | |
| `newMusicFriday` | ✅ | | | |
| `radio` | ✅ | ✅ | | |
| `fullyPersonalized` | ✅ | | | |
| `brand` | ✅ | | ✅ | |
| `majorCurator` | ✅ | | ✅ | |
| `musicBrand` | | ✅ | | |
| `nonMusicBrand` | | ✅ | | |
| `popularIndie` | ✅ | | ✅ | |
| `indie` | ✅ | ✅ | ✅ | |
| `audiobook` | ✅ | | | |
| `personalityArtist` | | ✅ | | |

**⚠️ Important:** When no filter parameters are specified, the API may return an empty array. Specify filters explicitly to get data.

### Example Requests

```bash
# Basic - all current Spotify playlists
GET /api/artist/1022311/spotify/current/playlists

# With date range and sorting
GET /api/artist/1022311/spotify/current/playlists?since=2025-01-01&sortColumn=followers&limit=50

# Only New Music Friday playlists
GET /api/artist/1022311/spotify/current/playlists?editorial=true&personalized=true&chart=false&thisIs=false&newMusicFriday=true&radio=false&fullyPersonalized=false&brand=true&majorCurator=true&popularIndie=true&indie=true&audiobook=false
```

**Note:** The generic `/artist/:id/playlists` returns 401 - use platform-specific path instead.

---

## Related Artists ✅

### Basic Endpoint
```
GET /api/artist/:id/relatedartists?limit=10
```

| Param | Required | Description |
|-------|----------|-------------|
| `limit` | ✅ | Number of artists (1-100) |

### Similar Artists by Configurations ✅
```
GET /api/artist/:id/similar-artists/by-configurations?audience=high&genre=high&limit=10
```

| Param | Required | Values | Description |
|-------|----------|--------|-------------|
| `audience` | ⚠️ At least one config required | `high`, `medium`, `low` | Audience similarity |
| `mood` | ⚠️ At least one config required | `high`, `medium`, `low` | Mood similarity |
| `genre` | ⚠️ At least one config required | `high`, `medium`, `low` | Genre similarity |
| `musicality` | ⚠️ At least one config required | `high`, `medium`, `low` | Musicality similarity |
| `limit` | optional | integer | Number of results (default: 10) |
| `offset` | optional | integer | Pagination offset (default: 0) |

**Response includes:**
- `similarity` score (0-1)
- `career_stage` (undiscovered, developing, mid-level, mainstream, superstar, legendary)
- `recent_momentum` (decline, gradual decline, steady, growth, explosive growth)
- Spotify followers, monthly listeners, playlist reach
- YouTube subscribers, TikTok followers, Instagram followers

**Note:** `/artist/:id/similar` returns 401 - use `relatedartists` or `similar-artists/by-configurations` instead.

---

## Curator Endpoints ✅

```
GET /api/curator/:platform/:numeric_id
```

| Param | Values |
|-------|--------|
| `platform` | `spotify` |
| `numeric_id` | Chartmetric curator ID (integer) |

Example: `/api/curator/spotify/1` returns PlayStation curator

**Note:** `/curator/search` returns 401 - must have numeric curator ID.

---

## Endpoints That Return 401 (Internal Only)

These specific paths are internal and not accessible:

1. `/api/charts/` - Charts Introduction (use specific chart endpoints)
2. `/api/artist/:id/playlists` - Use `/artist/:id/:platform/current/playlists`
3. `/api/artist/:id/similar` - Use `/artist/:id/relatedartists?limit=N`
4. `/api/curator/search` - Use `/curator/:platform/:id` with numeric ID
5. `/api/charts/tiktok/popular` - Use `/charts/tiktok/tracks`
6. `/api/charts/tiktok/viral` - Use `/charts/tiktok/tracks`

---

## Summary

**Verified Working: 57+ core endpoints**

All essential functionality is available:
- ✅ Search (artists, tracks, albums)
- ✅ Artist data (metadata, stats, cities, URLs, albums, tracks, career)
- ✅ Artist playlists (per platform: spotify, applemusic, deezer, amazon, youtube)
  - With filter support: editorial, newMusicFriday, indie, chart, etc.
- ✅ Related artists (basic endpoint)
- ✅ Similar artists by configurations (with audience/mood/genre/musicality filters)
- ✅ Platform metrics (14 sources)
- ✅ Track/album lookup by Spotify ID
- ✅ Curator lookup (by numeric ID)
- ✅ Charts (Spotify, Apple Music, iTunes, YouTube, TikTok, Shazam, Deezer, Amazon, SoundCloud, Melon, Hanteo)
- ✅ Genre discovery
- ✅ ANR playlists

---

## Quick Reference: Most Used Endpoints

```bash
# Search
GET /api/search?q=Drake&type=artists

# Artist profile
GET /api/artist/1320

# Artist by Spotify
GET /api/artist/spotify/3TVXtAsR1Inumwj472S9r4/get-ids

# Artist stats
GET /api/artist/1320/stat/spotify

# Artist cities
GET /api/artist/1320/where-people-listen

# Spotify charts
GET /api/charts/spotify?latest=true&country_code=US&interval=daily&type=plays

# TikTok charts
GET /api/charts/tiktok/tracks?latest=true
```
