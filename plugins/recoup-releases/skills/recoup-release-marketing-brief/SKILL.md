---
name: recoup-release-marketing-brief
description: >
  ARTIFACT: a data-grounded pre-release CREATIVE BRIEF — 3 visualizer concept
  directions, 5 content angles, platform hooks, ranked playlist targets, and a
  narrative thread, all grounded in the artist's real audience data. Use for
  "creative directions for {release}", "content angles for {release}", "prep
  {release}", "what should I make for {release}", "pre-release brief for {release}".
  The output is structured INPUT for downstream creative work — not finished
  assets. This is one of three release skills — for the DATED SCHEDULE use
  recoup-release-campaign; for the master DOC + DSP pitch use recoup-release-doc;
  this one is the CREATIVE BRIEF. Refuses to invent release details (sound, lyrics,
  themes) — asks when missing.
license: Proprietary
metadata:
  owner: agent@recoupable.com
  status: draft
  user-invocable: true
---

# Release Marketing Brief

A pre-release marketing brief. The skill exists because generic AI-generated
marketing copy is slop, and an LLM asked for "marketing ideas" with no
grounding will always produce slop. This skill produces **structured input**
that's grounded in real audience data and the user's stated creative direction
— not finished marketing assets.

The output is the scaffold: visualizer directions, content angles, playlist
targets, narrative thread. The user renders those into actual videos, copy,
and creative through whatever pipeline they have.

## When to use

- "Release pack for {release name}"
- "Prep {release}" / "Rollout plan for {release}"
- "Marketing for {release}" / "What should I do for {release}"
- "Pre-release brief for {release}" / "Marketing pack for {release}"

For ongoing weekly artist tracking, use `recoup-weekly-brief`. For one-shot
artist research with no release context, use `recoup-artist-research`.

## Setup

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## What you need from the user (refuse to proceed without it)

A release pack requires **release-specific facts** the API does not have. Before
fetching anything, confirm with the user:

1. **Artist** (workspace slug or Chartmetric ID)
2. **Release name** (track or album title)
3. **Release date** (or "TBD" if not set — still useful)
4. **Release type** (single, EP, album, deluxe, remix, collab, soundtrack)
5. **One-line creative direction** — vibe / themes / inspirations / collaborators
6. **What asset gaps exist** — e.g., "no music video yet", "no cover art lock",
   "we have stems but no remix plan"

If any of #2, #3, #5 are missing, **ask** — don't invent. A release pack about
a release the agent has no concrete information about is exactly the slop this
skill is meant to prevent.

## Workflow

### 1. Confirm release facts (above)

Ask once, get the 6 inputs, proceed. Do not loop on this.

### 2. Pull artist context (in parallel)

```bash
# Audience demographics — drives platform mix
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=tiktok" \
  -H "x-api-key: $RECOUP_API_KEY" &

curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" \
  -H "x-api-key: $RECOUP_API_KEY" &

# Similar artists — drives playlist targets + collab/feature ideas
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&limit=20" \
  -H "x-api-key: $RECOUP_API_KEY" &

# Current playlist position — drives gap analysis for new pitches
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&platform=spotify&status=current&limit=50" \
  -H "x-api-key: $RECOUP_API_KEY" &

wait
```

> **Geographic rollout note:** there is no `/research/cities` endpoint anymore.
> For geo hooks, use any non-empty `/research/audience` country data, else a
> `POST /research/web` query for the artist's strongest markets — and label it as
> web-sourced, not first-party analytics.

### 3. (Optional) Track lookup if the release exists in Chartmetric

If the release is already in the system (e.g., a re-pitch of a soon-to-drop
single that already has a `cm_track_id`):

```bash
curl -s "$RECOUP_API/research/track?id={CM_TRACK_ID}" \
  -H "x-api-key: $RECOUP_API_KEY"
```

For most pre-release packs, the track isn't ingested yet — skip this step.

### 4. Synthesize the pack

Write to `releases/{artist-slug}/{release-slug}/brief/brief-$(date +%F).md` (the
shared release workspace). The `{release-slug}` is the kebab-case release title.

Template:

```markdown
# Release Pack — {Artist} — *{Release Name}*
**Type:** {single|EP|album|...} | **Release date:** {YYYY-MM-DD or "TBD"} | **Generated:** {YYYY-MM-DD}

## Creative direction (from user)
{The 1-line creative direction the user gave verbatim. This is the source of truth.
Everything below is in service of THIS direction.}

## Narrative thread
{2–4 sentences. The cohesive story for the rollout. What's the one thing
listeners should remember after the campaign. Anchored in the creative direction,
not invented.}

## 3 visualizer concept directions

### Direction A — {short name, e.g., "Mood Piece"}
- **Concept (2 sentences):** ...
- **Visual references:** {3–5 reference touchpoints — artists, films, eras}
- **Production bar:** {low / med / high — be honest about what this needs}
- **Why this for {Artist}:** {tie to audience data — TT skew, geo, similar-artist visual language}

### Direction B — {short name, e.g., "Narrative"}
{Same structure}

### Direction C — {short name, e.g., "Archive / Lo-Fi"}
{Same structure}

## 5 content angles

Each angle is a *premise for a content series*, not a single post. Each should
be sustainable across 4–8 pieces of content.

| # | Angle | Why it works for THIS release | First 3 piece ideas |
|---|---|---|---|
| 1 | {name} | {tie to audience + creative direction} | {3 concrete posts} |
| 2 | ... | ... | ... |
| ... | ... | ... | ... |

## Platform hooks

| Platform | Audience signal | Hook approach |
|---|---|---|
| TikTok | {top age/gender/geo from audience endpoint} | {1–2 hook formats matched to that audience} |
| IG Reels | {top age/gender/geo from audience endpoint} | {1–2 hook formats} |
| YouTube Shorts | {if data available} | {hook format} |
| Twitter/X | {if relevant for this artist's lane} | {hook format} |

## Playlist targets (ranked)

| Playlist | Curator/owner | Why this fits | Warm path? |
|---|---|---|---|
| {top from similar artists' placements that this artist isn't on} | ... | ... | {yes/no/unknown} |
| ... | ... | ... | ... |

Source the targets from `/research/playlists` cross-referenced against
`/research/similar` — playlists where peers sit and this artist doesn't.

## Geographic rollout

Top markets for the artist (from `/research/audience` country data if present, else `POST /research/web` — label web-sourced):
1. {city, country, listeners}
2. ...
3. ...

Rollout implications: {1–2 sentences on which cities to weight, e.g., "Geo-pinned
content for the top 3 cities; physical events viable in top 1 if budget allows."}

## Open creative decisions (for the user to resolve)

- {gap from input #6, or surfaced from analysis}
- ...

## What this pack is NOT

This is structured input for downstream creative work. It is not:
- Final copy
- Finished video scripts
- Approved playlist pitch emails (use `recoup-playlist-intelligence` for that)
- Cover art or visualizer assets

Take the directions above into whatever creative pipeline you use, and produce
the assets.

---
*Generated {ISO timestamp}. Re-run with `/recoup-release-marketing-brief {release-slug}`.*
```

### 5. Print a short chat summary

3–5 sentences: the creative direction restated, the 3 visualizer direction
names, and the top 3 content angle names. So the user can decide whether to
open the file.

## What this skill refuses to do

- **No inventing the release.** If the user can't tell us what the release
  sounds like or what it's about in one line, this skill stops. A release pack
  for a release the agent has no creative knowledge of will produce slop —
  refuse instead.
- **No fake playlist names.** Playlist targets come from `/research/playlists`
  + `/research/similar`. If no good targets surface, the section says so.
- **No copy generation.** This is a brief, not assets.
- **No hallucinated audience numbers.** If `/research/audience` returns thin
  data for the platform, the platform hooks section says "thin audience data —
  weight by similar-artist behavior instead."

## Audience-driven hooks

The platform hooks section is the most-likely-to-go-slop part. To prevent that,
anchor every hook in a concrete audience data point:

❌ "TikTok hook: relatable Gen Z humor about heartbreak"
✅ "TikTok hook: top audience is F 18–24 in NYC + LA (37% of artist's TT
   audience). Hook format that's worked for similar acts: POV setup where the
   creator lip-syncs the bridge over a personal story. Source: {similar artist
   {name}} has done this format with {N}K avg views."

If you can't ground a hook in a number, drop the hook.

## Saving

Path: `releases/{artist-slug}/{release-slug}/brief/brief-$(date +%F).md`

This is the `brief/` folder of the shared release workspace, so multiple releases
per artist don't collide. Re-running the same day is a no-op (file exists → tell
the user). Re-running a different day creates a new dated file — useful for
tracking how the pack evolves as more data comes in.

## Credit awareness

The 5 parallel calls in step 2 are typically 1 credit each (≤5 credits per
run). The optional `/research/track` adds 1 more. Total budget per pack: ~6
credits.

## References

- `references/endpoints.md` — full curl examples
- `references/response-shapes.md` — exact JSON shapes
- `recoup-playlist-intelligence` — for the actual playlist pitch emails
- `recoup-audience-analysis` — for deeper geographic / demo analysis
- `recoup-weekly-brief` — for ongoing tracking after release
