# Research workflows, interpretation, and synthesis

Multi-step workflows that chain `/api/research/*` endpoints to answer strategic
questions, plus the interpretation rules of thumb and cross-cutting synthesis
patterns to apply once you have the data.

The research API is backed by **Songstats** — IDs are short alphanumeric
strings, and several endpoints from older versions (`cities`, `charts`,
`discover`, `genres`, `festivals`, `radio`, `venues`, `rank`,
`instagram-posts`, `playlist`/`curator` detail) **no longer exist**. The
workflows below only use endpoints that are live in production.

All examples assume:

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
AUTH="x-api-key: $RECOUP_API_KEY"
```

---

## Interpretation cheat sheet

Raw numbers are noise without interpretation. Heuristics for each data type:

**Metrics** (`/research/metrics?source=spotify` → `stats[0].data`):

- `followers_total ÷ monthly_listeners_current` above ~20% = dedicated fan base
  (they follow, not just stream)
- `popularity_current` near 100 = strong algorithmic favor
- `playlists_editorial_current` low relative to `monthly_listeners_current` =
  under-playlisted (editorial pitch opportunity)
- Compare `*_current` vs `*_total` (e.g. `playlists_current` vs
  `playlists_total`) to see what's active now vs all-time
- These are **current snapshots**, not time series — to track change over time,
  store today's snapshot and diff against a prior one (this is what
  `recoup-research` (weekly-update mode) does)

**Similar artists** (`/research/similar` → `artists[]`):

- It's a flat, ranked list of artist references — **no scores, no career stage,
  no momentum**. To size up a peer, call `/research/metrics` on them.
- Weight the match with `audience` / `genre` / `mood` / `musicality`
  (`high|medium|low`). `audience=high` for shared-fanbase peers; `musicality=high`
  for sonic look-alikes (better for discovery of smaller artists).
- Peers with playlists you're NOT on = pitch targets.

**Playlists** (`/research/playlists` → `placements[]`):

- `followers_total` is a formatted string (`"34.3M"`), not an integer — parse it
  if you need to sort numerically.
- Artist-level placements have **no editorial flag**; for editorial-only
  filtering use `/research/track/playlists?...&editorial=true` per track, or read
  `playlists_editorial_current` from `/research/metrics`.
- `status=past` placements that dropped off = re-pitch opportunities.

**Audience** (`/research/audience?platform=` → `audience[]`):

- The only geographic/demographic source now (Spotify city data was removed).
  Country breakdown here is your geography signal.
- Gender skew → content strategy (visual style, messaging).
- Age concentration → platform priority (Gen Z = TikTok, 25–34 = Instagram).
- Often `[]` for smaller artists — fall back to another platform or web research.

**Activity feeds** (`/research/career`, `/research/insights`, `/research/milestones`):

- Each entry has `activity_tier` (integer, **lower = more significant**) — sort
  ascending to surface the biggest events. There is no star rating.
- Empty arrays are legitimate; don't retry. Cross-read the three feeds for
  narrative.

---

## Cross-cutting synthesis patterns

Don't dump raw JSON. Combine endpoints and draw conclusions:

- **Geographic strategy:** `audience?platform=instagram` + `audience?platform=tiktok`
  → "IG audience is 80% US but TikTok is 35% Brazil — the Brazilian fan base
  isn't being served with localized content."
- **Playlist gap analysis:** `similar` → `playlists` on each peer → "5 of your 10
  peers are on 'RapCaviar', you're not. Top pitch target."
- **Platform pipeline:** `metrics?source=tiktok` + `metrics?source=spotify` →
  "TikTok followers far ahead of Spotify conversion. Virality isn't translating.
  Add Spotify-specific CTAs to TikTok content."
- **Editorial gap:** `metrics?source=spotify` (`playlists_editorial_current`) +
  `playlists` → "568 editorial placements for 99M listeners is healthy; the gap is
  algorithmic, not editorial."
- **Catalog momentum:** `tracks` + `milestones` → identify recent playlist/chart
  events tied to specific tracks the artist could amplify.

---

## Saving research

If working in an artist workspace, save research results to `research/` with timestamps:

```
research/artist-intel-2026-04-17.md
```

Don't overwrite `context/artist.md` with research data. Static context (who the
artist IS) is separate from dynamic research (how they're performing NOW). If
the research reveals something that should update the static profile, suggest it
— don't auto-update.

---

## 1. Playlist Pitching Intelligence

**Question:** "Which playlists should I pitch to?"

```bash
# 1. Find similar artists slightly bigger than yours (good benchmarks)
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&genre=high&limit=50" -H "$AUTH"

# 2. For each similar artist, get their current playlist placements
curl -s "$RECOUP_API/research/playlists?artist={similar_artist}&platform=spotify&status=current" -H "$AUTH"

# 3. Look for overlap — playlists hosting multiple similar artists that yours isn't on

# 4. For per-track editorial detail, resolve a track id then page the track-level endpoint
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks" -H "$AUTH"            # get track id
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&editorial=true&indie=true&majorCurator=true&popularIndie=true" -H "$AUTH"

# 5. Check if the target artist was ever on these playlists before
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=past" -H "$AUTH"
```

**What to synthesize:** Playlists that already host similar artists but haven't
added yours yet. Prioritize playlists hosting 2+ similar artists — they're the
warmest targets.

---

## 2. TikTok-to-Spotify Pipeline Analysis

**Question:** "Is TikTok virality translating to Spotify growth?"

```bash
# 1. TikTok metrics snapshot
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "$AUTH"

# 2. Spotify metrics snapshot
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "$AUTH"

# 3. TikTok audience demographics
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "$AUTH"

# 4. Instagram audience for geographic cross-check
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "$AUTH"

# 5. Narrative context for any spike
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} viral TikTok moment 2026","max_results":10}'
```

**What to synthesize:** Compare TikTok scale against Spotify conversion.
Geographic mismatch between TikTok audience and Spotify audience = opportunity
(e.g. TikTok skews Brazil but Spotify skews US → Brazil is untapped). Because
metrics are snapshots, store today's reading to measure change next time.

---

## 3. Geographic & Tour Strategy

**Question:** "Where is this artist strong, and where should they tour?"

> The dedicated `cities`, `venues`, and `festivals` endpoints were removed.
> Geography now comes from `/research/audience` country breakdowns plus web
> research for venues/festivals.

```bash
# 1. Audience geography across platforms (country breakdown lives here now)
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" -H "$AUTH"

# 2. Similar artists (for co-headlining / routing comps)
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=20" -H "$AUTH"

# 3. Venue history, festival fit, recent touring — web/deep research
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} tour dates venues capacity 2025 2026","max_results":10}'
curl -s -X POST "$RECOUP_API/research/deep" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} touring history, venue sizes, and festival appearances over the last two years"}'
```

**What to synthesize:** Ranked markets by audience concentration, cross-checked
with where similar artists tour successfully (from web research) and the
artist's own venue history. Markets with audience but no recent touring =
expansion opportunities.

---

## 4. A&R Discovery

**Question:** "Find emerging artists in [genre] before they blow up"

> The `discover` (filter-based) and `genres` endpoints were removed. Discovery
> now starts from a known **anchor artist** and fans out through `/similar`,
> validated with `/metrics`. Use web/deep research to find anchors or scan a
> scene.

```bash
# 1. Pick an anchor — a known artist in the target sound. Find them, or scout via web.
curl -s "$RECOUP_API/research?q={ANCHOR_ARTIST}&type=artists" -H "$AUTH"
# (or) discover candidate names from the web:
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"emerging {GENRE} artists to watch 2026","max_results":15}'

# 2. Fan out to sonic look-alikes (musicality=high surfaces smaller, undiscovered acts)
curl -s "$RECOUP_API/research/similar?artist={ANCHOR_ARTIST}&musicality=high&genre=high&limit=50" -H "$AUTH"

# 3. For each candidate, validate trajectory on two platforms (size them — similar has no metrics)
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=tiktok" -H "$AUTH"

# 4. Editorial pickup = label interest signal
curl -s "$RECOUP_API/research/metrics?artist={candidate}&source=spotify" -H "$AUTH"   # playlists_editorial_current
curl -s "$RECOUP_API/research/playlists?artist={candidate}&status=current" -H "$AUTH"

# 5. AI-generated insights for context
curl -s "$RECOUP_API/research/insights?artist={candidate}" -H "$AUTH"
```

**What to synthesize:** Emerging artists with a similar sound but a smaller
audience. Since `/similar` gives no stage/score, rank candidates yourself by the
`/metrics` snapshot (lower `monthly_listeners_current` with rising editorial
pickup = the breakout window).

---

## 5. Catalog Optimization

**Question:** "Which songs should we push and where?"

```bash
# 1. All tracks (artist-scoped)
curl -s "$RECOUP_API/research/tracks?artist={ARTIST}" -H "$AUTH"

# 2. Albums (needs the provider artist id — get it from search)
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists" -H "$AUTH"                 # get id
curl -s "$RECOUP_API/research/albums?artist_id={artist_id}" -H "$AUTH"

# 3. Current playlist placements (which songs are playlisted today?)
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=current" -H "$AUTH"

# 4. For deep per-track playlist coverage, resolve a track id first
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks" -H "$AUTH"              # get track id
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&editorial=true&indie=true&majorCurator=true&popularIndie=true" -H "$AUTH"

# 5. Track detail (genres, audio analysis, collaborators) for sound fit
curl -s "$RECOUP_API/research/track?id={track_id}" -H "$AUTH"

# 6. Artist metrics for context
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "$AUTH"
```

**What to synthesize:** Track-by-track. Look for:

- Tracks on many playlists but not converting to streams = discovery issue
- Tracks with strong audio-analysis fit for a target playlist = pitch candidates
- Old songs suddenly getting playlisted (from `/milestones`) = catalog momentum

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

# 3. Playlist placements
curl -s "$RECOUP_API/research/playlists?artist={your_artist}&status=current" -H "$AUTH"
curl -s "$RECOUP_API/research/playlists?artist={competitor_artist}&status=current" -H "$AUTH"

# 4. Audience demographics + geography
curl -s "$RECOUP_API/research/audience?artist={your_artist}&platform=instagram" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={competitor_artist}&platform=instagram" -H "$AUTH"

# 5. Headline numbers come from /metrics (there is no /rank endpoint)
curl -s "$RECOUP_API/research/metrics?artist={competitor_artist}&source=spotify" -H "$AUTH"
```

**What to synthesize:** Side-by-side comparison of `/metrics` snapshots
(monthly listeners, followers, editorial playlists, playlist reach). Identify
where your roster under-indexes vs competitors — those are the gaps to close.

---

## 7. Viral Song Autopsy

**Question:** "Why did this song go viral? Can we replicate it?"

```bash
# 1. Resolve + fetch track details (genres, audio analysis, collaborators)
curl -s "$RECOUP_API/research?q={TRACK_NAME}&type=tracks" -H "$AUTH"             # get track id
curl -s "$RECOUP_API/research/track?id={track_id}" -H "$AUTH"

# 2. Artist metrics snapshots
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "$AUTH"

# 3. Playlist timeline for this track specifically (5 credits)
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&status=current" -H "$AUTH"
curl -s "$RECOUP_API/research/track/playlists?id={track_id}&status=past&since=2025-01-01" -H "$AUTH"

# 4. Artist-level activity feed — chart entries, big playlist adds
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "$AUTH"

# 5. AI insights (often mention the viral moment)
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" -H "$AUTH"

# 6. Narrative context for press / cultural framing
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{TRACK_NAME} {ARTIST} viral TikTok moment","max_results":10}'
```

**What to synthesize:** Timeline of the viral moment — which playlists amplified
it (from `track/playlists`), what the audio analysis suggests about its hook,
which audience drove sharing. The per-song TikTok *counts* aren't in the API —
get that narrative from web/deep research, not fabricated numbers.

---

## 8. Market Expansion Scouting

**Question:** "Which new markets should we focus on?"

```bash
# 1. Platform-specific audience country breakdown (the geography source)
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=youtube" -H "$AUTH"

# 2. Similar artists and their audience geography
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&genre=high&limit=10" -H "$AUTH"
# For each similar artist:
curl -s "$RECOUP_API/research/audience?artist={similar_artist}&platform=instagram" -H "$AUTH"

# 3. Playlist coverage (curator markets as a soft regional proxy)
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=current" -H "$AUTH"

# 4. Regional/scene context for a candidate market
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{GENRE} scene streaming growth Brazil 2026","max_results":10,"country":"BR"}'
```

**What to synthesize:** Markets where similar artists over-index but the target
artist is weak = expansion opportunities. Cross-reference with playlist coverage
— markets with fans but no playlist presence need pitching.

---

## 9. Collaboration Finder

**Question:** "Which artists should we collaborate with?"

```bash
# 1. Shared fanbase
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=30" -H "$AUTH"

# 2. Genre/sound overlap
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&genre=high&musicality=high" -H "$AUTH"

# 3. Size each candidate (similar has no metrics) + playlist synergy
curl -s "$RECOUP_API/research/metrics?artist={collab_target}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/playlists?artist={collab_target}&status=current" -H "$AUTH"

# 4. Geographic overlap (shared markets = tour collab opportunity)
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "$AUTH"
curl -s "$RECOUP_API/research/audience?artist={collab_target}&platform=instagram" -H "$AUTH"

# 5. Enrich collaborator with structured facts (label, management) if needed
curl -s -X POST "$RECOUP_API/research/enrich" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"input":"{collab_target} musician","schema":{"type":"object","properties":{"label":{"type":"string"},"manager":{"type":"string"}}}}'
```

**What to synthesize:** Ranked collaboration targets by audience overlap, size
(slightly bigger via `/metrics` = ideal exposure uplift), and playlist synergy.
Shared playlists + shared audience markets = strongest collab case.

---

## 10. Release Strategy Timing

**Question:** "When should we release, and how should we roll it out?"

```bash
# 1. Analyze past releases (albums needs provider artist_id)
curl -s "$RECOUP_API/research?q={ARTIST}&type=artists" -H "$AUTH"                 # get id
curl -s "$RECOUP_API/research/albums?artist_id={artist_id}" -H "$AUTH"
curl -s "$RECOUP_API/research/career?artist={ARTIST}" -H "$AUTH"

# 2. What worked — past playlist adds after previous releases
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=past" -H "$AUTH"

# 3. Similar artists' release cadence
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&audience=high&limit=10" -H "$AUTH"
# For each peer:
curl -s "$RECOUP_API/research?q={similar_artist}&type=artists" -H "$AUTH"         # get peer id
curl -s "$RECOUP_API/research/albums?artist_id={peer_artist_id}" -H "$AUTH"
curl -s "$RECOUP_API/research/career?artist={similar_artist}" -H "$AUTH"

# 4. Which platforms are hottest right now
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok" -H "$AUTH"
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=youtube_channel" -H "$AUTH"
```

**What to synthesize:** Release timing grounded in historical patterns (when did
past releases get the most playlist adds, from `career`/`milestones`?), peer
release cycles, and which platform has the most momentum right now.

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

**What to synthesize:** A ranked outreach list with title, recent relevant work,
and a suggested angle for the pitch.

---

## Chaining workflows and tools

The 11 workflows above are **building blocks, not complete answers**. Almost no
real user question maps cleanly onto exactly one workflow — the real deliverable
is usually a chain: `Workflow A` → `Workflow B` → external tool call → hand off
to another skill.

This section teaches you how to compose.

### The three chain patterns

Every chain you'll ever build is one of three shapes:

| Pattern | Shape | Example |
| ------- | ----- | ------- |
| **Data → Data** | Workflow A's output feeds Workflow B's input | `/similar` (W9) returns peer list → for each peer, run playlist gap analysis (W1) |
| **Data → Draft** | Research output becomes a deliverable the user can act on | Peer research (W9) + people search (W11) → drafted outreach email the user reviews and sends themselves |
| **Skill → Skill** | Finish with this skill, hand off to another | Research sweep (W4) → hand off to `content-creation` skill for press one-sheet; or to `release-management` for timing; or to `streaming-growth` for ads strategy |

Most real deliverables are all three stacked: compose several workflows (Data →
Data), turn the result into a draft (Data → Draft), then hand off whatever
remains to another skill (Skill → Skill).

### What this skill produces

Beyond the `/research/*` endpoints, the agent running this skill typically produces:

- **Written drafts** for the user to act on — outreach emails, pitch copy, press
  blurbs, DSP pitches. This skill drafts; the user sends. It does not execute
  external-facing actions (no email sending, no social posting, no contacting
  managers).
- **Artist workspace writes** — save synthesized research to `context/artist.md`,
  `research/{date}.md`, `releases/{slug}/RELEASE.md`. See "Saving research" above.
- **Handoffs to other skills** — `content-creation` (promo content, captions,
  one-sheets), `release-management` (RELEASE.md lifecycle), `streaming-growth`
  (Spotify Showcase/Marquee, DSP ads), `recoup-artists` (workspace
  setup/lookup), `trend-to-song` (reverse from cultural moment to song).

### Chaining rules (read before composing)

1. **Don't re-fetch what you already have.** If `/metrics` already gave you the
   peer's snapshot, reuse it — don't call it again.
2. **Preserve artist context through the chain.** Every downstream step should
   reference the user's specific artist data (audience geography, playlist reach,
   metrics), not generic templates. That's what makes the final output feel
   researched instead of auto-generated.
3. **Draft, don't execute, for external-facing actions.** Anything that touches a
   real human (cold outreach to managers/A&R, social posts, press contacts)
   should be drafted and presented for the user to send themselves.
4. **Save once, reference many.** Write synthesized research to the artist
   workspace once; subsequent chains read from there instead of re-running the
   whole fan-out. Check `context/artist.md` before starting a new research pass.
5. **Stop when the question is answered.** Chains can loop forever if ungated.
   Finish when the user's original ask is satisfied, not when you run out of
   endpoints to call.

---

### Example A — Peer collab outreach draft

**User question:** "Who should Artist X collab with, and draft some outreach I can send?"

```text
Step 1 — Research the artist (full sweep per SKILL.md decision tree)
  Calls: /research/profile + /research/metrics?source=spotify
         + /research/audience + /research/similar
  Writes: context/artist.md (if workspace exists)
  Output: full artist context — audience geography, metrics, peer set

Step 2 — Narrow to realistic collab targets (Workflow 9)
  Input: similar[] from Step 1
  Filters: size each peer via /metrics (slightly bigger = ideal),
           audience overlap, shared-market overlap >= 2
  Output: 3-5 ranked peer candidates

Step 3 — Find each target's manager / A&R (Workflow 11)
  For each peer in Step 2:
    POST /research/people  {query: "manager for {peer}"}
    POST /research/enrich  {input, schema: {type: "object", properties: {name, role, email, recent_signings}}}
  Output: ranked outreach list with contact + angle

Step 4 — Draft outreach (LLM, no tool call)
  Reference:
    - Artist X specifics from Step 1 (markets, listeners, reach)
    - Peer specifics from Step 3 (recent signings, stylistic fit)
  Output: personalized drafts — NOT generic "love your music" copy.
  Present drafts to the user with recipient, subject, and body.
  The user sends them manually.

Optional handoff:
  → content-creation skill: draft the follow-up nurture sequence
  → release-management skill: if a collab lands, open a RELEASE.md
```

---

### Example B — "How is Artist X doing, and what's next?"

**User question:** State of the artist + recommended next move.

```text
Step 1 — Snapshot
  Calls: /research/profile + /research/metrics?source=spotify
         + /research/audience + /research/insights + /research/milestones
  Output:
    - metrics.stats[0].data → monthly listeners, followers, popularity,
      playlists_editorial_current, playlist_reach_current
    - audience → geographic / demographic concentration
    - milestones (sorted by activity_tier) → recent notable events

Step 2 — Diagnose the gap (Workflow 1: playlist pitching)
  Input: metrics snapshot from Step 1
  If playlists_editorial_current is low relative to monthly_listeners_current
     → editorial gap confirmed
  Call: /research/similar (peers) → /research/playlists (each peer)
  Output: playlists peers are on that Artist X isn't → pitch targets

Step 3 — HANDOFF to streaming-growth skill
  Context to pass:
    - Current monthly listeners + recent milestones from Step 1
    - Editorial gap from Step 2
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
Step 1 — Find candidates (no charts/discover endpoints — start from web + anchors)
  Calls: POST /research/web {query: "songs blowing up on TikTok {GENRE} 2026"}
         /research?q={ANCHOR_ARTIST}&type=artists
         /research/similar?artist={ANCHOR}&musicality=high&genre=high
  Output: candidate track + artist list

Step 2 — Validate TikTok-to-Spotify pipeline (Workflow 2)
  For each candidate:
    /research/metrics?source=tiktok  (TikTok scale)
    /research/metrics?source=spotify (listener response)
    /research/track/playlists?id={track_id} (editorial pickup?)
  Output: ranked by TikTok scale + Spotify conversion + editorial pickup

Step 3 — Enrich (optional, deep context)
  POST /research/deep {query: "why is {track} going viral?"}
  Output: cited narrative — the cultural thread driving the trend

Step 4 — Write to artist workspace
  If any candidate warrants ongoing tracking:
    Create context/artist.md scaffold via recoup-artists skill
    Save Step 1-3 synthesis to research/{date}-tiktok-scout.md

Step 5 — HANDOFF to trend-to-song skill
  If the trend itself (not the artist) is the opportunity:
    trend-to-song owns: reverse from cultural moment to song
                        + test campaign in 72 hours

Human-approval gate: none for research; required if Step 5 triggers an ad spend.
```

---

### When NOT to chain

Chaining has a cost — every step is latency, credits, and a place for the agent
to lose context. Don't chain when:

- The user asked a single-fact question ("how many Spotify followers does Artist
  X have?"). Just answer it.
- The next workflow depends on data the previous one already surfaced well
  enough. Reuse the data; don't re-query.
- You're about to write to the artist workspace or kick off a long chain without
  clear user intent. Confirm first.

A three-step chain that answers the real question beats an eleven-step chain that
shows off every endpoint.

---

## Building Your Own Workflows

The power is in combining data types:

| What You Need | Endpoint | Use For |
|---------------|----------|---------|
| **Who** — peers, competitors, collaborators | `/research/similar` | Benchmarks, pitch targets, collabs |
| **Where** — geography | `/research/audience` (country breakdown) | Tour routing, market expansion |
| **What** — content and catalog | `/research/playlists`, `/research/tracks`, `/research/albums`, `/research/track`, `/research/track/playlists` | Content strategy, playlist pitching |
| **How big / how hot** — metrics | `/research/metrics` (snapshot per source) | Sizing artists, release timing, growth analysis |
| **When** — timeline & events | `/research/career`, `/research/milestones` | Release timing, activity feeds |
| **Why** — narrative + context | `/research/insights`, `/research/web`, `/research/deep` | Cultural positioning, press strategy, brand partnerships |
| **People** — industry contacts | `/research/people`, `/research/enrich`, `/research/extract` | Outreach, CRM enrichment |

Endpoints that no longer exist (don't reach for them): `cities`, `charts`,
`discover`, `genres`, `festivals`, `radio`, `venues`, `rank`, `instagram-posts`,
`playlist` (singular), `curator`. Geography → `/research/audience`; discovery →
anchor artist + `/research/similar` + `/research/web`; headline rank → compare
`/research/metrics` snapshots.
