---
name: industry-research
description: Music industry research via `recoup research` CLI — streaming metrics, audience demographics, playlist placements, competitive analysis, people search, URL extraction, structured enrichment, and web intelligence. Use when the user needs artist analytics, streaming numbers, audience insights, playlist tracking, similar artists, collaboration targets, tour routing data, or any music industry research. Also use for finding people in the industry (managers, A&R), extracting data from URLs, or enriching entities with structured web research. Triggers on requests involving Spotify followers, monthly listeners, TikTok trends, Instagram audience, playlist pitching, competitive analysis, "how is [artist] doing," "research [artist]," "find me [people]," or any question about an artist's performance, market position, or industry contacts.
---

# Recoup Research

Music industry research through the `recoup research` CLI. All commands use `RECOUP_API_KEY` for auth. In sandboxes, this is already configured.

## Before You Research

1. Check if the artist has a workspace with `context/artist.md` — don't re-research what's already known.
2. Decide what the user actually needs. "How's Drake doing?" needs 2-3 commands, not 20.
3. Always use `--json` when you'll process the output programmatically.

## Decision Tree

Start here based on what the user asks:

**"How is [artist] doing?"** → `metrics --source spotify` + `cities` + `insights`

**"Research [artist] for me"** → Full chain: `profile` → parallel(`metrics`, `audience`, `cities`, `similar`, `playlists`) → `web` for narrative context → synthesize

**"Who should I pitch to?"** → `similar --audience high --genre high` → `playlists` on each peer → find playlists that have peers but not your artist

**"Where should we tour?"** → `cities` + `audience --platform youtube` + `festivals`

**"Find me [people]"** → `people "A&R reps at [label]"`

**"Tell me about [entity]"** → `enrich "[entity]" --schema '{...}'` for structured data, or `report "[entity]"` for a narrative

**"What does this page say?"** → `extract "https://..."` 

**"Find emerging artists"** → `discover --country US --genre GENRE_ID --spotify-listeners 50000,200000` (get IDs from `recoup research genres`)

If none of these match, start with `web "query"` for general research.

---

## Commands Quick Reference

### Artist Data (accept artist name, API resolves internally)

```bash
recoup research "Drake" --json                    # search — returns { results: [{ name, id, sp_monthly_listeners, sp_followers }] }
recoup research profile "Drake" --json            # full profile — { name, genres, country_code, cm_artist_score, ... }
recoup research metrics "Drake" --source spotify --json  # time-series — { followers: [...], listeners: [...], popularity: [...] }
recoup research audience "Drake" --json           # demographics — { audience_genders: [...], audience_genders_per_age: [...], top_countries: [...] }
recoup research cities "Drake" --json             # geography — { cities: [{ name, country, listeners }] }
recoup research similar "Drake" --json            # competitors — { artists: [{ name, career_stage, recent_momentum, sp_monthly_listeners }] }
recoup research playlists "Drake" --json          # placements — { placements: [{ playlist: { name, followers }, track: { name } }] }
recoup research albums "Drake" --json             # discography — { albums: [{ name, release_date }] }
recoup research tracks "Drake" --json             # tracks — { tracks: [{ name, id }] }
recoup research career "Drake" --json             # timeline — career milestones array
recoup research insights "Drake" --json           # AI observations — { insights: [{ insight: "text" }] }
recoup research urls "Drake" --json               # social links — { urls: [{ domain, url }] }
recoup research instagram-posts "Drake" --json    # top posts/reels
```

### Non-Artist Data

```bash
recoup research lookup "https://open.spotify.com/artist/..." --json
recoup research track "God's Plan" --json
recoup research playlist spotify 1645080 --json
recoup research curator spotify 1 --json
recoup research discover --country US --spotify-listeners 100000,500000 --json
recoup research genres --json
recoup research festivals --json
```

### Web Intelligence

```bash
recoup research web "Drake brand partnerships" --json              # web search — { results: [{ title, url, snippet }] }
recoup research report "Tell me about Drake" --json          # deep research — { content: "markdown report", citations: [...] }
recoup research people "A&R reps at Atlantic Records" --json       # people search — { results: [{ title, url, summary }] }
recoup research extract "https://example.com" --json               # URL scraping — { results: [{ title, url, excerpts: [...] }] }
recoup research enrich "Drake" --schema '{"properties":{"label":{"type":"string"}}}' --json  # structured — { output: { label: "OVO Sound" } }
```

### Platform Sources (for `metrics` command)

`spotify`, `instagram`, `tiktok`, `twitter`, `facebook`, `youtube_channel`, `youtube_artist`, `soundcloud`, `deezer`, `twitch`, `line`, `melon`, `wikipedia`, `bandsintown`

For **`metrics` only**, YouTube uses `youtube_channel` (not plain `youtube`). The **`audience`** command is different: Chartmetric’s path is `youtube-audience-stats`, so there you pass `--platform youtube` (see examples above). Do not use `youtube_channel` for `audience`.

---

## Interpreting the Data

Raw numbers are noise without interpretation. Here's what to look for:

**Metrics:**
- Follower-to-listener ratio above 20% = dedicated fan base (they follow, not just stream)
- Save-to-listener ratio above 3% = strong catalog stickiness
- Week-over-week listener growth above 5% = momentum
- Popularity score trending up = algorithmic favor

**Cities:**
- If top cities are international but playlists are US-only = untapped international opportunity
- If a city has high listeners but the artist has never toured there = tour opportunity
- Compare with similar artists' cities to find geographic white space

**Similar Artists:**
- `career_stage`: undiscovered → developing → mid-level → mainstream → superstar → legendary
- `recent_momentum`: decline → gradual decline → steady → growth → explosive growth
- If the artist's peers are all "mainstream" but they're "mid-level" = breakout potential
- Peers with playlists you're NOT on = pitch targets

**Playlists:**
- 2 editorial playlists for 5M+ listeners = severely under-playlisted (pitch immediately)
- Follower count on playlists tells you reach potential
- Past placements (`--status past`) that dropped off = re-pitch opportunities

**Audience:**
- Gender skew tells you content strategy (visual style, messaging)
- Age concentration tells you platform priority (Gen Z = TikTok, 25-34 = Instagram)
- Country mismatch between audience and cities = content localization opportunity

---

## Synthesis Patterns

Don't dump raw data. Combine endpoints and draw conclusions:

**Geographic Strategy:** `cities` + `audience` → "Sao Paulo is #1 (135K listeners) but audience is 80% US on Instagram. There's a massive Brazilian fan base that isn't being served with localized content."

**Playlist Gap Analysis:** `similar` → `playlists` on each peer → "5 of your 10 peers are on 'R&B Rotation' (450K followers) but you're not. That's your top pitch target."

**Platform Pipeline:** `metrics --source tiktok` + `metrics --source spotify` → "TikTok followers grew 40% last month but Spotify listeners are flat. The TikTok virality isn't converting. Need Spotify-specific CTAs on TikTok content."

**Career Positioning:** `similar` → compare career stages → "You're the only 'mainstream' artist in your peer group — everyone else is 'mid-level'. You have positioning leverage for brand deals and festival slots."

---

## Saving Research

If working in an artist workspace, save research results to `research/` with timestamps:

```
research/artist-intel-2026-03-27.md
```

Don't overwrite `context/artist.md` with research data. Static context (who the artist IS) is separate from dynamic research (how they're performing NOW). If the research reveals something that should update the static profile, suggest it to the user — don't auto-update.

---

## What Not to Do

- **Don't run 20 commands when 3 will answer the question.** Start small, expand if needed.
- **Don't dump raw JSON to the user.** Interpret the data and draw conclusions.
- **Don't re-research what `context/artist.md` already covers.** Read it first.
- **Don't ignore the `--json` flag when chaining.** Tables are for humans, JSON is for you.
- **Don't assume Chartmetric has every artist.** If search returns no results, fall back to `web` or `report`.

---

## Graceful Degradation

If `recoup research "Artist Name"` returns no results:
1. Try `recoup research web "Artist Name musician"` for web-based research
2. Try `recoup research enrich "Artist Name" --schema '{...}'` for structured extraction
3. For very emerging artists, Chartmetric may not have data yet — web research is the fallback

## More Workflows

Read `references/workflows.md` for 10 complete multi-step workflow chains covering playlist pitching, competitive analysis, tour routing, A&R discovery, and more.
