---
name: recoup-roster-onboard
description: Bootstrap an empty org's roster — gather the confirmed roster, verify each Spotify identity, then resolve/attach and enrich artists through recoup-roster-add-artist in bounded parallel batches. Resume partial onboarding from saved identities and workspace scope. Use for "set up our roster", "we have no artists yet", "onboard our whole roster", "import these artists", or when recoup-platform-build-os / recoup-platform-connect-account finds an empty roster. For a single artist use recoup-roster-add-artist; to see the roster use recoup-roster-list-artists.
---

# Recoup — Onboard Roster

Bootstrap a brand-new/empty org: turn a list of artist names into a fully created + enriched roster by
fanning `recoup-roster-add-artist` out across parallel subagents. The empty-org entry point that
`recoup-platform-build-os` hands off to.

## Procedure

1. **Read the current authenticated scope and roster.** Via `recoup-platform-api-access`, use the
   already selected account and organization and read `GET /artists?org_id=…`. A fresh bootstrap
   starts with an empty roster; an unrelated populated roster belongs with `recoup-roster-add-artist`
   or `recoup-platform-build-os`. A partial run may already have artists: load its saved plan and
   reconcile only those confirmed identities instead of treating it as a fresh bootstrap.
2. **Refuse throwaway accounts.** Use the already resolved authenticated account ID and its profile
   (`GET /accounts/{accountId}`) to check the account email. If it is an `agent+` throwaway account,
   stop and obtain the intended account connection before creating artists. `/accounts/id` supplies
   the account ID, not the email; do not probe an unknown credential to create an identity.
3. **Get the roster to create.** Either:
   - the user supplies names (or a pasted / CSV list) — use those; or
   - they want A&R help — run **`recoup-research-find-talent`** to propose candidates, then
     **confirm the final list with the user before creating anything** (creation changes the live
     account; later enrichment can require credits).
4. **Verify, then fan out (parallel subagents).** Each confirmed artist runs
   **`recoup-roster-add-artist`**: verified Spotify identity -> canonical resolve/attach in the
   requested organization -> research/catalog/social enrichment. Ambiguous identities stop for
   selection; manual/name-only onboarding requires an explicit separate choice. Keep batches
   bounded (≈5–8 at a time) and pass only that artist's saved identity/checklist plus the exact
   org/auth context. Reuse a visible exact Spotify/account-ID match; a matching name alone does
   not establish identity. Each `RECOUP.md` retains verified Spotify ID, organization, returned
   artist account ID, actual `200` reused / `201` created outcome and unfinished steps.
5. **Reconcile partial results before another write.** Read the scoped roster and compare each
   saved exact identity and returned account ID. `id` and `account_id` are the same artist account
   ID. Continue unfinished enrichment on confirmed matches. Preserve uncertain outcomes when a
   response was lost; do not invent created/reused from a later read. Authorization, conflict or
   persistence failures never trigger name-only creation or a different Spotify match. A denied,
   missing or ambiguous result stays unresolved until access/scope/identity is reviewed.
6. **Hand back.** Return to **`recoup-platform-build-os`** to scaffold / refresh the workspace around
   the now-populated roster.

## Guardrails

- **API-first — never `mkdir` a roster.** Each artist is created through `recoup-roster-add-artist`
  (which goes through the Recoup API); folders follow from the API result.
- **Confirm the roster before creating.** Artist creation writes to the live account; enrichment
  may need credits. No silent bulk-create.
- **Resume by identity.** Reconcile saved Spotify/workspace/account IDs before another mutation;
  do not skip or create by name alone, or blindly replay a failed batch.
- **One artist per subagent.** Keeps each chain resumable and isolates failures.
