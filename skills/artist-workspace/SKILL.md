---
name: artist-workspace
description: How to work in artist directories and how to enumerate what artists or orgs exist in the sandbox. Use when adding or updating artist context (identity, brand, voice, audience), adding songs, organizing files inside an artist directory, or figuring out where something belongs. Also use when the user asks inventory questions like "what artists do I have", "list my artists", "which orgs am I in", "what's in this sandbox" — the filesystem tree is the authoritative answer. And use when the user mentions an artist by name and the task involves their files, context, or content — even if they don't say "artist directory." This includes tasks like researching an artist, creating content for an artist, updating an artist's brand, or adding a face guide.
---

# Artist Workspace

Every artist has a workspace — a directory that holds context, songs, and reference material. The `RECOUP.md` file at the root connects it to the Recoupable platform.

Artist directories live inside the sandbox at `orgs/{org-slug}/artists/{artist-slug}/`.

## Listing what's in the sandbox

When the user asks *"what artists do I have"*, *"list my artists"*, *"which orgs am I in"*, or any other inventory question about the sandbox, **walk the filesystem — it is authoritative for this sandbox.** Do not call the Recoupable API for this: the API answers "what artists does this user have access to across everything", which is a different (and usually larger) set than what the sandbox was opened for.

```bash
# All artist workspaces in this sandbox, across all orgs
ls -d orgs/*/artists/*/

# Every artist's identity file — read the frontmatter for name/slug/id
find orgs -type f -name RECOUP.md
```

Each `RECOUP.md` has frontmatter (`artistName`, `artistSlug`, `artistId`) — read it with `head` or any YAML parser to get the canonical identity. The parent directory name two levels above the `RECOUP.md` is the `{org-slug}`.

If `orgs/` does not exist, the sandbox has not been set up yet — point the user at the `setup-sandbox` skill rather than inventing data.

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

When songs are grouped into a release (EP, album, single), the release document references them by slug — it doesn't duplicate or move them. If you need to know which songs belong to a release, check the release document.

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
