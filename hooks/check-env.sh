#!/bin/bash
#
# check-env.sh — SessionStart directive for the Recoup Skills plugin.
#
# GLOBAL-INSTALL SAFETY (the whole point of the gate below):
#   This plugin may be installed user-wide, so this SessionStart hook fires at
#   the start of EVERY Claude Code session — including ones that have nothing to
#   do with Recoup. A hook that injects a "connect Recoup / route through
#   RESOLVER.md" directive into an unrelated repo is context pollution. So this
#   script emits NOTHING unless the current project is actually a Recoup
#   workspace. Outside a Recoup context it exits silently — the plugin stays
#   invisible in other people's projects.
#
# When we ARE in a Recoup workspace, it emits ONE imperative, position-pinned
# directive (a session-start hook must DIRECT, not merely describe):
#   - No Recoup credential -> "run recoup-platform-connect-account first".
#   - Configured           -> "route through RESOLVER.md before acting".
#
# Non-blocking by contract: always exit 0. stdout is added to session context.

set -uo pipefail

# Read the session JSON from stdin and pull cwd (fall back to $PWD). The hook
# runs in the project directory, so $PWD is a safe fallback if jq/cwd is absent.
input="$(cat 2>/dev/null || true)"
cwd=""
if [ -n "$input" ] && command -v jq >/dev/null 2>&1; then
  cwd="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null || true)"
fi
[ -z "$cwd" ] && cwd="$PWD"

# --- Recoup-context gate --------------------------------------------------
# Return 0 only when $cwd looks like a real Recoup workspace. Signals are
# Recoup-specific conventions, chosen to avoid false positives in unrelated
# repos (the bug this gate exists to prevent):
#   - RECOUP.md / .recoup            -> build-os workspace markers
#   - artists/*/RECOUP.md            -> a Recoup roster
#   - deals/*/{assumptions.yaml,evidence-ledger.json} -> a catalog deal workspace
#   - releases/**/RELEASE.md         -> a release workspace
#   - CLAUDE.md/AGENTS.md naming recoup -> a Recoup-aware project brain
is_recoup_context() {
  local d="$1"
  [ -f "$d/RECOUP.md" ] && return 0
  [ -e "$d/.recoup" ] && return 0
  ls "$d"/artists/*/RECOUP.md             >/dev/null 2>&1 && return 0
  ls "$d"/deals/*/assumptions.yaml        >/dev/null 2>&1 && return 0
  ls "$d"/deals/*/evidence-ledger.json    >/dev/null 2>&1 && return 0
  ls "$d"/releases/*/*/RELEASE.md          >/dev/null 2>&1 && return 0
  ls "$d"/releases/*/RELEASE.md            >/dev/null 2>&1 && return 0
  local f
  for f in "$d/CLAUDE.md" "$d/AGENTS.md"; do
    [ -f "$f" ] && grep -qi 'recoup' "$f" && return 0
  done
  return 1
}

# Not a Recoup project -> stay silent so we never inject into unrelated sessions.
is_recoup_context "$cwd" || exit 0

# --- We are in a Recoup workspace: emit the single directive ----------------
have_cred="no"
if [ -n "${RECOUP_API_KEY:-}" ] || [ -n "${RECOUP_ACCESS_TOKEN:-}" ]; then
  have_cred="yes"
fi

ffmpeg_note=""
if ! command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg_note=" (note: ffmpeg not on PATH — the async content pipeline still works; only the short-video manual compose/mux step needs it.)"
fi

echo "[SESSION-START DIRECTIVE — Recoup Skills]"

if [ "$have_cred" = "no" ]; then
  # Single directive: nothing else works without a credential, so this wins.
  echo "DIRECTIVE: No Recoup credential is set (RECOUP_API_KEY / RECOUP_ACCESS_TOKEN)."
  echo "Run recoup-platform-connect-account now. Do NOT attempt artist, research, content, deal, or"
  echo "release work until a credential is set — those skills will fail. After setup,"
  echo "route every request through the bundle's RESOLVER.md.${ffmpeg_note}"
else
  # Single directive: routing. Picking the right skill is the job.
  echo "DIRECTIVE: Before acting on any request, consult the"
  echo "RESOLVER.md (the skill dispatcher at the plugin root): match the request to"
  echo "one skill, then READ that skill's SKILL.md before doing the work. If two"
  echo "skills could match, read both and pick the narrower. Do not improvise a"
  echo "job a skill already owns.${ffmpeg_note}"
fi

exit 0
