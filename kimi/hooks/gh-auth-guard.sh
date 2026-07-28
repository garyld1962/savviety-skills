#!/usr/bin/env bash
# Kimi PreToolUse hook: block gh commands that require auth when gh is not authenticated.
# Advisory guard for skills that call gh pr create / gh issue create / gh release create.
set -uo pipefail

PAYLOAD=$(cat)
COMMAND=$(echo "$PAYLOAD" | jq -r '.tool_input.command // ""')

# Only guard GitHub write commands.
if ! echo "$COMMAND" | grep -Eq '^\s*gh\s+(pr\s+create|issue\s+create|release\s+create)\b'; then
  exit 0
fi

# Check gh is installed.
if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed. Install it before running '$COMMAND'." >&2
  exit 2
fi

# Check gh is authenticated.
if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not authenticated. Run 'gh auth login' first." >&2
  exit 2
fi

exit 0
