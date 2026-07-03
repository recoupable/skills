---
name: recoup-research-find-talent
description: Find emerging or unsigned artists you don't already track — A&R scouting that fans out from an anchor artist and sizes candidates, plus "why did this song go viral". Use for "find emerging artists", "A&R scouting", "who should we sign", "scout new talent in [genre]", or "why did [song] go viral". For research on an artist you already have, use recoup-research-artist-overview.
---

# Recoup Research — Find Talent

A&R discovery of artists you *don't* already track.

```bash
export RECOUP_API="https://api.recoupable.dev/api"   # auth header: x-api-key: $RECOUP_API_KEY
```

Discovery starts from a known **anchor** artist and fans out through `/similar`,
validated with `/metrics`. Use web/deep research to find anchors or scan a
scene. Full chains in `references/workflows.md` (A&R Discovery, Viral Song
Autopsy).

## Procedure

1. Pick an anchor in the target sound (or scout candidate names via
   recoup-research-the-web).
2. Fan out: `/similar?artist={ANCHOR}&musicality=high&genre=high&limit=50`
   (`musicality=high` surfaces smaller, undiscovered acts).
3. Size each candidate with `/metrics` (emerging = real growth, modest absolute);
   `/similar` has no scores, so rank candidates yourself.
4. Editorial pickup (`playlists_editorial_current`) = label-interest signal.
5. For "why did [song] go viral": `/track` + `/milestones` + web.

Return ranked candidates with the signal that flagged each (e.g. low monthly
listeners + rising editorial pickup = the breakout window).

## Guardrails

- **No invented numbers.** Missing metric → `—`.
- **Rank by the metrics snapshot**, not by `/similar` order (it has no stage/score).
- **Credits:** surface `checkoutUrl` on `insufficient_credits`.

## References

- `references/workflows.md` — A&R discovery + viral-autopsy chains.
