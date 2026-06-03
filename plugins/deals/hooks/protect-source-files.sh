#!/bin/bash
#
# protect-source-files.sh
#
# PreToolUse hook that blocks Write/Edit/MultiEdit calls targeting any path
# inside a deal's source/ directory. Seller-provided files in deals/*/source/
# are immutable evidence per references/deal-workspace.md.
#
# Contract (Claude Code hooks):
#   - stdin:  JSON describing the pending tool call
#   - stdout: JSON with hookSpecificOutput.permissionDecision = "allow" | "deny"
#   - exit 0 on success; the decision itself is carried in the JSON body
#
# Why a regex on /source/?
#   The deal workspace convention (references/deal-workspace.md) places raw
#   seller files under deals/{deal-id}/source/. Any write into that subtree
#   would mutate evidence, so we deny it categorically and tell the agent
#   where to write instead.

set -euo pipefail

# Read the entire stdin payload from Claude Code into a variable.
# Hooks always receive a single JSON document on stdin.
input="$(cat)"

# Pull the target file path out of the JSON. `// empty` means "if the field
# is missing or null, return an empty string" so the script does not crash
# on tools that have no file_path (the matcher should prevent that, but
# defensive parsing keeps the hook safe).
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

# If for some reason no path was provided, allow the call. The matcher in
# hooks.json already restricts us to file-mutating tools, so this is a
# belt-and-suspenders fallback rather than a real code path.
if [ -z "$file_path" ]; then
  printf '{"hookSpecificOutput":{"permissionDecision":"allow"}}\n'
  exit 0
fi

# The deny rule: any path containing "/source/" inside a deals/ workspace.
# We require both segments so we do not accidentally block unrelated repos
# that happen to have a directory called "source" (e.g. a generic src tree).
case "$file_path" in
  */deals/*/source/*)
    reason="Refused write to immutable source file: ${file_path}. "
    reason+="Per references/deal-workspace.md, deals/{deal-id}/source/ holds "
    reason+="raw seller evidence and must not be edited. Write to normalized/, "
    reason+="workpapers/, findings/, or memos/ inside the same deal instead."
    # jq -n builds JSON from scratch using --arg to inject the reason safely
    # (no shell interpolation into the JSON body, which would break on quotes
    # or newlines in the path).
    jq -n --arg reason "$reason" '{
      hookSpecificOutput: {
        permissionDecision: "deny"
      },
      systemMessage: $reason
    }'
    exit 0
    ;;
esac

# Default path: allow the write. We still emit a JSON body so Claude Code
# always sees a structured decision.
printf '{"hookSpecificOutput":{"permissionDecision":"allow"}}\n'
exit 0
