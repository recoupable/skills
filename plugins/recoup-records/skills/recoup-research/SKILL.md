---
name: recoup-research
description: All music-industry research for an artist or any entity, in one place. Modes — overview (full artist sweep), audience (demographics/geography/markets/tour routing), competition (compare artists, positioning, collaborators, release timing), discover (find emerging/unsigned talent + viral songs), playlists (which playlists an artist OR a whole catalog/roster should target + gaps), contacts (find managers/A&R/press + draft outreach), tiktok (which of an artist's songs are popping), weekly-update (recurring "what changed" + streaming spikes), and web (search the open web / deep research / why a song or release went viral, with citations / enrich any company, label, venue, or person). Use for "research [artist]", "tell me about [artist]", "where are the fans", "compare [a] vs [b]", "find collaborators", "find emerging artists", "which playlists", "find the manager for", "which songs are blowing up on TikTok", "weekly brief", "are streams spiking", "search the web", "deep research [topic]", or "enrich [entity]". Picks the mode from the ask. This is data + open-web research (including playlist strategy and "why did X happen, with citations"): for analysis of a track's AUDIO file use recoup-songs; for catalog royalty/rights/valuation deal work use recoup-catalogs.
---

# Recoup Research

One skill for every research question — about an artist, their market, their
competition, their playlists, the people around them, or anything on the open
web. It **picks a mode from what you ask**, runs the right Recoup research API
calls, and synthesizes an answer (never a raw JSON dump, never a fabricated
number).

```bash
export RECOUP_API_KEY="recoup_sk_..."   # already set in Recoup sandboxes
export RECOUP_API="https://api.recoupable.com/api"
```

All GET endpoints live under `$RECOUP_API/research` and auth with `x-api-key`.
The API is backed by **Songstats**; entity IDs are short alphanumeric strings.
Full curl examples, response shapes, and workflow chains ship alongside this
skill in `references/endpoints.md`, `references/response-shapes.md`, and
`references/workflows.md` — read them before calling.

## Mode dispatch (pick one from the ask)

| The user wants… | Mode | Core endpoints |
|---|---|---|
| "research [artist]", "tell me about", "overview", "how are they doing" | **overview** | profile + metrics + similar + playlists + audience + insights |
| "where are the fans", "demographics", "markets to expand", "tour routing" | **audience** | `audience`, `metrics` |
| "compare [a] vs [b]", "positioning", "find collaborators", "when to release" | **competition** | `similar`, `metrics`, `career` |
| "find emerging artists", "A&R scouting", "why did [song] go viral" | **discover** | `similar`, trends, `track` |
| "which playlists", "placement gaps", "editorial vs algorithmic" | **playlists** | `playlists`, `track/playlists` |
| "find the manager/A&R/press", "draft outreach" | **contacts** | `enrich`, `web`, `deep` |
| "which of their songs are popping on TikTok" | **tiktok** | `tracks`, `milestones`, `web`/`deep` |
| "weekly brief", "what's new this week", "are streams spiking/dropping" | **weekly-update** | `metrics` ×3 + `milestones` + `insights` (diffed vs last run) |
| "search the web", "deep research", "what does this URL say", "enrich [entity]" | **web** | `web`, `deep`, `extract`, `enrich` |

If the ask spans modes ("research them and find their manager"), run the modes
in sequence. If unsure which mode, default to **overview**, then narrow.

Before any artist mode: check the workspace `context/artist.md` — don't
re-research what's already known.

---

## Mode: overview (the default full sweep)

Run in parallel, then synthesize. Pass `artist=<name>`; use `id=<provider id>`
for an exact entity.

```bash
curl -s "$RECOUP_API/research/profile?artist={ARTIST}"  -H "x-api-key: $RECOUP_API_KEY" | jq '.artist_info'
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY" | jq '.stats[0].data'
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&limit=20" -H "x-api-key: $RECOUP_API_KEY" | jq '.artists'
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=current" -H "x-api-key: $RECOUP_API_KEY" | jq '.placements'
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY" | jq '.audience'
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" | jq '.insights'
```

**Read the data right:** `/profile` carries **no** counts (identity only);
`/metrics?source=spotify` carries the counts under `stats[0].data`
(`monthly_listeners_current`, `followers_total`, `popularity_current`,
`playlists_editorial_current`, `playlist_reach_current`). Call `/metrics` once
per platform (`spotify`, `tiktok`, `instagram`, `youtube_channel`).

**Synthesize** into: Genres/Country · Streaming snapshot (per platform) ·
Audience profile · Playlist position · Competitive position (peers from
`/similar`, sized via `/metrics`) · Key insights · Recommendations.

## Mode: audience

`audience?artist=&platform=instagram|tiktok|youtube` is the geography + demos
source (the only one — `cities` was removed). Pull age/gender/country, then
answer the real question: **where to grow, where to tour, TikTok→Spotify
conversion**. Synthesize markets ranked by opportunity, not a raw dump.

## Mode: competition

`/similar` for the peer set, `/metrics` to size each peer (judge stage), `/career`
for trajectory. Answer: how they stack up, who's a realistic collaborator (peers
at their level, not superstars), and release-timing whitespace vs peers.

## Mode: discover

A&R discovery of artists you *don't* already track. Use `/similar` to fan out
from a seed, size candidates with `/metrics` (emerging = real growth, modest
absolute), and for "why did [song] go viral" pull `/track` + `milestones` + web.
Return ranked candidates with the signal that flagged each.

## Mode: playlists

Catalog-wide playlist strategy from research data (not one audio file):
`/playlists?status=current` for placements, `/track/playlists?id=` (5 credits)
for per-track coverage. Answer: target playlists, placement gaps, editorial vs
algorithmic balance, and which catalog tracks to push.

## Mode: contacts

Find industry people (managers, A&R, press) and draft outreach. Lead with
`/research/enrich` (structured facts about a label/manager/company), fall back to
`/web` + `/deep` for narrative and contact leads. **Never fabricate a contact** —
only surface people who appear in sourced results; draft outreach only after the
person is confirmed.

## Mode: tiktok

"Which of {artist}'s songs are popping on TikTok." The API does **not** expose
per-song TikTok counts, so build a per-song **signal** view from what exists:
track-level activity (`/tracks`, `/milestones`) + web/deep research with
citations + artist-level TikTok metrics. **Refuse to fabricate per-track
uses/views** — label everything as a signal, cite sources, and rank by signal
strength.

## Mode: weekly-update (recurring, dated, diffed)

The recurring artifact a customer opens. **Idempotency:** if today's file already
exists at `artists/{slug}/research/brief-$(date +%F).md`, stop and surface it.
Read the prior brief for the baseline, then fan out in parallel:

```bash
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify"   -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok"    -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=instagram" -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/insights?artist={ARTIST}"   -H "x-api-key: $RECOUP_API_KEY" &
wait
```

Compute deltas vs the prior brief (snapshots, not time series — the delta is vs
your last file). **Streaming spot-check sub-mode** ("are streams spiking?"):
pull only Spotify metrics + playlists + milestones, classify SPIKE/DROP/FLAT
(≥15% or a large absolute move), and name the likely cause (editorial add /
release / chart entry) only if it appears in the feed. Write a dated file +
print a short chat summary. First reading shows current values with "first
reading" in the Δ column.

## Mode: web (general web + any entity)

Not artist-only and the graceful-degradation fallback. `POST /research/web`
(quick ranked, seconds, cheap), `/deep` (cited narrative, 2+ min, expensive),
`/extract` (read specific URLs), `/enrich` (structured facts about ANY entity —
label, manager, venue, brand, person; schema must include `"type":"object"`).
**Verify citations** (every material claim cited; the source actually supports
it; drop dead URLs) and **distill to a sourced one-page dossier** (fact vs
inference vs open question) — not a link dump.

---

## Graceful degradation (any artist mode)

If structured data is thin (empty `results`, thin `/profile`+`/metrics`, or a
`501`), fall through to the **web** mode chain: `/web` → `/enrich` → `/deep`.
For very emerging artists Songstats may have nothing — web is the alternative.

## Guardrails (all modes)

- **No invented numbers.** Missing metric → `—`. Never substitute a guess.
- **No causation without evidence.** Name a driver only if it appears in the data
  this run; otherwise "no obvious driver."
- **Credits:** on `{ "error": "insufficient_credits" }`, surface the `checkoutUrl`
  (+ `remaining_credits`/`required_credits`); don't silently skip or retry.
- **Snapshots, not history.** Deltas come from diffing your own prior file.
- **Don't overwrite `context/artist.md`** with dynamic research; save sweeps to
  `research/` with a date. Suggest profile updates, don't auto-apply.
- **Latency:** `/enrich` 60–90s, `/deep` 2+ min — set timeouts ≥3 min.

## References

- `references/endpoints.md` — full curl examples, params, credit costs, latency.
- `references/response-shapes.md` — actual JSON shapes per endpoint.
- `references/workflows.md` — multi-step chains and when NOT to chain.
