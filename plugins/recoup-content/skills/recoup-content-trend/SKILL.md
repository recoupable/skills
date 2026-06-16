---
name: recoup-content-trend
description: Turn a real, timely trigger into content for an artist — a fresh milestone (crossed 2B streams, added to a flagship playlist, a TV/film sync, a chart entry) or a current trend/sound. Use when the user says "they just hit [X], make something", "make something for the milestone", "what's the move right now", "make it feel current/timely", or "react to [news]". Reads the artist's research feed to find the real moment, picks the angle, then routes the actual asset to the right content skill (promo graphic / caption / short video). Not for evergreen "make a post" requests with no trigger — use the router for those.
---

# Recoup Trend-Jack (reactive content)

Most content skills answer "make me a [format]." This one answers a different question:
**"something is happening — what should we make of it?"** The trigger is *news*, not a
format. The job is to find the real moment, choose the angle, and hand the actual asset to
the skill that makes it. Never manufacture a moment that isn't real.

Scripts and references ship alongside this skill in its own `references/`; read them with
relative paths.

## When this fires vs. the router

- "Make a TikTok for Mari Vega" → a **format** request → router → `recoup-content-video`.
- "Mari just crossed 1M monthly listeners, make something" → a **trigger** → **this skill**.
- "What's the move for her right now?" → a **trigger** (find one) → **this skill**.

If the user already named both the trigger *and* the format ("milestone graphic for the 2B
streams"), you can skip straight to the format skill with the angle in hand — but still
verify the milestone is real first (step 2).

## Workflow

### 1. Resolve the artist + read context

Standard backbone. Resolve the workspace and IDs (see the account-resolver reference), read
`context/artist.md` (voice) and `context/audience.md` (how fans talk). These set the tone of
whatever you end up making.

### 2. Find the real trigger (don't invent one)

Pull the research feed and look for something genuinely fresh. See the research-context
reference for the auth + provider-ID chain and the `research_get` retry helper.

```bash
# Latest milestone (often empty; inspect fields — naming varies):
research_get "milestones?id=$PROVIDER_ID" \
  | jq -r 'if (.milestones|length)>0 then .milestones[-1] else "no fresh milestone" end'
# Recent activity feed — chart entries, syncs, co-signs (note: under .career, not .activities):
research_get "career?id=$PROVIDER_ID" \
  | jq -r '.career[0:5][]? | "\(.activity_date): \(.activity_text)"'
# A real playlist placement worth bragging about (followers_total is a string like "9.09M"):
research_get "playlists?id=$PROVIDER_ID" | jq -r '.placements[0:3][]? | .playlist_name'
```

For a *trend* (no milestone, "make it current") pull lightweight web intelligence and use it
only as **direction** for the format/look — never as a source of facts:

```bash
research_get "web?q=$(printf %s "$ARTIST_NAME current trends" | jq -sRr @uri)" | jq -r '.summary // .content'
```

**Triage the result:**
- **Fresh, real milestone/event** → that's the headline. Continue.
- **Only stale milestones (months old)** → tell the user there's no fresh moment; offer an
  evergreen post or a different angle instead of faking urgency.
- **Trend only** → use it to pick a timely format/reference; keep the facts from context.

### 3. Pick the angle + the format

Match the trigger to the asset that carries it best:

| Trigger | Best format → skill |
| --- | --- |
| Streams / followers milestone, playlist add, chart entry | `recoup-content-graphic` (a "the numbers" graphic) |
| Sync / press / co-sign, or a story to tell | `recoup-content-caption` (+ a graphic) |
| A sound/format trend, "make it move" | `recoup-content-video` (let the song's audio drive the edit) |

Write a one-line angle in the artist's voice ("2,000,000,000 streams. thank you 🤍") drawn
from `context/artist.md`, then hand off.

### 4. Route to the format skill — don't re-implement it

Invoke the chosen `recoup-content-*` skill with the trigger + angle as inputs. It already
owns generation, the audio→edit mapping, and the analyze gate. Your job ends at a correct,
real, well-framed brief plus the routing.

### 5. Verify + write back

Whatever asset comes back goes through the analyze gate (benchmarked against the artist's top
recent posts when available — see the analyze-gate reference) and is written into the
workspace with a `{what}: {why}` commit. A reactive post that ships late or off-fact is worse
than none — accuracy and timing are the whole point.

## Guardrails

- **Real or nothing.** Every number, date, and claim traces to the research feed or the
  workspace. If you can't verify the trigger, say so; don't generate around a guess.
- **Don't double-spend.** This skill *routes*; it doesn't run a second generation pipeline.
- **Scope stops at the asset.** Like the rest of the plugin, this produces the finished
  asset + caption — it does not post or schedule.
