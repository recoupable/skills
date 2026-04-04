# Research Workflow Chains

Multi-step workflows that chain `recoup research` commands to answer strategic questions. Each workflow tells you what to run, in what order, and what to look for in the results.

---

## 1. Playlist Pitching Intelligence

**Question:** "Which playlist curators should I pitch to?"

```bash
# 1. Find similar artists who are slightly bigger (good benchmarks)
recoup research similar "{ARTIST}" --audience high --genre high --limit 50 --json

# 2. For each similar artist, get their editorial playlist placements
recoup research playlists "{similar_artist}" --editorial --json

# 3. Look for playlist overlap — curators who added multiple similar artists
#    These curators are most likely to add your artist

# 4. For promising playlists, get curator details
recoup research playlist spotify {playlist_id} --json
recoup research curator spotify {curator_id} --json

# 5. Check if target artist was ever on these playlists before
recoup research playlists "{ARTIST}" --status past --json
```

**What to synthesize:** List of curators who already playlist similar artists but haven't added yours yet. Prioritize curators who've added 2+ similar artists — they're the warmest targets.

---

## 2. TikTok-to-Spotify Pipeline Analysis

**Question:** "Is TikTok virality translating to Spotify growth?"

```bash
# 1. Get TikTok metrics over time
recoup research metrics "{ARTIST}" --source tiktok --json

# 2. Get Spotify metrics over same period
recoup research metrics "{ARTIST}" --source spotify --json

# 3. Get TikTok audience demographics
recoup research audience "{ARTIST}" --platform tiktok --json

# 4. Get Spotify listener cities
recoup research cities "{ARTIST}" --json

# 5. Get top Instagram posts (often cross-posted from TikTok)
recoup research instagram-posts "{ARTIST}" --json
```

**What to synthesize:** Correlation between TikTok follower spikes and Spotify listener growth. Geographic mismatch = opportunity (e.g., TikTok viral in Brazil but Spotify listeners mostly in US means Brazil is an untapped market).

---

## 3. Tour Routing Intelligence

**Question:** "Where should this artist tour next?"

```bash
# 1. Get top listener cities
recoup research cities "{ARTIST}" --json

# 2. Get festivals
recoup research festivals --json

# 3. Find similar artists and their cities (for co-headlining opportunities)
recoup research similar "{ARTIST}" --audience high --limit 20 --json

# 4. Get audience breakdown by platform and region
recoup research audience "{ARTIST}" --platform youtube --json
recoup research audience "{ARTIST}" --platform instagram --json

# 5. Check playlist reach by geography
recoup research playlists "{ARTIST}" --sort followers --json
```

**What to synthesize:** Ranked cities by streaming engagement, cross-referenced with festival opportunities. Cities where similar artists tour successfully but this artist hasn't been = expansion opportunities.

---

## 4. A&R Discovery

**Question:** "Find emerging artists in [genre] before they blow up"

```bash
# 1. Start with a breakout artist in the genre as anchor
recoup research "{ANCHOR_ARTIST}" --json

# 2. Find artists similar by musicality (not audience — we want undiscovered)
recoup research similar "{ANCHOR_ARTIST}" --musicality high --genre high --limit 50 --json

# 3. For promising candidates, check their trajectory
recoup research metrics "{candidate}" --source spotify --json
recoup research metrics "{candidate}" --source tiktok --json

# 4. Check playlist traction (editorial placements = label interest signal)
recoup research playlists "{candidate}" --editorial --json

# 5. Get AI insights
recoup research insights "{candidate}" --json
```

**What to synthesize:** Emerging artists with similar sound but smaller audience, sorted by growth velocity. Filter for career_stage "undiscovered" or "developing" in the similar artists response.

---

## 5. Catalog Optimization

**Question:** "Which songs should we push and where?"

```bash
# 1. Get all tracks
recoup research tracks "{ARTIST}" --json

# 2. Get playlist placements (which songs are playlisted?)
recoup research playlists "{ARTIST}" --json

# 3. Get albums with release dates
recoup research albums "{ARTIST}" --json

# 4. Get metrics to compare against release dates
recoup research metrics "{ARTIST}" --source spotify --json
recoup research metrics "{ARTIST}" --source tiktok --json
```

**What to synthesize:** Track-by-track analysis. Look for:
- High playlist reach but low streams = discovery issue (content isn't converting)
- Low playlist but high TikTok = pitch opportunity (organic momentum, needs editorial support)
- Old songs suddenly getting playlisted = catalog momentum (amplify it)

---

## 6. Competitive Roster Analysis

**Question:** "How does our roster compare to a competitor label?"

```bash
# For each artist on your roster:

# 1. Get profile and metrics
recoup research profile "{your_artist}" --json
recoup research metrics "{your_artist}" --source spotify --json

# 2. Find similar artists (potential competitor roster)
recoup research similar "{your_artist}" --audience high --genre high --json

# 3. Compare playlist reach
recoup research playlists "{your_artist}" --sort followers --json
recoup research playlists "{competitor_artist}" --sort followers --json

# 4. Compare audience demographics
recoup research audience "{your_artist}" --json
recoup research audience "{competitor_artist}" --json

# 5. Compare where fans listen
recoup research cities "{your_artist}" --json
recoup research cities "{competitor_artist}" --json
```

**What to synthesize:** Side-by-side comparison. Identify where your roster under-indexes vs competitors on specific metrics — those are the gaps to close.

---

## 7. Viral Song Autopsy

**Question:** "Why did this song go viral? Can we replicate it?"

```bash
# 1. Get track details
recoup research track "{SONG_NAME_OR_URL}" --json

# 2. Get metrics around release date
recoup research metrics "{ARTIST}" --source spotify --json
recoup research metrics "{ARTIST}" --source tiktok --json

# 3. Check playlist placements timeline
recoup research playlists "{ARTIST}" --since 2025-01-01 --sort followers --json

# 4. Get AI insights (may mention the viral moment)
recoup research insights "{ARTIST}" --json

# 5. Check if similar artists had similar trajectory
recoup research similar "{ARTIST}" --musicality high --json
```

**What to synthesize:** Timeline of the viral moment — what platform it started on, which playlists amplified it, which audience demographics drove sharing. Compare with similar artists' trajectories to identify if the pattern is replicable.

---

## 8. Market Expansion Scouting

**Question:** "Which new markets should we focus on?"

```bash
# 1. Current listener geography
recoup research cities "{ARTIST}" --json

# 2. Platform-specific audience breakdown
recoup research audience "{ARTIST}" --json
recoup research audience "{ARTIST}" --platform tiktok --json
recoup research audience "{ARTIST}" --platform youtube --json

# 3. Find similar artists and their top cities
recoup research similar "{ARTIST}" --genre high --limit 10 --json
# For each similar artist:
recoup research cities "{similar_artist}" --json

# 4. Check playlist coverage in potential markets
recoup research playlists "{ARTIST}" --json
```

**What to synthesize:** Cities where similar artists thrive but the target artist is weak = expansion opportunities. Cross-reference with playlist coverage — markets with fans but no playlist presence need pitching.

---

## 9. Collaboration Finder

**Question:** "Which artists should we collaborate with?"

```bash
# 1. Find artists with shared fanbase
recoup research similar "{ARTIST}" --audience high --limit 30 --json

# 2. Find artists with genre/sound overlap
recoup research similar "{ARTIST}" --genre high --musicality high --json

# 3. Compare playlist placements (shared playlists = easy collab pitch)
recoup research playlists "{ARTIST}" --editorial --json
recoup research playlists "{collab_target}" --editorial --json

# 4. Compare geographic overlap (shared cities = tour collab opportunity)
recoup research cities "{ARTIST}" --json
recoup research cities "{collab_target}" --json
```

**What to synthesize:** Ranked collaboration targets by audience overlap, career stage (slightly bigger = ideal), and playlist synergy. Shared playlists + shared cities = strongest collab case.

---

## 10. Release Strategy Timing

**Question:** "When should we release, and how should we roll it out?"

```bash
# 1. Analyze past releases
recoup research albums "{ARTIST}" --json
recoup research career "{ARTIST}" --json

# 2. Check what worked — playlist adds after previous releases
recoup research playlists "{ARTIST}" --status past --since 2024-01-01 --json

# 3. Look at similar artists' successful releases
recoup research similar "{ARTIST}" --audience high --limit 10 --json
recoup research albums "{similar_artist}" --json
recoup research career "{similar_artist}" --json

# 4. Check current playlist momentum
recoup research playlists "{ARTIST}" --editorial --json

# 5. Identify which platforms are hottest right now
recoup research metrics "{ARTIST}" --source spotify --json
recoup research metrics "{ARTIST}" --source tiktok --json
recoup research metrics "{ARTIST}" --source youtube_channel --json
```

**What to synthesize:** Release timing recommendation based on historical patterns (when did past releases get the most playlist adds?), similar artists' release cycles, and which platform has the most momentum right now.

---

## Building Your Own Workflows

The power is in combining data types:

| What You Need | Command | Use For |
|---------------|---------|---------|
| **Who** — peers, competitors, collaborators | `similar` | Finding benchmarks, pitch targets, collab opportunities |
| **Where** — geographic data | `cities`, `audience` | Tour routing, market expansion, geographic strategy |
| **What** — content and catalog | `playlists`, `tracks`, `albums` | Content strategy, playlist pitching, catalog optimization |
| **When** — timing and trajectory | `metrics`, `career` | Release timing, growth analysis, trend detection |
| **Why** — context and narrative | `insights`, `web`, `report` | Cultural positioning, press strategy, brand partnerships |
