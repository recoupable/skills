#!/bin/bash
#
# protect-source-files.sh
#
# PreToolUse hook that blocks Write/Edit/MultiEdit calls targeting any path
# inside a Recoup deal's source/ directory. Seller-provided files in
# deals/*/source/ are immutable evidence per references/deal-workspace.md.
#
# GLOBAL-INSTALL SAFETY:
#   This plugin may be installed user-wide, so this hook runs on every edit in
#   every project. It must therefore only ever deny writes inside a *Recoup*
#   deal workspace — never in an unrelated repo that merely happens to have a
#   `deals/<x>/source/` path. We confirm Recoup-ownership by requiring the
#   deal dir to carry a Recoup deal-workspace marker before denying; otherwise
#   we allow (it's not our workspace).
#
# Contract (Claude Code hooks):
#   - stdin:  JSON describing the pending tool call
#   - stdout: JSON with hookSpecificOutput.permissionDecision = "allow" | "deny"
#   - exit 0 on success; the decision itself is carried in the JSON body

set -euo pipefail

allow() { printf '{"hookSpecificOutput":{"permissionDecision":"allow"}}\n'; exit 0; }

# Read the entire stdin payload from Claude Code into a variable.
input="$(cat)"

# Pull the target file path out of the JSON. `// empty` means "if the field
# is missing or null, return an empty string" so the script does not crash.
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

# No path (the matcher should prevent this) -> allow.
[ -z "$file_path" ] && allow

# Match a deal source path, both absolute/nested (".../deals/{id}/source/...")
# and repo-relative ("deals/{id}/source/..."). If it isn't one, allow.
case "$file_path" in
  */deals/*/source/* | deals/*/source/*) ;;
  *) allow ;;
esac

# It LOOKS like a deal source path — but only protect it if the enclosing
# deal dir is a real Recoup deal workspace (carries Recoup deal markers).
# This is what keeps us from blocking a coincidental deals/<x>/source/ path
# in someone else's unrelated project.
deal_dir="${file_path%%/source/*}"
is_recoup_deal="no"
for marker in assumptions.yaml evidence-ledger.json normalized findings; do
  if [ -e "$deal_dir/$marker" ]; then
    is_recoup_deal="yes"
    break
  fi
done
[ "$is_recoup_deal" = "no" ] && allow   # not a Recoup deal workspace -> not ours

# Confirmed Recoup deal workspace: deny the write to immutable evidence.
reason="Refused write to immutable source file: ${file_path}. "
reason+="Per references/deal-workspace.md, deals/{deal-id}/source/ holds "
reason+="raw seller evidence and must not be edited. Write to normalized/, "
reason+="workpapers/, findings/, or memos/ inside the same deal instead."
jq -n --arg reason "$reason" '{
  hookSpecificOutput: {
    permissionDecision: "deny"
  },
  systemMessage: $reason
}'
exit 0
