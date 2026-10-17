# Discover CLI commands

Users can identify the installed version and discover available command groups without credentials.

## Sub-features

- Version prints the selected package version.
- Help lists whoami, artists, chats, songs, emails, sandboxes, orgs, tasks, and content.

## How to get to it (user POV)

Run `recoup --version` or `recoup --help`.

## Driving it with Node

Preconditions: the selected source has been built successfully in this run.

- Drive the compiled binary with `--version` and no API key. Expect exit zero and the package version.
- Drive it with `--help` and no API key. Expect exit zero and a standalone row for every listed command in the Commands section. Mentions elsewhere in help do not count.
- Inspect the helper's request observations. Both commands must make zero requests.

## Gotchas

A global `recoup` binary may point to a different checkout. The helper invokes the selected checkout's `dist/bin.cjs` directly. Matching versions alone do not prove identical code; retain the source commit and build hash.
