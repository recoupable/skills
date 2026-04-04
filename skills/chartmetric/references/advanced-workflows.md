# Advanced Workflow Chains

Multi-step workflows that chain Chartmetric endpoints to unlock powerful insights. Each workflow answers a strategic question.

---

## 1. Playlist Pitching Intelligence

**Question:** "Which playlist curators should I pitch to?"

```bash
# 1. Find similar artists who are slightly bigger (good benchmarks)
python scripts/get_similar_artists.py 241089 --by-config --audience high --genre high --limit 50

# 2. For each similar artist, get their playlist placements
python scripts/get_artist_playlists.py <similar_artist_id> --editorial --indie --limit 100

# 3. Look for playlist overlap - curators who added multiple similar artists
#    These curators are most likely to add your artist

# 4. For promising playlists, get curator details
python scripts/get_playlist.py spotify <playlist_id>
python scripts/get_curator.py <curator_id>

# 5. Check if target artist was ever on these playlists
python scripts/get_artist_playlists.py 241089 --status past
```

**Output:** List of curators who already playlist similar artists but haven't added yours yet.

---

## 2. TikTok-to-Spotify Pipeline Analysis

**Question:** "Is TikTok virality translating to Spotify growth?"

```bash
# 1. Get TikTok metrics over time
python scripts/get_artist_metrics.py 3380 --source tiktok

# 2. Get Spotify metrics over time (same period)
python scripts/get_artist_metrics.py 3380 --source spotify

# 3. Get TikTok audience demographics
python scripts/get_artist_audience.py 3380 --platform tiktok

# 4. Get Spotify listener cities
python scripts/get_artist_cities.py 3380

# 5. Compare: Are TikTok audience countries matching Spotify growth cities?
# 6. Get top Instagram posts (often cross-posted from TikTok)
python scripts/get_artist_instagram_posts.py 3380
```

**Output:** Correlation between TikTok spikes and Spotify follower/listener growth. Identify if there's a geographic mismatch (TikTok viral in Brazil but Spotify listeners in US = opportunity).

---

## 3. Tour Routing Intelligence

**Question:** "Where should this artist tour next?"

```bash
# 1. Get top listener cities
python scripts/get_artist_cities.py 3380

# 2. Get festivals in those regions
python scripts/list_festivals.py
# Filter by country/region from cities

# 3. For each city, find which similar artists are touring there
python scripts/get_similar_artists.py 3380 --by-config --audience high --limit 20
# Check their venues/events (if available)

# 4. Get YouTube audience by region
python scripts/get_artist_audience.py 3380 --platform youtube

# 5. Compare playlist reach by country
python scripts/get_artist_playlists.py 3380 --sort followers
# Group by playlist country code
```

**Output:** Ranked list of cities by streaming engagement, cross-referenced with festival opportunities and market coverage.

---

## 4. A&R Discovery Workflow

**Question:** "Find emerging artists in [genre] before they blow up"

```bash
# 1. Start with a breakout artist in the genre as anchor
python scripts/search_artist.py "Ice Spice"
# ID: 10574889

# 2. Find artists similar by musicality (not audience - we want undiscovered)
python scripts/get_similar_artists.py 10574889 --by-config --musicality high --genre high --limit 50

# 3. Filter response by career_stage: "undiscovered" or "developing"
# 4. For promising candidates, check their trajectory
python scripts/get_artist_metrics.py <candidate_id> --source spotify
python scripts/get_artist_metrics.py <candidate_id> --source tiktok

# 5. Check playlist traction (editorial = label interest)
python scripts/get_artist_playlists.py <candidate_id> --editorial

# 6. Get their insights for AI-generated summary
python scripts/get_artist_insights.py <candidate_id>
```

**Output:** List of emerging artists with similar sound but smaller audience, sorted by growth velocity.

---

## 5. Catalog Optimization

**Question:** "Which songs should we push and where?"

```bash
# 1. Get all artist tracks
python scripts/get_artist_tracks.py 3380

# 2. For each track, check playlist placements
python scripts/get_artist_playlists.py 3380
# Filter by track name to see which songs are playlisted

# 3. Check which tracks are performing on TikTok
# (from artist top tracks TikTok endpoint)
curl -s "https://api.chartmetric.com/api/artist/3380/top-tracks/tiktok" \
  -H "Authorization: Bearer $TOKEN"

# 4. Get album performance comparison
python scripts/get_artist_albums.py 3380
# Compare album release dates to metric spikes

# 5. Identify underperforming gems:
#    - High playlist reach but low streams = discovery issue
#    - Low playlist but high TikTok = pitch opportunity
#    - Old songs suddenly playlisted = catalog momentum
```

**Output:** Track-by-track analysis showing which songs to push on which platforms.

---

## 6. Competitive Roster Analysis

**Question:** "How does our roster compare to competitor label?"

```bash
# For each artist on your roster:
# 1. Get their profile and current metrics
python scripts/get_artist.py <artist_id>
python scripts/get_artist_metrics.py <artist_id> --source spotify

# 2. Find their similar artists (potential competitor roster)
python scripts/get_similar_artists.py <artist_id> --by-config --audience high --genre high

# 3. Compare playlist reach
python scripts/get_artist_playlists.py <artist_id> --sort followers
python scripts/get_artist_playlists.py <competitor_artist_id> --sort followers

# 4. Compare audience demographics
python scripts/get_artist_audience.py <artist_id> --platform instagram
python scripts/get_artist_audience.py <competitor_artist_id> --platform instagram

# 5. Compare where fans listen
python scripts/get_artist_cities.py <artist_id>
python scripts/get_artist_cities.py <competitor_artist_id>
```

**Output:** Side-by-side comparison of roster performance, identifying gaps and opportunities.

---

## 7. Viral Song Autopsy

**Question:** "Why did this song go viral? Can we replicate it?"

```bash
# 1. Get track details
python scripts/get_track_by_spotify.py "https://open.spotify.com/track/..."
python scripts/get_track.py <track_cm_id>

# 2. Get the artist's metrics around release date
python scripts/get_artist_metrics.py <artist_id> --source spotify
python scripts/get_artist_metrics.py <artist_id> --source tiktok

# 3. Check playlist placements timeline
python scripts/get_artist_playlists.py <artist_id> --since 2025-01-01 --sort added_at

# 4. Get artist insights (may mention the viral moment)
python scripts/get_artist_insights.py <artist_id>

# 5. Find which playlists were most impactful
python scripts/get_artist_playlists.py <artist_id> --editorial --sort followers

# 6. Check if similar artists had similar trajectory
python scripts/get_similar_artists.py <artist_id> --by-config --musicality high
```

**Output:** Timeline of the viral moment: What platform first, which playlists amplified, audience demographics that drove sharing.

---

## 8. Market Expansion Scouting

**Question:** "Which new markets should we focus on?"

```bash
# 1. Current listener geography
python scripts/get_artist_cities.py 3380

# 2. Platform-specific audience breakdown
python scripts/get_artist_audience.py 3380 --platform instagram
python scripts/get_artist_audience.py 3380 --platform youtube
python scripts/get_artist_audience.py 3380 --platform tiktok

# 3. Find similar artists and their top cities
python scripts/get_similar_artists.py 3380 --by-config --genre high --limit 10
# For each:
python scripts/get_artist_cities.py <similar_id>

# 4. Look for cities where similar artists thrive but target artist is weak
#    These are expansion opportunities

# 5. Check playlist coverage in target markets
python scripts/get_artist_playlists.py 3380
# Filter by playlist country codes
```

**Output:** Ranked list of underserved markets where similar artists succeed.

---

## 9. Collaboration Finder

**Question:** "Which artists should we collaborate with?"

```bash
# 1. Get similar artists by audience (shared fanbase)
python scripts/get_similar_artists.py 3380 --by-config --audience high --limit 30

# 2. Filter by career stage (slightly bigger = good collab target)
#    Look for "mid-level" or "mainstream" in response

# 3. Check genre overlap
python scripts/get_similar_artists.py 3380 --by-config --genre high --musicality high

# 4. Find overlap in playlist placements
python scripts/get_artist_playlists.py 3380 --editorial
python scripts/get_artist_playlists.py <potential_collab_id> --editorial
# Same playlists = easy collab pitch

# 5. Check geographic overlap
python scripts/get_artist_cities.py 3380
python scripts/get_artist_cities.py <potential_collab_id>
```

**Output:** Ranked collaboration targets by audience overlap, career stage, and playlist synergy.

---

## 10. Release Strategy Timing

**Question:** "When should we release, and how should we roll it out?"

```bash
# 1. Analyze past releases
python scripts/get_artist_albums.py 3380
python scripts/get_artist_career.py 3380

# 2. Check what worked - playlist adds after releases
python scripts/get_artist_playlists.py 3380 --status past --since 2024-01-01

# 3. Look at similar artists' successful releases
python scripts/get_similar_artists.py 3380 --by-config --audience high --limit 10
python scripts/get_artist_albums.py <similar_id>
python scripts/get_artist_career.py <similar_id>

# 4. Check current playlist momentum
python scripts/get_artist_playlists.py 3380 --editorial --newMusicFriday

# 5. Identify which platforms are hottest right now
python scripts/get_artist_metrics.py 3380 --source spotify
python scripts/get_artist_metrics.py 3380 --source tiktok
python scripts/get_artist_metrics.py 3380 --source youtube_channel
```

**Output:** Release timing recommendation based on historical patterns, playlist cycles, and platform momentum.

---

## Workflow Tips

1. **Cache tokens** - Multiple calls need valid auth
2. **Rate limit awareness** - Add 1s delay between calls if running many
3. **Save intermediate results** - Pipe to files for analysis: `python scripts/... > results.json`
4. **Cross-reference IDs** - Always use Chartmetric IDs, not Spotify IDs for API calls
5. **Compare timeframes** - Most insights come from comparing metrics over time

---

## Building Your Own Workflows

The power is in combining:

| Data Type | Endpoint | Use For |
|-----------|----------|---------|
| Who | `similar-artists`, `relatedartists` | Finding benchmarks, competitors, collaborators |
| Where | `cities`, `audience` | Geographic strategy, tour routing |
| What | `playlists`, `tracks`, `albums` | Content strategy, playlist pitching |
| When | `metrics`, `career` | Timing, trajectory analysis |
| Why | `insights` | AI-generated context |
