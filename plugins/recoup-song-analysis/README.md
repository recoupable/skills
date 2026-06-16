# Recoup Song Analysis

Agent plugin for **song audio analysis**. Turn a track's *sound* into
structured intelligence — catalog metadata, lyrics, playlist pitches, sync
briefs, and mix feedback — using Recoup's audio language model (Music
Flamingo). Built by [Recoup](https://recoupable.com).

Point it at a public audio URL and it resolves the right analysis preset,
calls the endpoint, and hands back something a label, supervisor, or producer
can act on. Three skills cover it: `recoup-song-analyze` to understand the audio,
`recoup-song-hook` to find the clip-worthy moment, and `recoup-song-pitch-kit`
for playlist and sync placement materials.

## Install

### Claude Code (CLI)

```bash
claude plugin install https://github.com/recoupable/recoup-song-analysis
```

### Claude Cowork

1. Open the plugin marketplace (puzzle-piece icon in the sidebar).
2. Click **Add custom plugin** and paste:
   `https://github.com/recoupable/recoup-song-analysis`
3. Approve the requested tool permissions (`Read`, `Write`).
4. Confirm install: type `/plugin` and check that `recoup-song-analysis` is listed.

### Cursor

1. Cursor → Settings → Plugins → **Add custom plugin**.
2. Paste the GitHub URL above.
3. Restart Cursor so `.cursor-plugin/plugin.json` loads the skills.

## Skills

| Skill | What it does |
|-------|-------------|
| [recoup-song-analyze](skills/recoup-song-analyze) | Understand the audio — full report, catalog metadata (BPM/key/genre/mood), lyric sheet, or mix critique |
| [recoup-song-hook](skills/recoup-song-hook) | Find the clip-worthy 5–15s moment (the hook/drop) with timestamps, for short-form video |
| [recoup-song-pitch-kit](skills/recoup-song-pitch-kit) | Placement materials — a playlist/editorial pitch and a music-supervisor sync brief |

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
