#!/bin/bash
#
# check-env.sh — SessionStart directive for the recoup-records bundle.
#
# Emits ONE imperative, position-pinned directive (not passive context the model
# silently absorbs and then ignores). Per docs/fat-skills-benchmark.md P6
# (the session-start-directive pattern): a session-start hook must DIRECT, not
# merely describe. It arbitrates to a single directive:
#
#   - No Recoup credential  -> the directive is "run recoup-platform-connect-account first" (a hard
#     blocker; nothing else can succeed, so it wins arbitration).
#   - Configured            -> the directive is "route through RESOLVER.md before
#     acting" (picking the right one is the whole game).
#
# Non-blocking by contract: always exit 0. stdin (session JSON) is ignored;
# stdout is added to session context.

set -uo pipefail
cat >/dev/null 2>&1 || true   # drain stdin

have_cred="no"
if [ -n "${RECOUP_API_KEY:-}" ] || [ -n "${RECOUP_ACCESS_TOKEN:-}" ]; then
  have_cred="yes"
fi

ffmpeg_note=""
if ! command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg_note=" (note: ffmpeg not on PATH — the async content pipeline still works; only the short-video manual compose/mux step needs it.)"
fi

echo "[SESSION-START DIRECTIVE — recoup-records]"

if [ "$have_cred" = "no" ]; then
  # Single directive: nothing else works without a credential, so this wins.
  echo "DIRECTIVE: No Recoup credential is set (RECOUP_API_KEY / RECOUP_ACCESS_TOKEN)."
  echo "Run recoup-platform-connect-account now. Do NOT attempt artist, research, content, deal, or"
  echo "release work until a credential is set — those skills will fail. After setup,"
  echo "route every request through the bundle's RESOLVER.md.${ffmpeg_note}"
else
  # Single directive: routing. Picking the right skill is the job.
  echo "DIRECTIVE: Before acting on any request, consult the recoup-records"
  echo "RESOLVER.md (the skill dispatcher at the plugin root): match the request to"
  echo "one skill, then READ that skill's SKILL.md before doing the work. If two"
  echo "skills could match, read both and pick the narrower. Do not improvise a"
  echo "job a skill already owns.${ffmpeg_note}"
fi

exit 0
