# Running post-production on Vercel Sandbox

An optional path for steps 8-9 of `podcast-episode.md` and section 4 of `podcast-shorts.md`. The raw media
lives on a Vercel Drive; every re-cut, build and render runs in its own 8-vCPU sandbox; the laptop only edits
text files and plays the results. Use it when the operator's machine is slow or needed during renders.

Evidence (Paula Moore, 2026-10-21): ch05 (86 s) rendered in 1m 29s in a sandbox vs 7m 06s on the Intel
laptop, frames matching the local render (SSIM 0.983, fonts and cards identical). A full re-cut + build +
render of ch05 took 4.0 min end to end. Cost is about $1.35 per sandbox-hour at full load (8 vCPU x $0.128
plus 16 GB x $0.0212 per hour on Pro), so an episode's chapters and shorts come to well under $10; the Drive
holds ~1.1 GB per episode at $0.05/GB-month.

## Which path this operator uses

`~/.config/recoup/podcast-sandbox.json` records it: `"default": "sandbox"` means every heavy step runs in a
sandbox for this operator. **Read this file at the start of post-production.** With the sandbox default, never
run `cut.py`, `build.py`, `build_hy.py`, `render.sh` or `hyperframes render` locally, not even a one-minute
re-cut after a small fix; ask the owner first. No file, or `"default": "local"`, means the local commands
in the episode and shorts references.

## Stays local vs runs in the sandbox

| Local (light) | Sandbox (`scripts/podcast/sandbox/studio.mjs`) |
|---|---|
| Editing `chapters.json`, `specs.py`, `shorts.json`, `episode.json`, `ANALYSIS.md` | Re-cut camera and audio media (`cut.py` via `build.py --recut` / `build_hy.py --recut`) |
| `rough_audio.py` (audio only, about a minute) | Chapter build, `edit/screen_share.py` when a chapter overlaps the share window, render |
| `readcheck.js` in an open browser tab on a comp pulled back by `build`; ffmpeg frame grabs from a rendered MP4 | Shorts build, render and loudness pass (`shorts/render.sh`); `hyperframes snapshot` (a full headless render) |
| Playing exports in Finder | |

Not covered yet (they run locally until the runner gains a job for them): `transcribe.py`,
`fix_host_video.py`, `make_intro.py` renders. `studio.mjs enhanced` (Adobe output -> `enhance_pack.py` unpack +
host gate) and `studio.mjs assemble` (opening join + `assemble.py`) run those two on the sandbox. `run` does not
always refresh the pulled-back comp: run `build` before a readcheck. With the sandbox default,
tell the owner which of these is next and how long it takes locally before running it.

## One-time setup

1. Credentials: `VERCEL_TOKEN`, `VERCEL_TEAM_ID`, `VERCEL_PROJECT_ID` in an env file (Pro plan: 8 vCPUs,
   24 h sessions). Pass it with `node --env-file=<file>`; never print the values.
2. SDK, installed outside the skill: `npm i --prefix ~/.cache/recoup/podcast-sandbox @vercel/sandbox@3.8.0`.
3. `node --env-file=<env> scripts/podcast/sandbox/studio.mjs setup`: installs ffmpeg, zsh, Chrome's
   libraries and HyperFrames into a base snapshot (~40 s) and writes its id plus `"default": "sandbox"` to
   the config file.

## Per episode

1. `studio.mjs media <project>` after the camera check and `fix_host_video.py`: uploads only what the cut reads
   (role-named raw files and their symlink targets, `host-video-fixed.mp4`, the screen share from
   `chapters.json`, any `*-enhanced` audio) to the `podcast-media` drive under `<project-folder-name>/raw/`.
   ~2.4 MB/s from the laptop: 1.1 GB took 7.6 min. Files already there at the same size are skipped; re-run it
   whenever a raw file changes. **Not during a live recording**: the upload competes with Restream.
2. Check before rendering: `studio.mjs build <project> ch05` re-cuts and builds in a sandbox and pulls
   `comp/chapters/ch05` back; snapshot it locally as in step 8.
3. Render: `studio.mjs run <project> ch02 ch05 s3 ...`. Every id gets its own sandbox, all in parallel, so
   the wall time is about the longest job. Chapters land in `exports/<ch>.mp4` (the previous file moves to
   `exports/.prev/`), shorts in `exports/shorts/<slug>.mp4`, and the built comp replaces the local one.
4. Open each export in Finder for the owner, as on the local path.

## Gotchas

- **Persistent by default.** A sandbox created without `persistent: false` snapshots itself on stop and bills
  snapshot storage; the runner opts out for every job.
- **Command working directory is the image's home, not `/vercel/sandbox`**: relative paths fail. The runner
  uses absolute paths.
- **One read-write mount per drive.** Parallel jobs mount a read-only drive snapshot; `media` is the only
  writer.
- **Rebuilds drop episode-only overlays.** `render.sh` rebuilds the comp; a chapter that needs
  `edit/screen_share.py` is built, overlaid and rendered by the runner directly.
- **macOS tar metadata**: archives made without `--no-xattrs` print a provenance warning per file on Linux.
- **Pin HyperFrames** to the version used locally (`studio.mjs` `HF`) so sandbox and laptop renders match.
