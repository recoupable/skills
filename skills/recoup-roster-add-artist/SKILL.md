---
name: recoup-roster-add-artist
description: Onboard a brand-new artist to your roster and enrich them — the 8-step chain (create → Spotify match → research → catalog → socials → knowledge base) that sets up the artist and their workspace folder. Use for "create/add/onboard an artist", "set up [artist]", "we just signed [artist]", or "new signing". To see your roster use recoup-roster-list-artists; to work inside an existing artist's files use recoup-roster-manage-artist.
---

# Recoup — Add Artist

Bring a new artist into the box: create the account, enrich it, and scaffold their
workspace. Driven by a checklist so the long chain is resumable.

## The 8-step onboarding chain (drive from the RECOUP.md checklist)

Long chains run from prose drop steps, so **drive from the `RECOUP.md` checklist**:
scaffold it first (frontmatter holds captured values; body holds the unchecked
steps), tick + persist after each step — the file IS the workflow state, resumable
from the first unchecked box. Don't run under an `agent+` account (data gets
orphaned). The 8 steps:

1. `POST /api/artists {name, organization_id}` → capture `account_id`.
2. `GET /api/spotify/search` → verified match (inspect identity and catalog) → `id`, `external_urls.spotify`, `images[0]`.
3. `PATCH /api/artists/{id}` with image + `profileUrls:{SPOTIFY}` (UPPERCASE keys).
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

Run in order; check HTTP status before using each response. Stop on `402` and
surface `billingUrl`; defer `429` until `Retry-After` allows a later attempt.
Retry only network failures or `5xx`, at most three attempts with a 90-second
timeout per request. Leave the step unchecked until errors are resolved. Uses
recoup-platform-api-access for the call shapes.

## Guardrails

- **The file is the state** — tick + persist each step or a fresh turn redoes/skips work.
- **No placeholder data** in artist files — real content or leave the section out.
- **Never invent a roster/artist** — confirm via recoup-platform-api-access first; an
  empty filesystem is not an empty roster.
