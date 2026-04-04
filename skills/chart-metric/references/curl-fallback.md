# Chartmetric API - Curl Fallback

Use these patterns when Python is unavailable. Requires `curl` (universal) and optionally `jq` (for pretty output).

---

## Token Management

### Get Token (with jq)

```bash
export CHARTMETRIC_TOKEN=$(curl -s -X POST "https://api.chartmetric.com/api/token" \
  -H "Content-Type: application/json" \
  -d "{\"refreshtoken\":\"$CHARTMETRIC_REFRESH_TOKEN\"}" | jq -r '.token')
```

### Get Token (without jq)

```bash
export CHARTMETRIC_TOKEN=$(curl -s -X POST "https://api.chartmetric.com/api/token" \
  -H "Content-Type: application/json" \
  -d "{\"refreshtoken\":\"$CHARTMETRIC_REFRESH_TOKEN\"}" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
```

### Token Caching (optional)

```bash
# Cache token to file (expires in ~1 hour)
TOKEN_FILE="/tmp/chartmetric_token"

get_token() {
  if [ -f "$TOKEN_FILE" ] && [ $(($(date +%s) - $(stat -f %m "$TOKEN_FILE" 2>/dev/null || stat -c %Y "$TOKEN_FILE"))) -lt 3500 ]; then
    cat "$TOKEN_FILE"
  else
    TOKEN=$(curl -s -X POST "https://api.chartmetric.com/api/token" \
      -H "Content-Type: application/json" \
      -d "{\"refreshtoken\":\"$CHARTMETRIC_REFRESH_TOKEN\"}" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    echo "$TOKEN" > "$TOKEN_FILE"
    echo "$TOKEN"
  fi
}

export CHARTMETRIC_TOKEN=$(get_token)
```

---

## Search

### Search Artists

```bash
curl -s "https://api.chartmetric.com/api/search?q=Drake&type=artists&limit=5" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Search Tracks

```bash
curl -s "https://api.chartmetric.com/api/search?q=One%20Dance&type=tracks&limit=5" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Search Albums

```bash
curl -s "https://api.chartmetric.com/api/search?q=Views&type=albums&limit=5" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

---

## Artist Endpoints

### Get Artist Profile

```bash
curl -s "https://api.chartmetric.com/api/artist/3380" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Lookup Artist by Spotify ID

```bash
# Extract ID from URL if needed: https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4
SPOTIFY_ID="3TVXtAsR1Inumwj472S9r4"
curl -s "https://api.chartmetric.com/api/artist/spotify/$SPOTIFY_ID/get-ids" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Get Artist Metrics

```bash
# Valid sources: spotify, instagram, tiktok, twitter, facebook, youtube_channel,
#                youtube_artist, soundcloud, deezer, twitch, line, melon, wikipedia, bandsintown
# ⚠️ Use youtube_channel or youtube_artist, NOT youtube

curl -s "https://api.chartmetric.com/api/artist/3380/stat/spotify" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"

curl -s "https://api.chartmetric.com/api/artist/3380/stat/youtube_channel" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Get Where People Listen (Cities)

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/where-people-listen" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Get Artist URLs

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/urls" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Get Artist Albums

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/albums" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Get Artist Tracks

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/tracks" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Get Artist Insights

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/noteworthy-insights" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Get Artist Career

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/career" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

---

## Playlist Placements

### Current Playlists

```bash
# Platforms: spotify, applemusic, deezer, amazon, youtube
# Status: current, past

curl -s "https://api.chartmetric.com/api/artist/3380/spotify/current/playlists?limit=50" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### With Filters (Spotify)

```bash
# Filters: editorial, personalized, chart, thisIs, newMusicFriday, radio, indie, majorCurator, popularIndie, brand

curl -s "https://api.chartmetric.com/api/artist/3380/spotify/current/playlists?editorial=true&newMusicFriday=true&limit=50" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### With Date Range and Sorting

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/spotify/current/playlists?since=2025-01-01&sortColumn=followers&limit=100" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Past Playlists

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/spotify/past/playlists?limit=50" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

---

## Similar/Related Artists

### Basic Related Artists

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/relatedartists?limit=10" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Advanced Similar Artists (by Configuration)

```bash
# Config options: audience, mood, genre, musicality (values: high, medium, low)
# At least one config required

curl -s "https://api.chartmetric.com/api/artist/3380/similar-artists/by-configurations?audience=high&genre=high&limit=10" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

---

## Audience Demographics

### Instagram Audience

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/instagram-audience-stats" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### TikTok Audience

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/tiktok-audience-stats" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### YouTube Audience

```bash
curl -s "https://api.chartmetric.com/api/artist/3380/youtube-audience-stats" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Instagram Top Posts

```bash
curl -s "https://api.chartmetric.com/api/SNS/deepSocial/cm_artist/3380/instagram" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

---

## Track Endpoints

### Get Track

```bash
curl -s "https://api.chartmetric.com/api/track/128613854" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Lookup Track by Spotify ID

```bash
SPOTIFY_ID="0VjIjW4GlUZAMYd2vXMi3b"
curl -s "https://api.chartmetric.com/api/track/spotify/$SPOTIFY_ID/get-ids" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

---

## Playlist & Curator

### Get Playlist

```bash
# Platforms: spotify, apple, deezer, amazon
curl -s "https://api.chartmetric.com/api/playlist/spotify/37i9dQZF1DXcBWIGoYBM5M" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### Get Curator

```bash
# ⚠️ Must use numeric Chartmetric curator ID, not name
curl -s "https://api.chartmetric.com/api/curator/spotify/1" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

---

## Discovery

### List Genres

```bash
curl -s "https://api.chartmetric.com/api/genres" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

### List Festivals

```bash
curl -s "https://api.chartmetric.com/api/festival/list" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN"
```

---

## Pretty Output (with jq)

If `jq` is available, pipe output for readability:

```bash
curl -s "https://api.chartmetric.com/api/artist/3380" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN" | jq .

# Extract specific fields
curl -s "https://api.chartmetric.com/api/search?q=Drake&type=artists" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN" | jq '.obj.artists[] | {name, id, spotify_id}'
```

---

## Error Handling

Check response status:

```bash
response=$(curl -s -w "\n%{http_code}" "https://api.chartmetric.com/api/artist/3380" \
  -H "Authorization: Bearer $CHARTMETRIC_TOKEN")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" != "200" ]; then
  echo "Error: HTTP $http_code"
  echo "$body"
else
  echo "$body"
fi
```

---

## Common Errors

| HTTP Code | Cause | Fix |
|-----------|-------|-----|
| 401 | Token expired or invalid | Re-run token command |
| 402 | Subscription issue | Check Chartmetric account |
| 404 | Invalid ID | Verify Chartmetric ID (not Spotify ID) |
| 429 | Rate limited | Wait 60 seconds |
