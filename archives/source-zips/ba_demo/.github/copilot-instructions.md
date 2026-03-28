# Project Instructions

> **This file is the single source of truth for project conventions.**
> All skills (code-review, checkpoint, execute-plan, plan, etc.) read this file for configuration.
> Update this file as the project evolves.

## Project Overview

<!-- TODO: Update with actual project description -->
This is a TypeScript project.

## Tech Stack

<!-- TODO: Update with actual stack -->
- **Language:** TypeScript (strict mode)
- **Package Manager:** pnpm
- **Test Runner:** vitest
- **Linter:** ESLint
- **Formatter:** Prettier

## Build & Test Commands

This project runs on WSL. **Always use `.scripts/run.sh`** for terminal commands:

```powershell
# All commands go through the runner:
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh <command> [args]

# Examples:
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh install
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh build
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh test
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh test @tdbt/api
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh lint
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh commit "feat(scope): message"
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh status
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh exec <any command>
```

**IMPORTANT — Terminal rules:**
- NEVER create throwaway `.sh` scripts — use `run.sh exec` for one-off commands
- NEVER run raw `pnpm`, `git`, `npm` etc. directly — always go through `run.sh`
- If a new command pattern is needed repeatedly, add it to `run.sh` as a new case
- The runner handles nvm/PATH setup automatically — do not source nvm manually
- `run.sh sudo-on` / `run.sh sudo-off` to toggle passwordless sudo

### Python

- Use **uv** for all Python operations — virtual environments, package installs, and running scripts
- Virtual environment: `uv venv .venv` (already created at project root)
- Install packages: `uv pip install <package>` (uses `.venv` automatically when present)
- Run scripts: `.venv\Scripts\python.exe <script>` (Windows) or `.venv/bin/python <script>` (WSL)
- For Zscaler proxy: set `SSL_CERT_FILE=C:\Users\coniiat\.custom_certs\ca-bundle.crt` before `uv pip install`
- NEVER use `pip install` directly — always use `uv pip install`

## Project Structure

```
.github/
  copilot-instructions.md  # This file
.scripts/
  run.sh                   # WSL command router — ALL terminal commands go through here
packages/
  shared/                  # Types, constants, scoring logic
  db/                      # Drizzle ORM + SQLite
  api/                     # Express REST API
  web/                     # Next.js frontend
```

## Coding Conventions

### General
- Use **strict TypeScript** — no `any` types without justification
- Use `unknown` instead of `any` for unknown values
- Use `@ts-expect-error` with explanation, never `@ts-ignore`
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
- Cover: happy path, invalid input, error paths, edge cases
- Keep tests isolated — no shared mutable state without cleanup
- Always `await` assertions on async operations

### Git & Commits
- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat(scope): description`
- One logical change per commit
- **Merge strategy:** Always squash-merge PRs to keep main clean
- Use `--squash` flag consistently across all skills (PR, Ship, Teams)

### Waves
- A **Wave** is a group of related tasks within a story that can be planned and executed as a unit.
- Stories may require multiple Waves to complete — each Wave is one code iteration cycle (plan → implement → review → merge).
- When a story has 11+ tasks, break it into sequential Waves rather than one massive plan.
- Each Wave should be independently shippable — it builds on the previous Wave but doesn't leave the codebase broken.
- When using parallel agent teams, each Wave can contain 2-4 teams working concurrently (see the `teams` skill).
- Wave naming: `Wave 1: <focus>`, `Wave 2: <focus>`, etc.
- Reference Waves in plan files, commit messages, and PR descriptions for traceability.

### Security
- No secrets in source code — use environment variables or secret managers
- No command injection — never interpolate user input into shell commands
- Auth on all user-facing endpoints (except health checks)
- Validate all external input before processing

## ADO Integration

<!-- TODO: Update with actual org/project -->
- **Organization:** (configure via `az devops configure --defaults`)
- **Project:** (configure via `az devops configure --defaults`)
- Use the `ado-item` skill to fetch work items

## Known Issues

<!-- Document known test failures or quirks here so checkpoint doesn't flag them -->
None currently.
