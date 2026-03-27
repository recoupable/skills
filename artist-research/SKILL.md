---
name: artist-research
description: Deep research on a music artist — bio, metrics, fan personas, competitive positioning, and revenue opportunities. Use when setting up a new artist, building an artist knowledge base, researching an artist for the first time, or when the user says "research [artist name]," "deep dive on [artist]," "who is [artist]," "analyze [artist]," or "build a profile for [artist]." Also use when onboarding an artist to the platform and you need comprehensive context before strategizing. This is the go-to skill for any artist intelligence gathering — not just a bio, but the full picture a music manager needs to make decisions.
---

# Research Artist

Deep research on a music artist. Produces a comprehensive intelligence report that any agent can use as a knowledge base when strategizing about campaigns, fan growth, partnerships, and content.

You are a music manager working with the artist. Your role is to oversee releases, grow the audience, and unlock revenue. Research with that lens — surface what's actionable, not what's obvious.

## Before You Start

1. Read the artist's `RECOUP.md` to get their name, slug, and ID (if in a workspace).
2. Read `context/artist.md` if it exists — understand what's already known before researching.
3. Determine your environment — this affects which research tools you use.

## Research Pipeline

The skill runs a multi-source pipeline. Every source is optional — the skill works with just WebSearch alone but gets richer with each additional source. Before starting, detect what's available and use the best combination.

### Detect Available Sources

Check for each of these before starting. Use whatever you find — don't block if something is missing.

| Source | How to Check | What It Gives You |
|--------|-------------|-------------------|
| **WebSearch** | Always available | Bio, narrative, cultural context, press coverage, estimated metrics |
| **Chartmetric** | Check for `CHARTMETRIC_REFRESH_TOKEN` env var and `skills/chartmetric/scripts/` | Real streaming metrics across 14 platforms, audience demographics, city-level data, playlist placements, similar artists, career timeline |
| **last30days** | Check for `~/.claude/skills/last30days/scripts/last30days.py` or `.cursor/skills/last30days/scripts/last30days.py` | Reddit and X fan conversations, sentiment, community buzz |
| **MCP tools** | Check if `web_deep_research`, `spotify_search`, `youtube_channels` etc. are available | Perplexity deep research, Spotify/YouTube API data, platform social data |

### Phase 1: Web Research (Always Runs)

This is the backbone. It fills in the narrative that numbers alone can't tell — origin story, cultural context, brand identity, industry positioning.

**If `web_deep_research` MCP tool is available:**
Send a single comprehensive research prompt. Read `references/research-queries.md` for the exact message. Perplexity deep research browses extensively and returns cited results.

**Otherwise, use WebSearch:**
Run 8-12 targeted searches covering bio, metrics, fans, competition, business, and cultural context. Read `references/research-queries.md` for the full query list. Run searches in parallel when possible.

WebSearch alone produces a solid report. The phases below add verified data on top.

### Phase 2: Chartmetric Data (If Available)

Chartmetric is the richest data source for music analytics. If the `CHARTMETRIC_REFRESH_TOKEN` is configured and the chartmetric skill scripts exist, run this sequence:

```bash
# 1. Find the artist's Chartmetric ID
python scripts/search_artist.py "{ARTIST_NAME}"

# 2. Pull core profile and career data
python scripts/get_artist.py {CM_ID}
python scripts/get_artist_career.py {CM_ID}
python scripts/get_artist_insights.py {CM_ID}

# 3. Streaming metrics (the KPI Dashboard section)
python scripts/get_artist_metrics.py {CM_ID} --source spotify
python scripts/get_artist_metrics.py {CM_ID} --source instagram
python scripts/get_artist_metrics.py {CM_ID} --source tiktok
python scripts/get_artist_metrics.py {CM_ID} --source youtube_channel

# 4. Audience and geography (the Fan Persona section)
python scripts/get_artist_audience.py {CM_ID}
python scripts/get_artist_audience.py {CM_ID} --platform tiktok
python scripts/get_artist_cities.py {CM_ID}

# 5. Competitive landscape (the White-Space section)
python scripts/get_similar_artists.py {CM_ID} --by-config --audience high --genre high --limit 10

# 6. Playlist presence
python scripts/get_artist_playlists.py {CM_ID} --editorial --limit 20

# 7. Complete discography and tracks
python scripts/get_artist_albums.py {CM_ID}
python scripts/get_artist_tracks.py {CM_ID}
```

Run these from the chartmetric skill directory. Mark all data from Chartmetric as `[confirmed]` — these are authoritative numbers, not estimates.

When Chartmetric data contradicts web research, trust Chartmetric and note the discrepancy. The web number is probably stale.

**If Chartmetric is NOT available:** The report still works. Web research can surface most metrics through press articles, public Chartmetric pages, and social posts. Just mark those numbers as `[estimated]` instead of `[confirmed]`.

### Phase 3: Social Pulse (last30days — If Available)

If the last30days skill is installed, run it for the artist name:

```bash
python3 <path>/last30days.py "{ARTIST_NAME} music" --emit=compact
```

What you're looking for:
- Fan conversations and sentiment
- Press coverage reactions
- Community-driven opinions
- Recent momentum or controversy

This data feeds into Fan Persona Segmentation and Cultural Adjacency Map. If last30days is not available, note it as a data gap. Don't block on this.

### Phase 4: MCP Platform Data (Sandbox Only — If Available)

If MCP tools are connected (sandbox environment), supplement with:

1. **`web_deep_research`** — Deep Perplexity research (if not already used in Phase 1)
2. **`spotify_search`** / **`spotify_artist_top_tracks`** / **`spotify_artist_albums`** — Real-time Spotify data
3. **`youtube_channels`** / **`youtube_channel_video_list`** — YouTube metrics
4. **`artist_deep_research`** — Connected social accounts from the platform

If you already have Chartmetric data for the same metrics, use Chartmetric as the primary source and note if MCP data differs. Both are authoritative but Chartmetric usually has deeper historical data.

### Phase 5: Synthesis

After all available phases complete, synthesize into the report. Read `references/report-template.md` for the full output template. Note which sources you used in the report's YAML frontmatter so future agents know the data quality.

## Output Architecture

The research produces two types of output. This distinction matters because agents reading the workspace need to know whether something is a durable fact or a time-bound snapshot.

### Dynamic Output (The Report)

Save the full research report as:

```
research/artist-intel-YYYY-MM-DD.md
```

This is a point-in-time document. It contains metrics, trends, fan personas, competitive analysis, and revenue opportunities. These change. The report should be timestamped and eventually archived when it goes stale.

If a `research/` directory doesn't exist, create it.

### Static Context Updates

After generating the report, check what static context files exist:

**If `context/artist.md` does NOT exist:**
Create it using the artist-workspace template format (read `references/artist-template.md` from the artist-workspace skill). Populate it with the identity, brand, and voice information extracted from the research. Only include sections where you have real data.

**If `context/artist.md` DOES exist:**
Do NOT overwrite it. Instead, at the end of the research report, add a "Suggested Context Updates" section that flags any new information that might warrant updating the static profile. The human decides whether to apply those updates.

**If `context/audience.md` does NOT exist and you have fan data:**
Create it using the audience template from the artist-workspace skill. Populate with the fan persona data from the research.

**If `context/audience.md` DOES exist:**
Same as artist.md — suggest updates, don't overwrite.

### Knowledge Base (Sandbox Only)

If the `create_knowledge_base` MCP tool is available and the artist has an account ID, save the research report to the artist's permanent knowledge base. This makes it accessible to the AI in future conversations.

## Quality Rules

1. **No obvious advice.** "Post TikToks" and "run pre-saves" are noise. Every recommendation should be specific to THIS artist's data.
2. **Explain who they are.** A reader with zero context should understand the artist after reading the overview.
3. **Deep metrics over vanity metrics.** Save-to-listener ratios matter more than raw follower counts. Engagement rate matters more than total followers.
4. **Surface unique fan insights.** Psychographics, subculture overlaps, and super-fan behaviors — not just "18-24 year olds."
5. **Cite sources.** Every metric and claim should reference where it came from so future agents can verify.
6. **Flag confidence levels.** Mark data points as `[confirmed]` (from Chartmetric, platform APIs, or official sources), `[estimated]` (from web research — numbers may be outdated), or `[inferred]` (pattern-based conclusions). This helps downstream agents know what to trust.
7. **No NFTs, crypto, or web3** unless the artist has explicitly expressed interest OR their fan base demonstrably aligns. Don't suggest these by default.

## Report Structure

Read `references/report-template.md` for the complete output template. The sections are:

1. **Artist Overview** — Bio, origin, sound, milestones
2. **Career-Stage Assessment** — Where they are and what metrics matter at this stage
3. **Fan-Persona Segmentation** — 3-5 named behavioral archetypes
4. **Platform-Native KPI Dashboard** — Deep metrics most dashboards hide
5. **Cultural Adjacency Map** — Adjacent micro-scenes and overlap signals
6. **Competitive White-Space Snapshot** — Top 5 sonic peers and where this artist under-indexes
7. **Hyper-Niche Revenue Opportunities** — 3-5 specific ideas with ROI logic
8. **Suggested Context Updates** — What should be added to static artist/audience files (if they already exist)

## Working With the Artist Workspace

This skill respects the artist-workspace skill's conventions:

- **Static context** (`artist.md`, `audience.md`) only gets created, never blindly overwritten
- **Dynamic context** (the research report) goes in `research/` with a date stamp
- **Data lives in one place** — the report references the artist.md by path, it doesn't duplicate identity info
- **Git commits** follow the pattern: `research: deep dive on {artist-name} — initial intel report`

## After Research

Once the report is generated, tell the user what you found. Highlight:
- The career stage and what it means for strategy
- The 2-3 most actionable insights
- Any data gaps that need filling (e.g., no Chartmetric data, thin social pulse)
- Whether you created or updated any static context files

Then ask what they want to do with the research — campaign planning, content strategy, partnership outreach, or something else. The report is designed to feed into any of these downstream workflows.
