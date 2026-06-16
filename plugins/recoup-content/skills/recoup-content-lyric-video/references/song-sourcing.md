# Song sourcing fallback chain

Any skill that needs the song's audio (lipsync video, lyric video, visualizer, hook
finder, the compose/mux step) needs a real `song.mp3`. Don't assume one exists locally, and
don't assume the user has one to hand. Never fabricate or substitute audio.

> This file ships inside the skill that reads it. It is a byte-identical vendored copy of
> the canonical `plugins/recoup-content/references/song-sourcing.md`; edit the canonical and
> re-sync (see `scripts/vendored.json`).

## Order of attempts

### 1. Check the artist workspace first

If you're in an artist workspace, songs live at a predictable path:

```bash
ls "$ARTIST_DIR/songs/"{song-slug}"/"*.mp3 2>/dev/null
```

The filename is the song title — `songs/midnight/midnight.mp3` → "midnight". If the song
isn't on disk but the artist has imported it through Recoup, fetch it from the backing
sandbox repo: discover with `GET /api/sandboxes` (returns `github_repo` + `filetree`),
then `GET /api/sandboxes/file?path=…`.

**Binary files (`.mp3`, `.png`, `.mp4`) come back base64-encoded in the `content` field.
Decode before writing to disk.** Skipping this produces a file that's the right size but
unplayable, which then fails silently in ffmpeg.

### 2. If no song is found, ask the user how to proceed

Two options — **don't pick silently;** pulling the wrong track from YouTube is costly
enough that the user should choose:

- *"Want me to fetch the audio from YouTube?"* — download via `yt-dlp` (or equivalent). The
  user owns any rights / DSP-licensing implications.
- *"Want to supply the song yourself?"* — the user provides a path or upload; read from
  there.

### 3. Do not fall back to a placeholder track

A music asset with the wrong (or no) song is not a deliverable. If sourcing fails through
both paths, stop and surface the blocker rather than shipping wrong audio.

## Why this matters

Audio is the one stage where the agent can produce something that *looks* correct (right
runtime, format, resolution) while being substantively wrong — visual stages either render
or 422, but audio renders fine with the wrong content. That's why this chain is opinionated
and surfaces failure instead of guessing.
