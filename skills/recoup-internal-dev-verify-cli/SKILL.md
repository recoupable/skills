---
name: recoup-internal-dev-verify-cli
description: Verify the compiled Recoup CLI through its actual commands and a loopback API fixture. Use for recoup-internal requests to check CLI command discovery, account output, credential failures, or HTTP error handling before a release.
---

# Verify Recoup CLI behavior

Run the actual `recoupable/cli` executable and retain commands, output, exit codes, and observed HTTP requests. The fixture replaces the backend at the CLI's existing `RECOUP_API_URL` boundary. It does not prove production authentication, account authorization, or backend correctness.

## Launch

Use Node 22 or newer and pnpm on macOS or Linux. The helper requires POSIX process groups and rejects unsupported operating systems before launching a CLI case. Select a clean, isolated CLI checkout at the revision under review. Record its commit and working-tree status. Preserve an existing dirty checkout by using a separate worktree. Set `CLI_REPO` to that checkout's absolute path and `CLI_EVIDENCE` to a fresh evidence directory outside it.

Run from the CLI checkout:

```sh
git rev-parse HEAD
git status --short
pnpm install --frozen-lockfile
pnpm build
```

The build must exit zero and produce `dist/bin.cjs`. This is a short-lived command, so there is no app server to keep running. The helper starts its own fixture on an unused loopback port and closes it after the checks.

## Doctor

Run `node "$CLI_REPO/dist/bin.cjs" --version`. Require exit zero and a version equal to the selected checkout's `package.json`. The build must have completed in this run. Record the commit alongside the evidence, since a version alone cannot identify a build.

## Drive

Read `features/README.md` and the matching feature recipe. Scripts ship alongside this skill. From the skill directory, run:

```sh
node scripts/verify-cli.mjs "$CLI_REPO" "$CLI_EVIDENCE"
```

The helper drives seven cases through child processes with an isolated environment, a fresh working directory, and its own loopback URL. It provides a dummy API key only for identity and HTTP-error cases; version, help, and missing-credentials cases run without a key. Caller API settings, proxy variables, and Node preload options are not inherited. It requires no real credentials. A sandbox that forbids listening on loopback needs the host's normal approval for this local server. Do not change the fixture to use a production URL.

## Evidence

Require exit zero and `pass: true` in `cli-verification.json`. Read the per-case output and observed requests. The version and help cases must make no requests. The missing-key case must fail before any request. Identity and HTTP-error cases must reach the documented GET endpoint and produce the expected stdout or stderr.

The report includes the compiled file's SHA-256, package version, command arguments, outputs, exit codes, synthetic HTTP request details, and cleanup status. Keep the source commit and build output beside it. Use a fresh evidence directory per attempt so an unsuccessful run remains inspectable.

Report a passing run as CLI behavior against synthetic HTTP fixtures. Backend availability, real credentials, authorization, writes, and the other CLI commands remain unverified by this skill. The feature map describes exactly which entry points were covered.

## Cleanup

Each CLI case has its own process group. When the direct child exits or exceeds ten seconds, the helper kills that group, including descendants with inherited or redirected output. Output pipes have one additional second to close before the case fails. Programs that deliberately leave the group to daemonize are unsupported; the helper does not claim to clean those unrelated groups.

On normal completion or a caught failure, the helper closes its own server, removes its temporary working directory, and preserves the evidence directory. Missing source metadata or build output produces a failed report before starting the server. Require both cleanup fields to be true and read the evidence file after exit. No process in a case's group should remain running. An unwritable evidence directory prevents saving a report and is itself a failed attempt.

Forced host termination can prevent this cleanup and the evidence write. The helper has no persistent recovery manifest. Treat that attempt as unverified. Use the host's process information to identify any surviving process from this run before cleanup; never kill by process name or assume that an old PID still belongs to this run.

When the CLI changes, update the matching feature recipe and helper, then repeat this workflow. Extend the map only when its new journey can be exercised and observed.
