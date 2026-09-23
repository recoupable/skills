---
name: recoup-research-weekly-brief
description: The recurring "what changed this week" update for an artist — streaming/social deltas vs the last run, milestones, and a spike/drop check. Use for "weekly brief", "what's new this week", "what changed for [artist]", or "are streams spiking or dropping". Recurring and dated; diffs against your own prior file.
---

# Recoup Research — Weekly Brief

The recurring artifact a customer opens. Play counts are dated captures in the
measurement store; audience and context are snapshots — the delta is vs your last file.

```bash
export RECOUP_API="https://api.recoupable.dev/api"   # auth header: x-api-key: $RECOUP_API_KEY
```

## Procedure (idempotent, dated, diffed)

**Idempotency:** if today's file already exists at
`artists/{slug}/research/brief-$(date +%F).md`, stop and surface it. Read the prior
brief for the baseline, then fan out in parallel:

```bash
# Streaming: capture this week's play counts, then read the store
curl -s -X POST "$RECOUP_API/research/measurement-jobs" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" -d '{"scope":{"album_ids":[...]},"source":"current"}'
curl -s "$RECOUP_API/research/playcounts?spotify_album_id={ALBUM_ID}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/research/track/playcount-deltas?isrc={ISRC}&since={PRIOR_BRIEF_DATE}" -H "x-api-key: $RECOUP_API_KEY"
# Audience: Spotify followers/popularity + connected social follower counts
curl -s "$RECOUP_API/spotify/artist?id={SPOTIFY_ARTIST_ID}" -H "x-api-key: $RECOUP_API_KEY"
curl -s "$RECOUP_API/artists/{ARTIST_ACCOUNT_ID}/socials" -H "x-api-key: $RECOUP_API_KEY"
# Context: one web search for press, playlist adds, announcements this week
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" -d '{"query":"{ARTIST} music news playlist press","max_results":10}'
```

Compute deltas vs the prior brief (play counts come with real capture dates, so
report the span each delta covers). **Streaming spot-check sub-mode** ("are streams
spiking?"): read `playcount-deltas` per focus track, classify SPIKE/DROP/FLAT (≥15%
or a large absolute move), and name the likely cause only if it appears in the web
results, with the source link. Write a dated file + a short chat summary. First
reading shows current values with "first reading" in the Δ column. Monthly listeners
are not available from any endpoint — never estimate them.

## Guardrails

- **Deltas are diffs** — play-count deltas from the store's dated captures, everything else from your own prior file.
- **No invented numbers / no causation without evidence.**
- **Credits:** surface `checkoutUrl` on `insufficient_credits`.

## References

- `references/workflows.md` — interpretation cheat sheet + the catalog momentum and social-to-streaming workflows.
