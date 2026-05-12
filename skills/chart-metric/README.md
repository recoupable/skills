# Chartmetric

A skill for AI agents to access music industry analytics via the Chartmetric API.

## Install

This skill ships in the [`recoup-skills`](https://github.com/recoupable/skills) plugin. Install via your agent's marketplace:

```bash
# Claude Code
/plugin marketplace add recoupable/skills
/plugin install recoup-skills@recoup

# Codex
codex plugin marketplace add recoupable/skills
codex plugin install recoup-skills@recoup

# Vercel skills CLI (works in 18+ agents)
npx skills add recoupable/skills --skill chart-metric
```

## What It Does

Query streaming metrics, playlist placements, audience demographics, and competitive insights for any artist, track, or album.

### Key Capabilities

- **Artist Discovery** - Filter artists by Spotify listeners, TikTok followers, geography, genre
- **Platform Metrics** - Track performance across 14 platforms (Spotify, Instagram, TikTok, YouTube, etc.)
- **Playlist Intelligence** - Current and historical playlist placements with curator data
- **Audience Demographics** - Geographic and demographic breakdowns
- **Similar Artists** - Find related artists by audience, genre, mood, or musicality
- **Catalog Analysis** - Albums, tracks, career timeline

## Quick Start

```bash
# Search for an artist
python scripts/search_artist.py "Drake"

# Get artist profile
python scripts/get_artist.py 3380

# Discover artists by metrics
python scripts/discover_artists.py --country US --spotify-listeners 100000 500000
```

## Requirements

- Chartmetric API subscription
- Python 3.8+ with `requests` package
- Set `CHARTMETRIC_REFRESH_TOKEN` environment variable

## Documentation

See [SKILL.md](SKILL.md) for complete usage documentation, all available scripts, and workflow examples.

## Curl Fallback

If Python is unavailable, see [references/curl-fallback.md](references/curl-fallback.md) for curl-only patterns.

## License

Apache-2.0
