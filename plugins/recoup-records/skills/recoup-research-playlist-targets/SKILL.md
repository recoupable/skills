---
name: recoup-research-playlist-targets
description: Find which playlists an artist or whole catalog should target and where the placement gaps are — catalog-wide playlist strategy from research data. Use for "which playlists should we target", "placement gaps", "editorial vs algorithmic", or "which catalog tracks to push". This is desk strategy from data; to pitch ONE song from its audio use recoup-song-placement-pitch.
---

# Recoup Research — Playlist Targets

Catalog-wide playlist strategy from research data (not one audio file).

```bash
export RECOUP_API="https://api.recoupable.com/api"   # auth header: x-api-key: $RECOUP_API_KEY
```

## Procedure

- `/playlists?artist={ARTIST}&status=current` for placements; `status=past` for
  re-pitch opportunities.
- `/similar` → `/playlists` on each peer → playlists hosting 2+ peers you're NOT on
  are the warmest targets (the gap analysis).
- `/track/playlists?id={track_id}&editorial=true` (5 credits) for per-track
  editorial coverage.
- `/metrics` (`playlists_editorial_current`) to judge editorial vs algorithmic balance.

Answer: target playlists (ranked, warmest first), placement gaps, editorial vs
algorithmic, and which catalog tracks to push. Full chains in
`references/workflows.md` (Playlist Pitching Intelligence, Catalog Optimization).

## Guardrails

- **No invented placements.** `followers_total` is a formatted string ("34.3M") —
  parse it if sorting numerically.
- **Credits:** surface `checkoutUrl` on `insufficient_credits`.

## References

- `references/workflows.md` — playlist pitching + catalog optimization chains.
