# Project Instructions

> **This file is the single source of truth for project conventions.**
> All prompts and skills read this file for configuration. Update it as the project evolves.

## Scope Boundaries

- **This file** (`.github/copilot-instructions.md`) is the ONLY project-level instructions file for VS Code / GitHub Copilot prompts.
- **Do NOT read** `CLAUDE.md`, `.claude/`, or any Claude Code configuration. Those are for a different tool and contain instructions irrelevant to Copilot.
- **Prompts live in** `.github/prompts/`. Skills live in `.github/skills/`. Agents live in `.github/agents/`.
- **Domain rule skills** (used by `/code-review` and `/adversarial-review`): `typescript-quality`, `api-patterns`, `security`, `test-quality`, `ui-design-compliance`, `postgres`, `csharp-quality`, `dotnet-api`, `azure-functions`, `bicep`, `nextjs-patterns`, `monorepo`, `python-quality`.
- **Orchestration skills** (used only by `/code-review`): `code-review-orchestrator`, `review-report-writer`, `review-foundations`, `architecture-map`, `complexity`, `di-architecture`, `async-safety`, `k8s-readiness`, `team-roles`. Do NOT load these for adversarial reviews.

## Project Overview

<!-- TODO: Replace with your project description -->
This is a [language/framework] project that [brief purpose].

## Tech Stack

<!-- TODO: Update with your actual stack -->
- **Language:** <!-- e.g., TypeScript (strict mode), C#, Python -->
- **Package Manager:** <!-- e.g., pnpm, npm, dotnet, uv -->
- **Test Runner:** <!-- e.g., vitest, jest, dotnet test, pytest -->
- **Linter:** <!-- e.g., ESLint, Biome, dotnet format -->
- **Formatter:** <!-- e.g., Prettier, Biome, black -->

## Build & Test Commands

<!-- TODO: Configure for your environment. Examples below — adapt or remove as needed. -->

```bash
# Build
# TODO: e.g., pnpm build, dotnet build, npm run build

# Test
# TODO: e.g., pnpm test, dotnet test, pytest

# Lint
# TODO: e.g., pnpm lint, dotnet format --check

# Format
# TODO: e.g., pnpm format, prettier --write .
```

<!-- If using WSL or a command runner script, configure it here:
     See .scripts/run.sh for a reusable WSL command router template.
     Example: wsl -d Ubuntu-24.04 -e bash .scripts/run.sh <command> [args]
-->

**IMPORTANT — Terminal rules:**
- NEVER create throwaway `.sh` scripts — use `run.sh exec` for one-off commands (if using the runner)
- NEVER run raw package-manager or git commands directly if a runner is configured — always go through `run.sh`
- If a new command pattern is needed repeatedly, add it to `run.sh` as a new case

## Project Structure

<!-- TODO: Update with your actual project structure -->
```
.github/
  copilot-instructions.md  # This file
  prompts/                 # Copilot prompt files
  agents/                  # Copilot agent definitions
  skills/                  # Copilot skill definitions
.scripts/
  run.sh                   # Command runner (optional)
src/                       # Source code
tests/                     # Tests
```

## Coding Conventions

### General
- Use **strict typing** — no `any` types (TypeScript) or equivalent without justification
- Use `unknown` instead of `any` for unknown values
- Use `@ts-expect-error` with explanation, never `@ts-ignore` (TypeScript-specific)
- Prefer `const` over `let`; never use `var`
- No `console.log` in production code — use a structured logger if configured

### Naming
- **Files:** kebab-case (`my-component.ts`)
- **Types/Interfaces:** PascalCase (`UserProfile`)
- **Functions/Variables:** camelCase (`getUserProfile`)
- **Constants:** UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`)

### Imports
- No cross-package internal imports — only import from public package exports
- Prefer type-only imports: `import type { Foo } from './types'`
- Group imports: external deps → internal packages → relative paths

### Error Handling
- Always handle async errors — no unhandled promise rejections
- Validate user input at system boundaries (API endpoints, CLI args)
- Use custom error classes for domain errors when the project defines them

### Testing
- Write tests for all core business logic
- Test behavior, not implementation details
- **Minimum coverage:** each exported function needs happy path + at least one edge case; each API endpoint needs success, validation failure (400), and not-found (404) scenarios
- Keep tests isolated — no shared mutable state without cleanup
- Always `await` assertions on async operations
- **Test count verification (BLOCKING):** Before marking a package as complete, count your test cases against the minimum coverage rules above. If your count is below the minimum, write more tests before proceeding. Do NOT skip tests to save time — under-tested packages hide bugs that surface later as cascading failures.

### Git & Commits
- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat(scope): description`
- **MANDATORY: commit after each completed package or wave.** Do NOT defer all commits to the end. Each unit of work that passes build+test = one commit.
- Aim for 4-8 commits on a greenfield MVP, not 15-20.
- **Merge strategy:** Always squash-merge PRs to keep main clean
- Use `--squash` flag consistently across all skills (PR, Ship, Teams)
- **Commit gate (BLOCKING):** After each package builds and tests pass, you MUST commit before starting the next package. Commits are checkpoints — they let you `git diff` to verify what changed and recover if the next package introduces corruption. If you find yourself wanting to skip a commit, STOP — that impulse means something is wrong.

### Waves
- A **Wave** is a group of related tasks within a story that can be planned and executed as a unit.
- Stories may require multiple Waves to complete — each Wave is one code iteration cycle (plan → implement → review → merge).
- When a story has 11+ tasks, break it into sequential Waves rather than one massive plan.
- Each Wave should be independently shippable — it builds on the previous Wave but doesn't leave the codebase broken.
- When using parallel agent teams, each Wave can contain 2-4 teams working concurrently (see the `teams` skill).
- Wave naming: `Wave 1: <focus>`, `Wave 2: <focus>`, etc.
- Reference Waves in plan files, commit messages, and PR descriptions for traceability.

### Architecture
<!-- TODO: Update with project-specific patterns. These are sensible defaults. -->
- **Database: use factory functions** for connection/context, not module-level singletons. This enables test isolation (each test creates its own temp DB).
- **Repository pattern**: data access behind an interface, injected into the app. Route handlers never import the ORM directly.
- **API structure**: use a factory pattern (e.g., `createApp({ repository })`) — the app receives its dependencies, making it testable without global state.
- **Shared logic**: types, enums, validation, and domain logic belong in a shared package when multiple packages need them. Never duplicate.

### Code Generation Strategy

**Patch size limits — MANDATORY:**
- **NEVER generate more than 5 files in a single patch.** If a task requires more files, break it into multiple sequential patches. Large patches (10+ files) cause file content corruption where two implementations get merged into one file.
- After each patch, **READ every file you just created** to verify no content was duplicated or concatenated. Look for: two `import` blocks, two `export default` statements, two function definitions with the same name, or file length more than 2× what you intended.
- If any file shows duplication: **rewrite that file from scratch** — do NOT try to fix individual compiler errors. The root cause is structural corruption, not a logic bug.

**Build-before-fix pattern:**
- After creating all files for a package, run the build **immediately**.
- If build fails, **read every file in the package first** (not just the error location) and check for merged/duplicated file bodies BEFORE fixing type errors.
- Only after confirming all files are structurally clean: fix actual type errors.

### Execution Strategy
- **When the PRD or spec is detailed** (data models, endpoints, pages specified): the PRD is the plan. Scaffold immediately, then implement package-by-package. Do NOT spend a separate planning phase re-deriving what the PRD already says.
- **Do NOT use parallel worktrees or `#prompt:teams`** when the dependency chain is linear. Sequential is faster for projects under ~5,000 lines with cross-package type dependencies. Use `#prompt:teams` only when packages have zero shared types and zero file overlap.
- Build and test each package before moving to the next.

### Security
- No secrets in source code — use environment variables or secret managers
- No command injection — never interpolate user input into shell commands
- Auth on all user-facing endpoints (except health checks)
- Validate all external input before processing

## ADO Integration

<!-- TODO: Update with actual org/project, or remove if not using Azure DevOps -->
- **Organization:** (configure via `az devops configure --defaults`)
- **Project:** (configure via `az devops configure --defaults`)
- Use the `ado-item` skill to fetch work items

## Known Issues

<!-- Document known test failures or quirks here so checkpoint doesn't flag them -->
None currently.
