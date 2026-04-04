# Chartmetric API - Complete Endpoint Reference

> Base URL: `https://api.chartmetric.com`
> Full docs JSON: `references/api_data.json`

## Legend
- ✅ Working on your subscription
- 🔒 Locked (401 - needs higher tier)
- ⚠️ Needs specific params (400 with test data)

---

## Authorization (1 endpoint)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | POST | `/api/token` | Get API access token |

---

## Album (6 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/album/:id` | Album metadata |
| ✅ | GET | `/api/album/:id/tracks` | Album tracks |
| ✅ | GET | `/api/album/:id/:platform/:status/playlists` | Album playlists |
| ✅ | GET | `/api/album/:type/:id/get-ids` | Lookup album by platform ID |
| ⚠️ | GET | `/api/album/:id/:platform/:stats` | Album stats |
| ⚠️ | GET | `/api/album/:id/:type/charts` | Album charts |

---

## Artist (35 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/artist/:id` | Artist metadata |
| ✅ | GET | `/api/artist/:id/albums` | Artist albums |
| ✅ | GET | `/api/artist/:id/tracks` | Artist tracks |
| ✅ | GET | `/api/artist/:id/urls` | Social/streaming URLs |
| ✅ | GET | `/api/artist/:id/milestones` | Career milestones |
| ✅ | GET | `/api/artist/:id/news` | Recent news |
| ✅ | GET | `/api/artist/:id/noteworthy-insights` | AI insights |
| ✅ | GET | `/api/artist/:id/neighboring-artists` | Similar artists |
| ✅ | GET | `/api/artist/:id/riaa` | RIAA certifications |
| ✅ | GET | `/api/artist/:id/artist-rank` | Artist ranking |
| ✅ | GET | `/api/artist/:id/past-artist-rank` | Historical ranking |
| ✅ | GET | `/api/artist/:id/cmStats` | Cached stats & trends |
| ✅ | GET | `/api/artist/:id/career` | Career history |
| ✅ | GET | `/api/artist/:id/stat/:source` | Platform stats (spotify, instagram, etc.) |
| ✅ | GET | `/api/artist/:id/where-people-listen` | Spotify listeners by city |
| ✅ | GET | `/api/artist/:id/:platform/:status/playlists` | Playlist placements |
| ✅ | GET | `/api/artist/:id/venues` | Concert venues |
| ✅ | GET | `/api/artist/:id/tvmaze` | TV appearances |
| ✅ | GET | `/api/artist/:id/instagram-audience-stats` | Instagram audience demographics |
| ✅ | GET | `/api/artist/:id/instagram-audience-stats/dates` | IG audience data dates |
| ✅ | GET | `/api/artist/:id/tiktok-audience-stats` | TikTok audience demographics |
| ✅ | GET | `/api/artist/:id/youtube-audience-stats` | YouTube audience demographics |
| ✅ | GET | `/api/artist/:id/market-coverage-views/youtube` | YouTube views by market |
| ✅ | GET | `/api/artist/:type/:id/get-ids` | Lookup artist by platform ID |
| ✅ | GET | `/api/artist/list/filter` | Filter/discover artists |
| ⚠️ | GET | `/api/artist/anr/by/playlists` | ANR by playlists |
| ⚠️ | GET | `/api/artist/anr/by/social-index` | ANR by social index |
| ⚠️ | GET | `/api/artist/:id/cpp` | Cross-platform performance |
| ⚠️ | GET | `/api/artist/:id/:status/events` | Live events |
| ⚠️ | GET | `/api/artist/:id/top-tracks/:source` | Top tracks by platform |
| ⚠️ | GET | `/api/artist/:id/relatedartists` | Related artists |
| ⚠️ | GET | `/api/artist/:id/similar-artists/by-configurations` | Similar artists (configurable) |
| ⚠️ | GET | `/api/artist/:id/social-audience-stats` | Social audience stats |
| ⚠️ | GET | `/api/artist/:type/list` | List artists by metric |

---

## Brand (3 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/brand/list` | List all brands |
| ✅ | GET | `/api/brand/list/by/interest` | Brands by interest |
| ⚠️ | GET | `/api/brand/:brandId` | Brand info |

---

## Charts (32 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/charts/shazam/:country_code/cities` | Shazam cities |
| 🔒 | GET | `/api/charts/` | Charts introduction |
| 🔒 | GET | `/api/charts/airplay/:chart_type` | Airplay charts |
| 🔒 | GET | `/api/charts/amazon/:chart-type` | Amazon charts |
| 🔒 | GET | `/api/charts/applemusic/:chart-type` | Apple Music charts |
| 🔒 | GET | `/api/charts/tiktok/:chart-type` | TikTok charts |
| 🔒 | GET | `/api/charts/youtube/:chart_type` | YouTube charts |
| 🔒 | GET | `/api/charts/itunes/:chart-type` | iTunes charts |
| ⚠️ | GET | `/api/charts/anghami/track/:chartType` | Anghami track charts |
| ⚠️ | GET | `/api/charts/beatport` | Beatport charts |
| ⚠️ | GET | `/api/charts/:platform/countries` | Chart countries |
| ⚠️ | GET | `/api/charts/:streamingType/dates` | Chart dates |
| ⚠️ | GET | `/api/charts/genres/:platform` | Chart genres |
| ⚠️ | GET | `/api/charts/:type/:type_id/:chart_type/cm-score` | Chartmetric score |
| ⚠️ | GET | `/api/charts/circle/album/:chartType` | Circle album charts |
| ⚠️ | GET | `/api/charts/circle/track/:chartType` | Circle track charts |
| ⚠️ | GET | `/api/charts/deezer/` | Deezer charts |
| ⚠️ | GET | `/api/charts/hanteo/album/:chartType` | Hanteo album charts |
| ⚠️ | GET | `/api/charts/hanteo/track/:chartType` | Hanteo track charts |
| ⚠️ | GET | `/api/charts/line_music/album/:chartType` | Line Music album charts |
| ⚠️ | GET | `/api/charts/line_music/track/:chartType` | Line Music track charts |
| ⚠️ | GET | `/api/charts/melon/track/:chartType` | Melon track charts |
| ⚠️ | GET | `/api/charts/pandora/track/:chartType` | Pandora track charts |
| ⚠️ | GET | `/api/charts/qq/` | QQ Music charts |
| ⚠️ | GET | `/api/charts/shazam` | Shazam charts |
| ⚠️ | GET | `/api/charts/soundcloud` | SoundCloud (legacy) |
| ⚠️ | GET | `/api/charts/soundcloud/track/:chartType` | SoundCloud charts |
| ⚠️ | GET | `/api/charts/spotify/artists` | Spotify artist charts |
| ⚠️ | GET | `/api/charts/spotify/freshfind` | Spotify Freshfind |
| ⚠️ | GET | `/api/charts/spotify` | Spotify track charts |
| ⚠️ | GET | `/api/charts/tiktok/tracks/:chart-type` | TikTok track charts |
| ⚠️ | GET | `/api/charts/twitch/users` | Twitch charts |

---

## City (2 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/city/:id/:source/top-artists` | Top artists in city |
| ⚠️ | GET | `/api/city/:id/:source/top-tracks` | Top tracks in city |

---

## Curator (5 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/curator/:platform/:id/` | Curator metadata |
| ✅ | GET | `/api/curator/:platform/:id/playlists` | Curator's playlists |
| ✅ | GET | `/api/curator/:platform/:id/stat/:source` | Curator fan metrics |
| ✅ | GET | `/api/curator/:platform/:id/urls` | Curator social URLs |
| ✅ | GET | `/api/curator/:platform/lists` | List curators |

---

## Event (1 endpoint)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/event/venue/:venueId` | Events at venue |

---

## Festival (1 endpoint)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/festival/list` | List festivals |

---

## Genre (1 endpoint)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/genre` | List all genres |

---

## Playlist (9 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/playlist/:platform/:id` | Playlist metadata |
| ✅ | GET | `/api/playlist/:platform/:id/stats` | Playlist stats over time |
| ✅ | GET | `/api/playlist/:platform/:id/updated` | Last updated time |
| ✅ | GET | `/api/playlist/:platform/lists` | List playlists |
| ⚠️ | GET | `/api/playlist/by/:type/:id/evolution` | Playlist evolution |
| ⚠️ | GET | `/api/playlist/by/:type/:id/playlist-evolution` | Playlist evolution (alt) |
| ⚠️ | GET | `/api/playlist/:platform/:id/journey-progression/:type` | Playlist journey |
| ⚠️ | GET | `/api/playlist/:platform/:id/snapshot` | Playlist snapshot |
| ⚠️ | GET | `/api/playlist/:platform/:id/:span/tracks` | Playlist tracks |

---

## Radio (5 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/radio/station-list` | Radio station list |
| ⚠️ | GET | `/api/radio/:type/:id/airplay-totals` | Total airplays |
| ⚠️ | GET | `/api/radio/:type/:id/airplay-totals/:entity` | Airplays by entity |
| ⚠️ | GET | `/api/radio/:type/:id/airplays` | Airplay time series |
| ⚠️ | GET | `/api/radio/:type/:id/broadcast-markets` | Broadcast markets |

---

## Recommendation (1 endpoint)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ⚠️ | GET | `/api/playlist/:platform/:id/similarplaylists` | Similar playlists |

---

## SNS (1 endpoint)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/SNS/deepSocial/cm_artist/:id/instagram` | Instagram top posts/reels |

---

## Search (5 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/search` | Universal search |
| ✅ | GET | `/api/genres` | List genre IDs and names |
| ✅ | GET | `/api/genres/:id` | Get genre by ID |
| ⚠️ | GET | `/api/cities` | Get city info |
| ⚠️ | GET | `/api/search/social` | Social search |

---

## Track (12 endpoints)

| Status | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| ✅ | GET | `/api/track/:id` | Track metadata |
| ✅ | GET | `/api/track/:id/milestones` | Track milestones |
| ✅ | GET | `/api/track/:id/topVideos` | Top TikTok videos |
| ✅ | GET | `/api/track/youtube/:id/topShorts` | Top YouTube Shorts |
| ✅ | GET | `/api/track/:id/video-trends` | TikTok video trends |
| ✅ | GET | `/api/track/:type/:id/get-ids` | Lookup track by platform ID |
| ✅ | GET | `/api/track/list/filter` | Filter/discover tracks |
| ⚠️ | GET | `/api/track/:id/:platform/:status/playlists` | Track playlists |
| ⚠️ | GET | `/api/track/:id/relatedTracks` | Related tracks |
| ⚠️ | GET | `/api/track/:id/:platform/stats/:mode` | Track stats |
| ⚠️ | GET | `/api/track/:id/:platform/playlists/snapshot` | Playlist snapshot |
| ⚠️ | GET | `/api/track/:id/:type/charts` | Track charts |

---

## Summary

| Category | Total | Working | Locked | Needs Params |
|----------|-------|---------|--------|--------------|
| Authorization | 1 | 1 | 0 | 0 |
| Album | 6 | 4 | 0 | 2 |
| Artist | 35 | 24 | 0 | 11 |
| Brand | 3 | 2 | 0 | 1 |
| Charts | 32 | 1 | 7 | 24 |
| City | 2 | 1 | 0 | 1 |
| Curator | 5 | 5 | 0 | 0 |
| Event | 1 | 1 | 0 | 0 |
| Festival | 1 | 1 | 0 | 0 |
| Genre | 1 | 1 | 0 | 0 |
| Playlist | 9 | 4 | 0 | 5 |
| Radio | 5 | 1 | 0 | 4 |
| Recommendation | 1 | 0 | 0 | 1 |
| SNS | 1 | 1 | 0 | 0 |
| Search | 5 | 3 | 0 | 2 |
| Track | 12 | 7 | 0 | 5 |
| **TOTAL** | **120** | **55** | **7** | **58** |
