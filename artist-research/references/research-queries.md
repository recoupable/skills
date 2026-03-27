# Research Queries

How to gather data depending on your environment.

## Option A: Perplexity Deep Research (Sandbox — `web_deep_research` MCP tool)

Send this as a single message to the `web_deep_research` tool. Replace `{ARTIST_NAME}` with the actual artist name:

```
Research the music artist {ARTIST_NAME} comprehensively. I need the following:

1. BIOGRAPHY: Real name, age, hometown, origin story, how they got started in music, key career milestones (chart positions, awards, notable features, viral moments, label signings). Where are they right now — current release cycle, tour status, recent activity.

2. STREAMING & PLATFORM METRICS: Spotify monthly listeners, follower count, top tracks and their popularity. YouTube subscribers, average views, most-viewed video. TikTok followers and any viral sounds. Instagram followers and engagement. Any other platform presence (SoundCloud, Bandcamp, Apple Music Shazam data).

3. DISCOGRAPHY: Complete album/EP/single timeline with release dates. Most commercially successful releases. Critical reception. Collaborations and features.

4. FAN BASE: Who listens to this artist? Age demographics, geographic concentration, psychographic traits. What subcultures or communities overlap with the fan base? How do fans behave — are they collectors, concert-goers, streamers, vinyl buyers? What brands or interests do the fans share?

5. LIVE PERFORMANCE: Tour history, venue sizes, ticket price ranges, primary touring markets. Festival appearances. Sell-through rates if available.

6. COMPETITIVE LANDSCAPE: Top 5 similar artists in the same lane. How does {ARTIST_NAME} compare on streaming numbers, social following, and live performance? Where does {ARTIST_NAME} outperform or underperform vs peers?

7. CULTURAL CONTEXT: What micro-scenes or subgenres does {ARTIST_NAME} belong to? What adjacent music communities have fan overlap? What cultural moments, trends, or movements is {ARTIST_NAME} connected to?

8. BUSINESS & PARTNERSHIPS: Current label situation (independent, signed, distribution deal). Known brand partnerships or sync placements. Revenue streams beyond streaming (merch, touring, sync, licensing). Management and team (if publicly known).

Cite all sources. Include specific numbers where available. Note when data is estimated vs confirmed.
```

This single call replaces 8-12 individual web searches. Perplexity will browse extensively and return citations.

## Option B: WebSearch (Cursor/Local — No MCP Tools)

Run these searches. Batch independent searches in parallel when possible.

### Core Identity (Run first — these inform everything else)

1. `"{ARTIST_NAME}" musician biography discography`
2. `"{ARTIST_NAME}" artist interview origin story`

### Streaming & Metrics

3. `"{ARTIST_NAME}" spotify monthly listeners 2026`
4. `"{ARTIST_NAME}" streaming numbers charts`

### Fan Base & Audience

5. `"{ARTIST_NAME}" fan base demographics audience`
6. `"{ARTIST_NAME}" reddit fans community` (skip if last30days is handling this)

### Competitive Landscape

7. `"{ARTIST_NAME}" similar artists comparisons`
8. `"artists like {ARTIST_NAME}" OR "{ARTIST_NAME} compared to"`

### Business & Industry

9. `"{ARTIST_NAME}" label deal management brand partnership`
10. `"{ARTIST_NAME}" tour concerts live shows 2025 2026`

### Cultural Context

11. `"{ARTIST_NAME}" genre scene subculture movement`
12. `"{ARTIST_NAME}" sync placement TV film commercial`

### Supplemental (if initial results are thin)

13. `"{ARTIST_NAME}" press coverage interview profile`
14. `site:genius.com "{ARTIST_NAME}"` (for discography and lyrical context)

### Search Tips

- Put the artist name in quotes to avoid false matches
- If the artist name is common (e.g., "Jada"), add qualifiers: genre, label, city
- If initial searches return thin results, try variations: stage name vs real name, former group names, collaborator names
- For emerging artists with little press coverage, try SoundCloud, Bandcamp, and local music blogs
- When you get streaming numbers from web articles, note the date — these change fast

## Option C: MCP Platform Data (Sandbox — Structured API Data)

If these MCP tools are available, use them for authoritative data:

### Spotify

1. `spotify_search` — Search for the artist to get their Spotify ID
2. `spotify_artist_top_tracks` — Get top tracks with popularity scores
3. `spotify_artist_albums` — Get full discography with release dates
4. `spotify_album` — For specific album details (track listings, popularity)

### YouTube

1. `youtube_channels` — Get channel data (subscribers, total views)
2. `youtube_channel_video_list` — Get recent videos with view counts

### Artist Platform Data

1. `artist_deep_research` — Get all connected social accounts and follower data
2. `get_artist_socials` — Social media links and metrics

### Data Priority

When platform API data conflicts with web-scraped data, trust the API data. It's real-time and authoritative. Note the discrepancy in the report — it may indicate the web data is stale.

## Option D: Chartmetric (Python Scripts — Requires CHARTMETRIC_REFRESH_TOKEN)

Chartmetric provides the deepest music analytics data. If the token is configured, run these scripts from the chartmetric skill directory. Each script outputs JSON you can parse.

### Discovery and Profile

```bash
# Find the artist — get their Chartmetric ID
python scripts/search_artist.py "{ARTIST_NAME}"

# Full profile (bio, genres, social links, label)
python scripts/get_artist.py {CM_ID}

# Career timeline — key moments, trajectory
python scripts/get_artist_career.py {CM_ID}

# AI-generated insights (Chartmetric's own analysis)
python scripts/get_artist_insights.py {CM_ID}
```

### Streaming Metrics (Feeds Section 4: KPI Dashboard)

```bash
# Spotify: monthly listeners, followers, popularity scores
python scripts/get_artist_metrics.py {CM_ID} --source spotify

# Instagram: followers, engagement
python scripts/get_artist_metrics.py {CM_ID} --source instagram

# TikTok: followers, video performance
python scripts/get_artist_metrics.py {CM_ID} --source tiktok

# YouTube: subscribers, views
python scripts/get_artist_metrics.py {CM_ID} --source youtube_channel

# SoundCloud (for indie/underground artists)
python scripts/get_artist_metrics.py {CM_ID} --source soundcloud
```

All 14 valid sources: `spotify`, `instagram`, `tiktok`, `twitter`, `facebook`, `youtube_channel`, `youtube_artist`, `soundcloud`, `deezer`, `twitch`, `line`, `melon`, `wikipedia`, `bandsintown`

### Audience and Geography (Feeds Section 3: Fan Personas)

```bash
# Instagram audience demographics (age, gender, location)
python scripts/get_artist_audience.py {CM_ID}

# TikTok audience demographics
python scripts/get_artist_audience.py {CM_ID} --platform tiktok

# YouTube audience demographics
python scripts/get_artist_audience.py {CM_ID} --platform youtube

# Top cities by listener concentration
python scripts/get_artist_cities.py {CM_ID}

# Top Instagram posts/reels (what content resonates)
python scripts/get_artist_instagram_posts.py {CM_ID}
```

### Competitive Landscape (Feeds Section 6: White-Space)

```bash
# Similar artists by audience and genre overlap
python scripts/get_similar_artists.py {CM_ID} --by-config --audience high --genre high --limit 10

# Compare metrics with a specific competitor
python scripts/get_artist_metrics.py {CM_ID} --source spotify
python scripts/get_artist_metrics.py {COMPETITOR_CM_ID} --source spotify
```

### Playlist Intelligence

```bash
# Current editorial playlist placements
python scripts/get_artist_playlists.py {CM_ID} --editorial --limit 20

# Past placements (historical)
python scripts/get_artist_playlists.py {CM_ID} --status past --limit 20

# All platforms
python scripts/get_artist_playlists.py {CM_ID} --platform applemusic
```

### Discography

```bash
# All albums/EPs/singles
python scripts/get_artist_albums.py {CM_ID}

# All tracks with popularity data
python scripts/get_artist_tracks.py {CM_ID}

# Deep dive on a specific track
python scripts/get_track.py {TRACK_CM_ID}
```

### What Chartmetric Data Maps to in the Report

| Chartmetric Script | Report Section |
|-------------------|----------------|
| `get_artist.py` + `get_artist_career.py` | Section 1: Artist Overview |
| `get_artist_metrics.py` (all platforms) | Section 2: Career-Stage Assessment, Section 4: KPI Dashboard |
| `get_artist_audience.py` + `get_artist_cities.py` | Section 3: Fan Personas |
| `get_artist_playlists.py` | Section 4: KPI Dashboard (playlist presence) |
| `get_similar_artists.py` | Section 5: Cultural Adjacency, Section 6: Competitive White-Space |
| `get_artist_insights.py` | Cross-reference with your own analysis |

---

## Combining Sources

The best report comes from layering every available source:

1. **Chartmetric** gives you authoritative, historical, multi-platform data you can trust
2. **Web research** gives you narrative context, cultural positioning, press coverage, and brand partnerships that APIs don't capture
3. **MCP Platform APIs** give you real-time platform data (Spotify/YouTube) if available in sandbox
4. **Social pulse** (last30days) gives you what fans are saying RIGHT NOW on Reddit and X

### Data Priority When Sources Conflict

If Chartmetric and a web article both cite Spotify monthly listeners:
- **Use Chartmetric's number** — it's pulled from the API, not a journalist's article from 3 months ago
- **Note the discrepancy** — the difference might be a growth signal worth mentioning

If web research mentions something Chartmetric doesn't cover (brand deals, press narrative, cultural context):
- **Include it as `[estimated]`** — web research is the only source for qualitative insights

### When You Have No Data Sources Beyond WebSearch

The report is still valuable. Web research surfaces most of what you need:
- Chartmetric's public artist pages are indexed and appear in search results
- Press articles quote streaming numbers (mark as `[estimated]` and note the article date)
- Social media profiles show follower counts
- Interview quotes reveal personality, brand voice, and creative direction
- Fan forums and Reddit surface psychographic insights

The report will have more `[estimated]` and `[gap]` markers, but that's honest and useful — it tells the next person exactly where to invest in better data.
