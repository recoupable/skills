---
name: artist-workspace
description: How to work in artist directories — including creating, enumerating, and editing them. Use when creating or onboarding a new artist ("create artist", "onboard X", "add this artist", "set up a new artist") — this skill scaffolds the artist's `RECOUP.md` checklist file and drives the multi-step setup from it. Use when adding or updating artist context (identity, brand, voice, audience), adding songs, organizing files inside an artist directory, or figuring out where something belongs. Also use when the account asks inventory questions like "what artists do I have", "list my artists", "which orgs am I in", "what's in this sandbox" — the filesystem tree is the authoritative answer. And use when the account mentions an artist by name and the task involves their files, context, or content — even if they don't say "artist directory." This includes tasks like researching an artist, creating content for an artist, updating an artist's brand, or adding a face guide.
---

# Artist Workspace

Every artist has a workspace — a directory that holds context, songs, and reference material. The `RECOUP.md` file at the root connects it to the Recoupable platform.

Artist directories live inside the sandbox at `artists/{artist-slug}/`. The sandbox is already scoped to a single Recoupable organization (its repo *is* the org), so artists live at the top level — there is no `orgs/` directory.

## Listing what's in the sandbox

When the account asks *"what artists do I have"*, *"list my artists"*, *"which orgs am I in"*, or any other inventory question about the sandbox, **walk the filesystem — it is authoritative for this sandbox.** Do not call the Recoupable API for this: the API answers "what artists does this account have access to across everything", which is a different (and usually larger) set than what the sandbox was opened for.

```bash
# All artist workspaces in this sandbox
ls -d artists/*/ 2>/dev/null

# Every artist's identity file — read the frontmatter for name/slug/id
find artists -type f -name RECOUP.md 2>/dev/null
```

Each `RECOUP.md` has frontmatter (`artistName`, `artistSlug`, `artistId`) — read it with `head` or any YAML parser to get the canonical identity.

If `artists/` does not exist, the sandbox has not been set up yet — point the account at the `setup-sandbox` skill rather than inventing data.

## Creating a new artist

When the user asks to create a new artist (or onboard, add, or set one up), drive the work from a **checklist file** — don't try to run the chain from memory. The setup is 8 sequential API calls and the agent loop loses state between turns; the checklist is what lets you resume cleanly and prove which steps actually ran.

### Step 0: Scaffold the workspace BEFORE any API call

Pick a slug, make the directory, and write the initial `RECOUP.md` template — frontmatter holds the values the chain captures, body holds the unchecked steps:

```bash
ARTIST_SLUG=$(echo "$ARTIST_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g; s/^-//; s/-$//')
ARTIST_DIR="artists/$ARTIST_SLUG"
mkdir -p "$ARTIST_DIR"

cat > "$ARTIST_DIR/RECOUP.md" <<EOF
---
artistName: $ARTIST_NAME
artistSlug: $ARTIST_SLUG
artistId:
spotifyArtistId:
spotifyProfileUrl:
imageUrl:
cmArtistId:
---

# $ARTIST_NAME

## Setup checklist

- [ ] 1. Create the artist (\`POST /api/artists\`) — capture \`account_id\` → \`artistId\`
- [ ] 2. Find canonical Spotify match (\`GET /api/spotify/search\`) — capture \`id\`, \`external_urls.spotify\`, \`images[0].url\`
- [ ] 3. PATCH artist with image + Spotify profile URL
- [ ] 4. Structured research — \`/research/lookup\` (capture \`cmArtistId\`) → \`/research/profile\` + \`/research/career\` + \`/research/playlists\` + \`/research/web\`. Save responses under \`## Research\` in this file.
- [ ] 5. Pull Spotify catalog → write \`releases/{album-slug}/RELEASE.md\` per album + \`releases/top-tracks.md\` (see Releases section)
- [ ] 6. Web search for additional socials (instagram / tiktok / twitter / youtube)
- [ ] 7. PATCH artist with discovered socials
- [ ] 8. Synthesize knowledge base — append it as \`## Knowledge base\` in this file

## Notes
EOF
```

Don't proceed to step 1 until the file exists on disk.

The full curl-by-curl playbook for steps 1–8 lives at `https://developers.recoupable.com/workflows/create-artist` and is also linked from the `recoup-api` skill. Fetch it once at scaffold time and follow it in order.

### After every step: tick + persist

Two writes back to `RECOUP.md` after each step completes:

1. **Tick the checkbox** (`- [ ]` → `- [x]`) for the step that just ran.
2. **Write the captured value** into frontmatter (`artistId:`, `spotifyArtistId:`, `spotifyProfileUrl:`, `imageUrl:`, `cmArtistId:`). Later steps read these values from the frontmatter — never re-derive what's already saved. Larger payloads (research responses, social URLs) belong under their own headed subsection in the body, not in frontmatter.

The file IS the workflow state. If a value isn't on disk, the next turn doesn't know it.

### Resuming a partial setup

If `$ARTIST_DIR/RECOUP.md` already exists, do not re-run completed steps. Read the file, find the first unchecked item, and resume from there using the captured frontmatter values:

```bash
# Show the next unchecked step
grep -n '^- \[ \]' "$ARTIST_DIR/RECOUP.md" | head -1
```

If every item is checked, the artist is fully set up — confirm with the user before doing anything else.

### Why the checklist

Long deterministic chains executed from prose tend to drop steps: the agent reads the doc once, runs a few calls, and forgets the rest. A file-as-state checklist sidesteps that — progress is visible on disk, every step has a write-back side effect, and a fresh turn can resume from the file rather than re-deriving what's already been done.

## Entering an Artist Workspace

When starting work in an artist directory:

1. Read `RECOUP.md` to confirm you're in an artist workspace and get the artist's name, slug, and ID.
2. Check what exists — `ls` the directory to see which files and folders are already there.
3. Read `context/artist.md` if it exists — this is the source of truth for who the artist is. Everything you do should be consistent with it.
4. Check recent git history for this artist — from the repo root, `git log --oneline -10 -- artists/{artist-slug}/` shows only commits that touched this artist's files. If you're already inside the artist directory, use `git log --oneline -10 -- .` instead. Read the commit messages to understand recent changes before making your own.

---

## Working in an Artist Directory

### What Goes Where

A populated artist workspace looks like this. Nothing here is pre-created — each file and directory gets added when there's real content for it.

```
{artist-slug}/
├── RECOUP.md                    # identity — connects workspace to the platform
├── context/
│   ├── artist.md                # who they are, how they present, creative constraints
│   ├── audience.md              # who listens and what resonates
│   └── images/
│       └── face-guide.png       # face reference for visual content generation
├── releases/
│   ├── top-tracks.md            # cross-release Spotify top tracks (snapshot)
│   └── {release-slug}/          # one folder per album / EP / single
│       └── RELEASE.md           # tracklist + Spotify metadata + cover art URL
└── songs/
    └── {song-slug}/
        ├── {song-slug}.mp3
        └── {song-slug}.wav
```

If a file or directory doesn't exist yet, create it when the content arrives. If it already exists, update it — don't overwrite without reading what's there first. The directory structure emerges from the work, not from scaffolding.

### Static vs Dynamic Context

Think of artist context in two layers:

**Static context** is who the artist IS. It evolves slowly — across months, release cycles, career phases. `artist.md` and `audience.md` are static. A 20-year-old bedroom-pop pianist might still be a bedroom-pop pianist next year, but over time she may grow into new sonics, shift her aesthetic, or reach a different audience. Update static context deliberately, not casually. When you change `artist.md`, you're changing the source of truth that every tool and agent relies on.

**Dynamic context** is what's happening NOW. Release documents, campaign research, strategy docs — these are tied to a moment in time. They get appended to, they go stale, they get replaced by the next cycle. Treat them as time-bound. When a release cycle ends or research becomes outdated, archive it rather than letting it clutter the working directory.

This distinction matters because agents reading the workspace need to know: is this a durable fact about the artist, or a snapshot from three months ago? Static context should feel trustworthy. Dynamic context should feel current — and if it's not current, it should be moved out of the way.

### Artist Context (`context/artist.md`)

The most important file in the workspace. Defines identity, brand, voice, aesthetic, and creative constraints. Other tools and agents read it to stay on-brand. This is static context — update it when the artist genuinely evolves, not for every campaign shift.

Create it when you have real information. A partial profile with real data beats a complete template with placeholders. Don't fabricate details you don't know — leave sections out rather than guessing.

Read `references/artist-template.md` for the section-by-section structure when creating one for the first time. See `references/artist-example.md` for what a filled one looks like.

### Audience Context (`context/audience.md`)

Who the fans are, what resonates with them, how they talk. Static context — the audience shifts gradually as the artist grows, not with every release.

Create when you have real audience data. Read `references/audience-template.md` when creating it for the first time.

### Songs

Songs are the source material. They live in `songs/{song-slug}/` permanently. Name the mp3 after the song — the filename becomes the song title in downstream tools.

```
songs/adhd/adhd.mp3           ✓  title becomes "adhd"
songs/adhd/audio.mp3          ✗  title becomes "audio"
```

### Releases

Releases live at `releases/{release-slug}/`. Each release is a folder with a `RELEASE.md` at the root — the master release-management document that travels with the release through every lifecycle stage (announcement, release week, sustain). Every other release-level artifact (research, copy, assets, derivative reports) goes in the same folder.

**Slug convention** — `lowercase-kebab-case` of the project title plus a format suffix:

- **Album** → `releases/{title-slug}/` (no suffix — album is the default)
- **EP** → `releases/{title-slug}-ep/`
- **Single** → `releases/{title-slug}-single/`
- **Compilation** → `releases/{title-slug}-compilation/`

```
releases/after-hours/RELEASE.md          # album
releases/adhd-ep/RELEASE.md              # EP
releases/blinding-lights-single/RELEASE.md
```

The `RELEASE.md` is **18 sections** covering project snapshot, identifiers + metadata, narrative, audience, DSP strategy, marketing, social, PR, visuals, physical/merch/touring, team, budget, KPI tracking, and a links hub — plus an Outstanding Deliverables table and a Document History log. Read `references/release-template.md` for the full canonical template, sharing-tag conventions (`[INTERNAL]` / `[SHAREABLE]` / `[OPS]`), and status markers (`✅` / `❌` / `⚠️ TBD` / `N/A`).

It references songs by slug — it doesn't duplicate or move them.

#### Where Spotify catalog data lands

Step 5 of the create-artist chain (Spotify catalog) populates this folder:

- **Each album returned by `GET /api/spotify/artist/albums`** → `releases/{release-slug}/RELEASE.md` scaffolded from `references/release-template.md`. Step 5 fills the Spotify-derivable fields (Section 1: artist name, project title, release date, format; Section 2.1: Spotify URI; Section 2.2: per-track title + duration + explicit; Section 2.3: cross-reference local `songs/`; Section 18: cover art URL) and leaves everything else as `⚠️ TBD`. ISRC, UPC, writers/producers, label, distributor, and all marketing/PR/budget sections aren't in the public Spotify response — they stay TBD until the user provides them. See `references/release-template.md` for the full mapping.
- **`GET /api/spotify/artist/topTracks`** → `releases/top-tracks.md` (cross-release snapshot — these aren't a release themselves but live here because it's all Spotify catalog data and pinning it next to releases keeps the catalog in one place). Inline structure:

  ```markdown
  ---
  title: Top Tracks
  source: spotify
  snapshotDate: {YYYY-MM-DD}
  ---

  # Top Tracks

  | # | Track | Album | Duration |
  |---|-------|-------|----------|
  | 1 | {name} | {album-slug or external} | {mm:ss} |
  ```

### Organizing Other Files

Group related files together. A competitive analysis, brand bible, and strategy doc are all research — they belong in the same directory, not scattered across three. Before creating a new directory, check if the file fits somewhere that already exists.

When dynamic context gets stale — a release cycle ends, a strategy doc becomes outdated — move it to an archive rather than deleting it or leaving it where active files live. Create the archive when you need it, not before.

Data lives in one place. Songs live in `songs/`, not copied into release folders. Context lives in `context/`, not duplicated into research docs. If something needs to reference data from another location, reference it by path — don't copy it.

## Naming Conventions

- **Directories and slugs:** `lowercase-kebab-case`
- **Song files:** `songs/{song-slug}/{song-slug}.mp3`

## Tracking Changes

Use git history as the progress log. Every change to an artist directory should be a commit with a message that captures what changed and why.

**Good commit messages for artist directories:**

```
artist: update aesthetic — shifting from bedroom to lo-fi studio (user direction)
songs: add 5 tracks from ADHD EP with lyrics and clips
research: competitive analysis for Q2 release planning
release: update ADHD EP — distributor confirmed as SpaceHeater
context: refine audience — adding Gen Alpha psychographics from fan survey
archive: move pre-release strategy docs from ADHD EP cycle
```

The pattern: `{what}: {why}`. The "what" tells you the area. The "why" tells the next agent the intent — not just that something changed, but the reason it changed. This is especially important for static context changes, where a future agent needs to understand whether an update was a deliberate evolution or a mistake.

Don't maintain a separate progress file per artist. The git log is the source of truth. If you need to understand what happened, read the commits.

## Why This Structure

Artist workspaces used to have 10+ pre-created directories, README files in every folder, placeholder templates, a scoped memory system, and per-artist config files. Most of it went stale immediately because agents couldn't tell what was real data versus scaffolding. A file full of `{placeholder}` tokens looks like real data to an agent that wasn't there when it was created — and the output suffers.

The current structure is deliberately minimal. Nothing gets created until there's real content to put in it. The skill teaches where things go so agents can build the workspace organically as the work happens.
