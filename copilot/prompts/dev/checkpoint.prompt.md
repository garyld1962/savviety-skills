---
description: >-
  Run a repo-specific quality gate across the changed scope by detecting the
  real lint, build, and test commands before execution.
argument-hint: '[optional scope]'
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# Checkpoint

Use this prompt for a fast quality gate before pushing, merging, or shipping.

Follow the skills:

- `.github/skills/repo-delivery/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`

## Step 0: Detect project tooling

Before running any commands, discover what commands actually exist in this project. Do not assume defaults.

1. Check for a declared command contract first — look for a `## Commands` section in `CLAUDE.md` or `.github/copilot-instructions.md`. If present, use those exact commands and skip manifest inspection.

2. If no contract exists, inspect the project manifests in order:

   | Manifest | What to read |
   |---|---|
   | `package.json` | `scripts.lint`, `scripts.build`, `scripts.test`, `scripts.typecheck` |
   | `pnpm-workspace.yaml` | Presence indicates a pnpm monorepo — prefer `pnpm -r <script>` |
   | `Cargo.toml` | `[workspace]` presence; use `cargo clippy`, `cargo build`, `cargo test` |
   | `pyproject.toml` | `[tool.ruff]`, `[tool.pytest]`, `[tool.mypy]` sections |
   | `Makefile` | `lint`, `build`, `test` targets |

3. Record only the commands that are actually defined. Mark any that are absent as SKIP — do not invent fallback commands.

4. Report the detected toolchain before proceeding:
   ```
   Detected: package_manager=<pm>  lint=<cmd|none>  build=<cmd|none>  test=<cmd|none>
   ```

## Copilot-native usage

- Prefer configured repo commands over invented ones.
- Report PASS, FAIL, and SKIP with enough evidence to act.
- Use built-in `/review` separately for the quick/default review path.
- Use `prompts/review/domain-review.prompt.md` when a deeper defect-focused review is needed.
- Use `prompts/review/professional-review.prompt.md` when the implementation also needs a senior engineering-judgment pass.
