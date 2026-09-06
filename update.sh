#!/usr/bin/env bash
# Refresh the skills command, install utilities, and update Claude or Hermes.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./update.sh [--claude] [<target>] [--clean-settings] [--dry-run]
       ./update.sh --hermes [<profile-home>]

Installs/repairs the skills command and shell PATH, installs missing uv and
CLI utilities, then refreshes Claude assets in the target Git repository.
The target defaults to the current directory. A new target is initialized.

Preserves existing settings by default. With --clean-settings, removes
permissions from both Claude settings files and asks whether to keep each
hook (Enter keeps, n removes, q cancels). Backs up changed settings files.
--dry-run previews skill/settings changes without installing utilities.
Package installation may use sudo on Debian/Ubuntu.

With --hermes, install/update the pilot skills in HERMES_HOME (default
~/.hermes), or an explicit profile home. No Git repository is required.
Local skill edits stop the update; Hermes configuration and hooks are untouched.
EOF
}

platform=claude
target_arg=""
clean_settings=0
dry_run=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --hermes) platform=hermes ;;
    --claude) platform=claude ;;
    --clean-settings) clean_settings=1 ;;
    --dry-run) dry_run=1 ;;
    -*) usage >&2; exit 1 ;;
    *)
      [[ -z "$target_arg" ]] || { usage >&2; exit 1; }
      target_arg="$1"
      ;;
  esac
  shift
done
if [[ "$platform" != claude && "$clean_settings" == 1 ]]; then
  printf '%s\n' '--clean-settings is only supported for Claude settings.' >&2
  exit 1
fi
settings_args=()
(( clean_settings == 0 )) || settings_args+=(--clean-settings)

if [[ "$platform" == hermes ]]; then
  target="${target_arg:-${HERMES_HOME:-$HOME/.hermes}}"
else
  target=$(cd -- "${target_arg:-.}" && pwd)
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

if (( dry_run )); then
  REPO_SKILLS_HOME="$repo_dir" REPO_SKILLS_NO_RTK=1 \
    bash "$repo_dir/cli/skill.sh" "--$platform" "$action" "$target" "${settings_args[@]}" --dry-run
  exit
fi

bash "$repo_dir/install.sh"
export PATH="$HOME/.local/bin:$PATH"
bash "$repo_dir/bin/install-agentic-tools"

# Use the updated checkout even when the caller has an old source override.
REPO_SKILLS_HOME="$repo_dir" REPO_SKILLS_NO_RTK=1 \
  bash "$repo_dir/cli/skill.sh" "--$platform" "$action" "$target" "${settings_args[@]}"
if [[ "$platform" == hermes ]]; then
  printf '\nUpdated Hermes skills; utilities are installed.\n'
else
  printf '\nUpdated Claude settings and skills; utilities are installed.\n'
fi
