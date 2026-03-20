---
applyTo: "**/*.{ts,tsx,cs,js,jsx}"
description: "Code generation guardrails: read before write, verify imports, match project patterns. Applies to all source code edits."
---

# Code Generation Rules

These rules apply whenever you create or modify source code files.

## Read Before Write

- Before creating a new file: read 2-3 sibling files in the same directory to learn naming, export, and import patterns.
- Before modifying a file: read the ENTIRE file first. Do NOT edit based on a partial view.
- Before using any function/type: read its definition or type signature. Do NOT guess at parameters or return types.

## Imports

- Every import must reference a file or package that EXISTS in the project.
- Copy import patterns (aliases, barrel exports, relative vs absolute) from nearby files.
- Do NOT add new package dependencies without asking the user first.
- Before importing from a package, verify it's in `package.json` or the project's dependency file.

## Match the Project

- Use the same patterns as existing code. If the codebase uses `function` declarations, use `function` declarations.
- Use the same error handling pattern. Do NOT add try-catch if the project uses error middleware or Result types.
- Use the same logging approach. Do NOT add `console.log` if the project uses a structured logger.
- Use the same test patterns. Do NOT introduce jest assertions in a vitest project, or vice versa.

## Minimal Changes

- Implement only what was requested. No bonus features, no drive-by refactors.
- Do NOT add comments explaining obvious code.
- Do NOT add type annotations that TypeScript can infer.
- Do NOT add error handling beyond what existing code in this area does.
- Do NOT add configuration, options, or parameters "for future flexibility."

## Do Not Guess

- File paths: search and verify before referencing.
- API methods: read the type definitions.
- Build/test commands: read `package.json` scripts.
- Branch names: check with git, do not assume `main`.
- Package names: read `package.json` `name` field, do NOT use directory names.

## Do Not Read

- `CLAUDE.md` or `.claude/` — those are for Claude Code, not this environment.
- `code-review-orchestrator`, `review-report-writer`, `review-foundations` skills — those are review infrastructure, not code generation context.
