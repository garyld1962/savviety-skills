# `skill.sh` — Design

> Status: draft, not implemented.
> Owner: Gary.
> Related: `claude/README.md` (source→target mapping), `templates/CLAUDE.local.md`,
> `claude/settings.template.json`.

## 1. Problem

Today, when starting a new repo and wanting the savviety-skills shared assets,
the workflow is "manually copy folders from `~/repos/savviety-skills` into
`.claude/` or `.github/`." That:

- forgets files (rubrics, hooks, guardrail scripts)
- gets the source→target mapping wrong (`claude/<skill>/` is **not** literally
  the deployed layout)
- leaves `settings.local.json` untouched, so hooks defined in the template
  don't actually run
- never creates `CLAUDE.md` or `.github/copilot-instructions.md`, so the
  repo-wide source of truth layer is missing on day one
- has no safe re-run story when the source repo evolves

We need one command that, given a target repo path and a platform flag,
produces a working baseline and is safe to re-run later.

## 2. Closed decisions

These are decided. The implementation should not relitigate them.

### 2.1. Source

Read directly from `~/repos/savviety-skills` (overridable via
`REPO_SKILLS_HOME`). Not skill-factory output.

**Why:** simpler today, single source of truth, no publish step in the loop.
If we later ship to multiple consumer machines, the script can grow a
factory-aware mode behind a flag.

### 2.2. Copy, not symlink

The script copies files. It never creates symlinks.

**Why:** the most common downstream pattern is committing `.claude/` and
`.github/` into the consumer repo. Symlinks don't survive that. Copy makes
each consumer hermetic; `--update` is the answer to drift.

### 2.3. Settings split (the most important decision)

Mirror Claude Code's own layering. Two separate files with different rules:

| File | Owner | Behavior on `--init` | Behavior on `--update` |
|---|---|---|---|
| `.claude/settings.json` | shared / refreshable | written from `claude/settings.template.json` | overwritten |
| `.claude/settings.local.json` | user / personal | created empty `{}` if absent | never touched |

**Why:** no merge logic. The template owns the hooks and shared permissions;
the user owns local overrides. Drift is impossible because the two files don't
overlap responsibilities. Matches Claude Code's documented precedence.

If the user wants to elevate a personal grant to shared, they edit
`claude/settings.template.json` upstream and re-run `--update`.

For Copilot, no per-user equivalent exists; instructions live in
`.github/instructions/personal.instructions.md` and follow the same
"create-if-missing, never overwrite" rule.

### 2.4. All-in by default

`--init` and `--update` install everything. No profiles in v1. A
`--skills foo,bar` opt-out flag may come later if subsetting becomes a real
need; today it isn't.

**Why:** profiles add config surface that won't earn its keep until there are
multiple obviously-different consumer shapes. Premature.

### 2.5. Repo-wide source-of-truth files (`CLAUDE.md`, `copilot-instructions.md`)

The script creates these from a starter template **if and only if they don't
already exist**. It never modifies existing files.

| Platform | File | Source template |
|---|---|---|
| `--claude` | `CLAUDE.md` (repo root) | `templates/CLAUDE.starter.md` (new — see §6) |
| `--copilot` | `.github/copilot-instructions.md` | `templates/copilot-instructions.starter.md` (new — see §6) |

**Why:** these are the top-level source-of-truth layer for each platform. A
fresh repo without one means every skill operates with no context. Templates
are minimal — pointers, not policy — so they're safe to drop in unmodified.

### 2.6. `--prune` is interactive

`--update --prune` does **not** silently delete. For each shared skill present
in the target but absent from source, the script prompts:

```
Skill 'old-thing' exists in target but not in source. Delete? [y/N/a/q]
  y = delete this one
  N = keep this one (default)
  a = delete this and all remaining (yes-to-all for the rest of the run)
  q = quit pruning, leave remaining as-is
```

Without `--prune`, removed-upstream skills are listed in the summary as
"orphaned" but left in place. A `--yes` flag (only meaningful with `--prune`)
skips the prompt entirely for non-interactive runs (CI, scripted setup).

**Why:** silent deletion of work is the kind of "destructive shortcut" your
global instructions warn against. Asking is cheap; recovering deleted skill
content from a fresh repo isn't.

### 2.7. `CLAUDE.local.md` created if absent

`--claude --init` copies `templates/CLAUDE.local.md` to `<target>/CLAUDE.local.md`
**only if the target file does not already exist**. `--update` never touches it.

**Why:** the personal-overrides file is per-repo, not per-user (different
projects warrant different personal preferences), so seeding the file lowers
friction. Same "create-if-absent, never overwrite" rule as `CLAUDE.md`.

For Copilot, the equivalent is `.github/instructions/personal.instructions.md`
— same rule, already covered by §5.3 step 4.

### 2.8. Copilot `templates/` copied on `--init`

`copilot-native/templates/` (currently just `env.config.template.md`) copies
into `<target>/.github/templates/` on `--init`, refreshes on `--update`. Same
shared-vs-user rules as everything else: anything matching `*.user.*` or
under a `_local/` subdir is left alone.

**Why:** the templates folder is the seed material for `/configure`-style
workflows. Skipping it would silently break those skills.

### 2.9. Manifest format is JSON

The manifest at `manifest.json` (see §6.3) is JSON, not YAML or TOML.

**Why:** `jq` is universally available and ships with the bash script's
existing dependencies. JSON is also what `settings.json` uses, so the repo
stays one config language.

## 3. Open questions

All previously-listed open questions resolved into §2.6–§2.9.

Hook scripts referenced by `settings.template.json` are copied via explicit
manifest extras. Source files live under `claude/infra/`; installed hook paths
live directly under `.claude/` (for example `.claude/pr-guardrail/` and
`.claude/journal/`).

## 4. Command surface

```
cli/skill.sh --claude   --init    [<target-path>] [--force] [--dry-run]
cli/skill.sh --claude   --update  [<target-path>] [--prune [--yes]] [--dry-run]
cli/skill.sh --copilot  --init    [<target-path>] [--force] [--dry-run]
cli/skill.sh --copilot  --update  [<target-path>] [--prune [--yes]] [--dry-run]
cli/skill.sh --codex    --init    [<target-path>] [--force] [--dry-run]
cli/skill.sh --codex    --update  [<target-path>] [--dry-run]
cli/skill.sh --version
cli/skill.sh --help
```

- `<target-path>` defaults to `.` (current directory).
- `--init` refuses if the platform's primary directory already exists, unless
  `--force` is given. With `--force`, existing savviety-owned assets are
  **moved aside** to `<name>.bak-<UTC-timestamp>/` (or `.md.bak-<TS>` for
  files) before fresh install. Nothing is overwritten or deleted.
- For Claude, the whole `.claude/` is moved (it's all ours).
- For Copilot, only the assets we own are moved
  (`prompts/`, `agents/`, `skills/`, `instructions/`, `templates/`,
  `copilot-instructions.md`); other `.github/` content
  (`workflows/`, `CODEOWNERS`, `ISSUE_TEMPLATE/`, etc.) is left untouched.
- Refuses if target is not a git repo.
- `--update` is the safe, re-runnable verb. No-op when nothing has changed.
- `--dry-run` prints what would change without writing.
- Exit codes: `0` success, `1` user error (bad path, missing flag),
  `2` refused (would clobber, target not a git repo), `3` source repo missing
  or unreadable.

Mutually exclusive: `--claude` xor `--copilot` xor `--codex`. Mutually exclusive:
`--init` xor `--update`.

## 5. Behavior

### 5.1. `--claude --init <target>`

Pre-flight:
- Verify `REPO_SKILLS_HOME` (or `~/repos/savviety-skills`) exists and looks
  like the right repo (presence of `claude/README.md`).
- Verify `<target>` is a git repo.
- If `<target>/.claude/skills/` exists: refuse unless `--force`. With
  `--force`, move `<target>/.claude/` to `<target>/.claude.bak-<UTC-timestamp>/`
  and continue.

Actions:
1. Create `<target>/.claude/skills/`.
2. Copy each `claude/<skill>/` directory into `<target>/.claude/skills/<skill>/`,
   skipping `claude/README.md`, `claude/SESSION-CONTEXT.md`, and any other
   source-only docs flagged in a manifest (see §6.3).
3. Copy `claude/_internal/` into `<target>/.claude/skills/_internal/`.
4. Copy `claude/infra/pr-guardrail/`, `claude/infra/journal/`, and
   `claude/install-scan/` into their `.claude/<asset>/` hook locations.
5. Copy `claude/settings.template.json` to `<target>/.claude/settings.json`.
6. Create `<target>/.claude/settings.local.json` containing `{}` if absent.
7. Create `<target>/CLAUDE.md` from `templates/CLAUDE.starter.md` if absent.
8. Create `<target>/CLAUDE.local.md` from `templates/CLAUDE.local.md` if absent.
9. Print summary: skills copied, files created, files left alone.

### 5.2. `--claude --update <target>`

Pre-flight: same source/target checks. Refuse if `<target>/.claude/skills/`
does not exist (use `--init` instead).

Actions:
1. For each `claude/<skill>/`, sync into `<target>/.claude/skills/<skill>/`,
   overwriting shared files. **Never** touch `_project/`, `_local/`, or any
   directory matching `_*` inside the target.
2. Refresh `_internal/`, infra extras, and `settings.json` the same way.
3. With `--prune`: for each shared skill in target that no longer exists in
   source, prompt the user (`y/N/a/q` per §2.6). With `--prune --yes`: skip
   prompts and delete all orphans. Without `--prune`: list orphans in the
   summary, delete nothing.
4. **Never** touch `settings.local.json`, `CLAUDE.md`, `CLAUDE.local.md`, or
   anything under `<target>/.claude/skills/_*/`.
5. Print summary: skills updated, skills added, skills pruned (if any), files
   skipped because user-owned.

### 5.3. `--copilot --init <target>`

Pre-flight: same target checks. If any savviety-owned asset already exists
under `<target>/.github/`, refuse unless `--force`. With `--force`, move
each owned asset (the five subdirs plus `copilot-instructions.md`) to
`<original>.bak-<UTC-timestamp>/`. Other `.github/` content (CI workflows,
`CODEOWNERS`, `ISSUE_TEMPLATE/`, etc.) is never touched.

Actions:
1. Copy `copilot-native/prompts/` → `<target>/.github/prompts/`.
2. Copy `copilot-native/agents/` → `<target>/.github/agents/`.
3. Copy `copilot-native/skills/` → `<target>/.github/skills/`.
4. Copy `copilot-native/instructions/` → `<target>/.github/instructions/`,
   except `personal.instructions.md` is created only if absent.
5. Copy `copilot-native/templates/` → `<target>/.github/templates/`.
6. Create `<target>/.github/copilot-instructions.md` from
   `templates/copilot-instructions.starter.md` if absent.
7. Print summary.

### 5.4. `--copilot --update <target>`

Same as `--claude --update` semantics, applied to the Copilot tree:
overwrite shared, never touch `personal.instructions.md` or
`copilot-instructions.md`.

### 5.5. `--codex --init <target>`

Pre-flight: same target checks. If any Savviety-owned Codex asset already
exists, refuse unless `--force`. With `--force`, move only owned assets aside:
`.codex/plugins`, `.codex/agents`, `.codex/prompts`, `.codex/rules`,
`.codex/hooks`, `.codex/config.toml`, `.codex/hooks.json`, and
`.claude-plugin/marketplace.json`.

Actions:

1. Copy `codex/plugins/` -> `<target>/.codex/plugins/`.
2. Copy `codex/agents/` -> `<target>/.codex/agents/`.
3. Copy `codex/prompts/` -> `<target>/.codex/prompts/`.
4. Copy `codex/templates/rules/` -> `<target>/.codex/rules/`.
5. Copy `codex/templates/hooks/` -> `<target>/.codex/hooks/`.
6. Copy `codex/templates/config.toml` -> `<target>/.codex/config.toml`.
7. Copy `codex/templates/hooks.json` -> `<target>/.codex/hooks.json`.
8. Copy `codex/templates/marketplace.json` ->
   `<target>/.claude-plugin/marketplace.json`.
9. Create `<target>/AGENTS.md` from `codex/templates/AGENTS.starter.md` if
   absent.

`.agents/plugins/marketplace.json` is the preferred Codex marketplace location,
but this repo currently uses `.claude-plugin/marketplace.json` because the
workspace `.agents/` directory is read-only. Codex supports both locations.

### 5.6. `--codex --update <target>`

Refresh the shared Codex trees and extras. Never overwrite `AGENTS.md`.
Codex orphan pruning is deferred to v2, matching Copilot tree pruning.

## 6. New artifacts to add to savviety-skills

These don't exist yet and are prerequisites for the script.

### 6.1. `templates/CLAUDE.starter.md`

Minimal starter for downstream consumers:

```markdown
# CLAUDE.md

Project-specific instructions for Claude Code.

## Stack & build

<!-- describe build/test/lint commands here -->

## Conventions

<!-- code style, file layout, naming -->

## Personal overrides

Personal preferences live in `CLAUDE.local.md` (gitignored).
Shared per-skill config lives under `.claude/skills/_project/`.
```

### 6.2. `templates/copilot-instructions.starter.md`

Equivalent for Copilot. Also minimal — pointer, not policy.

### 6.3. `manifest.json` (or similar) at repo root

Declares what the script should and should not copy. Avoids hardcoding
"skip these files" inside the script.

```json
{
  "claude": {
    "source_dir": "claude",
    "skip": ["README.md", "MODEL-POLICY.md", "SESSION-CONTEXT.md", "settings.template.json", "infra"],
    "extras": [
      { "from": "claude/infra/pr-guardrail", "to": ".claude/pr-guardrail" },
      { "from": "claude/infra/journal", "to": ".claude/journal" },
      { "from": "claude/install-scan", "to": ".claude/install-scan" },
      { "from": "claude/settings.template.json", "to": ".claude/settings.json" }
    ],
    "starters": [
      { "template": "templates/CLAUDE.starter.md", "to": "CLAUDE.md",       "if_absent": true },
      { "template": "templates/CLAUDE.local.md",   "to": "CLAUDE.local.md", "if_absent": true }
    ],
    "user_owned": [
      ".claude/settings.local.json",
      "CLAUDE.md",
      "CLAUDE.local.md"
    ]
  },
  "copilot": {
    "source_dirs": {
      "copilot-native/prompts": ".github/prompts",
      "copilot-native/agents":  ".github/agents",
      "copilot-native/skills":  ".github/skills",
      "copilot-native/instructions": ".github/instructions",
      "copilot-native/templates":    ".github/templates"
    },
    "starters": [
      { "template": "templates/copilot-instructions.starter.md",
        "to": ".github/copilot-instructions.md", "if_absent": true }
    ],
    "user_owned": [
      ".github/instructions/personal.instructions.md",
      ".github/copilot-instructions.md"
    ]
  }
}
```

The script reads the manifest. Adding a new asset type to the repo means
updating the manifest, not the script.

## 7. Implementation notes

- **Language:** bash. Lives in `~/.local/bin/skill.sh`. Mirrors the `run`
  pattern from your global `CLAUDE.md`.
- **Dependencies:** `rsync` for copy + delete semantics, `jq` for the manifest.
  Both standard on Linux/macOS dev machines.
- **Verbosity:** quiet by default (just the summary). `-v` for per-file
  output. `--dry-run` always prints what would happen.
- **Logging:** none persisted. The summary is the log.
- **Tests:** a small `tests/` folder with bash-based scenarios — fresh init,
  re-run update, update with `_project/` content, update with `--prune`. Use
  a temp dir as the target.

## 8. Out of scope (v1)

- **Profiles / skill subsetting.** Defer until the need is concrete.
- **Settings merge logic.** Decision 2.3 makes this unnecessary.
- **Two-platform install in one command.** A repo is either Claude or Copilot
  primary; mixed setups can run both commands.
- **Auto-update / cron.** Re-running `--update` is a manual ritual on
  purpose — surfaces drift to the user.
- **Skill-factory integration.** Decision 2.1 defers this.
- **Windows / PowerShell.** Bash only. WSL covers your Windows machines.

## 9. Validation before merge

The script should pass these by-hand checks:

1. `--claude --init` into a fresh git repo produces a working `.claude/` and
   a `CLAUDE.md`. Open in Claude Code: skills are discoverable, hooks fire.
2. `--claude --update` against the same repo is a no-op (nothing changes).
3. Add a file to `<target>/.claude/skills/_project/foo.md`, run `--update`,
   confirm the file survives.
4. Edit `<target>/.claude/settings.local.json`, run `--update`, confirm the
   edits survive.
5. Edit `<target>/CLAUDE.md`, run `--update`, confirm the edits survive.
6. Delete a skill from source, run `--update --prune`, confirm it's removed
   from target.
7. Run `--copilot --init` into a fresh repo. Open in VS Code with Copilot:
   prompts and agents are discoverable.
8. Run `--init` into a non-git directory: refused with exit code 2.
9. Run `--init` over existing `.claude/`: refused without `--force`.

## 10. Future questions (not blocking v1)

- Should the script self-update? (Probably no — it's small enough that
  re-copying it from savviety-skills is fine.)
- Should there be a `skill.sh doctor` subcommand that reports drift
  between target and source? (Probably yes, in v2.)
- Should the script know about plugins (superpowers, ba-*, etc.) and warn
  when a target repo lacks one a shared skill depends on? (Maybe — but
  that's really a `skill-audit` concern.)
