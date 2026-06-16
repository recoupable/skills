---
name: recoup-artist-create
description: End-to-end playbook for creating, identifying, and enriching a new artist account. Use when the user asks to create, add, onboard, or set up a new artist — phrases like "create artist", "onboard X", "add this artist", "set up a new artist", or any task that starts a brand-new artist record from a name. The skill drives 8 sequential API calls (create → Spotify match → PATCH profile → Songstats research → Spotify catalog → web socials search → PATCH socials → synthesize KB) from a `RECOUP.md` checklist scaffolded by the `recoup-artist-workspace` skill, ticking each box and persisting captured values back to the file as it goes.
---

# Create New Artist

The canonical recipe used internally by Recoup's chat agent. Follow it step-by-step to bring a brand-new artist account up to "researched + enriched" parity from a sandbox or any external agent.

The chain is **8 sequential API calls**. Long deterministic chains executed from prose memory tend to drop steps — the agent reads the doc once, runs a couple of calls, and forgets the rest. Drive the work from the `RECOUP.md` checklist file scaffolded by the [`recoup-artist-workspace`](https://github.com/recoupable/skills/tree/main/plugins/recoup-essentials/skills/recoup-artist-workspace) skill: tick each box and persist captured values back to the frontmatter as you go. The file IS the workflow state, and a fresh turn can resume by reading it.

## Prerequisites

- `$RECOUP_ACCESS_TOKEN` — Bearer token for `api.recoupable.com`
- `$RECOUP_ORG_ID` — the org the artist should belong to (recommended in sandboxes)
- An artist name to create (e.g. `ARTIST_NAME="The Weeknd"`)
- The artist's `RECOUP.md` already scaffolded (see `recoup-artist-workspace` skill, Step 0)

The flow has three phases, all driven from the single checklist file:

1. **Create + identify** — `POST /api/artists`, then find the canonical Spotify match
2. **Enrich** — `PATCH` the artist with image/label/socials, then run structured research (Songstats profile/career/playlists) plus a web search for narrative context and additional socials
3. **Synthesize + persist** — generate a knowledge-base report, save it (RECOUP.md tree or hosted URL), then optionally `PATCH` the `knowledges` array

**Don't run this chain under a throwaway `agent+` account.** Artist data created against an `agent+...@recoupable.com` email is permanently isolated to that account and can't be recovered if the API key is lost. Only run after the user has authenticated with their real email.

## Resuming a partial setup

If `$ARTIST_DIR/RECOUP.md` already exists, do not re-scaffold and do not re-run completed steps. Read the file, find the first unchecked item, and resume from there using the values already saved in the frontmatter:

```bash
# Show the next unchecked step
grep -n '^- \[ \]' "$ARTIST_DIR/RECOUP.md" | head -1
```

If every item is checked, the artist is fully set up — confirm with the user before doing anything else.

## Step 1: Create the artist

```bash
ARTIST_RESPONSE=$(curl -sS -X POST "https://api.recoupable.com/api/artists" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg name "$ARTIST_NAME" --arg org "$RECOUP_ORG_ID" \
        '{name: $name, organization_id: $org}')")

ARTIST_ID=$(echo "$ARTIST_RESPONSE" | jq -r '.artist.account_id')
```

Capture `account_id` as `$ARTIST_ID` — every subsequent step needs it. `organization_id` is optional but should be included when running inside a sandbox so the artist is scoped to the right org.

Full request/response schema: `https://developers.recoupable.com/api-reference/artists/create`.

**After this step:** write `artistId: $ARTIST_ID` into the frontmatter and tick `- [ ] 1.` → `- [x] 1.` in `RECOUP.md`.

## Step 2: Find the canonical Spotify match

```bash
SPOTIFY=$(curl -sS -G "https://api.recoupable.com/api/spotify/search" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  --data-urlencode "q=$ARTIST_NAME" \
  --data-urlencode "type=artist" \
  --data-urlencode "limit=10")
```

Pick the best match: prefer an exact case-insensitive name match; if multiple, prefer the highest popularity score. Export the fields the rest of the chain needs:

```bash
MATCH=$(echo "$SPOTIFY" | jq --arg name "$ARTIST_NAME" '
  .artists.items
  | (map(select((.name | ascii_downcase) == ($name | ascii_downcase))) | sort_by(-.popularity) | first)
    // (sort_by(-.popularity) | first)
')

SPOTIFY_ARTIST_ID=$(echo "$MATCH" | jq -r '.id // empty')
SPOTIFY_PROFILE_URL=$(echo "$MATCH" | jq -r '.external_urls.spotify // empty')
SPOTIFY_IMAGE_URL=$(echo "$MATCH" | jq -r '.images[0].url // empty')

[ -n "$SPOTIFY_ARTIST_ID" ] || { echo "No Spotify match for $ARTIST_NAME"; exit 1; }
```

Also keep `genres`, `followers.total`, and `popularity` from `$MATCH` for the KB report later.

Full schema: `https://developers.recoupable.com/api-reference/spotify/search`.

**After this step:** write `spotifyArtistId`, `spotifyProfileUrl`, and `imageUrl` into the frontmatter, save `genres` / `followers.total` / `popularity` to the `## Notes` section, and tick `- [ ] 2.` → `- [x] 2.`.

## Step 3: Set basic profile + Spotify URL

One `PATCH` covers the image and the Spotify social URL. Use **uppercase** platform keys in `profileUrls` (the API matches platforms case-sensitively — see the platform key reference at the bottom of this file).

```bash
curl -sS -X PATCH "https://api.recoupable.com/api/artists/$ARTIST_ID" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg image "$SPOTIFY_IMAGE_URL" --arg url "$SPOTIFY_PROFILE_URL" \
        '{image: $image, profileUrls: {SPOTIFY: $url}}')"
```

This single endpoint replaces what the chat tool chain runs as four separate MCP calls (`update_account_info` ×2, `update_artist_socials` ×2). Add `label` to the body if you discover one (e.g. from the step 4e web search or press) — the structured `profile` endpoint does **not** return a label field. Full body schema: `https://developers.recoupable.com/api-reference/artists/update`.

**After this step:** tick `- [ ] 3.` → `- [x] 3.`.

## Step 4: Run structured research

Don't use `POST /api/research/deep` here — it tends to hang in sandboxes and returns paraphrased prose. Instead, fan out across four bounded structured endpoints (one prerequisite lookup + three structured pulls + one web search). The outputs are typed JSON the agent can use directly without paraphrasing.

**Retry transient misses.** The research endpoints sit behind a cache/refresh layer — a *cold* call can come back `status: "error"` (or `202`) and then succeed on retry. Treat any non-`success` response as transient and retry once or twice before giving up, so a cold miss doesn't silently write empty research into the workspace. Use this helper for the GET pulls below:

```bash
research_get() {  # usage: research_get <endpoint> [curl -G args...]
  local ep="$1"; shift
  local out=""
  for attempt in 1 2 3; do
    out=$(curl -sS --max-time 90 -G "https://api.recoupable.com/api/research/$ep" \
      -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" "$@")
    [ "$(echo "$out" | jq -r '.status // "error"')" = "success" ] && { echo "$out"; return 0; }
    sleep 3
  done
  echo "$out"; return 1   # last non-success body; caller logs it and leaves the box unchecked
}
```

### 4a: Look up the provider `artist_id` (Songstats)

Most of the structured research endpoints take the research provider's `artist_id` — a short alphanumeric Songstats id like `wjcgfd9i`, **not** the Spotify ID. Resolve it once (from `artist_info.songstats_artist_id`) and reuse it for the rest of step 4.

```bash
LOOKUP=$(research_get lookup --data-urlencode "spotifyId=$SPOTIFY_ARTIST_ID")

PROVIDER_ARTIST_ID=$(echo "$LOOKUP" | jq -r '.artist_info.songstats_artist_id // empty')

[ -n "$PROVIDER_ARTIST_ID" ] || { echo "No provider match for Spotify ID $SPOTIFY_ARTIST_ID — skipping structured research"; }
```

If the lookup fails (rare — most Spotify-discoverable artists have a provider profile), skip 4b–4d and just run 4e (web search). Full schema: `https://developers.recoupable.com/api-reference/research/lookup`.

### 4b: Pull the artist profile

Returns bio, genres, country, social/streaming URLs (`links`), related artists, and avatar. Note: it does **not** return label, career stage, or follower/listener metrics — pull those from `/api/research/metrics` or the web search if you need them.

```bash
PROFILE=$(research_get profile --data-urlencode "id=$PROVIDER_ARTIST_ID")
```

Full schema: `https://developers.recoupable.com/api-reference/research/profile`.

### 4c: Pull the career timeline

Career milestones and trajectory (key events over time) — covers the "notable achievements" portion of what deep research returned.

```bash
CAREER=$(research_get career --data-urlencode "id=$PROVIDER_ARTIST_ID")
```

Full schema: `https://developers.recoupable.com/api-reference/research/career`.

### 4d: Pull editorial + algorithmic playlist placements

Replaces the "playlists / radio rotations / editorial features" portion of the deep-research Spotify-presence query.

```bash
PLAYLISTS=$(research_get playlists --data-urlencode "id=$PROVIDER_ARTIST_ID")
```

Full schema: `https://developers.recoupable.com/api-reference/research/playlists`.

### 4e: Web search for narrative / press / collaborations

Structured endpoints don't cover press coverage, cultural narrative, or recent feature/collab announcements. Fill that gap with a single web search.

```bash
RESEARCH_WEB=$(curl -sS -X POST "https://api.recoupable.com/api/research/web" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg name "$ARTIST_NAME" \
        '{query: ($name + " biography press recent collaborations")}')")
```

Full schema: `https://developers.recoupable.com/api-reference/research/web`.

**After this step:** persist `providerArtistId: $PROVIDER_ARTIST_ID` into the frontmatter, save the four response payloads (profile, career, playlists, web) into a new `## Research` section of `RECOUP.md` — one subsection per endpoint, each with the raw JSON or a tight markdown summary so step 8 can compose from it. Tick `- [ ] 4.` → `- [x] 4.`.

## Step 5: Pull the Spotify catalog

```bash
TOP_TRACKS=$(curl -sS -G "https://api.recoupable.com/api/spotify/artist/topTracks" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  --data-urlencode "id=$SPOTIFY_ARTIST_ID")

ALBUMS=$(curl -sS -G "https://api.recoupable.com/api/spotify/artist/albums" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  --data-urlencode "id=$SPOTIFY_ARTIST_ID")

# For each notable album, drill in (ALBUM_ID from $ALBUMS):
ALBUM_DETAIL=$(curl -sS -G "https://api.recoupable.com/api/spotify/album" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  --data-urlencode "id=$ALBUM_ID")
```

`$SPOTIFY_ARTIST_ID` is the value you exported in step 2.

Full schemas: top tracks (`/api-reference/spotify/artist-top-tracks`), albums (`/api-reference/spotify/artist-albums`), album detail (`/api-reference/spotify/album`).

**After this step:** populate the artist's `releases/` folder — write one `releases/{release-slug}/RELEASE.md` per album (album slugs are bare, `-ep` / `-single` / `-compilation` suffixes for other types) using the per-album `GET /api/spotify/album?id=$ALBUM_ID` response, and write the top tracks snapshot to `releases/top-tracks.md`. `RELEASE.md` is the 18-section master release-management document — Step 5 fills the Spotify-derivable fields and leaves the rest as `⚠️ TBD`. The full template + the field-by-field Spotify mapping live in the [`recoup-artist-workspace`](https://github.com/recoupable/skills/tree/main/plugins/recoup-essentials/skills/recoup-artist-workspace) skill's release-template reference. Tick `- [ ] 5.` → `- [x] 5.`.

## Step 6: Search the web for additional socials

```bash
SOCIALS_SEARCH=$(curl -sS -X POST "https://api.recoupable.com/api/research/web" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg name "$ARTIST_NAME" \
        '{query: ($name + " official instagram tiktok twitter youtube")}')")
```

Parse the results to extract any new social URLs whose host matches the platform reference table below.

**After this step:** save the discovered URLs (one per platform) into the `## Notes` section so step 7 can read them without re-querying. Tick `- [ ] 6.` → `- [x] 6.`.

## Step 7: PATCH the artist with the discovered socials

```bash
curl -sS -X PATCH "https://api.recoupable.com/api/artists/$ARTIST_ID" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profileUrls": {
      "INSTAGRAM": "https://instagram.com/...",
      "TIKTOK": "https://tiktok.com/@...",
      "TWITTER": "https://x.com/...",
      "YOUTUBE": "https://youtube.com/@..."
    }
  }'
```

Only include keys for platforms you actually found URLs for. The PATCH preserves existing socials for keys you omit, so this is safe to run incrementally.

Full body schema: `https://developers.recoupable.com/api-reference/artists/update`.

**After this step:** tick `- [ ] 7.` → `- [x] 7.`.

## Step 8: Synthesize the knowledge base

Combine the structured research outputs (`## Research` section — profile, career, playlists, web), the Spotify catalog (`releases/`), and the discovered socials into a comprehensive markdown report. Recommended sections:

- Artist biography and origin
- Discography highlights (top tracks + key albums)
- Spotify presence (genres, listener count, notable playlists)
- Social media footprint
- Recent activity / press
- Notable collaborations and achievements

Append the report to the same `RECOUP.md` you scaffolded in Step 0 — add it as a `## Knowledge base` section below the checklist. The path is `artists/$ARTIST_SLUG/RECOUP.md`.

This dovetails with the [`recoup-artist-workspace`](https://github.com/recoupable/skills/tree/main/plugins/recoup-essentials/skills/recoup-artist-workspace) skill's filesystem conventions, so future sandbox sessions can read both the checklist and the KB without needing a hosted URL.

**After this step:** tick `- [ ] 8.` → `- [x] 8.`. With every box ticked, the artist is fully set up.

## Platform key reference

`profileUrls` keys are **uppercase** platform identifiers, inferred from the URL host. Recognized platforms:

| URL contains | `profileUrls` key |
| --- | --- |
| `spotify.com` | `SPOTIFY` |
| `instagram.com` | `INSTAGRAM` |
| `tiktok.com` | `TIKTOK` |
| `x.com`, `twitter.com` | `TWITTER` |
| `youtube.` | `YOUTUBE` |
| `apple.com` | `APPLE` |
| `facebook.com` | `FACEBOOK` |
| `threads.net`, `threads.com` | `THREADS` |

URLs that don't match any of these are silently skipped — they won't be saved.

## What this chain doesn't enforce

There's no server-side orchestrator forcing each step to run in order — the chain is honor-system. The `RECOUP.md` checklist is what gives you determinism in practice: as long as you tick boxes and persist values after each step, a fresh turn (or a different agent) can pick up exactly where the last one stopped. If you skip a checkbox or skip the persist, the next turn won't know that step ran and may either redo it or, worse, treat downstream calls as ready when they aren't.

A few constraints to honor:

- **Run steps in order.** The frontmatter values written at one step are the inputs for later steps.
- **Don't continue past a 4xx/5xx without recovery.** Leave the box unchecked, write the error to `## Notes`, and resolve before resuming.
- **Treat the file as the source of truth.** If something isn't on disk, don't assume it ran.
