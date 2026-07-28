# CLAUDE.md

Project-specific instructions for Claude Code in this repository.

## Commands
lint: find claude -name "*.mjs" -print0 | xargs -0 bin/check-workflow-syntax && jq empty manifest.json
build: jq empty claude/settings.template.json && jq empty manifest.json
test: find claude -name "*.mjs" -print0 | xargs -0 bin/check-workflow-syntax
default_branch: main
package_manager: npm

## Stack

This is a Claude Code skill library, not a runnable application. There
is no package manager or dependency tree in the conventional sense —
`package_manager: npm` above is a placeholder to satisfy the
repo-delivery schema; nothing here is actually installed via npm.
Verification is structural: `bin/check-workflow-syntax` (a `node
--check` wrapper that tolerates the top-level `return`/`await` these
scripts use — the Workflow tool wraps the script body in an async
function at execution time, which plain `node --check` on the raw
file doesn't know about) on every Workflow script
(`claude/**/workflows/*.mjs`) and `jq` validation on the two JSON
config files that gate installation (`manifest.json`,
`settings.template.json`). There is no automated test framework for
skill prose itself — skill behavior is validated by the harness smoke
test (`claude/execute-plan/tests/smoke.md`), which requires a
live interactive session and is not a CI-runnable command.

## Conventions

- Skills live in platform-specific top-level trees: `claude/` (stable,
  installed via `manifest.json`), `claude/` (staging tree for the
  execute-prd/execute-plan rebuild — not yet wired into
  `manifest.json`), `codex/`, `copilot/`, `kimi/`.
- `claude/_internal`, `claude/execute-plan`, and
  `claude/execute-prd` are also overlaid into this repo's own
  `.claude/skills/` so they can be exercised directly here (self-hosting).
  `claude/validate-plan` (fixed for the new plan-format contract) is
  overlaid the same way.
- Frontmatter `name:` must match the containing directory name.

## Workflow

- Branch before any non-trivial change; this repo's own `default_branch`
  is `main`.
- Commit after every task when executing a plan.
