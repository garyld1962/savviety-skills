#!/usr/bin/env bash
# Kimi-aware PR guardrail hook.
# Reads Kimi's PreToolUse stdin JSON and blocks `gh pr create` when the current
# branch already has an open PR or the user has other open PRs.
set -uo pipefail

PAYLOAD=$(cat)

# Kimi's payload shape: tool_input.command holds the Bash command.
COMMAND=$(echo "$PAYLOAD" | jq -r '.tool_input.command // ""')

# Only intercept gh pr create commands.
if ! echo "$COMMAND" | grep -q "gh pr create"; then
  exit 0
fi

BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
CURRENT_PR=$(gh pr view --json number,url,title 2>/dev/null || echo "")
OPEN_PRS=$(gh pr list --author @me --state open --json number,title,headRefName,url 2>/dev/null || echo "[]")
PR_COUNT=$(echo "$OPEN_PRS" | jq 'length // 0')

if [ "$PR_COUNT" -eq 0 ] && [ -z "$CURRENT_PR" ]; then
  exit 0
fi

MSG="Open PRs detected before creating a new one:\n\n"

if [ "$PR_COUNT" -gt 0 ]; then
  while IFS= read -r pr; do
    NUM=$(echo "$pr" | jq -r '.number')
    TITLE=$(echo "$pr" | jq -r '.title')
    REF=$(echo "$pr" | jq -r '.headRefName')
    MSG="${MSG}  #${NUM} ${REF} — \"${TITLE}\"\n"
  done < <(echo "$OPEN_PRS" | jq -c '.[]')
fi

if [ -n "$CURRENT_PR" ]; then
  MSG="${MSG}\nCurrent branch '${BRANCH}' already has a PR.\n"
fi

MSG="${MSG}\nUse --force if you are sure, or close/review existing PRs first."

echo -e "$MSG" >&2
exit 2
