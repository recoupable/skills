---
name: recoup-artists
description: Manage your roster — onboard a new artist and operate inside an artist's workspace. Modes — create (onboard + enrich a brand-new artist via the 8-call chain: create → Spotify match → research → catalog → socials → knowledge base) and workspace (work inside artists/{slug}/ — read/update context, songs, releases, and answer "what artists do I have"). Use for "create/add/onboard an artist", "set up [artist]", "what artists do I have", "list my roster", "organize this artist's files", "update [artist]'s brand/context", or any task about a named artist's files. For research/metrics on an artist use recoup-research; for the API call layer use recoup-api.
---

# Recoup Artists

Roster management — bring a new artist into the box, and operate inside an
existing artist's workspace. It **picks a mode from the ask**.

| The user wants… | Mode |
|---|---|
| "create / onboard / add an artist", "set up [artist]" | **create** |
| "what artists do I have", organize/update an artist's files | **workspace** |

## Mode: create (8-call onboarding chain — driven by a checklist)

Long chains run from prose drop steps, so **drive from the `RECOUP.md` checklist**:
scaffold it first (frontmatter holds captured values; body holds the unchecked
steps), tick + persist after each step — the file IS the workflow state, resumable
from the first unchecked box. Don't run under an `agent+` account (data gets
orphaned). The 8 calls:

1. `POST /api/artists {name, organization_id}` → capture `account_id`.
2. `GET /api/spotify/search` → best match → `id`, `external_urls.spotify`, `images[0]`.
3. `PATCH /api/artists/{id}` with image + `profileUrls:{SPOTIFY}` (UPPERCASE keys).
4. Structured research (retry transient misses): `/research/lookup?spotifyId=` →
   `songstats_artist_id`, then `/research/profile|career|playlists` + `/research/web`.
5. Spotify catalog (`topTracks`, `albums`, `album`) → write `releases/{slug}/RELEASE.md`
   per album (from `references/release-template.md`) + `releases/top-tracks.md`.
6. Web search for socials (ig/tiktok/twitter/youtube).
7. `PATCH /api/artists/{id}` with discovered `profileUrls` (only platforms found).
8. Synthesize a `## Knowledge base` section into `RECOUP.md`.

Run in order; don't continue past a 4xx/5xx without recovery. (Uses `recoup-api`
for the call shapes.)

## Mode: workspace (operate inside an artist's folder)

Artist dirs live at `artists/{artist-slug}/`; `RECOUP.md` (frontmatter
`artistName`/`artistSlug`/`artistId`) is the identity file.

**Inventory** ("what artists do I have", "list my roster", "what's in this
sandbox") → walk the filesystem when it's a real sandbox (`ls -d artists/*/`,
`find artists -name RECOUP.md`); if `artists/` is missing/empty, fall back to
`recoup-api` roster discovery — **never report an empty roster from a missing
filesystem.**

**Layout:** `context/artist.md` (who they are — static), `context/audience.md`
(static), `context/images/face-guide.png`, `releases/{slug}/RELEASE.md`
(18-section master doc — `references/release-template.md`), `songs/{slug}/{slug}.mp3`.
Nothing is pre-created — add files when real content arrives; never write
placeholder tokens.

**Static vs dynamic context:** update `artist.md`/`audience.md` deliberately
(they're the source of truth other skills read); treat research/release docs as
time-bound — archive when stale. Templates: `references/artist-template.md`
(+ `references/artist-example.md`), `references/audience-template.md`,
`references/release-template.md`. Commit `{what}: {why}`; the git log is the
per-artist progress log.

## Guardrails

- **The file is the state** for create — tick + persist each step or a fresh turn
  redoes/skips work.
- **No placeholder data** in artist files — real content or leave the section out.
- **Don't overwrite static context** casually — `artist.md` changes are
  deliberate evolutions; note the why in the commit.
- **Never invent a roster/artist** — empty filesystem ≠ empty roster; confirm via
  `recoup-api` first.

## References

- `references/artist-template.md` · `references/artist-example.md` ·
  `references/audience-template.md` · `references/release-template.md` — the
  workspace context + release scaffolds.
