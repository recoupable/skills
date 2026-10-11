---
name: recoup-roster-onboard
description: Bootstrap an empty org's roster — when the account has no artists yet, gather the label's roster (names or a pasted list) and onboard them all by fanning recoup-roster-add-artist out across parallel subagents (each runs the full create → enrich chain), optionally scouting talent first. Use for "set up our roster", "we have no artists yet", "onboard our whole roster", "import these artists", or when recoup-platform-build-os / recoup-platform-connect-account finds an empty roster. For a single artist use recoup-roster-add-artist; to see the roster use recoup-roster-list-artists.
---

# Recoup — Onboard Roster

Bootstrap a brand-new/empty org: turn a list of artist names into a fully created + enriched roster by
fanning `recoup-roster-add-artist` out across parallel subagents. The empty-org entry point that
`recoup-platform-build-os` hands off to.

## Procedure

1. **Confirm the roster is actually empty.** Via `recoup-platform-api-access`, roster-discover
   (`GET /accounts/id` -> `GET /organizations` -> `GET /artists?org_id=…`). If any artists already
   exist, **stop** — that's `recoup-roster-add-artist` (one more) or `recoup-platform-build-os`
   (scaffold) territory, not a bootstrap. Never run on a populated roster.
2. **Refuse throwaway accounts.** If `/accounts/id` resolves to an `agent+…@recoupable.com` email,
   stop and ask for a real-account credential — artists created under a throwaway key get orphaned.
3. **Get the roster to create.** Either:
   - the user supplies names (or a pasted / CSV list) — use those; or
   - they want A&R help — run **`recoup-research-find-talent`** to propose candidates, then
     **confirm the final list with the user before creating anything** (creation is a real, billable
     mutation on the live account).
4. **Fan out (parallel subagents).** For each confirmed artist, dispatch a subagent that runs
   **`recoup-roster-add-artist`** for that one name (the create -> Spotify -> research -> catalog ->
   socials -> knowledge-base chain; writes `artists/{slug}/RECOUP.md`). Run them in parallel, but keep
   the batch to a sane width (≈5–8 at a time); pass each subagent only its one artist plus the
   org/auth context. Skip any name already on the roster.
5. **Reconcile.** When the subagents finish, run **`recoup-roster-list-artists`** to verify every
   intended artist now exists; retry the ones that failed (never fabricate a success).
6. **Hand back.** Return to **`recoup-platform-build-os`** to scaffold / refresh the workspace around
   the now-populated roster.

## Guardrails

- **API-first — never `mkdir` a roster.** Each artist is created through `recoup-roster-add-artist`
  (which goes through the Recoup API); folders follow from the API result.
- **Confirm names before creating.** Creating artists costs credits and writes to the live account —
  no silent bulk-create.
- **Idempotent.** Skip artists that already exist; safe to re-run after a partial failure.
- **One artist per subagent.** Keeps each chain resumable and isolates failures.
