# Recoup Songs

Agent plugin for **song audio analysis**. Turn a track's *sound* into
structured intelligence — catalog metadata, lyrics, playlist pitches, sync
briefs, and mix feedback — using Recoup's audio language model (Music
Flamingo). Built by [Recoup](https://recoupable.com).

Point it at a public audio URL and it resolves the right analysis preset,
calls the endpoint, and hands back something a label, supervisor, or producer
can act on. Start with `recoup-song-analyzer` — it routes to the focused
workflow skills below.

## Install

### Claude Code (CLI)

```bash
claude plugin install https://github.com/recoupable/recoup-songs
```

### Claude Cowork

1. Open the plugin marketplace (puzzle-piece icon in the sidebar).
2. Click **Add custom plugin** and paste:
   `https://github.com/recoupable/recoup-songs`
3. Approve the requested tool permissions (`Read`, `Write`).
4. Confirm install: type `/plugin` and check that `recoup-songs` is listed.

### Cursor

1. Cursor → Settings → Plugins → **Add custom plugin**.
2. Paste the GitHub URL above.
3. Restart Cursor so `.cursor-plugin/plugin.json` loads the skills.

## Skills

| Skill | What it does |
|-------|-------------|
| [recoup-song-analyzer](skills/recoup-song-analyzer) | Entry point — resolves the audio URL, picks the right preset, and routes to the focused workflows below |
| [recoup-song-metadata](skills/recoup-song-metadata) | Structured catalog metadata (BPM, key, genre, mood, instruments) for DSPs and catalog systems |
| [recoup-song-lyrics](skills/recoup-song-lyrics) | Sectioned lyric sheet from audio (draft for human review) + optional content advisory |
| [recoup-song-playlist-pitch](skills/recoup-song-playlist-pitch) | DSP / editorial playlist pitch plus positioning notes |
| [recoup-song-sync-brief](skills/recoup-song-sync-brief) | Music-supervisor sync brief with scene fit, brand-safety, and sample/clearance risk |
| [recoup-song-mix-feedback](skills/recoup-song-mix-feedback) | Technical mix critique by frequency band, with a prioritized fix checklist |

## How it works

All skills call the Music Flamingo endpoint (`POST /api/songs/analyze`). The
full contract — auth, base URL, request/response shapes, every preset, and the
REST/CLI/MCP call patterns — lives in
[`references/flamingo-api.md`](references/flamingo-api.md) and is vendored
byte-identical into each skill so every skill stays self-contained.

**Requirements that apply to every skill:**

- A **public `audio_url`** — the endpoint cannot take a local file upload.
- **No `account_id`** in the request body; auth determines the account.
- REST calls work with the sandbox bearer token (`RECOUP_ACCESS_TOKEN`); the
  `recoup` CLI works only when `RECOUP_API_KEY` is set.

## License

Apache-2.0. See [LICENSE](LICENSE).
