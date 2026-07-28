# AGENTS.md

## Repository Expectations

- Use the installed Savviety Workflows skills for repeatable planning, review, checkpoint, and delivery work.
- Run the repository's documented lint, build, and test commands before opening a pull request.
- Keep project-specific decisions in this file or nearby `AGENTS.md` files close to the code they govern.
- Put personal preferences in your Codex user configuration, not in shared repository instructions.

## Commands

lint: <cmd>
build: <cmd>
test: <cmd>
default_branch: main
package_manager: <npm|pnpm|yarn|bun|pip|poetry|cargo|go|dotnet|...>

Optional fields:

adversarial_triggers:
  - src/auth/**
  - migrations/**
retry_budget:
  max_total_retries: 20
  max_wall_clock_minutes: 60
auto_accept_deviations:
  - lockfile
  - formatter
auto_generated_paths:
  - "**/generated/**"
runtime_probes:
  - node -e "require('sharp')"

## Savviety Workflows

- Use `repo-status` before delivery or after a long break.
- Use `validate-plan` before executing implementation plans.
- Use `checkpoint` before push, PR creation, or release.
- Use project-scoped custom agents only when the task explicitly calls for subagent delegation.
