#!/bin/bash
# .scripts/run.sh — Universal entrypoint for all WSL commands
# Usage: wsl -d Ubuntu-24.04 -e bash .scripts/run.sh <command> [args...]
#
# Examples:
#   run.sh build              — dotnet build the solution
#   run.sh test               — dotnet test
#   run.sh run precalc        — run PricingPrecalc console app
#   run.sh run web            — run PricingWeb
#   run.sh restore            — dotnet restore
#   run.sh exec <cmd> [args]  — run arbitrary command

set -euo pipefail

# --- Environment setup (done once per invocation) ---
export GIT_PAGER=cat
export FORCE_COLOR=1
export DOTNET_CLI_TELEMETRY_OPTOUT=1

cd "$(dirname "$0")/.."

# --- Project mappings ---
PROJECT_PRECALC="PricingPrecalc/PricingPrecalc.csproj"
PROJECT_WEB="PricingWeb/PricingWeb.csproj"
SOLUTION="pricing-precalc.sln"

resolve_project() {
  case "${1:-}" in
    precalc|PricingPrecalc)  echo "$PROJECT_PRECALC" ;;
    web|PricingWeb)          echo "$PROJECT_WEB" ;;
    *)                       echo "$SOLUTION" ;;
  esac
}

# --- Command routing ---
CMD="${1:-help}"
shift || true

case "$CMD" in
  restore)
    dotnet restore "$SOLUTION"
    ;;
  build)
    PROJECT=$(resolve_project "${1:-}")
    dotnet build "$PROJECT" --no-restore "${@:2}"
    ;;
  test)
    dotnet test "$SOLUTION" "${@}"
    ;;
  run)
    TARGET="${1:-web}"
    PROJECT=$(resolve_project "$TARGET")
    shift || true
    dotnet run --project "$PROJECT" "$@"
    ;;
  watch)
    TARGET="${1:-web}"
    PROJECT=$(resolve_project "$TARGET")
    shift || true
    dotnet watch run --project "$PROJECT" "$@"
    ;;
  publish)
    PROJECT=$(resolve_project "${1:-}")
    dotnet publish "$PROJECT" -c Release "${@:2}"
    ;;
  clean)
    dotnet clean "$SOLUTION"
    ;;
  format)
    dotnet format "$SOLUTION" "$@"
    ;;
  ef)
    # Usage: run.sh ef migrations add <name> / run.sh ef database update
    dotnet ef "$@" --project "$PROJECT_PRECALC"
    ;;
  git)
    git "$@"
    ;;
  commit)
    # Usage: run.sh commit "feat: add feature"
    git add -A
    git commit -m "$1"
    ;;
  status)
    git status --short
    echo "---"
    git log --oneline -5
    ;;
  exec)
    exec "$@"
    ;;
  all)
    echo "=== Restore ===" && dotnet restore "$SOLUTION"
    echo "=== Build ===" && dotnet build "$SOLUTION" --no-restore
    echo "=== Test ===" && dotnet test "$SOLUTION" --no-build
    echo "=== All passed ==="
    ;;
  help)
    echo "Usage: run.sh <command> [args]"
    echo ""
    echo ".NET commands:"
    echo "  restore             Restore NuGet packages"
    echo "  build [project]     Build solution or project (precalc|web)"
    echo "  test [args]         Run tests"
    echo "  run <project>       Run a project (precalc|web, default: web)"
    echo "  watch <project>     Run with hot-reload (precalc|web, default: web)"
    echo "  publish [project]   Publish for deployment"
    echo "  clean               Clean build outputs"
    echo "  format [args]       Format code"
    echo "  ef <args>           Entity Framework commands"
    echo "  all                 Full pipeline (restore+build+test)"
    echo ""
    echo "Git commands:"
    echo "  git <args>          Run git command"
    echo "  commit <msg>        Stage all + commit"
    echo "  status              Short status + recent log"
    echo ""
    echo "Other:"
    echo "  exec <cmd>          Run arbitrary command"
    ;;
  *)
    echo "Unknown command: $CMD" >&2
    echo "Run 'run.sh help' for usage" >&2
    exit 1
    ;;
esac
