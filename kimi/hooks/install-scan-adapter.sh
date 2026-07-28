#!/usr/bin/env bash
# Kimi-aware install-scan adapter.
# Reads Kimi's PostToolUse stdin JSON, detects package-install commands, and
# delegates to the existing install-scan.sh scanner. Advisory only (exit 0).
set -uo pipefail

PAYLOAD=$(cat)
COMMAND=$(echo "$PAYLOAD" | jq -r '.tool_input.command // ""')

# Map common install commands to package manager + package names.
MANAGER=""
PACKAGES=""

if echo "$COMMAND" | grep -Eq '^\s*npm\s+(install|i|add)\s+' ; then
  MANAGER="npm"
  PACKAGES=$(echo "$COMMAND" | sed -E 's/^\s*npm\s+(install|i|add)\s+//; s/\s+-[-a-zA-Z0-9]+//g' | tr ' ' '\n' | grep -v '^$' | paste -sd ' ' -)
elif echo "$COMMAND" | grep -Eq '^\s*yarn\s+(add|install)\s+' ; then
  MANAGER="yarn"
  PACKAGES=$(echo "$COMMAND" | sed -E 's/^\s*yarn\s+(add|install)\s+//; s/\s+-[-a-zA-Z0-9]+//g' | tr ' ' '\n' | grep -v '^$' | paste -sd ' ' -)
elif echo "$COMMAND" | grep -Eq '^\s*pnpm\s+(add|install)\s+' ; then
  MANAGER="pnpm"
  PACKAGES=$(echo "$COMMAND" | sed -E 's/^\s*pnpm\s+(add|install)\s+//; s/\s+-[-a-zA-Z0-9]+//g' | tr ' ' '\n' | grep -v '^$' | paste -sd ' ' -)
elif echo "$COMMAND" | grep -Eq '^\s*pip\s+(install)\s+' ; then
  MANAGER="pip"
  PACKAGES=$(echo "$COMMAND" | sed -E 's/^\s*pip\s+install\s+//; s/\s+-[-a-zA-Z0-9]+//g' | tr ' ' '\n' | grep -v '^$' | paste -sd ' ' -)
fi

if [ -z "$MANAGER" ] || [ -z "$PACKAGES" ]; then
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/../../.kimi/install-scan/install-scan.sh" "$MANAGER" $PACKAGES || true
exit 0
