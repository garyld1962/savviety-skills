#!/bin/sh
# PreToolUse hook (matcher: Bash, if: "Bash(git commit*)").
# Blocks commits on the repo's default branch during execute-plan runs.
input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
case "$cmd" in
  *"git commit"*) ;;
  *) exit 0 ;;
esac
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0
default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|.*/||')
[ -z "$default" ] && default=main
if [ "$branch" = "$default" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Commit on default branch %s blocked — create a feature branch (execute-plan policy)."}}\n' "$default"
fi
exit 0
