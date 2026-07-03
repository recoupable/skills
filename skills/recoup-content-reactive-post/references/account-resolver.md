# Auth + resolving the artist (the 404 footgun)

Recoup content skills authenticate one of two ways and must pass the **right artist
identifier** to the right endpoint. Getting either wrong is the most common cause of a
silent 401/404. Read this before writing curl calls.

## 1. Auth — two modes

Pick whichever credential the environment provides; prefer the API key when both exist.

| Credential | Header | Where it comes from |
| --- | --- | --- |
| `RECOUP_API_KEY` (`recoup_sk_…`) | `-H "x-api-key: $RECOUP_API_KEY"` | agent signup; see docs.recoupable.dev/agents |
| `RECOUP_ACCESS_TOKEN` | `-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"` | short-lived sandbox token |

```bash
if [ -n "$RECOUP_API_KEY" ]; then
  AUTH=(-H "x-api-key: $RECOUP_API_KEY")
elif [ -n "$RECOUP_ACCESS_TOKEN" ]; then
  AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN")
else
  echo "No Recoup credential set — ask the user to authenticate; do not retry blindly." >&2
  return 1 2>/dev/null || exit 1   # stop — never call the API unauthenticated
fi
# Use as:  curl -sS "${AUTH[@]}" "https://api.recoupable.dev/api/..."
```

If neither is set, the user is not authenticated — tell them to sign in rather than
retrying.

## 2. Two different artist identifiers

The API exposes **two** IDs for an artist, and they are not interchangeable:

- **`account_id`** — the underlying account that owns the artist. Content **creation**
  endpoints (`POST /api/content/create`) key off this, **and so does
  `GET /api/artists/{account_id}/socials`** (verified live 2026-06-07 — passing the row
  `id` there returns `404 "Artist not found"`).
- **`id`** — the artist row's primary key. Some per-artist resource endpoints under
  `/api/artists/{id}/…` use this.

Passing the wrong one returns a 404 from an endpoint that otherwise looks correct. **Capture
both from the same list response, and try `account_id` first when a `/api/artists/{…}/` read
404s.**

## 3. Resolve from the workspace first

If `RECOUP.md` exists, its frontmatter already holds the IDs — read them, don't re-query:

```bash
ARTIST_ID=$(sed -n 's/^artistId:[[:space:]]*//p' "$ARTIST_DIR/RECOUP.md")
```

(`artistId` in `RECOUP.md` is the `account_id` captured at create time — the value
`POST /api/content/*` wants. For `/api/artists/{id}/…` resource reads you may still need
the row `id` from §4.)

## 4. Resolve from the API (no workspace)

Scope to the sandbox org when `RECOUP_ORG_ID` is set; otherwise the account-scoped list
spans every org the account belongs to. Org rows expose `organization_id` (pass this as
`org_id`), `organization_name`, and their own row `id`.

```bash
ORG_ID="${RECOUP_ORG_ID:-$(curl -sS "${AUTH[@]}" \
  "https://api.recoupable.dev/api/organizations" | jq -r '.organizations[0].organization_id')}"

# Capture BOTH ids for the matched artist.
ARTISTS_JSON=$(curl -sS "${AUTH[@]}" \
  "https://api.recoupable.dev/api/artists?org_id=$ORG_ID")

ARTIST_ACCOUNT_ID=$(echo "$ARTISTS_JSON" \
  | jq -r --arg n "$ARTIST_NAME" '.artists[] | select(.name==$n) | .account_id')
ARTIST_ROW_ID=$(echo "$ARTISTS_JSON" \
  | jq -r --arg n "$ARTIST_NAME" '.artists[] | select(.name==$n) | .id')
```

**Browsing instead of matching:** if the user hasn't named the artist (e.g. "pick one of my
artists"), drop the `select(.name==$n)` filter and present the full list
(`.artists[] | [.name, .account_id] | @tsv`) for them to choose from — don't silently pick one.

**Empty / wrong-account guard:** if `organizations` and `artists` both come back empty, or
`GET /api/accounts/{accountId}` shows an `agent+…@recoupable.com` email, this credential is a
throwaway / agent key, not the user's real account. Stop and ask for the right key — do **not**
fabricate an artist. (See `recoup-platform-api-access`'s "Stop rule — never invent a roster".)

If a real account simply has no row for a named artist, the artist doesn't exist yet — run the
`recoup-roster-add-artist` skill before continuing. Do not invent an ID.

## 5. Quick reference — which ID goes where

| Endpoint | Identifier |
| --- | --- |
| `POST /api/content/create`, `POST /api/content/*` (body `artist_account_id`) | `account_id` |
| `GET /api/artists/{account_id}/socials` | `account_id` (verified 2026-06-07) |
| `GET /api/artists/{id}/posts` | row `id` (try `account_id` first if it 404s) |

When a call 404s on an ID you believe is correct, try the other identifier before assuming
the resource is missing.
