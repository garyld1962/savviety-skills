---
name: checkpoint
description: "Quality gate for changed scope. Discovers package tooling, then runs lint, typecheck/build, tests, and a quick security-oriented diff review before push or PR."
---

# Checkpoint

Run a repository quality gate for the current work.

## Workflow

1. Inspect the repo's scripts and build files.
2. When the `jev-gate` MCP server is available and `.jev-gate.toml` defines `[[invariants]]`, run `verify_code_invariants(git_diff)` first ( ~15ms on the local RTX 5090 `/v1/systemone` endpoint) and fix any violated invariant before running slow builds/tests; if unreachable, log `Invariants: SKIP (jev-gate unreachable)`.
3. Run `python3 <skill-root>/scripts/checkpoint.py` from the repo root.
4. If the script cannot infer commands, ask for the repo's lint, build/typecheck, and test commands.
5. Report commands run, pass/fail status, and any skipped gate with the reason.

## Rules

- Prefer existing project commands over inventing new commands.
- Keep the gate scoped to changed packages when the repo exposes a clear command for that.
- Do not install dependencies unless the user explicitly approves.
- Do not create commits or PRs.
- Treat failing lint, typecheck/build, or tests as blocking until the user says otherwise.
