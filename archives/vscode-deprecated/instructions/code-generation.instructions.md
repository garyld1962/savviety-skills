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
- Build/test commands: read `package.json` scripts or project docs.
- Branch names: check with git, do not assume `main`.
- Package names: read `package.json` `name` field, do NOT use directory names.

## After Every Patch — Merge Detection (MANDATORY)

After generating ANY patch that creates or modifies files, scan each affected file for these corruption signals:

1. **Two `import` blocks** at the top of the file (separated by code, not just grouped imports)
2. **Two `export default` statements** in the same file
3. **Two function/class/component definitions** with the same name
4. **Two complete module bodies** — the file reads like two separate files concatenated
5. **File length more than 2× what you intended** (e.g., you wrote a 30-line component but the file is 65 lines)

**If ANY of these are true:** The file is corrupted by a generation merge. **Rewrite the entire file from scratch** — do NOT try to "fix" individual compiler errors. The errors are symptoms of structural duplication, not logic bugs. Attempting to fix symptoms without removing the duplication wastes many iterations.

**Why this matters:** Large patches (5+ files) can produce files where two complete implementations are concatenated together. This causes cascading build failures that look like type errors but are actually structural corruption. The fastest recovery is always: detect → rewrite clean → rebuild.

## Patch Size Discipline

- **Maximum 5 files per patch.** If a task requires more, break into sequential patches.
- After each patch, **read every file you just touched** before proceeding to the next patch.
- If generating package scaffolding (package.json, tsconfig, source files), split into:
  - Patch 1: config files (package.json, tsconfig.json, project config)
  - Patch 2: source files (types, schemas, implementations)
  - Patch 3: test files

## Do Not Read

- `CLAUDE.md` or `.claude/` — those are for Claude Code, not this environment.
- `code-review-orchestrator`, `review-report-writer`, `review-foundations` skills — those are review infrastructure, not code generation context.
