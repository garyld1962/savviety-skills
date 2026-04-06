---
name: repo-delivery
description: "Delivery and quality-gate playbook for executing plans, running checkpoints, shipping changes, and handling hotfixes in a repo-specific way. Not user-invokable — referenced by execute-plan, execute-workflow, ship, hotfix, checkpoint."
---

# Repo Delivery

Use this rubric for delivery workflows:

- `/execute-plan`
- `/execute-workflow`
- `/checkpoint`
- `/ship`
- `/hotfix`

## Relationship to Built-ins

- Use `superpowers:writing-plans` or `/plan` before `/execute-plan` when the work still needs an implementation plan.
- Use `pr-review-toolkit:review-pr` or `/code-review` for review; these workflows are about execution and release orchestration, not generic code review.
- Use Task tracking (TaskCreate / TaskUpdate) when long-running build/test commands should be tracked explicitly.

## Core Rules

- Detect the package manager, scripts, default branch, and repo conventions before proposing commands.
- Follow an accepted plan literally unless the user explicitly wants deviations.
- Prefer the repo's configured lint/build/test commands over invented command lines.
- Continue gathering evidence on failures instead of reporting only the first problem.

## Execute-plan Contract

- find the requested or most relevant plan file
- extract the ordered task list
- detect repo commands before implementation
- execute in dependency order
- run build and test checks after each logical chunk when the repo supports them
- stop and report clearly on a real blocker instead of skipping ahead

## Checkpoint Contract

- detect lint/build/test commands from the repo (check `CLAUDE.md`, `package.json`, `Makefile`, `pyproject.toml`, or equivalent)
- map changed files to the relevant package or project scope
- run the configured checks without inventing missing tooling
- report PASS, FAIL, or SKIP per check with enough evidence to act

## Ship Contract

- confirm branch state and staged changes
- run checkpoint first unless the user intentionally skips it
- create a clean commit and PR summary based on actual repo changes
- stop on CI or merge blockers instead of papering over them
- follow project-specific delivery commands if defined (see `/configure ship`)

## Hotfix Contract

- require a clearly stated breakage, root cause, and minimal fix scope
- keep the fix intentionally narrow
- require at least the relevant regression coverage or targeted verification
- skip unnecessary ceremony, but do not skip essential safety checks

## Guardrails

- Do not assume package manager, branch name, or script names.
- Do not auto-ship unrelated changes.
- Do not turn a hotfix into a refactor.
- Do not claim success without build/test or other configured verification.
