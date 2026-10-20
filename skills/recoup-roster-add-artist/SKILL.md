---
name: recoup-roster-add-artist
description: Add or attach an artist to your roster and enrich them — verify Spotify identity, resolve the artist in the requested workspace, then research, catalog, socials and knowledge base. Supports deliberate manual onboarding when Spotify identity is unavailable. Use for "create/add/onboard an artist", "set up [artist]", "we just signed [artist]", or "new signing". To see your roster use recoup-roster-list-artists; to work inside an existing artist's files use recoup-roster-manage-artist.
---

# Recoup — Add Artist

Bring the correct artist into the requested workspace, reusing an existing
canonical profile when available. Use the authenticated account and organization
already selected through recoup-platform-api-access. Confirm the intended artist
and roster action before a live mutation; a name or local folder alone is not
identity. Do not use an unknown or throwaway `agent+` credential.

## The 8-step onboarding chain (drive from the RECOUP.md checklist)

Drive the workflow from the existing `RECOUP.md` checklist. Persist confirmed
values and unfinished steps there, without credentials. A checkpoint can describe
pending work; do not label an artist created or attached before an API result.

1. **Resolve identity before creation.** Verify a supplied Spotify artist URL/ID,
   or use `GET /api/spotify/search` and inspect the artist and catalog. Capture the
   exact 22-character, case-sensitive `spotify_artist_id`, verified URL and image
   if present. Ambiguous matches stop for selection. An unavailable match does
   not authorize creating by name; use the deliberate manual path below only when
   appropriate. On resume, retain the saved verified identity instead of searching
   for a new match.
2. **Resolve/attach in the requested organization.** Before the first write, save
   the authenticated account ID, requested `organization_id`, mode `spotify`,
   verified Spotify ID and pending state. Submit
   `POST /api/artists {name, spotify_artist_id, organization_id}` with that exact
   identity and workspace. `200` means an existing canonical artist was reused;
   `201` means an artist was created. Save the actual HTTP status, outcome and
   returned artist account ID immediately. `artist.id` and `artist.account_id`
   identify the same artist account, never an `account_info` row. If both are
   present and disagree, stop for reconciliation. This operation establishes the
   Spotify association; do not create by name and then patch Spotify onto it.
3. **Continue on the returned artist ID.** Reconcile the current scoped roster
   before resuming an interrupted run. If the exact artist is already visible,
   continue enrichment on that ID. Optional artwork/profile changes use
   `PATCH /api/artists/{id}` only after identity is known; they are separate from
   canonical onboarding.
4. `GET /api/research/lookup?spotifyId={verifiedSpotifyId}` → capture the nonempty
   string `id` as `researchArtistId` in the frontmatter. It is an opaque research
   ID, separate from the artist account UUID and Spotify ID. Re-resolve older
   saved research IDs instead of copying them. When an ID is available, read
   `GET /api/research/profile|career|playlists?id={researchArtistId}`. Profile
   coverage may be partial; career is an activity feed and playlists returns
   `placements`. A successful lookup without an ID skips these reads; record the
   gap. Run `POST /api/research/web` with a JSON `query` for biography and press.
   Persist returned evidence and coverage gaps under `## Research`; empty data
   does not trigger a warm-up job or justify invented facts.
5. Spotify catalog (`topTracks`, `albums`, `album`) → write `releases/{slug}/RELEASE.md`
   per album + `releases/top-tracks.md`.
6. Web search for socials (ig/tiktok/twitter/youtube).
7. `PATCH /api/artists/{id}` with discovered `profileUrls` (only platforms found).
8. Synthesize a `## Knowledge base` section into `RECOUP.md`.

Check HTTP status before using each response. Stop on `402` and surface
`billingUrl`; defer `429` until `Retry-After` permits a later attempt. Authorization,
identity-conflict and persistence failures never switch to name-only creation.
Do not automatically retry a mutation on a network failure or `5xx`: it may have
committed. Keep the checkpoint and reconcile first. Read-only enrichment requests
may retry network/`5xx` failures up to three attempts with a 90-second timeout per
request. Keep failed steps unchecked. Uses recoup-platform-api-access for call
shapes; connected MCP calls must preserve the same identity and workspace.

## Request examples and a deliberate manual path

`scripts/onboarding_examples.sh` ships alongside this skill. The examples require
Bash, jq and an already configured `RECOUP_API_KEY` or `RECOUP_ACCESS_TOKEN`;
they never extract a host's OAuth token. Prefer a connected tool when available.
Sourcing defines functions and makes no request. From this skill's directory:

```bash
source scripts/onboarding_examples.sh
# These values must come from the verified identity and selected workspace.
onboard_spotify_artist "$ARTIST_NAME" "$SPOTIFY_ARTIST_ID" "$ORGANIZATION_ID"
```

The one-request example prints the verified identity, organization, returned
artist ID, `create_http_status` and `outcome`; persist those actual values in
`RECOUP.md`. It performs no enrichment and no automatic retry or fallback.

**Manual/name-only onboarding is separate.** If there is no verified Spotify
identity and the user deliberately wants a manual artist, record mode `manual`
and that unresolved identity first. Submit only `{name, organization_id}`. This
does not establish a shared identity, link another artist by matching name, or
create a professional-roster record. The explicit REST example is:

```bash
onboard_manual_artist "$ARTIST_NAME" "$ORGANIZATION_ID" confirmed-manual
```

The confirmation argument records the chosen example, not authorization or proof
of ownership. Never use it after a failed canonical request. If a manual request
has an uncertain outcome, inspect the roster and any returned ID; do not repeat
creation because a name search is empty.

## Resume without duplicating the artist

Load the saved account, organization, mode, Spotify identity, returned artist ID
when known, and create status/outcome before any new mutation. If the authenticated
account or selected organization has changed, stop and re-establish the intended
scope instead of moving the run. Read `GET /api/artists?org_id={savedOrganizationId}`;
reconcile by exact verified Spotify association and the saved artist account ID,
not by display name. The read-only example is:

```bash
reconcile_spotify_artist "$SPOTIFY_ARTIST_ID" "$ORGANIZATION_ID" "${SAVED_ARTIST_ACCOUNT_ID:-}"
```

This performs one GET and never POSTs. A unique exact match returns its artist ID
and `reconciliation: matched`. Preserve the original `create_http_status` and
created/reused outcome; a later roster read cannot reconstruct a lost creation
response. Resume unfinished enrichment on that ID. A saved-ID mismatch, multiple
matches, denial, or incomplete roster response stops for review. Exit 2 means the
successful roster read has no exact match, not proof the earlier write never
happened. Check access and scope before a further authorized canonical request,
using the same saved Spotify ID and organization. Never choose a new identity or
fall back to manual creation to clear the error.

## Guardrails

- **The file is the state** — tick + persist each step or a fresh turn redoes/skips work.
- **No placeholder data** in artist files — real content or leave the section out.
- **Never invent a roster/artist** — confirm via recoup-platform-api-access first; an
  empty filesystem is not an empty roster.
