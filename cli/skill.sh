#!/usr/bin/env bash
# skills — install savviety-skills into a target repo.
#
# Source of truth: docs/repo-skills-design.md and manifest.json in the
# REPO_SKILLS_HOME directory (defaults to this script's checkout).
#
# For --kimi, the native skill tree in kimi/skills/ is generated from claude/
# by bin/build-kimi-plugin. Run that script before --init/--update so Kimi
# receives native frontmatter (type, whenToUse, arguments, flow).
#
# Usage:
#   skills --claude  --init   [<target>] [--force] [--dry-run]
#   skills --claude  --update [<target>] [--prune [--yes]] [--dry-run]
#   skills --copilot --init   [<target>] [--force] [--dry-run]
#   skills --copilot --update [<target>] [--prune [--yes]] [--dry-run]
#   skills --codex   --init   [<target>] [--force] [--dry-run]
#   skills --codex   --update [<target>] [--dry-run]
#   skills --kimi    --init   [<target>] [--force] [--dry-run]
#   skills --kimi    --update [<target>] [--prune [--yes]] [--dry-run]
#   skills --version | --help

set -euo pipefail

VERSION="0.1.0"
if [[ -z "${REPO_SKILLS_HOME:-}" ]]; then
  # Resolve ~/.local/bin/skills back to this checkout, including relative links.
  script_path="${BASH_SOURCE[0]}"
  while [[ -L "$script_path" ]]; do
    script_dir="$(cd -P -- "$(dirname -- "$script_path")" && pwd)"
    script_path="$(readlink -- "$script_path")"
    [[ "$script_path" == /* ]] || script_path="$script_dir/$script_path"
  done
  REPO_SKILLS_HOME="$(cd -P -- "$(dirname -- "$script_path")/.." && pwd)"
fi

# ---- output helpers ----------------------------------------------------------
c_dim()  { printf '\033[2m%s\033[0m'  "$*"; }
c_red()  { printf '\033[31m%s\033[0m' "$*"; }
c_grn()  { printf '\033[32m%s\033[0m' "$*"; }
c_yel()  { printf '\033[33m%s\033[0m' "$*"; }
c_bld()  { printf '\033[1m%s\033[0m'  "$*"; }

die()    { echo "$(c_red error:) $*" >&2; exit "${2:-1}"; }
warn()   { echo "$(c_yel warn:)  $*" >&2; }
info()   { echo "$(c_dim '·')    $*"; }
done_()  { echo "$(c_grn '✓')    $*"; }

# ---- usage -------------------------------------------------------------------
usage() {
  cat <<'EOF'
skills — install savviety-skills into a target repo

SETUP
  Run ./install.sh from the savviety-skills checkout, then open a new terminal.

USAGE
  skills --claude  --init   [<target>] [--force] [--dry-run]
  skills --claude  --update [<target>] [--prune [--yes]] [--dry-run]
  skills --copilot --init   [<target>] [--force] [--dry-run]
  skills --copilot --update [<target>] [--prune [--yes]] [--dry-run]
  skills --codex   --init   [<target>] [--force] [--dry-run]
  skills --codex   --update [<target>] [--dry-run]
  skills --kimi    --init   [<target>] [--force] [--dry-run]
  skills --kimi    --update [<target>] [--prune [--yes]] [--dry-run]
  skills --version | --help

PLATFORM (one required)
  --claude    install Claude Code assets into <target>/.claude
  --copilot   install Copilot assets into <target>/.github
  --codex     install Codex assets into <target>/.codex and AGENTS.md
  --kimi      install Kimi Code CLI assets into <target>/.kimi and AGENTS.md
              (run bin/build-kimi-plugin first to regenerate kimi/skills/)

ACTION (one required)
  --init      first-time install. Refuses if target assets already exist.
  --update    refresh shared assets. Safe to re-run. Never touches user-owned files.

OPTIONS
  --force     allow --init over an existing install. Existing assets are
              moved aside to <name>.bak-<UTC-timestamp>/ before reinstall
  --prune     with --update, prompt to delete shared skills no longer in source
  --yes       with --prune, skip prompts and delete all orphans
  --dry-run   show what would change, write nothing
  --version   print version and exit
  --help      print this help and exit

ENVIRONMENT
  REPO_SKILLS_HOME  override the source repo (default: the installed checkout)
  REPO_SKILLS_NO_RTK  if set, skip the post-install RTK prompt entirely

RTK INTEGRATION
  After install completes, you'll be prompted to install RTK (Rust Token
  Killer) — a CLI proxy that cuts LLM token usage 60-90% on common dev
  commands. Skipped silently if rtk is already on PATH, if stdin isn't a
  TTY, or if running on Windows-native (Windows is not supported; WSL is).

EXIT CODES
  0  success
  1  user error (bad flags, missing target)
  2  refused (would clobber, target not a git repo)
  3  source repo missing or invalid
EOF
}

# ---- argument parsing --------------------------------------------------------
PLATFORM=""
ACTION=""
TARGET=""
FORCE=0
PRUNE=0
YES=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude)   PLATFORM="claude" ;;
    --copilot)  PLATFORM="copilot" ;;
    --codex)    PLATFORM="codex" ;;
    --kimi)     PLATFORM="kimi" ;;
    --init)     ACTION="init" ;;
    --update)   ACTION="update" ;;
    --force)    FORCE=1 ;;
    --prune)    PRUNE=1 ;;
    --yes|-y)   YES=1 ;;
    --dry-run)  DRY_RUN=1 ;;
    --version)  echo "skills $VERSION"; exit 0 ;;
    --help|-h)  usage; exit 0 ;;
    -*)         die "unknown flag: $1" 1 ;;
    *)
      [[ -n "$TARGET" ]] && die "unexpected argument: $1 (target already set to $TARGET)" 1
      TARGET="$1"
      ;;
  esac
  shift
done

[[ -z "$PLATFORM" ]] && { usage; die "missing platform flag (--claude, --copilot, --codex, or --kimi)" 1; }
[[ -z "$ACTION"   ]] && { usage; die "missing action flag (--init or --update)" 1; }
[[ "$ACTION" == "init" && "$PRUNE" == 1 ]] && die "--prune is only valid with --update" 1
[[ "$YES" == 1 && "$PRUNE" == 0 ]] && die "--yes is only valid with --prune" 1

TARGET="${TARGET:-.}"
TARGET="$(cd "$TARGET" 2>/dev/null && pwd)" || die "target does not exist: $TARGET" 1

# ---- source repo validation --------------------------------------------------
[[ -d "$REPO_SKILLS_HOME" ]] || die "source repo missing: $REPO_SKILLS_HOME (set REPO_SKILLS_HOME)" 3
[[ -f "$REPO_SKILLS_HOME/manifest.json" ]] || die "manifest.json not found in $REPO_SKILLS_HOME" 3
[[ -f "$REPO_SKILLS_HOME/claude/README.md" ]] || die "$REPO_SKILLS_HOME does not look like savviety-skills (missing claude/README.md)" 3
command -v jq >/dev/null || die "jq is required" 3
command -v rsync >/dev/null || die "rsync is required" 3

MANIFEST="$REPO_SKILLS_HOME/manifest.json"

# Validate every selected source before creating directories or copying starters.
# A partial install must not look successful when a source tree was renamed.
jq empty "$MANIFEST" || die "invalid manifest.json" 3
while IFS= read -r source_path; do
  [[ -e "$REPO_SKILLS_HOME/$source_path" ]] \
    || die "manifest source missing: $source_path" 3
done < <(jq -r --arg p "$PLATFORM" \
  '.[$p] | (.skills.from // empty), (.trees[]?.from), (.extras[]?.from), (.starters[]?.from)' \
  "$MANIFEST")

# ---- target validation -------------------------------------------------------
[[ -d "$TARGET/.git" ]] || git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1 \
  || die "target is not a git repo: $TARGET" 2

# ---- summary tracking --------------------------------------------------------
declare -a SUMMARY=()
record() { SUMMARY+=("$1"); }

# ---- dry-run aware actions ---------------------------------------------------
do_mkdir() {
  local d="$1"
  if (( DRY_RUN )); then
    info "[dry-run] mkdir -p $d"
  else
    mkdir -p "$d"
  fi
}

do_rsync() {
  # do_rsync <src> <dst> [<extra rsync args>...]
  # Caller decides whether to pass --delete; we never default to deletion.
  local src="$1" dst="$2"; shift 2
  local args=(-a "$@")
  if (( DRY_RUN )); then
    args+=(-n -i)
    info "[dry-run] rsync ${args[*]} $src $dst"
    rsync "${args[@]}" "$src" "$dst" || true
  else
    rsync "${args[@]}" "$src" "$dst"
  fi
}

do_copy_file() {
  local src="$1" dst="$2"
  if (( DRY_RUN )); then
    info "[dry-run] cp $src $dst"
  else
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
  fi
}

do_write_file() {
  local content="$1" dst="$2"
  if (( DRY_RUN )); then
    info "[dry-run] write $dst (${#content} bytes)"
  else
    mkdir -p "$(dirname "$dst")"
    printf '%s' "$content" > "$dst"
  fi
}

# ---- user_owned membership ---------------------------------------------------
is_user_owned() {
  local rel="$1"
  jq -e --arg p "$rel" '.user_owned | index($p)' "$MANIFEST" >/dev/null 2>&1
}

# ---- starter handling --------------------------------------------------------
apply_starters() {
  # Starters: copy templates/X to <target>/Y only if Y is absent.
  local platform="$1"
  local count
  count=$(jq -r --arg p "$platform" '.[$p].starters | length' "$MANIFEST")
  for ((i = 0; i < count; i++)); do
    local from to abs_from abs_to
    from=$(jq -r --arg p "$platform" --argjson i "$i" '.[$p].starters[$i].from' "$MANIFEST")
    to=$(jq -r   --arg p "$platform" --argjson i "$i" '.[$p].starters[$i].to'   "$MANIFEST")
    abs_from="$REPO_SKILLS_HOME/$from"
    abs_to="$TARGET/$to"
    if [[ -e "$abs_to" ]]; then
      record "starter:skip-exists  $to"
      info "$(c_dim "skip starter (exists):") $to"
    else
      do_copy_file "$abs_from" "$abs_to"
      record "starter:created     $to"
      done_ "starter created: $to"
    fi
  done
}

# ---- gitignore maintenance ---------------------------------------------------
apply_gitignore() {
  local platform="$1"
  local count
  count=$(jq -r --arg p "$platform" '.[$p].gitignore // [] | length' "$MANIFEST")
  (( count == 0 )) && return 0

  local gitignore="$TARGET/.gitignore"

  for ((i = 0; i < count; i++)); do
    local pattern
    pattern=$(jq -r --arg p "$platform" --argjson i "$i" '.[$p].gitignore[$i]' "$MANIFEST")

    # Already ignored (exact match or via broader rule)?
    if git -C "$TARGET" check-ignore --no-index "$pattern" >/dev/null 2>&1; then
      record "gitignore:already   $pattern"
      info "$(c_dim "already gitignored:") $pattern"
      continue
    fi

    if [[ ! -f "$gitignore" ]]; then
      if (( DRY_RUN )); then
        info "[dry-run] create $gitignore with '$pattern'"
      else
        printf '%s\n' "$pattern" > "$gitignore"
      fi
      record "gitignore:created   .gitignore (+ $pattern)"
      done_ ".gitignore created with $pattern"
    else
      if (( DRY_RUN )); then
        info "[dry-run] append '$pattern' to $gitignore"
      else
        # Ensure trailing newline on existing file before appending.
        [[ -n "$(tail -c 1 "$gitignore" 2>/dev/null)" ]] && printf '\n' >> "$gitignore"
        printf '%s\n' "$pattern" >> "$gitignore"
      fi
      record "gitignore:appended  $pattern"
      done_ "appended $pattern to .gitignore"
    fi
  done
}

# ---- ensure-files (Claude only today) ----------------------------------------
apply_ensure() {
  local platform="$1"
  local count
  count=$(jq -r --arg p "$platform" '.[$p].ensure // [] | length' "$MANIFEST")
  for ((i = 0; i < count; i++)); do
    local to content abs_to
    to=$(jq -r      --arg p "$platform" --argjson i "$i" '.[$p].ensure[$i].to'      "$MANIFEST")
    content=$(jq -r --arg p "$platform" --argjson i "$i" '.[$p].ensure[$i].content' "$MANIFEST")
    abs_to="$TARGET/$to"
    if [[ -e "$abs_to" ]]; then
      record "ensure:skip-exists  $to"
      info "$(c_dim "skip ensure (exists):") $to"
    else
      do_write_file "$content" "$abs_to"
      record "ensure:created     $to"
      done_ "ensured: $to"
    fi
  done
}

# ---- extras (single-source → single-dest pairs) ------------------------------
apply_extras() {
  local platform="$1"
  local count
  count=$(jq -r --arg p "$platform" '.[$p].extras // [] | length' "$MANIFEST")
  for ((i = 0; i < count; i++)); do
    local from to abs_from abs_to
    from=$(jq -r --arg p "$platform" --argjson i "$i" '.[$p].extras[$i].from' "$MANIFEST")
    to=$(jq -r   --arg p "$platform" --argjson i "$i" '.[$p].extras[$i].to'   "$MANIFEST")
    abs_from="$REPO_SKILLS_HOME/$from"
    abs_to="$TARGET/$to"

    if is_user_owned "$to"; then
      if [[ -e "$abs_to" ]]; then
        record "extra:skip-userowned $to"
        info "$(c_dim "skip user-owned:") $to"
        continue
      fi
    fi

    if [[ -d "$abs_from" ]]; then
      do_mkdir "$abs_to"
      do_rsync "$abs_from/" "$abs_to/"
      record "extra:synced       $to/"
      done_ "synced extra: $to/"
    elif [[ -f "$abs_from" ]]; then
      do_copy_file "$abs_from" "$abs_to"
      record "extra:copied       $to"
      done_ "copied extra: $to"
    else
      warn "extra source not found, skipping: $from"
    fi
  done
}

# ---- skills tree (Claude) ----------------------------------------------------
apply_claude_skills() {
  local from to
  from=$(jq -r '.claude.skills.from' "$MANIFEST")
  to=$(jq -r   '.claude.skills.to'   "$MANIFEST")
  local abs_from="$REPO_SKILLS_HOME/$from"
  local abs_to="$TARGET/$to"

  do_mkdir "$abs_to"

  local -a rsync_args=()

  # Skip top-level source entries we never want copied.
  while IFS= read -r entry; do
    rsync_args+=(--exclude="/$entry")
  done < <(jq -r '.claude.skills.skip[]' "$MANIFEST")

  # Preserve user subdirs (_project, _local) inside target.
  while IFS= read -r entry; do
    rsync_args+=(--filter="protect /$entry/" --filter="protect /$entry/**")
  done < <(jq -r '.claude.skills.preserve_subdirs[]' "$MANIFEST")

  # Protect orphan skill dirs (target-only) from --delete.
  # Orphans are handled explicitly by prune_claude_orphans, never silently.
  if [[ -d "$abs_to" ]]; then
    while IFS= read -r dir; do
      local name; name="$(basename "$dir")"
      [[ ! -e "$abs_from/$name" ]] && \
        rsync_args+=(--filter="protect /$name/" --filter="protect /$name/**")
    done < <(find "$abs_to" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
  fi

  # --delete is needed so files removed inside an existing source skill drop
  # from target on update. The protect filters above stop --delete from
  # touching orphan directories or user-owned subdirs.
  rsync_args+=(--delete)

  do_rsync "$abs_from/" "$abs_to/" "${rsync_args[@]}"
  record "skills:synced       $to/"
  done_ "skills synced into $to/"
}

# ---- trees (Copilot multi-tree sync) -----------------------------------------
apply_copilot_trees() {
  local count
  count=$(jq -r '.copilot.trees | length' "$MANIFEST")
  for ((i = 0; i < count; i++)); do
    local from to abs_from abs_to
    from=$(jq -r --argjson i "$i" '.copilot.trees[$i].from' "$MANIFEST")
    to=$(jq -r   --argjson i "$i" '.copilot.trees[$i].to'   "$MANIFEST")
    abs_from="$REPO_SKILLS_HOME/$from"
    abs_to="$TARGET/$to"

    [[ -d "$abs_from" ]] || { warn "tree source missing, skipping: $from"; continue; }

    do_mkdir "$abs_to"

    # Per-file user_owned protection: build --filter rules for any user_owned
    # file whose path lives under this tree's destination.
    local -a rsync_args=(--delete)
    while IFS= read -r owned; do
      if [[ "$owned" == "$to/"* ]]; then
        local rel="${owned#$to/}"
        rsync_args+=(--filter="protect /$rel")
      fi
    done < <(jq -r '.user_owned[]' "$MANIFEST")

    # If user_owned file exists in source but not in target, treat as starter (copy if absent).
    while IFS= read -r owned; do
      if [[ "$owned" == "$to/"* ]]; then
        local rel="${owned#$to/}"
        local src_file="$abs_from/$rel"
        local dst_file="$abs_to/$rel"
        if [[ -f "$src_file" && ! -e "$dst_file" ]]; then
          do_copy_file "$src_file" "$dst_file"
          record "tree:starter-copy   $owned"
          done_ "seeded user-owned: $owned"
        fi
        # Always exclude from main rsync to avoid overwriting.
        rsync_args+=(--exclude="/$rel")
      fi
    done < <(jq -r '.user_owned[]' "$MANIFEST")

    do_rsync "$abs_from/" "$abs_to/" "${rsync_args[@]}"
    record "tree:synced         $to/"
    done_ "tree synced: $to/"
  done
}

# ---- trees (Codex multi-tree sync) ------------------------------------------
apply_codex_trees() {
  local count
  count=$(jq -r '.codex.trees | length' "$MANIFEST")
  for ((i = 0; i < count; i++)); do
    local from to abs_from abs_to
    from=$(jq -r --argjson i "$i" '.codex.trees[$i].from' "$MANIFEST")
    to=$(jq -r   --argjson i "$i" '.codex.trees[$i].to'   "$MANIFEST")
    abs_from="$REPO_SKILLS_HOME/$from"
    abs_to="$TARGET/$to"

    [[ -d "$abs_from" ]] || { warn "tree source missing, skipping: $from"; continue; }

    do_mkdir "$abs_to"
    do_rsync "$abs_from/" "$abs_to/" --delete
    record "tree:synced         $to/"
    done_ "tree synced: $to/"
  done
}

# ---- skills tree (Kimi) ------------------------------------------------------
# Mirrors apply_claude_skills but sources from .kimi.skills (which today points
# at claude/ — single source of truth — but could point elsewhere later).
apply_kimi_skills() {
  local from to
  from=$(jq -r '.kimi.skills.from' "$MANIFEST")
  to=$(jq -r   '.kimi.skills.to'   "$MANIFEST")
  local abs_from="$REPO_SKILLS_HOME/$from"
  local abs_to="$TARGET/$to"

  do_mkdir "$abs_to"

  local -a rsync_args=()

  while IFS= read -r entry; do
    rsync_args+=(--exclude="/$entry")
  done < <(jq -r '.kimi.skills.skip[]' "$MANIFEST")

  while IFS= read -r entry; do
    rsync_args+=(--filter="protect /$entry/" --filter="protect /$entry/**")
  done < <(jq -r '.kimi.skills.preserve_subdirs[]' "$MANIFEST")

  if [[ -d "$abs_to" ]]; then
    while IFS= read -r dir; do
      local name; name="$(basename "$dir")"
      [[ ! -e "$abs_from/$name" ]] && \
        rsync_args+=(--filter="protect /$name/" --filter="protect /$name/**")
    done < <(find "$abs_to" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
  fi

  rsync_args+=(--delete)

  do_rsync "$abs_from/" "$abs_to/" "${rsync_args[@]}"
  record "skills:synced       $to/"
  done_ "skills synced into $to/"
}

# ---- trees (Kimi multi-tree sync) -------------------------------------------
apply_kimi_trees() {
  local count
  count=$(jq -r '.kimi.trees | length' "$MANIFEST")
  for ((i = 0; i < count; i++)); do
    local from to abs_from abs_to
    from=$(jq -r --argjson i "$i" '.kimi.trees[$i].from' "$MANIFEST")
    to=$(jq -r   --argjson i "$i" '.kimi.trees[$i].to'   "$MANIFEST")
    abs_from="$REPO_SKILLS_HOME/$from"
    abs_to="$TARGET/$to"

    [[ -d "$abs_from" ]] || { warn "tree source missing, skipping: $from"; continue; }

    do_mkdir "$abs_to"
    do_rsync "$abs_from/" "$abs_to/" --delete
    record "tree:synced         $to/"
    done_ "tree synced: $to/"
  done
}

# ---- orphan detection + interactive prune (Kimi skills) ----------------------
# Same shape as prune_claude_orphans but reads from .kimi.skills.
prune_kimi_orphans() {
  local from to
  from=$(jq -r '.kimi.skills.from' "$MANIFEST")
  to=$(jq -r   '.kimi.skills.to'   "$MANIFEST")
  local abs_from="$REPO_SKILLS_HOME/$from"
  local abs_to="$TARGET/$to"

  [[ -d "$abs_to" ]] || return 0

  local -A skip_set=()
  while IFS= read -r e; do skip_set["$e"]=1; done < <(jq -r '.kimi.skills.skip[]' "$MANIFEST")
  while IFS= read -r e; do skip_set["$e"]=1; done < <(jq -r '.kimi.skills.preserve_subdirs[]' "$MANIFEST")

  local -a orphans=()
  while IFS= read -r dir; do
    local name; name="$(basename "$dir")"
    [[ -n "${skip_set[$name]:-}" ]] && continue
    [[ ! -e "$abs_from/$name" ]] && orphans+=("$name")
  done < <(find "$abs_to" -mindepth 1 -maxdepth 1 -type d | sort)

  if (( ${#orphans[@]} == 0 )); then
    return 0
  fi

  if (( PRUNE == 0 )); then
    warn "orphans (in target but not in source): ${orphans[*]}"
    info "re-run with --prune to delete (or --prune --yes to skip prompts)"
    for o in "${orphans[@]}"; do record "orphan:left-alone   $to/$o/"; done
    return 0
  fi

  local yes_to_all=$YES
  for o in "${orphans[@]}"; do
    local choice="N"
    if (( yes_to_all )); then
      choice="y"
    else
      printf "Skill '%s' exists in target but not in source. Delete? [y/N/a/q] " "$o" >&2
      read -r choice </dev/tty || choice="q"
    fi
    case "$choice" in
      y|Y) ;;
      a|A) yes_to_all=1 ;;
      q|Q) info "prune cancelled by user"; break ;;
      *)   info "kept: $o"; record "orphan:kept         $to/$o/"; continue ;;
    esac
    if (( DRY_RUN )); then
      info "[dry-run] rm -rf $abs_to/$o"
    else
      rm -rf "${abs_to:?}/$o"
    fi
    record "orphan:deleted      $to/$o/"
    done_ "deleted orphan: $to/$o/"
  done
}

# ---- orphan detection + interactive prune (Claude skills) --------------------
prune_claude_orphans() {
  local from to
  from=$(jq -r '.claude.skills.from' "$MANIFEST")
  to=$(jq -r   '.claude.skills.to'   "$MANIFEST")
  local abs_from="$REPO_SKILLS_HOME/$from"
  local abs_to="$TARGET/$to"

  [[ -d "$abs_to" ]] || return 0

  # Build skip + preserve set
  local -A skip_set=()
  while IFS= read -r e; do skip_set["$e"]=1; done < <(jq -r '.claude.skills.skip[]' "$MANIFEST")
  while IFS= read -r e; do skip_set["$e"]=1; done < <(jq -r '.claude.skills.preserve_subdirs[]' "$MANIFEST")

  local -a orphans=()
  while IFS= read -r dir; do
    local name; name="$(basename "$dir")"
    [[ -n "${skip_set[$name]:-}" ]] && continue
    [[ ! -e "$abs_from/$name" ]] && orphans+=("$name")
  done < <(find "$abs_to" -mindepth 1 -maxdepth 1 -type d | sort)

  if (( ${#orphans[@]} == 0 )); then
    return 0
  fi

  if (( PRUNE == 0 )); then
    warn "orphans (in target but not in source): ${orphans[*]}"
    info "re-run with --prune to delete (or --prune --yes to skip prompts)"
    for o in "${orphans[@]}"; do record "orphan:left-alone   $to/$o/"; done
    return 0
  fi

  local yes_to_all=$YES
  for o in "${orphans[@]}"; do
    local choice="N"
    if (( yes_to_all )); then
      choice="y"
    else
      printf "Skill '%s' exists in target but not in source. Delete? [y/N/a/q] " "$o" >&2
      read -r choice </dev/tty || choice="q"
    fi
    case "$choice" in
      y|Y) ;;
      a|A) yes_to_all=1 ;;
      q|Q) info "prune cancelled by user"; break ;;
      *)   info "kept: $o"; record "orphan:kept         $to/$o/"; continue ;;
    esac
    if (( DRY_RUN )); then
      info "[dry-run] rm -rf $abs_to/$o"
    else
      rm -rf "${abs_to:?}/$o"
    fi
    record "orphan:deleted      $to/$o/"
    done_ "deleted orphan: $to/$o/"
  done
}

# ---- backup helpers (used by --force) ----------------------------------------
BACKUP_SUFFIX=""
backup_suffix() {
  # Lazy-init once per run so all backups in a single invocation share a stamp.
  [[ -z "$BACKUP_SUFFIX" ]] && BACKUP_SUFFIX="bak-$(date -u +%Y%m%dT%H%M%SZ)"
  printf '%s' "$BACKUP_SUFFIX"
}

backup_path_for() {
  # Echo a unique backup destination for $1 (file or dir). Adds .N if needed.
  local p="$1"
  local base="${p}.$(backup_suffix)"
  local cand="$base" n=1
  while [[ -e "$cand" ]]; do
    cand="${base}.${n}"
    n=$((n + 1))
  done
  printf '%s' "$cand"
}

backup_one() {
  local p="$1"
  [[ ! -e "$p" ]] && return 0
  local dst; dst="$(backup_path_for "$p")"
  if (( DRY_RUN )); then
    info "[dry-run] mv $p $dst"
  else
    mv "$p" "$dst"
  fi
  record "force:backup       $(basename "$p") → $(basename "$dst")"
  warn "moved aside: $p → $dst"
}

# ---- pre-flight refusal checks -----------------------------------------------
check_init_refusal() {
  local platform="$1"
  case "$platform" in
    claude)
      # Whole .claude/ is ours — back up wholesale.
      if [[ -d "$TARGET/.claude" ]]; then
        if (( FORCE )); then
          backup_one "$TARGET/.claude"
        elif [[ -d "$TARGET/.claude/skills" ]]; then
          die "$TARGET/.claude/skills already exists. Use --force to back up and reinstall, or --update to refresh." 2
        fi
      fi
      ;;
    copilot)
      # .github/ is shared with non-savviety content (workflows, CODEOWNERS,
      # ISSUE_TEMPLATE, etc.). Only back up the assets we own.
      local -a owned=(
        "$TARGET/.github/prompts"
        "$TARGET/.github/agents"
        "$TARGET/.github/skills"
        "$TARGET/.github/instructions"
        "$TARGET/.github/templates"
        "$TARGET/.github/copilot-instructions.md"
      )
      local -a existing=()
      for p in "${owned[@]}"; do
        [[ -e "$p" ]] && existing+=("$p")
      done
      if (( ${#existing[@]} > 0 )); then
        if (( FORCE )); then
          for p in "${existing[@]}"; do backup_one "$p"; done
        elif [[ -d "$TARGET/.github/skills" || -d "$TARGET/.github/prompts" ]]; then
          die "$TARGET/.github already has Copilot assets. Use --force to back up and reinstall, or --update to refresh." 2
        fi
      fi
      ;;
    codex)
      local -a owned=(
        "$TARGET/.codex/plugins"
        "$TARGET/.codex/agents"
        "$TARGET/.codex/prompts"
        "$TARGET/.codex/rules"
        "$TARGET/.codex/hooks"
        "$TARGET/.codex/config.toml"
        "$TARGET/.codex/hooks.json"
        "$TARGET/.claude-plugin/marketplace.json"
      )
      local -a existing=()
      for p in "${owned[@]}"; do
        [[ -e "$p" ]] && existing+=("$p")
      done
      if (( ${#existing[@]} > 0 )); then
        if (( FORCE )); then
          for p in "${existing[@]}"; do backup_one "$p"; done
        else
          die "$TARGET already has Codex assets. Use --force to back up and reinstall, or --update to refresh." 2
        fi
      fi
      ;;
    kimi)
      # .kimi/ is fully ours — back up wholesale.
      if [[ -d "$TARGET/.kimi" ]]; then
        if (( FORCE )); then
          backup_one "$TARGET/.kimi"
        elif [[ -d "$TARGET/.kimi/skills" ]]; then
          die "$TARGET/.kimi/skills already exists. Use --force to back up and reinstall, or --update to refresh." 2
        fi
      fi
      ;;
  esac
}

check_update_prereq() {
  local platform="$1"
  case "$platform" in
    claude)
      [[ -d "$TARGET/.claude/skills" ]] || die "$TARGET/.claude/skills does not exist. Run --init first." 1
      ;;
    copilot)
      [[ -d "$TARGET/.github/prompts" || -d "$TARGET/.github/skills" ]] \
        || die "$TARGET has no Copilot assets. Run --init first." 1
      ;;
    codex)
      [[ -d "$TARGET/.codex/plugins" || -d "$TARGET/.codex/agents" ]] \
        || die "$TARGET has no Codex assets. Run --init first." 1
      ;;
    kimi)
      [[ -d "$TARGET/.kimi/skills" ]] \
        || die "$TARGET has no Kimi assets. Run --init first." 1
      ;;
  esac
}

# ---- RTK post-install prompt -------------------------------------------------
# Offers to install RTK (https://github.com/rtk-ai/rtk) after the main install.
# Silent skip cases: dry-run, rtk already on PATH, REPO_SKILLS_NO_RTK set,
# stdin not a TTY, Windows-native (not WSL).
maybe_install_rtk() {
  (( DRY_RUN )) && return 0
  [[ -n "${REPO_SKILLS_NO_RTK:-}" ]] && return 0
  command -v rtk >/dev/null 2>&1 && return 0

  # Windows-native detection. WSL reports "Linux" from uname and is supported.
  local kernel
  kernel="$(uname -s 2>/dev/null || echo)"
  if [[ "$kernel" =~ ^(MINGW|MSYS|CYGWIN) ]]; then
    info "RTK install skipped — Windows is not supported (WSL works)"
    return 0
  fi

  if [[ ! -t 0 || ! -t 1 ]]; then
    info "RTK not installed. To install later:"
    info "  curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"
    return 0
  fi

  echo
  echo "$(c_bld 'RTK (Rust Token Killer)')"
  echo "  CLI proxy that cuts LLM token usage 60-90% on common dev commands."
  echo "  Source: https://github.com/rtk-ai/rtk"
  printf "  Install now? [y/N] "
  local choice=""
  read -r choice </dev/tty || choice=""
  case "$choice" in
    y|Y|yes|YES) ;;
    *)
      info "RTK install declined. To install later:"
      info "  curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"
      return 0
      ;;
  esac

  if curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh; then
    if command -v rtk >/dev/null 2>&1; then
      done_ "RTK installed: $(command -v rtk)"
    else
      done_ "RTK installed to ~/.local/bin"
      warn "rtk not on PATH — add to your shell rc:"
      warn "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
  else
    warn "RTK install failed (exit $?). Re-run manually if needed."
  fi
}

# ---- main dispatch -----------------------------------------------------------
echo
echo "$(c_bld 'skills') $VERSION"
echo "  source:   $REPO_SKILLS_HOME"
echo "  target:   $TARGET"
echo "  platform: $PLATFORM"
echo "  action:   $ACTION$([[ $PRUNE == 1 ]] && echo ' --prune')$([[ $YES == 1 ]] && echo ' --yes')$([[ $DRY_RUN == 1 ]] && echo ' --dry-run')"
echo

case "$ACTION" in
  init)
    check_init_refusal "$PLATFORM"
    case "$PLATFORM" in
      claude)
        apply_claude_skills
        apply_extras    "claude"
        apply_ensure    "claude"
        apply_starters  "claude"
        apply_gitignore "claude"
        ;;
      copilot)
        apply_copilot_trees
        apply_starters  "copilot"
        apply_gitignore "copilot"
        ;;
      codex)
        apply_codex_trees
        apply_extras    "codex"
        apply_starters  "codex"
        apply_gitignore "codex"
        ;;
      kimi)
        apply_kimi_skills
        apply_kimi_trees
        apply_extras    "kimi"
        apply_starters  "kimi"
        apply_gitignore "kimi"
        ;;
    esac
    ;;
  update)
    check_update_prereq "$PLATFORM"
    case "$PLATFORM" in
      claude)
        apply_claude_skills
        apply_extras    "claude"
        # ensure: only acts if absent — safe on update
        apply_ensure    "claude"
        # starters: only act if absent — safe on update
        apply_starters  "claude"
        # gitignore: idempotent — safe on update
        apply_gitignore "claude"
        prune_claude_orphans
        ;;
      copilot)
        apply_copilot_trees
        apply_starters  "copilot"
        apply_gitignore "copilot"
        # TODO(v2): copilot-tree orphan prune
        ;;
      codex)
        apply_codex_trees
        apply_extras    "codex"
        apply_starters  "codex"
        apply_gitignore "codex"
        # TODO(v2): codex-tree orphan prune
        ;;
      kimi)
        apply_kimi_skills
        apply_kimi_trees
        apply_extras    "kimi"
        apply_starters  "kimi"
        apply_gitignore "kimi"
        prune_kimi_orphans
        ;;
    esac
    ;;
esac

# ---- summary -----------------------------------------------------------------
echo
echo "$(c_bld 'Summary')"
if (( ${#SUMMARY[@]} == 0 )); then
  echo "  (no actions recorded)"
else
  for line in "${SUMMARY[@]}"; do
    echo "  $line"
  done
fi
echo

if (( DRY_RUN )); then
  echo "$(c_yel 'dry-run complete — no files written.')"
fi

maybe_install_rtk
