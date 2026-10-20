# Auth + resolving the artist (the 404 footgun)

Recoup content skills authenticate one of two ways and must pass the **right artist
identifier** to the right endpoint. Getting either wrong is the most common cause of a
silent 401/404. Read this before writing curl calls.

## 1. Prefer the connected MCP

For a matching operation, use the host's authenticated Recoup MCP tool and its
actual input schema. OAuth credentials stay in the host; never extract them or
put them in curl. Missing environment variables do not mean MCP is disconnected.
Use `list_artists` for roster discovery. An empty roster can be legitimate.
If the operation is not exposed by MCP, use the REST credentials below.

**Artist resolution is operation-specific.** A release pack can retain a supplied
song and campaign brief without an existing artist or GitHub workspace. Prefer
the connected pack operations when exposed; do not create an artist or run roster
onboarding just because the roster is empty. Resolve an artist ID only when the
selected operation actually requires one. Keep the original job through sign-in.

### REST fallback — two modes

Pick whichever credential the environment provides; prefer the API key when both exist.

| Credential | Header | Where it comes from |
| --- | --- | --- |
| `RECOUP_API_KEY` | `-H "x-api-key: $RECOUP_API_KEY"` | approved real-account REST setup; see docs.recoupable.dev/agents |
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

If neither is set, REST credentials are unavailable. Use a matching authenticated
MCP tool or explain which REST-only capability needs a separate credential.

## 2. Artist account identity

Current `GET /api/artists` rows expose `account_id` and an `id` alias with the
same artist account UUID. Use that UUID for content `artist_account_id` and
`/api/artists/{id}/socials|posts|fans` reads. Do not substitute an internal
profile-row key, a Spotify ID or an opaque research ID. Older saved IDs should
be verified against the current authenticated roster before use.

## 3. Resolve from the workspace first

If `RECOUP.md` exists, its frontmatter already holds the IDs — read them, don't re-query:

```bash
ARTIST_ID=$(sed -n 's/^artistId:[[:space:]]*//p' "$ARTIST_DIR/RECOUP.md")
```

`artistId` in `RECOUP.md` is the artist `account_id` captured at create time,
also used for the artist's resource reads.

## 4. Resolve from the API (no workspace)

Scope to the sandbox org when `RECOUP_ORG_ID` is set; otherwise the account-scoped list
spans every org the account belongs to. Org rows expose `organization_id` (pass this as
`org_id`), `organization_name`, and their own row `id`.

```bash
# Do not choose the first organization implicitly. Use the selected workspace,
# or query the account scope when no organization is selected.
ARTISTS_URL="https://api.recoupable.dev/api/artists"
if [ -n "$RECOUP_ORG_ID" ]; then
  ARTISTS_URL="$ARTISTS_URL?org_id=$RECOUP_ORG_ID"
fi
IDENTITY=$(curl --fail-with-body -sS "${AUTH[@]}" "https://api.recoupable.dev/api/accounts/id") || exit 1
ACCOUNT_ID=$(printf '%s' "$IDENTITY" | jq -er '.accountId') || exit 1
ACCOUNT=$(curl --fail-with-body -sS "${AUTH[@]}" "https://api.recoupable.dev/api/accounts/$ACCOUNT_ID") || exit 1
# Verify this is the user's intended account before any roster mutation.
if printf '%s' "$ACCOUNT" | jq -e '.account.email | test("^agent\\+.*@recoupable\\.(com|dev)$")' >/dev/null; then
  echo "Disposable agent identity: connect the user's real account before creating artists." >&2
  exit 1
fi
ARTISTS_JSON=$(curl --fail-with-body -sS "${AUTH[@]}" "$ARTISTS_URL") || exit 1

MATCHES=$(printf '%s' "$ARTISTS_JSON" | jq --arg n "$ARTIST_NAME" '[.artists[] | select(.name==$n)]')
MATCH_COUNT=$(printf '%s' "$MATCHES" | jq length)
if [ "$MATCH_COUNT" -eq 0 ]; then
  echo 'No visible artist matches; verify identity and workspace access before adding one.' >&2
  return 1 2>/dev/null || exit 1
elif [ "$MATCH_COUNT" -gt 1 ]; then
  echo 'Multiple artists match; select the intended account ID or filter the selected workspace.' >&2
  printf '%s' "$MATCHES" | jq '.[] | {id,account_id,name}' >&2
  return 1 2>/dev/null || exit 1
fi
ARTIST_ACCOUNT_ID=$(printf '%s' "$MATCHES" | jq -r '.[0].account_id // empty')
ARTIST_ROW_ID=$(printf '%s' "$MATCHES" | jq -r '.[0].id // empty')
if [ -z "$ARTIST_ACCOUNT_ID" ] || [ -z "$ARTIST_ROW_ID" ]; then
  echo 'Artist response is missing required identifiers; verify the current roster.' >&2
  return 1 2>/dev/null || exit 1
fi
```

**Browsing instead of matching:** if the user hasn't named the artist (e.g. "pick one of my
artists"), drop the `select(.name==$n)` filter and present the full list
(`.artists[] | [.name, .account_id] | @tsv`) for them to choose from — don't silently pick one.

**Access check:** an empty roster can be legitimate. Verify the credential's identity
and authorized workspace before interpreting a missing artist. Do not create a
disposable account, fabricate an artist or infer failed authentication from emptiness.

If an **artist-bound operation** requires an artist and no row is visible, verify
exact identity and access before offering to attach/create one. Use
`recoup-roster-add-artist` only for that requested roster action. Other content
operations can continue from supplied inputs without an artist ID. Do not invent
an ID or interpret absent roster data as authorization to create one.

## 5. Quick reference — which ID goes where

| Endpoint | Identifier |
| --- | --- |
| `POST /api/content/create`, `POST /api/content/*` (body `artist_account_id`) | `account_id` |
| `GET /api/artists/{id}/socials`, `GET /api/artists/{id}/posts`, `GET /api/artists/{id}/fans` | Artist `account_id`; current list `id` is its alias |

On `404`, verify the saved UUID, account and workspace access before retrying.
