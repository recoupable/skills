#!/bin/bash
#
# check-env.sh
#
# SessionStart hook for the recoup-content plugin. Non-blocking: it inspects the
# environment for the credentials and tools the content skills need and prints a
# short status line that Claude Code adds to session context. It NEVER fails the
# session (always exit 0) — a missing key should warn, not break startup.
#
# Contract (Claude Code hooks):
#   - stdin:  JSON describing the session (ignored here)
#   - stdout: plain text, added to the session context
#   - exit 0 always (this hook only advises)

set -uo pipefail

cat >/dev/null 2>&1 || true   # drain stdin; we don't need it

notes=()

# Auth: at least one Recoup credential must be present for any /api/content/* or
# /api/research/* call. Prefer the API key (recoup_sk_…); the Bearer token works too.
if [ -n "${RECOUP_API_KEY:-}" ]; then
  notes+=("RECOUP_API_KEY set — content + research APIs available.")
elif [ -n "${RECOUP_ACCESS_TOKEN:-}" ]; then
  notes+=("RECOUP_ACCESS_TOKEN set (no API key) — content + research APIs available.")
else
  notes+=("No Recoup credential found. Set RECOUP_API_KEY (recoup_sk_…) before generating content or pulling research. See https://developers.recoupable.com/agents — do not retry calls blindly.")
fi

# ffmpeg: only the short-video skill's manual compose/mux step needs it. The async
# pipeline does not, so a miss is a soft warning, not a blocker.
if command -v ffmpeg >/dev/null 2>&1; then
  notes+=("ffmpeg present — manual compose/mux step available.")
else
  notes+=("ffmpeg not on PATH — the async content pipeline still works; only short-video's manual compose step needs it.")
fi

echo "[recoup-content] environment check:"
for n in "${notes[@]}"; do echo "  - $n"; done

exit 0
