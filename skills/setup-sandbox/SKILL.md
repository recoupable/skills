---
name: setup-sandbox
description: Set up the initial file system for a new sandbox. Fetches the account's organizations and artists via the Recoup CLI and scaffolds the folder structure. Use when a sandbox has just been created and has no existing file system. Before running, check if the sandbox already has an orgs/ directory — if it does, this skill is not needed.
---

# Setup Sandbox

Create the folder structure for the connected account's organizations and artists.

## Environment

- `RECOUP_ACCOUNT_ID` — The account ID this sandbox belongs to. Injected automatically when a sandbox is provisioned. When set, pass `--account $RECOUP_ACCOUNT_ID` on CLI commands to scope requests to this account.

## Steps

1. Check if `RECOUP_ACCOUNT_ID` is set. If set, use `--account $RECOUP_ACCOUNT_ID` on all CLI commands below. If not set, omit the `--account` flag — the CLI will use the authenticated account automatically.
2. Run `recoup orgs list --json [--account $RECOUP_ACCOUNT_ID]` to get all organizations
3. For each organization, run `recoup artists list --org {organization_id} --json [--account $RECOUP_ACCOUNT_ID]` to get its artists
4. Create the folder structure and a `RECOUP.md` marker in each artist folder:
   - Use `artistSlug` from the CLI response as the exact directory name — never append UUIDs, IDs, or suffixes
   - If `orgs/{org}/artists/{artist-slug}/` already exists, skip it
   - `mkdir -p orgs/{org}/artists/{artist-slug}` for each new artist
   - Write a `RECOUP.md` using the template below
5. Commit and push:
   - `git add -A && git commit -m "setup: create org and artist folders" && git push`

## `RECOUP.md`

Every artist directory has a `RECOUP.md` at its root. This is the **identity file** — it connects the workspace to the Recoupable platform. The existence of this file means the workspace is active.

Fill it with data from the CLI response:

```markdown
---
artistName: {Artist Name}
artistSlug: {artist-slug}
artistId: {uuid-from-recoupable}
---
```

**Fields:**

- `artistName` — display name from the CLI (e.g. `Gatsby Grace`)
- `artistSlug` — lowercase-kebab-case folder name (e.g. `gatsby-grace`)
- `artistId` — the UUID from Recoup
