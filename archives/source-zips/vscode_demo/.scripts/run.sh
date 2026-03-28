#!/bin/bash
# .scripts/run.sh — Universal entrypoint for all WSL commands
# Usage: wsl -d Ubuntu-24.04 -e bash .scripts/run.sh <command> [args...]
#
# Examples:
#   run.sh build              — pnpm -r build
#   run.sh test               — pnpm -r test
#   run.sh test @tdbt/api     — pnpm --filter @tdbt/api test
#   run.sh lint               — pnpm -r lint
#   run.sh exec <cmd> [args]  — run arbitrary command
#   run.sh git log --oneline  — git (with pager disabled)

set -euo pipefail

# --- Environment setup (done once per invocation) ---
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
export GIT_PAGER=cat
export FORCE_COLOR=1

cd "$(dirname "$0")/.."

# --- Command routing ---
CMD="${1:-help}"
shift || true

case "$CMD" in
  build)
    if [ -n "${1:-}" ]; then
      pnpm --filter "$1" build
    else
      pnpm -r build
    fi
    ;;
  test)
    if [ -n "${1:-}" ]; then
      pnpm --filter "$1" test
    else
      pnpm -r test
    fi
    ;;
  lint)
    if [ -n "${1:-}" ]; then
      pnpm --filter "$1" lint
    else
      pnpm -r lint
    fi
    ;;
  install)
    pnpm install
    ;;
  add)
    # Usage: run.sh add @tdbt/api express  OR  run.sh add @tdbt/api -D vitest
    FILTER="$1"; shift
    pnpm --filter "$FILTER" add "$@"
    ;;
  dev)
    pnpm dev
    ;;
  git)
    git "$@"
    ;;
  commit)
    # Usage: run.sh commit "feat(api): add routes"
    git add -A
    git commit -m "$1"
    ;;
  status)
    git status --short
    echo "---"
    git log --oneline -5
    ;;
  migrate)
    cd packages/db && npx tsx src/migrate.ts
    ;;
  seed)
    cd packages/db && npx tsx src/seed.ts
    ;;
  generate)
    cd packages/db && npx drizzle-kit generate --config=./drizzle.config.cjs
    ;;
  worktree-setup)
    # Usage: run.sh worktree-setup <team-name> <branch-name>
    TEAM="$1"; BRANCH="$2"
    mkdir -p .worktrees
    git branch "$BRANCH" 2>/dev/null || true
    git worktree add ".worktrees/$TEAM" "$BRANCH"
    cd ".worktrees/$TEAM" && pnpm install
    ;;
  worktree-merge)
    # Usage: run.sh worktree-merge <branch-name>
    git merge "$1"
    ;;
  worktree-teardown)
    # Usage: run.sh worktree-teardown <team-name> <branch-name>
    git worktree remove ".worktrees/$1" --force 2>/dev/null || true
    git branch -D "$2" 2>/dev/null || true
    ;;
  all)
    echo "=== Install ===" && pnpm install
    echo "=== Build ===" && pnpm -r build
    echo "=== Test ===" && pnpm -r test
    echo "=== Lint ===" && pnpm -r lint
    echo "=== All passed ==="
    ;;
  sudo-on)
    # Enable passwordless sudo (requires wsl -u root, but we can self-elevate)
    wsl -d "$(grep -oP '(?<=PRETTY_NAME=").*(?=")' /etc/os-release 2>/dev/null || echo Ubuntu-24.04)" -u root bash -c "echo '$(whoami) ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/$(whoami)-nopasswd && chmod 0440 /etc/sudoers.d/$(whoami)-nopasswd" 2>/dev/null \
      || sudo bash -c "echo '$(whoami) ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/$(whoami)-nopasswd && chmod 0440 /etc/sudoers.d/$(whoami)-nopasswd"
    echo "Passwordless sudo enabled for $(whoami)"
    ;;
  sudo-off)
    # Disable passwordless sudo
    sudo rm -f "/etc/sudoers.d/$(whoami)-nopasswd"
    echo "Passwordless sudo disabled for $(whoami)"
    ;;
  exec)
    exec "$@"
    ;;
  help)
    echo "Usage: run.sh <command> [args]"
    echo ""
    echo "Package commands:"
    echo "  build [filter]    Build packages (optionally filtered)"
    echo "  test [filter]     Run tests (optionally filtered)"
    echo "  lint [filter]     Lint packages (optionally filtered)"
    echo "  install           pnpm install"
    echo "  add <pkg> <deps>  Add dependencies to a package"
    echo "  dev               Start dev servers"
    echo "  all               Full CI pipeline (install+build+test+lint)"
    echo ""
    echo "DB commands:"
    echo "  migrate           Run DB migrations"
    echo "  seed              Seed the database"
    echo "  generate          Generate new migration"
    echo ""
    echo "Git commands:"
    echo "  git <args>        Run git command"
    echo "  commit <msg>      Stage all + commit"
    echo "  status            Short status + recent log"
    echo ""
    echo "Worktree commands:"
    echo "  worktree-setup <team> <branch>"
    echo "  worktree-merge <branch>"
    echo "  worktree-teardown <team> <branch>"
    echo ""
    echo "Sudo commands:"
    echo "  sudo-on           Enable passwordless sudo"
    echo "  sudo-off          Disable passwordless sudo"
    echo ""
    echo "Other:"
    echo "  exec <cmd>        Run arbitrary command"
    ;;
  *)
    echo "Unknown command: $CMD" >&2
    echo "Run 'run.sh help' for usage" >&2
    exit 1
    ;;
esac
