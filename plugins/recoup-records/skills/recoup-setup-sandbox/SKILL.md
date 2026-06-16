---
name: recoup-setup-sandbox
description: Set up the initial file system for a new sandbox. Fetches the account's organizations and artists via the Recoup REST API and scaffolds the folder structure. Use when a sandbox has just been created and has no existing file system. Before running, check if the sandbox already has an orgs/ directory — if it does, this skill is not needed.
---

# Setup Sandbox

**Before running, check:** `ls orgs/` from the sandbox root. If the directory exists and contains org folders, the sandbox is already set up — stop here and read the `recoup-artist-workspace` skill instead. Only continue if `orgs/` doesn't exist or is empty.

Create the folder structure for the connected account's organizations and artists by calling the Recoup REST API.

## Environment & auth

This skill calls the Recoup API directly — the same conventions as the `recoup-api` skill:

- **Base URL:** `https://api.recoupable.com/api`
- **Auth:** `Authorization: Bearer $RECOUP_ACCESS_TOKEN` (the sandbox's account-scoped access token).
- **`RECOUP_ORG_ID`** *(optional)* — when set, the sandbox was opened for one specific org; scaffold only that org. When unset, scaffold every org the account belongs to.

If `RECOUP_ACCESS_TOKEN` is empty, the user is not authenticated — tell them to sign in rather than retrying. Defer to the `recoup-api` skill if any call shape is unclear.

Set up the shared request pieces once:

```bash
BASE="${RECOUP_API_URL:-https://api.recoupable.com/api}"
AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN")

# Turn any display name into a lowercase-kebab-case slug for folder names.
slugify() { echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g'; }
```

## Steps

1. **List the account's organizations** — `GET /api/organizations`. Each item has `organization_id` and `organization_name`:

   ```bash
   curl -sS "${AUTH[@]}" "$BASE/organizations" \
     | jq -r '.organizations[] | [.organization_id, .organization_name] | @tsv'
   ```

   If `RECOUP_ORG_ID` is set, keep only the row whose `organization_id` matches it.

2. **List each org's artists** — `GET /api/artists?org_id={organization_id}`. Each artist has `account_id` (the UUID) and `name` — there is **no slug field**, so derive the folder name from `name` with `slugify`:

   ```bash
   curl -sS "${AUTH[@]}" "$BASE/artists?org_id=$ORG_ID" \
     | jq -r '.artists[] | [.account_id, .name] | @tsv'
   ```

3. **Scaffold folders + a `RECOUP.md` marker** for each artist:
   - Org folder name = `slugify(organization_name)`; artist folder name = `slugify(name)`.
   - Never append UUIDs, IDs, or suffixes to folder names.
   - If `orgs/{org-slug}/artists/{artist-slug}/` already exists, skip it.
   - `mkdir -p orgs/{org-slug}/artists/{artist-slug}` for each new artist.
   - Write a `RECOUP.md` using the template below.

4. **Commit and push:**

   ```bash
   git add -A && git commit -m "setup: create org and artist folders" && git push
   ```

5. Read the `recoup-artist-workspace` skill — it teaches how to work inside the directories you just created.

### Putting it together

```bash
# Resolve which orgs to scaffold (one if RECOUP_ORG_ID is set, else all).
curl -sS "${AUTH[@]}" "$BASE/organizations" \
  | jq -r --arg only "${RECOUP_ORG_ID:-}" \
      '.organizations[] | select($only == "" or .organization_id == $only)
       | [.organization_id, .organization_name] | @tsv' \
| while IFS=$'\t' read -r ORG_ID ORG_NAME; do
    ORG_SLUG=$(slugify "$ORG_NAME")
    curl -sS "${AUTH[@]}" "$BASE/artists?org_id=$ORG_ID" \
      | jq -r '.artists[] | [.account_id, .name] | @tsv' \
    | while IFS=$'\t' read -r ARTIST_ID ARTIST_NAME; do
        ARTIST_SLUG=$(slugify "$ARTIST_NAME")
        DIR="orgs/$ORG_SLUG/artists/$ARTIST_SLUG"
        [ -d "$DIR" ] && continue
        mkdir -p "$DIR"
        cat > "$DIR/RECOUP.md" <<EOF
---
artistName: $ARTIST_NAME
artistSlug: $ARTIST_SLUG
artistId: $ARTIST_ID
---
EOF
      done
  done
```

## `RECOUP.md`

Every artist directory has a `RECOUP.md` at its root. This is the **identity file** — it connects the workspace to the Recoupable platform. The existence of this file means the workspace is active.

```markdown
---
artistName: {Artist Name}
artistSlug: {artist-slug}
artistId: {uuid-from-recoupable}
---
```

**Fields (mapped from the `GET /api/artists` response):**

- `artistName` — `name`, the display name (e.g. `Gatsby Grace`)
- `artistSlug` — `slugify(name)`, lowercase-kebab-case folder name (e.g. `gatsby-grace`)
- `artistId` — `account_id`, the artist account UUID from Recoup
