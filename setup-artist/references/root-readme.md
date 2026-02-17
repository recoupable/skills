# Root README Template

Create this as `README.md` at the artist workspace root. Replace all `{placeholders}`.

---

```markdown
# {Artist Name}

Artist workspace — contains all context, content, songs, releases, and configuration for one artist. This directory is the **root** of the artist's sandbox environment.

## Directory Structure

| Directory | Purpose | Start here? |
|-----------|---------|:-----------:|
| `context/` | Essential artist context — identity, brand, audience, era, services, tasks | ✅ Yes |
| `memory/` | Learned knowledge — what agents discover over time. See `README.md` inside | ✅ Yes |
| `songs/` | Song catalog — one folder per song with audio, lyrics, metadata | ✅ Yes |
| `releases/` | Release catalog — one folder per release with RELEASE.md and artwork | ✅ Yes |
| `config/` | Per-artist config and state for shared tools (content-creation, content-poster, etc.) | When ready |
| `content/` | Created content — `images/` and `videos/{type}/` (e.g. `shortform`) | When ready |
| `library/` | Deep-dive reference docs — research, reports, strategies. See `README.md` inside | When ready |
| `apps/` | Artist-specific applications (e.g. personal website). See `README.md` inside | When ready |

## Context Files

| File | Format | Purpose |
|------|--------|---------|
| `context/artist.md` | Markdown | Complete artist profile — identity, brand, visual world, voice, tone |
| `context/audience.md` | Markdown | Emotional relationship with listeners — why they connect, how they talk, what earns shares |
| `context/era.json` | JSON | Machine routing — current release, song, phase, release date |
| `context/services.json` | JSON | All tools/accounts/capabilities — universal + optional services |
| `context/tasks.md` | Markdown | What needs to be done — organized by phase |
| `context/images/` | Images | Visual references — face guide, expressions, style references |

## Shared Tools

Shared automation apps (content-creation, content-poster) run **outside** this workspace. They read artist identity from `context/` and songs from `songs/`, and store their per-artist config in `config/{app-name}/`.

The `apps/` directory is for **artist-specific applications** only (like a personal website). Most artists start with it empty.

## Setup Checklist

### 1. Core Identity (do first)
- [ ] Verify `RECOUP.md` — artist slug, Recoup ID, status is `active`
- [ ] Write `context/artist.md` — identity, brand, visual world, voice, tone
- [ ] Write `context/audience.md` — who listens?

### 2. Music (do next)
- [ ] Add songs to `songs/{song-slug}/` (see `songs/README.md`)
- [ ] Create first release in `releases/{release-slug}/` (see `releases/README.md`)
- [ ] Set `context/era.json` — current release and phase

### 3. Accounts & Services
- [ ] Set up social accounts — TikTok, Instagram, YouTube, Twitter
- [ ] Update `context/services.json` with handles and account IDs

### 4. Content Pipeline (when ready)
- [ ] Add a face guide image to `context/images/face-guide.png`
- [ ] Set up `config/content-creation/config.json` (see `config/README.md`)
- [ ] Set up PostBridge — `config/content-poster/config.json`
- [ ] Start generating content
```
