# Research workflows, interpretation, and synthesis

Multi-step workflows that chain the Recoup API to answer strategic questions,
plus the interpretation rules of thumb and cross-cutting synthesis patterns to
apply once you have the data.

The research surface is **web intelligence** (`/research/web`, `/deep`,
`/people`, `/extract`, `/enrich`, `/events`) plus **measured numbers** from the
Apify-backed measurement store (`/research/playcounts`, `/track/stats`,
`/track/historic-stats`, `/track/playcount-deltas`, `/tracks/{isrc}/measurements`,
`/measurement-jobs`). Artist and catalog facts come from the Spotify endpoints
(`/spotify/search`, `/spotify/artist`, `/spotify/artist/albums`,
`/spotify/artist/topTracks`, `/spotify/album`); follower counts per social
platform come from a rostered artist's connected profiles
(`/artists/{id}/socials`). There is no structured third-party artist-stats
provider: no monthly listeners, no audience demographics, no playlist feeds.
Say so when a question needs them; never estimate them.

All examples assume:

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.dev/api"
AUTH="x-api-key: $RECOUP_API_KEY"
```

---

## Interpretation cheat sheet

Raw numbers are noise without interpretation. Heuristics for each data type:

**Play counts** (`/research/playcounts?spotify_album_id=` → `playcounts[]`,
`/research/track/playcount-deltas?isrc=&since=` → `deltas[]`):

- `platform_displayed_play_count` is the number Spotify shows on the track —
  a platform-displayed count, **not** a royalty-bearing stream count.
- Every value carries `captured_at` and `data_source`. A delta is only real
  between two captures on different days; skip same-day captures (retries and
  ad-hoc snapshots make the window meaningless) and report the span covered
  ("+23,741 plays over 22 days").
- `run_rate_annualized` in `deltas[]` is a trailing proxy — it needs two
  captures at least 7 days apart. Empty `deltas` is "not enough history", not zero.
- A play count of `0` means "not captured", never a real zero.
- Nothing stored for an album? `POST /research/measurement-jobs`
  (`source:"current"`) captures it in minutes; there is no historical backfill.

**Spotify artist object** (`/spotify/artist?id=` → `followers.total`,
`popularity`, `genres`, `images`):

- `popularity` (0–100) tracks recent algorithmic favor; `followers.total` is
  the durable fan base. Followers high but popularity low = catalog artist
  without a current moment; the reverse = a moment without a base.
- These are current snapshots. Store today's reading and diff against a prior
  one to see change (this is what `recoup-research-weekly-brief` does).
- Monthly listeners are not available from any endpoint.

**Connected socials** (`/artists/{id}/socials` → per-platform follower counts):

- Only rostered artists with connected profiles return numbers. `0`/`null`
  means "not stored" — omit the platform rather than print zero. A fresh
  `POST /artist/socials/scrape` refreshes the counts and recent posts.

**Web search** (`POST /research/web` → `results[]` of `{title, url, snippet}` +
`formatted`):

- Results are leads, not facts. Keep only items clearly about the artist and
  dated inside the window the question implies (14 days for "recent").
- Always carry the source URL into the deliverable; never paraphrase a number
  out of a snippet without the link next to it.

**Deep research** (`POST /research/deep` → cited narrative): 2+ minutes and
expensive. Use it for "why" questions after web search has framed the "what".

**Live events** (`POST /research/events {artist_id}` → `events[]` with venue,
city, country, date, ticket link): exact, resolved through the artist's connected
live-events profile. `404` means no profile is connected — say so.

---

## Cross-cutting synthesis patterns

Don't dump raw JSON. Combine sources and draw conclusions:

- **Catalog momentum:** `playcount-deltas` per focus track → "three tracks from
  the 2024 EP gained 40% of this month's plays; the new single is flat — the
  catalog is carrying the artist."
- **Social-to-streaming conversion:** connected-social follower counts + play
  count deltas → "TikTok followers doubled in a month but Spotify plays grew
  4% — virality isn't converting. Add Spotify CTAs to TikTok content."
- **Base vs moment:** `followers.total` + `popularity` + web coverage → "1.2M
  followers, popularity 41, no press in 60 days — a large dormant base; the play
  is reactivation, not discovery."
- **Routing:** `events` + web/deep venue history → "four dates in the Midwest,
  none on the coasts where the last tour sold out — an under-served market."
- **Peer sizing:** `spotify/artist` on each peer → followers/popularity table →
  "the three peers slightly above are the collab targets; the ones far above
  are exposure plays."

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

## 1. Catalog Momentum

**Question:** "Which songs are gaining, and which should we push?"

```bash
# 1. Resolve the artist and enumerate the catalog
curl -s "$RECOUP_API/spotify/search?q={ARTIST}&type=artist" -H "$AUTH"           # → spotify artist id
curl -s "$RECOUP_API/spotify/artist/albums?id={SPOTIFY_ARTIST_ID}&include_groups=album,single&limit=50" -H "$AUTH"

# 2. Capture today's play counts for every album (idempotent, minutes)
curl -s -X POST "$RECOUP_API/research/measurement-jobs" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"scope":{"album_ids":["{ALBUM_ID_1}","{ALBUM_ID_2}"]},"source":"current"}'

# 3. Read the counts per album, then the deltas per focus track
curl -s "$RECOUP_API/research/playcounts?spotify_album_id={ALBUM_ID}" -H "$AUTH"
curl -s "$RECOUP_API/research/track/playcount-deltas?isrc={ISRC}&since=2026-01-01" -H "$AUTH"

# 4. Full dated series for the tracks that matter
curl -s "$RECOUP_API/research/tracks/{ISRC}/measurements" -H "$AUTH"
```

**What to synthesize:** Rank tracks by plays gained over the window (not by
lifetime total). Old songs gaining faster than the new release = catalog
momentum to amplify; the new release flat after two captures = a promotion
problem, not a catalog problem. State the span every delta covers.

---

## 2. Social-to-Streaming Pipeline

**Question:** "Is social virality translating to Spotify growth?"

```bash
# 1. Refresh the connected profiles (rostered artist) and read follower counts
curl -s -X POST "$RECOUP_API/artist/socials/scrape" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"artist_account_id":"{ARTIST_ACCOUNT_ID}","posts":12}'
curl -s "$RECOUP_API/artists/{ARTIST_ACCOUNT_ID}/socials" -H "$AUTH"

# 2. Play-count deltas over the same window
curl -s "$RECOUP_API/research/track/playcount-deltas?isrc={ISRC}&since={WINDOW_START}" -H "$AUTH"

# 3. Narrative context for any spike
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} viral TikTok moment 2026","max_results":10}'
```

**What to synthesize:** Compare social follower change against play-count
change over the same span. Social up, plays flat = the content isn't pointing
at the music. Store both readings so next time is a real comparison.

---

## 3. Geographic & Tour Strategy

**Question:** "Where should this artist tour?"

> There is no audience-geography endpoint. Geography comes from the artist's
> own live-events history plus web/deep research on venues and festivals.

```bash
# 1. Upcoming and recent shows (exact — resolved through the connected live-events profile)
curl -s -X POST "$RECOUP_API/research/events" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"artist_id":"{ARTIST_ACCOUNT_ID}"}'

# 2. Venue history, festival fit, recent touring — web/deep research
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} tour dates venues capacity 2025 2026","max_results":10}'
curl -s -X POST "$RECOUP_API/research/deep" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} touring history, venue sizes, and festival appearances over the last two years"}'
```

**What to synthesize:** Markets the artist has played and sold, markets peers
in the same lane tour successfully (from web research), and the gaps between
them. Cite the source for every venue or sell-out claim.

---

## 4. A&R Discovery

**Question:** "Find emerging artists in [genre] before they blow up"

> There is no similar-artists endpoint. Candidates come from web coverage;
> sizing comes from the Spotify artist object.

```bash
# 1. Surface candidate names from the web (scene round-ups, "artists to watch", viral-song coverage)
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"emerging {GENRE} artists to watch 2026","max_results":15}'

# 2. Resolve and size each candidate
curl -s "$RECOUP_API/spotify/search?q={candidate}&type=artist" -H "$AUTH"
curl -s "$RECOUP_API/spotify/artist?id={candidate_spotify_id}" -H "$AUTH"            # followers.total, popularity, genres

# 3. Coverage signals = interest signal (press, editorial adds, label co-signs)
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{candidate} signed OR playlist OR premiere","max_results":10}'

# 4. Why this one (cited narrative, only for the shortlist)
curl -s -X POST "$RECOUP_API/research/deep" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"why is {candidate} gaining attention in {GENRE} right now?"}'
```

**What to synthesize:** A ranked shortlist: modest `followers.total`, rising
`popularity`, fresh coverage with links. Rank by those signals yourself; no
endpoint scores candidates for you.

---

## 5. Peer Comparison

**Question:** "How does our artist compare to their peers?"

For each artist in the set (yours + named peers):

```bash
curl -s "$RECOUP_API/spotify/search?q={artist}&type=artist" -H "$AUTH"
curl -s "$RECOUP_API/spotify/artist?id={spotify_id}" -H "$AUTH"                     # followers.total, popularity, genres
curl -s "$RECOUP_API/spotify/artist/topTracks?id={spotify_id}" -H "$AUTH"           # what carries them today
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{artist} label management recent release","max_results":8}'
```

**What to synthesize:** A side-by-side table (followers, popularity, top
tracks, label) and where your artist under-indexes. Peers slightly above are
collaboration targets; peers far above are exposure plays.

---

## 6. Viral Song Autopsy

**Question:** "Why did this song go viral? Can we replicate it?"

```bash
# 1. Resolve the track and its album
curl -s "$RECOUP_API/spotify/search?q={TRACK_NAME} {ARTIST}&type=track" -H "$AUTH"   # → track id, album id, ISRC

# 2. Measure it now and read the series (a first capture is the baseline for next time)
curl -s -X POST "$RECOUP_API/research/measurement-jobs" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"scope":{"album_ids":["{ALBUM_ID}"]},"source":"current"}'
curl -s "$RECOUP_API/research/tracks/{ISRC}/measurements" -H "$AUTH"

# 3. Narrative — what happened, where, and who drove it
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{TRACK_NAME} {ARTIST} viral TikTok moment","max_results":10}'
curl -s -X POST "$RECOUP_API/research/deep" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"why did {TRACK_NAME} by {ARTIST} go viral, and on which platform did it start?"}'
```

**What to synthesize:** A dated timeline built from cited coverage, aligned
with the measured play-count series where captures exist. Per-song TikTok
counts are not in the API — get that narrative from web/deep research, never
fabricated numbers.

---

## 7. Release Strategy Timing

**Question:** "When should we release, and how should we roll it out?"

```bash
# 1. Past releases and their dates
curl -s "$RECOUP_API/spotify/artist/albums?id={SPOTIFY_ARTIST_ID}&include_groups=album,single&limit=50" -H "$AUTH"

# 2. How past releases moved the catalog (where the store has history)
curl -s "$RECOUP_API/research/tracks/{ISRC}/measurements" -H "$AUTH"
curl -s "$RECOUP_API/research/track/playcount-deltas?isrc={ISRC}&since={RELEASE_DATE}" -H "$AUTH"

# 3. Peers' release cadence and what the press picked up
curl -s "$RECOUP_API/spotify/artist/albums?id={peer_spotify_id}&include_groups=album,single&limit=20" -H "$AUTH"
curl -s -X POST "$RECOUP_API/research/web" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"query":"{ARTIST} new single announcement premiere","max_results":10}'
```

**What to synthesize:** Release timing grounded in the artist's own cadence
and measured post-release lift, peers' cycles, and which platform the current
coverage is coming from.

---

## 8. People Outreach (Managers, A&R, Press)

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

The 8 workflows above are **building blocks, not complete answers**. Almost no
real user question maps cleanly onto exactly one workflow — the real deliverable
is usually a chain: `Workflow A` → `Workflow B` → external tool call → hand off
to another skill.

This section teaches you how to compose.

### The three chain patterns

Every chain you'll ever build is one of three shapes:

| Pattern | Shape | Example |
| ------- | ----- | ------- |
| **Data → Data** | Workflow A's output feeds Workflow B's input | Peer comparison (W5) returns the peer set → for each peer, pull top tracks and coverage (W5 step 3) |
| **Data → Draft** | Research output becomes a deliverable the user can act on | Peer research (W5) + people search (W8) → drafted outreach email the user reviews and sends themselves |
| **Skill → Skill** | Finish with this skill, hand off to another | Catalog momentum (W1) → hand off to a `recoup-content-*` skill for a one-sheet; or to `recoup-release-plan-rollout` for timing |

Most real deliverables are all three stacked: compose several workflows (Data →
Data), turn the result into a draft (Data → Draft), then hand off whatever
remains to another skill (Skill → Skill).

### What this skill produces

Beyond the API calls, the agent running this skill typically produces:

- **Written drafts** for the user to act on — outreach emails, pitch copy, press
  blurbs, DSP pitches. This skill drafts; the user sends. It does not execute
  external-facing actions (no email sending, no social posting, no contacting
  managers).
- **Artist workspace writes** — save synthesized research to `context/artist.md`,
  `research/{date}.md`, `releases/{slug}/RELEASE.md`. See "Saving research" above.
- **Handoffs to other skills** — the `recoup-content-*` skills (promo content,
  captions, one-sheets), `recoup-release-plan-rollout` (release lifecycle), the `recoup-roster-*`
  skills (workspace setup/lookup), `recoup-content-reactive-post` (turn a
  cultural moment into a post).

### Chaining rules (read before composing)

1. **Don't re-fetch what you already have.** If `/spotify/artist` already gave
   you the peer's snapshot, reuse it — don't call it again.
2. **Preserve artist context through the chain.** Every downstream step should
   reference the user's specific artist data (play-count deltas, follower
   counts, coverage), not generic templates. That's what makes the final output
   feel researched instead of auto-generated.
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
Step 1 — Size the artist (Workflow 5, own artist only)
  Calls: /spotify/search → /spotify/artist (followers.total, popularity, genres)
         + /artists/{id}/socials (rostered) + one POST /research/web for recent coverage
  Writes: context/artist.md (if workspace exists)
  Output: artist context — size, lane, what's current

Step 2 — Build and narrow the peer set (Workflow 5 on named peers)
  Input: peers the user names, plus names surfaced by web coverage of the lane
  Filters: /spotify/artist on each — slightly bigger = ideal; same genres;
           coverage in the last 90 days
  Output: 3-5 ranked peer candidates

Step 3 — Find each target's manager / A&R (Workflow 8)
  For each peer in Step 2:
    POST /research/people  {query: "manager for {peer}"}
    POST /research/enrich  {input, schema: {type: "object", properties: {name, role, email, recent_signings}}}
  Output: ranked outreach list with contact + angle

Step 4 — Draft outreach (LLM, no tool call)
  Reference:
    - Artist X specifics from Step 1 (followers, genres, what's current)
    - Peer specifics from Step 3 (recent signings, stylistic fit)
  Output: personalized drafts — NOT generic "love your music" copy.
  Present drafts to the user with recipient, subject, and body.
  The user sends them manually.

Optional handoff:
  → recoup-content-write-caption: draft the follow-up nurture sequence
  → recoup-release-plan-rollout: if a collab lands, open a RELEASE.md
```

---

### Example B — "How is Artist X doing, and what's next?"

**User question:** State of the artist + recommended next move.

```text
Step 1 — Snapshot
  Calls: /spotify/artist (followers.total, popularity)
         + /artists/{id}/socials (per-platform followers)
         + Workflow 1 (measurement job → playcounts → playcount-deltas on focus tracks)
         + POST /research/web (coverage in the last 14 days)
  Output:
    - size and current favor
    - which tracks gained plays over the window, and by how much
    - anything real that happened (with source links)

Step 2 — Diagnose (Workflow 2: social-to-streaming)
  Input: follower counts + play-count deltas from Step 1
  If socials grew and plays didn't → conversion gap
  If plays grew on catalog tracks, not the new release → promotion gap
  Output: the named gap

Step 3 — Decide the lever
  Inputs: the snapshot from Step 1, the gap from Step 2
  Pick which lever to pull first (catalog push vs social-to-DSP CTAs vs
  organic content) and say why, in this skill's output.

Step 4 — HANDOFF to recoup-release-plan-rollout
  If Step 3 recommends a new release:
    Open releases/{slug}/RELEASE.md
    Populate the DSP pitch from Step 1 data

Human-approval gate: none (internal reasoning only, no external contacts).
```

---

### Example C — Market scouting for a TikTok-driven breakout

**User question:** "Find tracks that are blowing up on TikTok and the indie artists driving them."

```text
Step 1 — Find candidates (no charts/discover endpoints — start from the web)
  Calls: POST /research/web {query: "songs blowing up on TikTok {GENRE} 2026"}
         POST /research/web {query: "{GENRE} viral TikTok sound indie artist"}
  Output: candidate track + artist list, each with a source link

Step 2 — Size and measure (Workflow 4 + Workflow 6)
  For each candidate:
    /spotify/search → /spotify/artist (followers.total, popularity)
    /spotify/search?type=track → album id → POST /research/measurement-jobs (baseline capture)
  Output: ranked by modest followers + rising popularity + fresh coverage

Step 3 — Enrich (optional, deep context)
  POST /research/deep {query: "why is {track} going viral?"}
  Output: cited narrative — the cultural thread driving the trend

Step 4 — Write to artist workspace
  If any candidate warrants ongoing tracking:
    Create context/artist.md scaffold via recoup-roster-add-artist
    Save Step 1-3 synthesis to research/{date}-tiktok-scout.md
    (the baseline capture from Step 2 makes next month's delta real)

Step 5 — HANDOFF to recoup-content-reactive-post
  If the trend itself (not the artist) is the opportunity:
    recoup-content-reactive-post owns: turn the cultural moment into a post
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

A three-step chain that answers the real question beats an eight-step chain that
shows off every endpoint.

---

## Building Your Own Workflows

The power is in combining data types:

| What You Need | Endpoint | Use For |
|---------------|----------|---------|
| **How big** — size and favor | `/spotify/artist` (`followers.total`, `popularity`, `genres`) | Sizing artists and peers, base-vs-moment reads |
| **How it's moving** — measured plays | `/research/playcounts`, `/track/playcount-deltas`, `/tracks/{isrc}/measurements`, `/measurement-jobs` | Catalog momentum, release lift, weekly deltas |
| **What** — catalog | `/spotify/artist/albums`, `/spotify/artist/topTracks`, `/spotify/album` | Release history, focus tracks, ISRCs and album ids |
| **Who follows** — social reach | `/artists/{id}/socials`, `/artist/socials/scrape` | Social-to-streaming conversion, platform priority |
| **Where** — live | `/research/events` | Tour routing, market gaps |
| **Why** — narrative + context | `/research/web`, `/research/deep` | Coverage, cultural positioning, press strategy, discovery |
| **People** — industry contacts | `/research/people`, `/research/enrich`, `/research/extract` | Outreach, CRM enrichment |

Discovery → web coverage + Spotify sizing; momentum → two captures and a delta;
headline comparison → `followers.total` and `popularity` side by side.
