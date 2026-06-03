# Song sourcing fallback chain

The short-video skill's compose step (and the async pipeline's lipsync mode) need a `song.mp3`. Don't assume one exists locally, and don't assume the user has one to hand.

## Order of attempts

### 1. Check the artist's sandbox repo first

Each Recoup account has a backing GitHub repo. If the user has imported songs through Recoup, they live at predictable paths:

```
.openclaw/workspace/orgs/{org-slug}/artists/{artist-slug}/songs/{song-slug}/{song-slug}.mp3
                                                                            /lyrics.json
                                                                            /clips.json
```

Discover the repo with `GET /api/sandboxes` (returns `github_repo` and a `filetree`). Fetch a file with `GET /api/sandboxes/file?path=…`.

**Binary files (`.mp3`, `.png`, `.mp4`) come back base64-encoded in the `content` field. Decode before writing to disk.** Skipping this step produces a file that looks the right size but isn't playable, which fails silently in ffmpeg.

### 2. If no song is in the sandbox, ask the user how to proceed

Two options to offer. **Don't pick silently — the cost of pulling the wrong song from YouTube is high enough that the user should make the call.**

- *"Want me to fetch the audio from YouTube?"* The agent downloads via `yt-dlp` (or equivalent) and saves locally. The user is responsible for any rights / DSP-licensing implications.
- *"Want to supply the song yourself?"* The user uploads or supplies a path; the agent reads from there.

### 3. Do not fall back to "use a placeholder track"

A music video without the song is not a deliverable. If sourcing fails through both paths above, stop and surface the blocker rather than producing a video with the wrong audio.

## Why this matters

The audio is the only stage where the agent can produce something that *looks* correct (right runtime, right format, right resolution) while being substantively wrong. Visual stages either render or 422; audio stages render fine with the wrong content. That's why the fallback chain is opinionated and surfaces failure rather than fabricating.
