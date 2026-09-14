# Portable video runtime

The installed skill is a resource bundle. Keep its scripts and assets read-only. Choose a project
for generated work and a separate runtime directory for Node dependencies. Existing workspace
folders can remain unchanged.

## Prepare once per runtime

Use Node 22 or newer and FFmpeg/ffprobe. Copy this skill's root `package.json` and
`package-lock.json` into an empty runtime directory outside the plugin, then run `npm ci` there.
The lockfile pins the dependency tree. It includes the CLI, producer, player, browser helpers,
GSAP, and Sharp. Package installation may run native setup and download Chromium; for an existing
browser, set `PUPPETEER_SKIP_DOWNLOAD=true` during setup and select it using
`PUPPETEER_EXECUTABLE_PATH` when running browser helpers.

Set `HYPERFRAMES_SKILL_RUNTIME_DIR` to that directory. Run helpers using their actual absolute
installed paths, with the selected output project as the working directory. The resolver checks
only explicitly selected roots, the current project, and the installed skill; it never searches
Downloads or a package manager's internal cache. `HYPERFRAMES_CLI` may explicitly override the
CLI JavaScript entrypoint. `HYPERFRAMES_ROOT` supports an explicitly supplied legacy checkout.

The CLI can be invoked as `node <runtime>/node_modules/hyperframes/bin/hyperframes.mjs`.
Run `--help` and `doctor` before relying on a feature. For command examples using `npx hyperframes`,
run from the prepared runtime or make its `node_modules/.bin` available on PATH. Keep project/output
arguments explicit. Creating a new project should preserve installed skills (`init --skip-skills`
where supported). Do not infer that a helper has been tested because its dependencies installed.

Package roles: [official HyperFrames repository](https://github.com/heygen-com/hyperframes).
Pinned versions were verified from the public npm registry when this runtime was prepared.

## Optional providers and Python tools

- Existing narration, transcripts, and supplied media can be used without provider calls.
- HeyGen and ElevenLabs require the selected account's credentials. Read only the project's
  `.env.local`/`.env`, or set `HYPERFRAMES_WORKSPACE_DIR` to the explicit workspace root.
  Environment loading admits only the provider key names used by the audio pipeline; shell values win.
- The audio helpers do not silently choose a home-directory HeyGen account. To reuse a CLI login,
  explicitly set `HEYGEN_CONFIG_DIR` to its credentials directory.
- WhisperX transcription requires `uvx`, Python, and model downloads. Native CLI transcription also
  downloads models on first use. Inspect the selected transcription path before running it.
- Music analysis and optional TTS providers may require Python packages. Use a project virtual
  environment and install the packages named by that helper there; record the resolved versions.
  `HYPERFRAMES_PYTHON` selects the Python used by ElevenLabs and optional background-music generation. No global pip installation.
- External media search, map data, remote sites, CDN scripts, and provider APIs require network access.
  Label unavailable capabilities and use a documented asset-free or supplied-media fallback.

## Brand fonts and demonstration assets

Read the selected workspace's `DESIGN.md` or supplied brief. Copy approved font files into the
output project's `assets/fonts/`, define local `@font-face` rules, and use those names in the
composition. This works with fonts added later without editing the plugin. Use a system font when
no brand font has been provided, and check layout after any font substitution.

Bundled fonts and effects retain their original notices. They are optional example assets, not a
blanket license to redistribute or use every theme commercially. In particular, the legacy
Cyberpunk coverword theme no longer loads its replica font by default: supply an approved TTF via
`HYPERFRAMES_BRAND_FONT` and corresponding glyph-width JSON via `HYPERFRAMES_BRAND_METRICS`, or choose
another theme. Personal-use replica and Virgil font binaries are not distributed in this public package.
There is no bundled demo-font opt-in.
Graphic overlay handwriting examples expect an approved workspace font. Preserve vendor notices.
