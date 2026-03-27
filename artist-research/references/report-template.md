# Artist Intelligence Report Template

Use this template for the `research/artist-intel-YYYY-MM-DD.md` output. Fill every section where you have real data. Leave a section out entirely if you have nothing substantive — a section with guesses is worse than no section.

## Frontmatter

```yaml
---
artist: "{Artist Name}"
date: YYYY-MM-DD
career_stage: emerging | breakout | established | legacy
sources: [list of sources used, e.g., perplexity, spotify-api, youtube-api, web, reddit, x]
confidence: high | medium | low
data_gaps: [list of things you couldn't find or verify]
---
```

The `confidence` rating reflects overall research quality:
- **high** — Chartmetric data + web research + social pulse (or MCP APIs + Perplexity)
- **medium** — Web research only, metrics are estimated from press/public pages
- **low** — Limited public information available, significant data gaps

---

## Section 1: Artist Overview

Bio snapshot, origin story, signature sound, key milestones.

Write this so someone with zero context understands who this artist is in 2-3 paragraphs. Include:
- Real name (if publicly known), age, hometown
- How they got started, when they broke through
- What their music sounds like — be specific (not just "hip-hop" but "sample-heavy boom-bap with jazz piano loops and confessional storytelling")
- Key milestones: chart positions, award nominations, notable features, viral moments, label signings
- Where they are right now — current release cycle, tour status, public narrative

---

## Section 2: Career-Stage Assessment

Identify the artist's career stage and pull the metrics that matter at that stage:

| Stage | Metrics to Pull | Why These Matter |
|-------|-----------------|------------------|
| **Emerging** (less than 3 years active, under 100K monthly listeners) | Follower growth rate (month-over-month), playlist adds per week, first tour/show sell-through percentage, save-to-listener ratio | Early momentum signals — are people discovering AND retaining? |
| **Breakout** (1-2 songs with real traction, 100K-1M monthly listeners) | Market-share gains vs. peers in same lane, international listener uptake curves, editorial playlist presence | Scaling levers — where is the growth coming from and can it be amplified? |
| **Established** (50+ tracks released, 1M+ monthly listeners, multiple release cycles) | Catalog half-life (how long tracks stay above X streams/day), royalty source diversification (streaming vs sync vs merch vs live), back-catalog performance | Long-tail levers — is the catalog appreciating or depreciating? |
| **Legacy / Revival** (5+ years since peak, catalog-driven revenue) | Re-engagement metrics on reissues or anniversary releases, sync licensing CAGR, estate or catalog management structure | Nostalgia monetization — where are the untapped cash hooks? |

After identifying the stage, write:
1. **Current stage** and why you classified them there (cite the metrics)
2. **Next-stage risks** — what could stall their progression
3. **Next-stage opportunities** — what levers can accelerate the transition

---

## Section 3: Fan-Persona Segmentation

Create 3-5 named fan archetypes. Build these from behavioral data, not just demographics. Each persona should feel like a real person you could describe to a marketing team.

For each persona:

**[Persona Name]** (e.g., "The Loop Queen," "The Vinyl Purist," "The TikTok Discoverer")

- **Who they are:** Age range, location tendency, one-sentence identity sketch
- **Motivation triggers:** Why they listen — emotional need, identity expression, social currency, nostalgia
- **Preferred platforms and content formats:** Where they spend time and what they engage with (short-form video, long-form podcasts, vinyl unboxings, live streams, lyric breakdowns)
- **Price elasticity:** Low (won't pay for anything beyond streaming), Medium (will buy merch or concert tickets if the moment is right), High (will buy limited drops, VIP, collectors editions)
- **Brand affinities outside music:** What other brands, products, subcultures, or interests overlap with this persona? Be specific — not "fashion" but "Carhartt WIP, New Balance 550, vintage Japanese denim"
- **Signal behaviors:** What do super-fans in this persona actually DO? (Save every song, share to stories, comment lyrics, attend multiple shows, buy physical formats, create fan art, participate in Discord)

---

## Section 4: Platform-Native KPI Dashboard

Provide the deep metrics most dashboards don't surface. Use real numbers when you have them. When estimating, mark with `~` and note the source.

| Platform | Metric | Value | Source | Notes |
|----------|--------|-------|--------|-------|
| **Spotify** | Monthly listeners | | | |
| | Followers | | | |
| | Save-to-listener ratio | | | Higher than 3% = strong retention |
| | Top track popularity score (0-100) | | | |
| | Active vs passive stream ratio | | | Algorithmic (passive) vs user-initiated (active) |
| | Editorial playlist count | | | |
| | Algorithmic playlist count | | | |
| **Apple Music** | Shazam count (if available) | | | Leading indicator of organic discovery |
| **TikTok** | Creator account followers | | | |
| | Sounds created using their music | | | |
| | Top-performing sound (uses) | | | |
| **YouTube** | Channel subscribers | | | |
| | Avg view count (last 10 videos) | | | |
| | Avg view duration as % of video length | | | Above 50% = strong retention |
| | Music video vs other content ratio | | | |
| **Instagram** | Followers | | | |
| | Avg engagement rate (last 10 posts) | | | |
| | Story view rate (if observable) | | | |
| **Twitter/X** | Followers | | | |
| | Avg engagement per post | | | |
| **Live** | Recent tour/show capacity and sell-through | | | |
| | Primary markets (top DMAs) | | | |
| | Ticket price range | | | |

Add any other platforms where the artist has meaningful presence.

### Key Ratios

Calculate and highlight these if you have the underlying data:
- **Save-to-Listener:** Spotify saves / monthly listeners (above 3% = strong catalog stickiness)
- **Follower-to-Listener:** Spotify followers / monthly listeners (above 20% = dedicated base)
- **Engagement-to-Follower:** Instagram engagement / followers (above 3% for under 100K followers = healthy)
- **View-to-Subscriber:** YouTube views / subscribers (above 30% = content is reaching beyond the base)

---

## Section 5: Cultural Adjacency Map

Identify micro-scenes, subcultures, and adjacent communities where this artist's fans also participate. Rank by overlap strength.

Format:
```
[Artist's primary scene] ↔ [Adjacent scene] — Overlap signal: [what connects them]
```

Examples of overlap signals:
- Playlist co-occurrence (the artist appears on playlists with X genre/scene)
- Reddit cross-posts (fans post in both r/ArtistFans and r/AdjacentScene)
- Hashtag overlap on TikTok/Instagram
- Similar artist algorithms (Spotify "Fans Also Like")
- Fashion/brand overlap between fan bases
- Festival lineup proximity (appear at same festivals)

Provide 5-8 adjacencies ranked from strongest to weakest overlap.

---

## Section 6: Competitive White-Space Snapshot

Identify the top 5 sonic peers — artists in the same lane competing for the same listeners.

| Peer Artist | Monthly Listeners | Key Metric Where They Outperform | Key Metric Where Subject Under-Indexes |
|------------|------------------|----------------------------------|----------------------------------------|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

After the table, identify the **biggest untouched white space** — the strategic opening none of the peers are exploiting. This is where the artist has the best chance to differentiate: a platform they're underweight on, a content format nobody in the lane is doing, a geographic market where the music is resonating but no one is investing in touring or localized marketing.

---

## Section 7: Hyper-Niche Revenue Opportunities

Provide 3-5 highly specific ideas. Each must reference the fan personas or cultural adjacencies from earlier sections. Generic merch or Zoom calls don't qualify.

For each opportunity:

**[Opportunity Title]**
- **What:** Specific description of the revenue play
- **Why it works for this artist:** Connect it to a fan persona or adjacency (e.g., "The Vinyl Purist persona has high price elasticity and the artist's jazz-sampling production style maps directly to the collector market")
- **Quick ROI logic:** Rough economics — unit cost, price point, addressable audience size from the fan base, expected conversion rate
- **Execution complexity:** Low / Medium / High
- **Time to revenue:** Immediate / 1-3 months / 3-6 months

---

## Section 8: Suggested Context Updates

Only include this section if `context/artist.md` or `context/audience.md` already exist. List specific pieces of new information from the research that might warrant updating the static profiles.

Format:
```
### artist.md
- [Section]: [What to update] — Source: [where this info came from]

### audience.md
- [Section]: [What to update] — Source: [where this info came from]
```

The human decides whether to apply these. Don't overwrite static files based on research alone.

---

## Data Confidence Legend

Use these markers throughout the report:

- `[confirmed]` — Data from platform APIs or official sources
- `[estimated]` — Data from web research, may be outdated or approximate
- `[inferred]` — Pattern-based conclusion, not directly observed
- `[gap]` — Data point you couldn't find — flag it so the next research pass knows what to look for
