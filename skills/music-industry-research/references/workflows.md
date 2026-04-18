# Research workflows, interpretation, and synthesis

Multi-step workflows that chain `/api/research/*` endpoints to answer strategic questions, plus the interpretation rules of thumb and cross-cutting synthesis patterns to apply once you have the data.

All examples assume:

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://recoup-api.vercel.app/api"
AUTH="x-api-key: $RECOUP_API_KEY"
```

---

## Interpretation cheat sheet

Raw numbers are noise without interpretation. Heuristics for each data type:

**Metrics:**

- Follower-to-listener ratio above 20% = dedicated fan base (they follow, not just stream)
- Save-to-listener ratio above 3% = strong catalog stickiness
- Week-over-week listener growth above 5% = momentum
- Popularity score trending up = algorithmic favor

**Cities:**

- Top cities international but playlists US-only = untapped international opportunity
- High listeners in a city the artist has never toured = tour opportunity
- Compare with similar artists' cities to find geographic white space

**Similar artists:**

- `career_stage`: undiscovered → developing → mid-level → mainstream → superstar → legendary
- `recent_momentum`: decline → gradual decline → steady → growth → explosive growth
- Peers all "mainstream" but artist is "mid-level" = breakout potential
- Peers with playlists you're NOT on = pitch targets

**Playlists:**

- 2 editorial playlists for 5M+ listeners = severely under-playlisted (pitch immediately)
- `placements[].playlist.followers` is often `0` — use `peak_position` or `/research/playlist?id=` for true reach
- Past placements (`status=past`) that dropped off = re-pitch opportunities

**Audience:**

- Gender skew tells you content strategy (visual style, messaging)
- Age concentration tells you platform priority (Gen Z = TikTok, 25–34 = Instagram)
- Country mismatch between audience and cities = content localization opportunity

**Charts / rank / milestones:**

- `/research/rank` is one number — useful for before/after deltas over time
- `/research/milestones` is the activity feed — filter for high star ratings when summarizing
- `/research/charts` is platform-wide, not artist-scoped — find what's hot on a market/platform, then cross-reference with `/similar`

---

## Cross-cutting synthesis patterns

Don't dump raw JSON. Combine endpoints and draw conclusions:

- **Geographic strategy:** `cities` + `audience?platform=instagram` → "Sao Paulo is #1 (135K listeners) but IG audience is 80% US. Massive Brazilian fan base isn't being served with localized content."
- **Playlist gap analysis:** `similar` → `playlists` on each peer → "5 of your 10 peers are on 'R&B Rotation' (450K followers), you're not. Top pitch target."
- **Platform pipeline:** `metrics?source=tiktok` + `metrics?source=spotify` → "TikTok followers up 40% last month, Spotify listeners flat. Virality isn't converting. Add Spotify-specific CTAs to TikTok content."
- **Career positioning:** `similar` → compare career stages → "You're the only 'mainstream' artist in your peer group — everyone else is 'mid-level'. Leverage for brand deals and festival slots."
- **Chart → catalog:** `charts?platform=tiktok&country=US` + `tracks` → identify sound trends the artist's catalog could slot into.

---

## Saving research

If working in an artist workspace, save research results to `research/` with timestamps:

```
research/artist-intel-2026-04-17.md
```

Don't overwrite `context/artist.md` with research data. Static context (who the artist IS) is separate from dynamic research (how they're performing NOW). If the research reveals something that should update the static profile, suggest it — don't auto-update.

---

## 1. Playlist Pitching Intelligence

**Question:** "Which playlist curators should I pitch to?"

```bash
# 1. Find similar artists slightly bigger than yours (good benchmarks)
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&genre=high&limit=50" -H "$AUTH"

# 2. For each similar artist, get their editorial playlist placements
curl -s "$RECOUP_API/research/playlists?artist={similar_artist}&editorial=true" -H "$AUTH"

# 3. Look for curator overlap — playlists adding multiple similar artists

# 4. For promising playlists, resolve Chartmetric IDs via search, then load detail
curl -s "$RECOUP_API/research?q={PLAYLIST_NAME}&type=playlists&beta=true" -H "$AUTH"
curl -s "$RECOUP_API/research/playlist?platform=spotify&id={cm_playlist_id}" -H "$AUTH"
curl -s "$RECOUP_API/research/curator?platform=spotify&id={cm_curator_id}" -H "$AUTH"

# 5. Check if the target artist was ever on these playlists before
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=past" -H "$AUTH"
```

**What to synthesize:** Curators who already playlist similar artists but haven't added yours yet. Prioritize curators who've added 2+ similar artists — they're the warmest targets.

---

## 2. TikTok-to-Spotify Pipeline Analysis

**Question:** "Is TikTok virality translating to Spotify growth?"

```bash
# 1. TikTok metrics over time
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "$AUTH"

# 2. Spotify metrics over the same period
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "$AUTH"

# 3. TikTok audience demographics
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "$AUTH"

# 4. Spotify listener cities
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "$AUTH"

# 5. Top Instagram posts (often cross-posted from TikTok)
curl -s "$RECOUP_API/research/instagram-posts?artist={ARTIST}" -H "$AUTH"
```

**What to synthesize:** Correlation between TikTok follower spikes and Spotify listener growth. Geographic mismatch = opportunity (e.g. TikTok viral in Brazil but Spotify listeners mostly in US → Brazil is untapped).

---

## 3. Tour Routing Intelligence

**Question:** "Where should this artist tour next?"

```bash
# 1. Top listener cities
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "$AUTH"

# 2. Festivals
curl -s "$RECOUP_API/research/festivals" -H "$AUTH"

# 3. Past venues (capacity history for routing anchors)
curl -s "$RECOUP_API/research/venues?artist={ARTIST}" -H "$AUTH"

# 4. Similar artists and their cities (for co-headlining)
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=20" -H "$AUTH"

# 5. Audience breakdown by platform
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "$AUTH"

# 6. Playlist reach sorted by followers (as proxy for regional strength via curator markets)
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&sort=followers" -H "$AUTH"
```

**What to synthesize:** Ranked cities by streaming engagement, cross-referenced with festival opportunities and historical venue capacity. Cities where similar artists tour successfully but this artist hasn't been = expansion opportunities.

---

## 4. A&R Discovery

**Question:** "Find emerging artists in [genre] before they blow up"

```bash
# 0. (Optional) list genre IDs once
curl -s "$RECOUP_API/research/genres" -H "$AUTH"

# 1. Either discover by filters, or start from a breakout anchor artist
curl -s "$RECOUP_API/research/discover?genre=86&country=US&sp_monthly_listeners_min=50000&sp_monthly_listeners_max=200000&sort=weekly_diff.sp_monthly_listeners&limit=50" -H "$AUTH"
# or
curl -s "$RECOUP_API/research?q={ANCHOR_ARTIST}&type=artists&beta=true" -H "$AUTH"

# 2. Find artists similar by musicality (we want undiscovered, not audience overlap)
curl -s "$RECOUP_API/research/similar?artist={ANCHOR_ARTIST}&musicality=high&genre=high&limit=50" -H "$AUTH"

# 3. For promising candidates, check trajectory on two platforms
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=tiktok" -H "$AUTH"

# 4. Editorial placements = label interest signal
curl -s "$RECOUP_API/research/playlists?artist={candidate}&editorial=true" -H "$AUTH"

# 5. AI-generated insights
curl -s "$RECOUP_API/research/insights?artist={candidate}" -H "$AUTH"
```

**What to synthesize:** Emerging artists with similar sound but smaller audience, sorted by growth velocity. Filter for `career_stage` = "undiscovered" or "developing" in the `/research/similar` response.

---

## 5. Catalog Optimization

**Question:** "Which songs should we push and where?"

```bash
# 1. All tracks (artist-scoped)
curl -s "$RECOUP_API/research/tracks?artist={ARTIST}" -H "$AUTH"

# 2. Playlist placements (which songs are playlisted today?)
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}" -H "$AUTH"

# 3. For deep per-track playlist coverage, resolve a Chartmetric track id first
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks&beta=true" -H "$AUTH"
curl -s "$RECOUP_API/research/track/playlists?id={cm_track_id}&editorial=true" -H "$AUTH"

# 4. Albums (needs the Chartmetric artist id)
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists&beta=true" -H "$AUTH"   # get id
curl -s "$RECOUP_API/research/albums?artist_id={cm_artist_id}" -H "$AUTH"

# 5. Metrics to compare against release dates
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "$AUTH"
```

**What to synthesize:** Track-by-track analysis. Look for:

- High playlist reach but low streams = discovery issue (content isn't converting)
- Low playlist but high TikTok = pitch opportunity (organic momentum, needs editorial support)
- Old songs suddenly getting playlisted = catalog momentum (amplify it)

---

## 6. Competitive Roster Analysis

**Question:** "How does our roster compare to a competitor label?"

For each artist on your roster:

```bash
# 1. Profile + metrics
curl -s "$RECOUP_API/research/profile?artist={your_artist}" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={your_artist}&source=spotify" -H "$AUTH"

# 2. Similar artists (to infer competitor roster)
curl -s "$RECOUP_API/research/similar?artist={your_artist}&audience=high&genre=high" -H "$AUTH"

# 3. Playlist reach
curl -s "$RECOUP_API/research/playlists?artist={your_artist}&sort=followers" -H "$AUTH"
curl -s "$RECOUP_API/research/playlists?artist={competitor_artist}&sort=followers" -H "$AUTH"

# 4. Audience demographics
curl -s "$RECOUP_API/research/audience?artist={your_artist}&platform=instagram" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={competitor_artist}&platform=instagram" -H "$AUTH"

# 5. Where fans listen
curl -s "$RECOUP_API/research/cities?artist={your_artist}" -H "$AUTH"
curl -s "$RECOUP_API/research/cities?artist={competitor_artist}" -H "$AUTH"

# 6. Single-number global rank for headline deltas
curl -s "$RECOUP_API/research/rank?artist={your_artist}" -H "$AUTH"
curl -s "$RECOUP_API/research/rank?artist={competitor_artist}" -H "$AUTH"
```

**What to synthesize:** Side-by-side comparison. Identify where your roster under-indexes vs competitors on specific metrics — those are the gaps to close.

---

## 7. Viral Song Autopsy

**Question:** "Why did this song go viral? Can we replicate it?"

```bash
# 1. Resolve + fetch track details
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks&beta=true" -H "$AUTH"
curl -s "$RECOUP_API/research/track?id={cm_track_id}" -H "$AUTH"

# 2. Metrics around release date
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "$AUTH"

# 3. Playlist timeline for this track specifically (5 credits)
curl -s "$RECOUP_API/research/track/playlists?id={cm_track_id}&status=current" -H "$AUTH"
curl -s "$RECOUP_API/research/track/playlists?id={cm_track_id}&status=past&since=2025-01-01" -H "$AUTH"

# 4. Artist-level milestone feed — chart entries, big playlist adds, rating stars
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "$AUTH"

# 5. AI insights (often mention the viral moment)
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" -H "$AUTH"

# 6. Check if similar artists had a similar trajectory
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&musicality=high" -H "$AUTH"

# 7. Narrative context for press / cultural framing
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"query\":\"{TRACK_NAME} {ARTIST} viral TikTok moment\",\"max_results\":10}"
```

**What to synthesize:** Timeline of the viral moment — what platform it started on, which playlists amplified it, which audience demographics drove sharing. Compare with similar artists' trajectories to judge replicability.

---

## 8. Market Expansion Scouting

**Question:** "Which new markets should we focus on?"

```bash
# 1. Current listener geography
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "$AUTH"

# 2. Platform-specific audience breakdown
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" -H "$AUTH"

# 3. Similar artists and their top cities
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&genre=high&limit=10" -H "$AUTH"
# For each similar artist:
curl -s "$RECOUP_API/research/cities?artist={similar_artist}" -H "$AUTH"

# 4. Playlist coverage by geography (via curator regions)
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}" -H "$AUTH"

# 5. Regional chart context for a candidate market
curl -s "$RECOUP_API/research/charts?platform=spotify&country=BR&interval=weekly" -H "$AUTH"
```

**What to synthesize:** Cities where similar artists thrive but the target artist is weak = expansion opportunities. Cross-reference with playlist coverage — markets with fans but no playlist presence need pitching.

---

## 9. Collaboration Finder

**Question:** "Which artists should we collaborate with?"

```bash
# 1. Shared fanbase
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=30" -H "$AUTH"

# 2. Genre/sound overlap
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&genre=high&musicality=high" -H "$AUTH"

# 3. Playlist synergy (shared playlists = easy collab pitch)
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&editorial=true" -H "$AUTH"
curl -s "$RECOUP_API/research/playlists?artist={collab_target}&editorial=true" -H "$AUTH"

# 4. Geographic overlap (shared cities = tour collab opportunity)
curl -s "$RECOUP_API/research/cities?artist={ARTIST}" -H "$AUTH"
curl -s "$RECOUP_API/research/cities?artist={collab_target}" -H "$AUTH"

# 5. Enrich collaborator with structured facts (label, management) if needed
curl -s -X POST "$RECOUP_API/research/enrich" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"input":"{collab_target} musician","schema":{"type":"object","properties":{"label":{"type":"string"},"manager":{"type":"string"}}}}'
```

**What to synthesize:** Ranked collaboration targets by audience overlap, career stage (slightly bigger = ideal), and playlist synergy. Shared playlists + shared cities = strongest collab case.

---

## 10. Release Strategy Timing

**Question:** "When should we release, and how should we roll it out?"

```bash
# 1. Analyze past releases (albums requires CM artist_id)
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists&beta=true" -H "$AUTH"   # get id
curl -s "$RECOUP_API/research/albums?artist_id={cm_artist_id}" -H "$AUTH"
curl -s "$RECOUP_API/research/career?artist={ARTIST}" -H "$AUTH"

# 2. What worked — past playlist adds after previous releases
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=past&since=2024-01-01" -H "$AUTH"

# 3. Similar artists' successful releases
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=10" -H "$AUTH"
# For each similar artist:
curl -s "$RECOUP_API/research/albums?artist_id={similar_cm_artist_id}" -H "$AUTH"
curl -s "$RECOUP_API/research/career?artist={similar_artist}" -H "$AUTH"

# 4. Current playlist momentum
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&editorial=true" -H "$AUTH"

# 5. Which platforms are hottest right now
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=youtube_channel" -H "$AUTH"
```

**What to synthesize:** Release timing recommendation grounded in historical patterns (when did past releases get the most playlist adds?), similar artists' release cycles, and which platform has the most momentum right now.

---

## 11. People Outreach (Managers, A&R, Press)

**Question:** "Who should we reach out to?"

```bash
# 1. People search — returns multi-source profiles (LinkedIn etc.)
curl -s -X POST "$RECOUP_API/research/people" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"A&R reps at Atlantic Records hip-hop","num_results":15}'

# 2. Pull source pages for specific candidates
curl -s -X POST "$RECOUP_API/research/extract" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"urls":["https://linkedin.com/in/...","https://example.com/team"],"objective":"role, tenure, recent signings"}'

# 3. Enrich the candidate into structured form you can paste into a CRM
curl -s -X POST "$RECOUP_API/research/enrich" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"input":"Jane Doe A&R at Atlantic Records","schema":{"type":"object","properties":{"title":{"type":"string"},"recent_signings":{"type":"array","items":{"type":"string"}},"contact":{"type":"string"}}},"processor":"core"}'
```

**What to synthesize:** A ranked outreach list with title, recent relevant work, and a suggested angle for the pitch.

---

## Chaining workflows and tools

The 11 workflows above are **building blocks, not complete answers**. Almost no real user question maps cleanly onto exactly one workflow — the real deliverable is usually a chain: `Workflow A` → `Workflow B` → external tool call → hand off to another skill.

This section teaches you how to compose.

### The three chain patterns

Every chain you'll ever build is one of three shapes:

| Pattern | Shape | Example |
| ------- | ----- | ------- |
| **Data → Data** | Workflow A's output feeds Workflow B's input | `/similar` (W9) returns peer list → for each peer, run playlist gap analysis (W1) |
| **Data → Action** | Research output triggers a tool call outside this skill | Peer research (W9) + people search (W11) → draft email → `send_email` MCP tool |
| **Skill → Skill** | Finish with this skill, hand off to another | Research sweep (W4) → hand off to `content-creation` skill for press one-sheet; or to `release-management` for timing; or to `streaming-growth` for ads strategy |

Most real deliverables are all three stacked: compose several workflows (Data → Data), pipe the result into an action (Data → Action), then hand off whatever remains to another skill (Skill → Skill).

### Tools this skill chains into

Beyond the `/research/*` endpoints, the agent running this skill typically has access to:

- **`send_email`** — MCP tool that sends via Resend from `@recoupable.com`. Used at the end of outreach chains. **Never auto-fire on cold contacts — require human approval first.**
- **Artist workspace writes** — save synthesized research to `context/artist.md`, `research/{date}.md`, `releases/{slug}/RELEASE.md`. See "Saving research" above.
- **Other skills in this repo** — `content-creation` (promo content, captions, one-sheets), `release-management` (RELEASE.md lifecycle), `streaming-growth` (Spotify Showcase/Marquee, DSP ads), `artist-workspace` (workspace setup/lookup), `trend-to-song` (reverse from cultural moment to song).

### Chaining rules (read before composing)

1. **Don't re-fetch what you already have.** If `/similar` already returned `cities` for a peer, reuse it — don't call `/research/cities` on the peer again.
2. **Preserve artist context through the chain.** Every downstream step should reference the user's specific artist data (cities, audience, playlist reach), not generic templates. That's what makes the final output feel researched instead of auto-generated.
3. **External-facing actions require a human-approval gate.** Anything that touches a real human (`send_email`, posting content, contacting a manager) must be drafted → presented → confirmed. Never auto-send cold outreach.
4. **Save once, reference many.** Write synthesized research to the artist workspace once; subsequent chains read from there instead of re-running the whole fan-out. Check `context/artist.md` before starting a new research pass.
5. **Stop when the question is answered.** Chains can loop forever if ungated. Finish when the user's original ask is satisfied, not when you run out of endpoints to call.

---

### Example A — Peer collab outreach

**User question:** "Who should Artist X collab with, and can you start outreach?"

```text
Step 1 — Research the artist (Workflow 0: full sweep)
  Calls: /research/profile + /research/metrics + /research/cities
         + /research/audience + /research/similar
  Writes: context/artist.md (if workspace exists)
  Output: full artist context — cities, audience demos, network strength

Step 2 — Narrow to realistic collab targets (Workflow 9)
  Input: similar[] from Step 1
  Filters: career_stage == "developing" (tier match),
           audience_match high, shared-city overlap >= 2
  Output: 3-5 ranked peer candidates

Step 3 — Find each target's manager / A&R (Workflow 11)
  For each peer in Step 2:
    POST /research/people  {query: "manager for {peer}"}
    POST /research/enrich  {input, schema: {name, role, email, recent_signings}}
  Output: ranked outreach list with contact + angle

Step 4 — Draft outreach (LLM, no tool call)
  Reference:
    - Artist X specifics from Step 1 (cities, listeners, reach)
    - Peer specifics from Step 3 (recent signings, stylistic fit)
  Output: personalized drafts — NOT generic "love your music" copy

Step 5 — HUMAN APPROVAL GATE (mandatory)
  Present full draft(s): recipient, subject, body.
  Wait for explicit "send" before Step 6.

Step 6 — Send (send_email MCP tool)
  Only after approval.
  send_email({to, subject, html})

Optional handoff:
  → content-creation skill: draft the follow-up nurture sequence
  → release-management skill: if the collab lands, open a RELEASE.md
```

---

### Example B — "How is Artist X doing, and what's next?"

**User question:** State of the artist + recommended next move.

```text
Step 1 — Snapshot (Workflow: metrics + cities + insights)
  Calls: /research/metrics?source=spotify + /research/cities
         + /research/insights + /research/milestones
  Output: trend read (follower/listener divergence, popularity direction)

Step 2 — Diagnose the gap (Workflow 1: playlist pitching)
  Input: profile.num_sp_editorial_playlists from Step 1
  If editorials == 0 and total_reach > 500k → editorial gap confirmed
  Call: /research/similar (peers) → /research/playlists (each peer)
  Output: playlists peers are on that Artist X isn't → pitch targets

Step 3 — HANDOFF to streaming-growth skill
  Context to pass:
    - Current monthly listeners + trend from Step 1
    - Editorial gap from Step 2
    - Nearest milestone (1k MLs for Showcase, 5k for Marquee)
  streaming-growth skill owns: which lever to pull first
  (playlist push vs social-to-DSP ads vs organic content)

Step 4 — HANDOFF to release-management skill
  If Step 3 recommends a new release:
    Open releases/{slug}/RELEASE.md
    Populate DSP pitch from Step 1 data + Step 2 playlist targets

Human-approval gate: none (internal reasoning only, no external contacts).
```

---

### Example C — Market scouting for a TikTok-driven breakout

**User question:** "Find tracks that are blowing up on TikTok and the indie artists driving them."

```text
Step 1 — Find trending music (Workflow: charts + discover)
  Calls: /research/charts?platform=tiktok&country=US
         /research/discover?country=US&genre={GENRE_ID}
                            &sp_monthly_listeners_min=10000
                            &sp_monthly_listeners_max=100000
  Output: candidate track + artist list

Step 2 — Validate TikTok-to-Spotify pipeline (Workflow 2)
  For each candidate:
    /research/metrics?source=tiktok (track posts trend)
    /research/metrics?source=spotify (listener response)
    /research/track/playlists?id={track_id} (editorial pickup?)
  Output: ranked by TikTok velocity + Spotify conversion

Step 3 — Enrich (optional, deep context)
  POST /research/deep {query: "why is {track} going viral?"}
  Output: cited narrative — the cultural thread driving the trend

Step 4 — Write to artist workspace
  If any candidate warrants ongoing tracking:
    Create context/artist.md scaffold via artist-workspace skill
    Save Step 1-3 synthesis to research/{date}-tiktok-scout.md

Step 5 — HANDOFF to trend-to-song skill
  If the trend itself (not the artist) is the opportunity:
    trend-to-song owns: reverse from cultural moment to song
                        + test campaign in 72 hours

Human-approval gate: none for research; required if Step 5 triggers an ad spend.
```

---

### When NOT to chain

Chaining has a cost — every step is latency, credits, and a place for the agent to lose context. Don't chain when:

- The user asked a single-fact question ("how many Spotify followers does Artist X have?"). Just answer it.
- The next workflow depends on data the previous one already surfaced well enough. Reuse the data; don't re-query.
- You're about to make an external-facing action without clear user intent. Stop and confirm first.

A three-step chain that answers the real question beats an eleven-step chain that shows off every endpoint.

---

## Building Your Own Workflows

The power is in combining data types:

| What You Need | Endpoint | Use For |
|---------------|----------|---------|
| **Who** — peers, competitors, collaborators | `/research/similar` | Benchmarks, pitch targets, collabs |
| **Where** — geography | `/research/cities`, `/research/audience`, `/research/venues` | Tour routing, market expansion |
| **What** — content and catalog | `/research/playlists`, `/research/tracks`, `/research/albums`, `/research/track/playlists` | Content strategy, playlist pitching |
| **When** — timing and trajectory | `/research/metrics`, `/research/career`, `/research/milestones` | Release timing, growth analysis |
| **Rank** — single-number deltas | `/research/rank` | Headline progress metrics |
| **Market** — platform-wide charts | `/research/charts`, `/research/discover`, `/research/festivals`, `/research/radio`, `/research/genres` | Market scouting, trend detection |
| **Why** — narrative + context | `/research/insights`, `/research/web`, `/research/deep` | Cultural positioning, press strategy, brand partnerships |
| **People** — industry contacts | `/research/people`, `/research/enrich`, `/research/extract` | Outreach, CRM enrichment |
