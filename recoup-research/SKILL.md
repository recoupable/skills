---
name: recoup-research
description: Music industry research via `recoup research` CLI — streaming metrics, audience demographics, playlist placements, competitive analysis, people search, URL extraction, structured enrichment, and web intelligence. Use when the user needs artist analytics, streaming numbers, audience insights, playlist tracking, similar artists, collaboration targets, tour routing data, or any music industry research. Also use for finding people in the industry (managers, A&R), extracting data from URLs, or enriching entities with structured web research. Triggers on requests involving Spotify followers, monthly listeners, TikTok trends, Instagram audience, playlist pitching, competitive analysis, "how is [artist] doing," "research [artist]," "find me [people]," or any question about an artist's performance, market position, or industry contacts.
---

# Recoup Research

Music industry research through the `recoup research` CLI. Covers artist analytics, web intelligence, people search, URL extraction, and structured data enrichment — all through one command with `RECOUP_API_KEY` auth.

## Setup

In sandboxes, the CLI is already installed and authenticated. Otherwise:

```bash
npm install -g @recoupable/cli
export RECOUP_API_KEY=your-api-key
```

## Quick Start

```bash
recoup research "Kaash Paige" --json          # find artist
recoup research metrics "Kaash Paige" --source spotify --json  # streaming data
recoup research cities "Kaash Paige" --json    # where fans are
recoup research similar "Kaash Paige" --json   # competitors
```

Every artist-scoped command accepts an **artist name** — the API resolves it internally. Always use `--json` when chaining commands.

---

## Commands

### Artist Data

| Command | What It Returns |
|---------|----------------|
| `recoup research "Drake"` | Search results with name, ID, listeners, followers |
| `recoup research profile "Drake"` | Bio, genres, social URLs, label, career stage |
| `recoup research metrics "Drake" --source spotify` | Time-series streaming/social metrics (14 platforms) |
| `recoup research audience "Drake"` | Age, gender, country demographics (Instagram default) |
| `recoup research audience "Drake" --platform tiktok` | TikTok demographics |
| `recoup research cities "Drake"` | Top cities ranked by listener count |
| `recoup research similar "Drake"` | Peers with career stage, momentum, listener counts |
| `recoup research similar "Drake" --audience high --genre high` | Filtered by similarity dimensions |
| `recoup research urls "Drake"` | All social/streaming links |
| `recoup research instagram-posts "Drake"` | Top posts/reels by engagement |
| `recoup research playlists "Drake"` | Current playlist placements with follower counts |
| `recoup research playlists "Drake" --editorial` | Editorial playlists only |
| `recoup research albums "Drake"` | Full discography with release dates |
| `recoup research tracks "Drake"` | All tracks with popularity |
| `recoup research career "Drake"` | Career timeline and milestones |
| `recoup research insights "Drake"` | AI-generated observations and trends |

### Non-Artist Data

| Command | What It Returns |
|---------|----------------|
| `recoup research lookup "https://open.spotify.com/artist/..."` | Artist from platform URL |
| `recoup research track "God's Plan"` | Track metadata |
| `recoup research playlist spotify 1645080` | Playlist details |
| `recoup research curator spotify 1` | Curator profile |
| `recoup research discover --country US --spotify-listeners 100000,500000` | Find artists by criteria |
| `recoup research genres` | All genre IDs (use with discover) |
| `recoup research festivals` | Music festivals |

### Web Intelligence

| Command | What It Returns |
|---------|----------------|
| `recoup research web "Drake brand partnerships"` | Web search results (Perplexity) |
| `recoup research report "Tell me about Kaash Paige"` | Comprehensive cited research report |
| `recoup research people "A&R reps at Atlantic Records"` | LinkedIn profiles and summaries (Exa) |
| `recoup research extract "https://en.wikipedia.org/wiki/Drake_(musician)"` | Clean markdown from any URL (Parallel) |
| `recoup research enrich "Kaash Paige" --schema '{"properties":{"label":{"type":"string"}}}'` | Structured data with citations (Parallel) |

### Platform Metrics Sources

Valid `--source` values for the `metrics` command: `spotify`, `instagram`, `tiktok`, `twitter`, `facebook`, `youtube_channel`, `youtube_artist`, `soundcloud`, `deezer`, `twitch`, `line`, `melon`, `wikipedia`, `bandsintown`

### Gotcha

YouTube metrics use `youtube_channel` — not `youtube`.

---

## When to Use Which Command

| User asks... | Use |
|-------------|-----|
| "How's Drake doing on Spotify?" | `metrics --source spotify` |
| "Where are Drake's fans?" | `cities` + `audience` |
| "Who should I pitch to?" | `similar` → `playlists` on each peer |
| "Who manages this artist?" | `people` |
| "What does this website say?" | `extract` |
| "Give me structured data about X" | `enrich` |
| "Tell me everything about X" | `report` (deep) or chain multiple commands |
| "Find emerging artists in hip-hop" | `discover --genre <id>` |
| "Is TikTok translating to Spotify?" | `metrics --source tiktok` + `metrics --source spotify` |

---

## Workflow Chains

For strategic questions that require chaining multiple commands, read `references/workflows.md`. It covers 10 workflow chains:

| Workflow | Question |
|----------|----------|
| Playlist Pitching | Which curators should I pitch to? |
| TikTok Pipeline | Is TikTok virality translating to Spotify? |
| Tour Routing | Where should this artist tour next? |
| A&R Discovery | Find emerging artists before they blow up |
| Catalog Optimization | Which songs should we push and where? |
| Competitive Roster | How does our roster compare? |
| Viral Autopsy | Why did this song go viral? |
| Market Expansion | Which new markets to focus on? |
| Collaboration Finder | Who should we collaborate with? |
| Release Timing | When should we release? |

---

## Tips

1. **Always use `--json`** when chaining — structured output is easier to parse.
2. **Run independent commands in parallel** — metrics, audience, cities don't depend on each other.
3. **YouTube uses `youtube_channel`** not `youtube` — the most common gotcha.
4. **Cross-reference for insights** — cities + audience = geographic strategy; similar + playlists = pitch targets.
5. **The `enrich` command is powerful** — define any JSON schema and get structured data back with citations. Use for anything web research can answer.
