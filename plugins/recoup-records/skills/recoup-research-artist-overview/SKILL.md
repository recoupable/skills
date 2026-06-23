---
name: recoup-research-artist-overview
description: Full research sweep on one of your artists — profile, streaming metrics, audience demographics/geography, competitive position, and which songs are popping on TikTok. Use for "research [artist]", "tell me about [artist]", "how are they doing", "where are the fans", "compare [a] vs [b]", "find collaborators", "when to release", or "which of their songs are blowing up on TikTok". Modes: overview, audience, competition, tiktok. For finding NEW artists use recoup-research-find-talent; for a recurring update use recoup-research-weekly-brief.
---

# Recoup Research — Artist Overview

Understand a known artist and their market: profile, metrics, audience, peers, and
TikTok momentum. Run the right calls, synthesize an answer — never a raw JSON dump,
never a fabricated number.

```bash
export RECOUP_API_KEY="recoup_sk_..."   # already set in Recoup sandboxes
export RECOUP_API="https://api.recoupable.com/api"
```

All GET endpoints live under `$RECOUP_API/research` and auth with `x-api-key`.
Backed by Songstats; entity IDs are short alphanumeric strings. Multi-step chains
and the interpretation cheat sheet ship alongside this skill in
`references/workflows.md` — read it before calling. Before any mode, check
`context/artist.md` — don't re-research what's already known.

## Mode: overview (default full sweep)

Run in parallel, then synthesize. Pass `artist=<name>`.

```bash
curl -s "$RECOUP_API/research/profile?artist={ARTIST}"  -H "x-api-key: $RECOUP_API_KEY" | jq '.artist_info'
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY" | jq '.stats[0].data'
curl -s "$RECOUP_API/research/similar?artist={ARTIST}&limit=20" -H "x-api-key: $RECOUP_API_KEY" | jq '.artists'
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&status=current" -H "x-api-key: $RECOUP_API_KEY" | jq '.placements'
curl -s "$RECOUP_API/research/audience?artist={ARTIST}&platform=instagram" -H "x-api-key: $RECOUP_API_KEY" | jq '.audience'
curl -s "$RECOUP_API/research/insights?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" | jq '.insights'
```

`/profile` carries **no** counts (identity only); `/metrics?source=spotify` carries
the counts under `stats[0].data`. Call `/metrics` once per platform (`spotify`,
`tiktok`, `instagram`, `youtube_channel`). Synthesize: Genres/Country · Streaming
snapshot · Audience profile · Playlist position · Competitive position · Key
insights · Recommendations.

## Mode: audience

`audience?artist=&platform=instagram|tiktok|youtube` is the geography + demos source.
Pull age/gender/country, then answer the real question: where to grow, where to
tour, TikTok→Spotify conversion. Rank markets by opportunity, not a raw dump.

## Mode: competition

`/similar` for the peer set, `/metrics` to size each peer, `/career` for trajectory.
Answer how they stack up, who's a realistic collaborator (peers at their level, not
superstars), and release-timing whitespace.

## Mode: tiktok

"Which of {artist}'s songs are popping on TikTok." The API does not expose per-song
TikTok counts — build a per-song **signal** view from track activity (`/tracks`,
`/milestones`) + web/deep research + artist-level TikTok metrics. **Refuse to
fabricate per-track uses/views** — label everything as a signal, cite sources, rank
by signal strength.

## Graceful degradation

If structured data is thin (empty results, thin profile+metrics, or a 501), fall
through to recoup-research-the-web. Very emerging artists may have nothing in
Songstats — the web is the alternative.

## Guardrails

- **No invented numbers.** Missing metric → `—`.
- **No causation without evidence.** Name a driver only if it appears in the data.
- **Credits:** on `{ "error": "insufficient_credits" }`, surface the `checkoutUrl`.
- **Snapshots, not history.** Deltas come from diffing a prior file.
- Don't overwrite `context/artist.md` with dynamic research; save to `research/` dated.

## References

- `references/workflows.md` — multi-step chains, interpretation cheat sheet, synthesis.
