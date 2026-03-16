#!/usr/bin/env bash
# deploy.sh — Copy skills from this repo to their consumption points.
#
# Usage:
#   ./deploy.sh              # Deploy everything (Claude + VS Code)
#   ./deploy.sh claude       # Deploy Claude skills only
#   ./deploy.sh vscode       # Deploy VS Code skills only
#   ./deploy.sh --dry-run    # Show what would be copied
#
# This script copies from the source-of-truth directories (claude/, vscode/)
# to the locations where Claude Code and VS Code actually read them.
#
# After the repo restructure (~/repos/.claude/skills/ exists):
#   Claude skills → ~/repos/.claude/skills/
#   VS Code skills → each project's .github/ directory
#
# Until restructure, Claude skills go to each project's .claude/skills/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_DIR="$HOME/repos"
DRY_RUN=false
TARGET=""

# Parse args
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    claude)    TARGET="claude" ;;
    vscode)    TARGET="vscode" ;;
    --help|-h)
      head -12 "$0" | tail -10
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      exit 1
      ;;
  esac
done

log() { echo "  $1"; }
header() { echo ""; echo "=== $1 ==="; }

copy_dir() {
  local src="$1" dst="$2" label="$3"
  if [ ! -d "$src" ]; then
    log "SKIP $label — source not found: $src"
    return
  fi
  if $DRY_RUN; then
    log "DRY-RUN: $src → $dst"
  else
    mkdir -p "$dst"
    cp -r "$src"/* "$dst"/ 2>/dev/null || true
    log "OK: $label → $dst"
  fi
}

copy_file() {
  local src="$1" dst="$2" label="$3"
  if [ ! -f "$src" ]; then
    log "SKIP $label — source not found: $src"
    return
  fi
  if $DRY_RUN; then
    log "DRY-RUN: $src → $dst"
  else
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    log "OK: $label → $dst"
  fi
}

# ─── Claude Code Skills ──────────────────────────────────────────────────

deploy_claude() {
  header "Claude Code Skills"

  # Determine target: prefer repos-level if it exists (post-restructure),
  # otherwise deploy to each project individually (pre-restructure)
  local repos_skills="$REPOS_DIR/.claude/skills"

  if [ -d "$repos_skills" ]; then
    # Post-restructure: single deployment point
    log "Target: $repos_skills (repos-level)"
    for skill_dir in "$SCRIPT_DIR"/claude/*/; do
      local name
      name="$(basename "$skill_dir")"
      copy_dir "$skill_dir" "$repos_skills/$name" "$name"
    done
  else
    # Pre-restructure: deploy to each project that has .claude/skills/
    log "Target: per-project .claude/skills/ (pre-restructure mode)"
    local projects=(
      "$REPOS_DIR/BuilderFlow"
      "$REPOS_DIR/baker-street-project/baker-street"
    )
    for project in "${projects[@]}"; do
      local target="$project/.claude/skills"
      if [ -d "$target" ]; then
        log "Project: $project"
        for skill_dir in "$SCRIPT_DIR"/claude/*/; do
          local name
          name="$(basename "$skill_dir")"
          copy_dir "$skill_dir" "$target/$name" "  $name"
        done
      else
        log "SKIP: $project — no .claude/skills/ directory"
      fi
    done
  fi
}

# ─── VS Code Skills ──────────────────────────────────────────────────────

deploy_vscode() {
  header "VS Code / GitHub Copilot Skills"

  # VS Code skills deploy to each project's .github/ directory.
  # Projects opt in by having a .github/ directory.
  local projects=(
    "$REPOS_DIR/BuilderFlow"
    "$REPOS_DIR/baker-street-project/baker-street"
  )

  for project in "${projects[@]}"; do
    local target="$project/.github"
    if [ -d "$project" ]; then
      log "Project: $(basename "$project")"
      mkdir -p "$target"

      # Prompts
      copy_dir "$SCRIPT_DIR/vscode/prompts" "$target/prompts" "prompts"

      # Skills (reusable context)
      copy_dir "$SCRIPT_DIR/vscode/skills" "$target/skills" "skills"

      # Instructions (auto-applied by path)
      copy_dir "$SCRIPT_DIR/vscode/instructions" "$target/instructions" "instructions"

      # Agents
      copy_dir "$SCRIPT_DIR/vscode/agents" "$target/agents" "agents"

      # Copilot instructions
      copy_file "$SCRIPT_DIR/vscode/copilot-instructions.md" "$target/copilot-instructions.md" "copilot-instructions.md"
    else
      log "SKIP: $project — directory not found"
    fi
  done
}

# ─── Main ─────────────────────────────────────────────────────────────────

if $DRY_RUN; then
  echo "DRY RUN — no files will be copied"
fi

case "$TARGET" in
  claude) deploy_claude ;;
  vscode) deploy_vscode ;;
  *)
    deploy_claude
    deploy_vscode
    ;;
esac

header "Done"
if $DRY_RUN; then
  log "Re-run without --dry-run to apply."
else
  log "Skills deployed. Open Claude Code or VS Code in a project to verify."
fi
