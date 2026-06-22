# Artist-workspace context (read first, API second)

Every Recoup content skill is **artist-workspace-native**: when an artist workspace
exists, the artist's own files are the source of truth for who they are and how they
sound. Read them before calling any API. The API is the *fallback* for when no workspace
exists (mirrors the `recoup-api` rule: "the filesystem is authoritative for this sandbox").

## Context is OPTIONAL — three modes

Content skills run in whichever mode fits the request. Context **enriches**; it is never a
hard requirement except where noted.

| Mode | When | Where inputs come from |
| --- | --- | --- |
| **Context mode** | "make a video for Mari Vega" + a workspace exists | read `context/` etc. (below) |
| **API-fallback mode** | a Recoup artist exists but no local workspace | pull from the API (§4) |
| **Generic mode** | "just make me a cinematic studio clip", no artist named | use the **user's** prompt, image, audio, and template directly — skip artist context entirely |

**Generic mode is fully valid.** If the user doesn't want artist context, don't force it —
take their explicit inputs and run the pipeline. The one thing you must never do is
*fabricate* an artist's voice or likeness: if a skill's whole point is "sound/look like
THIS artist" and there's no context and no API data, ask rather than invent. For
format-only jobs (a generic quote card, a stock-feel clip), just generate from the user's
inputs.

> This file ships inside the skill that reads it. It is a byte-identical vendored copy of
> the canonical `plugins/recoup-records/references/workspace-context.md`; edit the
> canonical and re-sync (see `scripts/vendored.json`).

## 1. Find the workspace

Artist workspaces live at `artists/{artist-slug}/`. Resolve the slug from the artist
name (lowercase, non-alphanumerics → hyphens), or list what exists:

```bash
ls -d artists/*/ 2>/dev/null            # all artist workspaces in this sandbox
ARTIST_SLUG=$(echo "$ARTIST_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g; s/^-//; s/-$//')
ARTIST_DIR="artists/$ARTIST_SLUG"
```

If `$ARTIST_DIR/RECOUP.md` exists, you are in a real workspace — read from it. If it does
not, skip to §4 (API fallback) and do **not** fabricate context.

## 2. The context files (the moat)

Read whichever exist. These are the inputs that make output sound like *this* artist
instead of generic AI:

| File | What it gives you | Used for |
| --- | --- | --- |
| `context/artist.md` | identity, brand, **voice/tone**, aesthetic, creative constraints | captions, image style, every text/visual job — **the source of truth** |
| `context/audience.md` | who fans are, what resonates, **how they talk** | audience-tuned phrasing, hashtags, slang |
| `context/images/face-guide.png` | face reference for visual generation | the reference image for image/video gen (`$REFERENCE_IMAGE_URL`) |
| `releases/{slug}/RELEASE.md` | release metadata, narrative, dates, cover art URL | announcements, release captions, packs |
| `songs/{song-slug}/{song-slug}.mp3` | the audio itself | anything that needs the song |

```bash
cat "$ARTIST_DIR/context/artist.md"   2>/dev/null   # voice + aesthetic
cat "$ARTIST_DIR/context/audience.md" 2>/dev/null   # how fans talk
ls   "$ARTIST_DIR/context/images/face-guide.png" 2>/dev/null
```

Treat `context/artist.md` as **static context** — the deliberate, maintained truth. Never
overwrite it as a side effect of generating content; only update it when the artist
genuinely evolves, with a clear commit reason.

## 3. Resolve `RECOUP.md` identity

`RECOUP.md` frontmatter carries the canonical IDs the API needs (`artistId`,
`spotifyArtistId`, etc.). Read them rather than re-deriving:

```bash
head -20 "$ARTIST_DIR/RECOUP.md"   # frontmatter: artistName, artistSlug, artistId, ...
```

## 4. API fallback (no workspace, or thin context)

When there is no workspace — or `context/artist.md` is missing — learn the voice from the
artist's real posts instead of inventing one. See the account-resolver reference for auth
and for resolving the artist's `id`.

```bash
# Real captions across platforms — the best available voice signal when there's no artist.md
curl -sS "$AUTH_HEADER" "https://api.recoupable.com/api/artists/$ARTIST_ID/posts" | jq
# Profile / socials for tone + handles
curl -sS "$AUTH_HEADER" "https://api.recoupable.com/api/artists/$ARTIST_ID/socials" | jq
```

If neither workspace context nor API posts are available, **say so and ask the user for
voice guidance** rather than producing a generic, off-brand result.

## 5. Write outputs BACK into the workspace

Finished assets are workspace artifacts, not throwaway chat output. When a workspace
exists, persist results so the next turn (and the next agent) can build on them:

- Per-release work → `artists/{slug}/releases/{release-slug}/` (next to its `RELEASE.md`).
- Cross-release / standalone work → `artists/{slug}/content/{job}/`.
- Commit with the workspace convention `{what}: {why}`, e.g.
  `content: brand-voice captions for "Midnight" single launch`.

Reference data by path — never copy a song or context file into an output folder.

## Why this order

Anyone can call an image or caption API. Only Recoup already holds the artist's voice,
audience, face, and catalog on disk. Reading that context first is the entire difference
between "a caption" and "a caption that sounds like them." The API floor is commodity;
the workspace context is the moat.
