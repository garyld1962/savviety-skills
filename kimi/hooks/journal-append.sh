#!/usr/bin/env bash
# Kimi-aware journal append hook.
# Reads Kimi's stdin JSON (with cwd, session_id, hook_event_name), extracts the
# project directory, and appends stdin content to .kimi/journal/YYYY-MM-DD.md.
set -euo pipefail

# Kimi passes hook payload on stdin; read it once.
PAYLOAD=$(cat)

# Extract cwd from Kimi's JSON payload. Fall back to $PWD if absent.
PROJECT_DIR=$(echo "$PAYLOAD" | jq -r '.cwd // "${PWD}"')
[[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "null" ]] && PROJECT_DIR="$PWD"

cd "$PROJECT_DIR"
mkdir -p .kimi/journal
target=".kimi/journal/$(date +%F).md"

# The hook command is invoked as "bash ./.kimi/hooks/journal-append.sh start|end".
# Append a timestamped line; any additional stdin from the payload is ignored.
event="${1:-log}"
{
  flock -x 9
  printf '## %s %s\n\n' "$(date -Iseconds)" "$event" >> "$target"
} 9>> "$target" 2>/dev/null || {
  # Fallback if flock is unavailable (macOS without util-linux).
  lock=".kimi/journal/.lock.$(date +%F)"
  trap 'rmdir "$lock" 2>/dev/null || true' EXIT
  while ! mkdir "$lock" 2>/dev/null; do sleep 0.05; done
  printf '## %s %s\n\n' "$(date -Iseconds)" "$event" >> "$target"
}
