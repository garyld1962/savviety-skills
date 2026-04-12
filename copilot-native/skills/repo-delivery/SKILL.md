---
name: repo-delivery
description: Delivery and quality-gate playbook for executing plans, running checkpoints, shipping changes, and handling hotfixes in a repo-specific way.
---

# Repo Delivery

Use this skill for built-in-aware delivery workflows:

- `#prompt:execute-plan`
- `#prompt:checkpoint`
- `#prompt:ship`
- `#prompt:hotfix`

## Relationship to Copilot built-ins

- Use built-in `/plan` before `execute-plan` when the work still needs an
  implementation plan.
- Use built-in `/review` for the default review path; these workflows are about
  execution and release orchestration, not generic code review.
- Use built-in `/tasks` when long-running build/test commands should be tracked
  explicitly.

## Core rules

- Detect the package manager, scripts, default branch, and repo conventions
  before proposing commands.
- Follow an accepted plan literally unless the user explicitly wants deviations.
- Prefer the repo's configured lint/build/test commands over invented command
  lines.
- Continue gathering evidence on failures instead of reporting only the first
  problem.

## Execute-plan contract

- find the requested or most relevant plan file
- extract the ordered task list
- detect repo commands before implementation
- execute in dependency order
- run build and test checks after each logical chunk when the repo supports them
- stop and report clearly on a real blocker instead of skipping ahead

## Checkpoint contract

- detect lint/build/test commands from the repo
- map changed files to the relevant package or project scope
- run the configured checks without inventing missing tooling
- report PASS, FAIL, or SKIP per check with enough evidence to act

## Ship contract

- confirm branch state and staged changes
- run checkpoint first unless the user intentionally skips it
- create a clean commit and PR summary based on actual repo changes
- stop on CI or merge blockers instead of papering over them

## Hotfix contract

- require a clearly stated breakage, root cause, and minimal fix scope
- keep the fix intentionally narrow
- require at least the relevant regression coverage or targeted verification
- skip unnecessary ceremony, but do not skip essential safety checks

## Examples

- **Execute-plan:** Read an accepted plan, detect the repo's real test and build
  commands, implement in dependency order, and stop on the first true blocker
  with enough evidence to continue later.
- **Checkpoint:** Map changed files to the affected package, run the repo's
  configured checks, and report `PASS`, `FAIL`, or `SKIP` per check without
  inventing missing scripts.
- **Hotfix:** Apply a narrow production fix for a known regression, add the
  targeted verification or regression coverage, and avoid folding in cleanup
  refactors.

## Guardrails

- Do not assume package manager, branch name, or script names.
- Do not auto-ship unrelated changes.
- Do not turn a hotfix into a refactor.
- Do not claim success without build/test or other configured verification.

## Do Nots

- Do not rewrite an accepted plan into a different solution unless the user
  explicitly changes direction.
- Do not skip checkpoint before `ship` unless the user intentionally bypasses
  it.
- Do not collapse execution evidence into a vague "done" summary with no check
  results or blocker detail.

## Closed Decisions

- Built-in `/plan` is the default planning step; this skill starts after the
  work is already planned.
- The repo's configured commands and conventions are the authority for build,
  test, lint, branch, and packaging behavior.
- `ship` assumes checkpoint-first by default.
- `hotfix` optimizes for minimum safe change, not opportunistic cleanup.
