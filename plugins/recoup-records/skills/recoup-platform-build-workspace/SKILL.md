---
name: recoup-platform-build-workspace
description: Scaffold your account's folder tree so the rest of the box has somewhere to work — builds the orgs/artists directories with a RECOUP.md identity file per artist from your real account. Use for "scaffold my sandbox", "build my workspace folders", or "set up my folder tree". Run after recoup-platform-connect-account. To work inside one artist's folder afterward use recoup-roster-manage-artist.
---

# Recoup — Build Workspace

Build the account's folder tree from the real roster. Idempotent; skips existing.

**Guard:** if `orgs/` already exists with content, stop → use
recoup-roster-manage-artist (work inside an artist) instead.

## Procedure

Auth `Authorization: Bearer $RECOUP_ACCESS_TOKEN`; `RECOUP_ORG_ID` (optional)
scopes to one org. Then: `GET /api/organizations` → for each (or just
`RECOUP_ORG_ID`), `GET /api/artists?org_id=…` →
`mkdir -p orgs/{slugify(org)}/artists/{slugify(name)}` and write a `RECOUP.md`
identity file (`artistName`/`artistSlug`/`artistId` from `account_id`) per artist;
skip existing; commit. `slugify` = lowercase-kebab; never append IDs to folder names.

(In an open-agents sandbox artists live at top-level `artists/` — no `orgs/`; that's
recoup-roster-manage-artist territory.) Uses recoup-platform-api-access for the call
shapes.

## Guardrails

- **Idempotent** — skip existing folders; never clobber an artist's work.
- **Never invent a roster** — empty orgs+artists = a throwaway-key credential
  problem to surface, not a blank canvas.
