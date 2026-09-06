#!/usr/bin/env bash
# Refresh the skills command, install utilities, and update Claude or Hermes.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./update.sh [--claude] [<target>]
       ./update.sh --hermes [<profile-home>]

Installs/repairs the skills command and shell PATH, installs missing uv and
CLI utilities, then refreshes Claude assets in the target Git repository.
The target defaults to the current directory. A new target is initialized.

Removes the old shared hook registrations from .claude/settings.json while
preserving existing permissions. Existing settings.local.json is untouched.
Package installation may use sudo on Debian/Ubuntu.

With --hermes, install/update the pilot skills in HERMES_HOME (default
~/.hermes), or an explicit profile home. No Git repository is required.
Local skill edits stop the update; Hermes configuration and hooks are untouched.
EOF
}

platform=claude
case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  --hermes) platform=hermes; shift ;;
  --claude) shift ;;
  -*) usage >&2; exit 1 ;;
esac
if [[ $# -gt 1 ]]; then usage >&2; exit 1; fi
case "${1:-}" in -*) usage >&2; exit 1 ;; esac

if [[ "$platform" == hermes ]]; then
  target="${1:-${HERMES_HOME:-$HOME/.hermes}}"
else
  target=$(cd -- "${1:-.}" && pwd)
  git -C "$target" rev-parse --git-dir >/dev/null 2>&1 \
    || { printf 'Target is not a Git repository: %s\n' "$target" >&2; exit 2; }
fi

script_path="${BASH_SOURCE[0]}"
while [[ -L "$script_path" ]]; do
  script_dir=$(cd -P -- "$(dirname -- "$script_path")" && pwd)
  script_path=$(readlink -- "$script_path")
  [[ "$script_path" == /* ]] || script_path="$script_dir/$script_path"
done
repo_dir=$(cd -P -- "$(dirname -- "$script_path")" && pwd)

# Check Hermes destination/conflicts before changing shell setup or packages.
action=--init
if [[ "$platform" == hermes ]]; then
  [[ ! -e "$target/.savviety-skills.json" ]] || action=--update
  REPO_SKILLS_HOME="$repo_dir" \
    bash "$repo_dir/cli/skill.sh" --hermes "$action" "$target" --dry-run
else
  [[ ! -d "$target/.claude/skills" ]] || action=--update
fi

bash "$repo_dir/install.sh"
export PATH="$HOME/.local/bin:$PATH"
bash "$repo_dir/bin/install-agentic-tools"

# Use the updated checkout even when the caller has an old source override.
REPO_SKILLS_HOME="$repo_dir" REPO_SKILLS_NO_RTK=1 \
  bash "$repo_dir/cli/skill.sh" "--$platform" "$action" "$target"
if [[ "$platform" == hermes ]]; then
  printf '\nUpdated Hermes skills; utilities are installed.\n'
else
  printf '\nUpdated Claude settings and skills; utilities are installed.\n'
fi
