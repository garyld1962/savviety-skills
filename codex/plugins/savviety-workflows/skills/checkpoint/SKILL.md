---
name: checkpoint
description: "Quality gate for changed scope. Discovers package tooling, then runs lint, typecheck/build, tests, and a quick security-oriented diff review before push or PR."
---

# Checkpoint

Run a repository quality gate for the current work.

## Workflow

1. Inspect the repo's scripts and build files.
2. Run `python3 <skill-root>/scripts/checkpoint.py` from the repo root.
3. If the script cannot infer commands, ask for the repo's lint, build/typecheck, and test commands.
4. Report commands run, pass/fail status, and any skipped gate with the reason.

## Rules

- Prefer existing project commands over inventing new commands.
- Keep the gate scoped to changed packages when the repo exposes a clear command for that.
- Do not install dependencies unless the user explicitly approves.
- Do not create commits or PRs.
- Treat failing lint, typecheck/build, or tests as blocking until the user says otherwise.
