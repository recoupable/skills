---
name: recoup-research-weekly-brief
description: The recurring "what changed this week" update for an artist — streaming/social deltas vs the last run, milestones, and a spike/drop check. Use for "weekly brief", "what's new this week", "what changed for [artist]", or "are streams spiking or dropping". Recurring and dated; diffs against your own prior file. For a one-time full sweep use recoup-research-artist-overview.
---

# Recoup Research — Weekly Brief

The recurring artifact a customer opens. Snapshots, not time series — the delta is
vs your last file.

```bash
export RECOUP_API="https://api.recoupable.com/api"   # auth header: x-api-key: $RECOUP_API_KEY
```

## Procedure (idempotent, dated, diffed)

**Idempotency:** if today's file already exists at
`artists/{slug}/research/brief-$(date +%F).md`, stop and surface it. Read the prior
brief for the baseline, then fan out in parallel:

```bash
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify"   -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=tiktok"    -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=instagram" -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &
curl -s "$RECOUP_API/research/insights?artist={ARTIST}"   -H "x-api-key: $RECOUP_API_KEY" &
wait
```

Compute deltas vs the prior brief. **Streaming spot-check sub-mode** ("are streams
spiking?"): pull Spotify metrics + playlists + milestones, classify SPIKE/DROP/FLAT
(≥15% or a large absolute move), and name the likely cause only if it appears in the
feed. Write a dated file + a short chat summary. First reading shows current values
with "first reading" in the Δ column.

## Guardrails

- **Snapshots, not history** — deltas come from diffing your own prior file.
- **No invented numbers / no causation without evidence.**
- **Credits:** surface `checkoutUrl` on `insufficient_credits`.

## References

- `references/workflows.md` — metrics interpretation + TikTok-to-Spotify pipeline.
