#!/usr/bin/env bash
# Install the skills command for the current user.
set -euo pipefail

if [[ $# -gt 0 ]]; then
  case "$1" in
    --help|-h)
      cat <<'EOF'
Usage: ./install.sh

Creates ~/.local/bin/skills and adds ~/.local/bin to your shell's PATH.
Supports Bash, Zsh and POSIX login shells (sh, dash and ksh).
Run again after moving your savviety-skills checkout.
EOF
      exit 0
      ;;
    *) printf 'Unknown argument: %s\nUsage: ./install.sh\n' "$1" >&2; exit 1 ;;
  esac
fi

# Follow symlinks without relying on GNU-only readlink -f.
installer_path="${BASH_SOURCE[0]}"
while [[ -L "$installer_path" ]]; do
  installer_dir="$(cd -P -- "$(dirname -- "$installer_path")" && pwd)"
  installer_path="$(readlink -- "$installer_path")"
  [[ "$installer_path" == /* ]] || installer_path="$installer_dir/$installer_path"
done
repo_dir="$(cd -P -- "$(dirname -- "$installer_path")" && pwd)"
cli_path="$repo_dir/cli/skill.sh"
bin_dir="$HOME/.local/bin"
command_path="$bin_dir/skills"

[[ -x "$cli_path" ]] || { printf 'Missing or non-executable CLI: %s\n' "$cli_path" >&2; exit 1; }
if [[ -e "$command_path" && ! -L "$command_path" ]]; then
  printf 'Refusing to replace %s: move the existing file or directory, then rerun ./install.sh.\n' "$command_path" >&2
  exit 1
fi

# Bash reads only the first existing login profile, plus .bashrc in interactive
# non-login shells. Zsh uses ZDOTDIR when configured.
shell_name="${SHELL:-bash}"
shell_name="${shell_name##*/}"
profiles=()
case "${shell_name:-bash}" in
  bash)
    login_profile="$HOME/.profile"
    for candidate in "$HOME/.bash_profile" "$HOME/.bash_login" "$HOME/.profile"; do
      if [[ -e "$candidate" ]]; then
        login_profile="$candidate"
        break
      fi
    done
    profiles=("$login_profile" "$HOME/.bashrc")
    ;;
  zsh) profiles=("${ZDOTDIR:-$HOME}/.zprofile" "${ZDOTDIR:-$HOME}/.zshrc") ;;
  sh|dash|ksh) profiles=("$HOME/.profile") ;;
  *) printf 'Unsupported shell: %s. Set SHELL to your Bash or Zsh executable and rerun ./install.sh.\n' "$shell_name" >&2; exit 1 ;;
esac

mkdir -p -- "$bin_dir"
ln -sfn -- "$cli_path" "$command_path"
printf 'Installed %s -> %s\n' "$command_path" "$cli_path"

for profile in "${profiles[@]}"; do
  if [[ -f "$profile" ]] && grep -Fqx '# >>> savviety-skills PATH >>>' "$profile"; then
    continue
  fi
  mkdir -p -- "$(dirname -- "$profile")"
  cat >> "$profile" <<'EOF'

# >>> savviety-skills PATH >>>
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac
# <<< savviety-skills PATH <<<
EOF
  printf 'Added PATH setup to %s\n' "$profile"
done

cat <<'EOF'

Open a new terminal, or enable skills in this terminal with:
  export PATH="$HOME/.local/bin:$PATH"

Then run:
  skills --help
EOF
