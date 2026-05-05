# tech-debt-tracker — skills-test scenario

Test project for exercising `company-skills/claude-working/` end-to-end
on a greenfield Next.js + Express + SQLite/Drizzle stack. Commands are
stubs until `/execute-plan` scaffolds the real project from the PRD.

## Commands

This section is the required repo-delivery contract
(`_rubrics/repo-delivery`). Consumers (`execute-plan`, `checkpoint`,
`review-adversarial`) read from here and fail fast if absent.

```
lint: pnpm -r lint
build: pnpm -r build
test: pnpm -r test -- --run
default_branch: main
package_manager: pnpm
adversarial_triggers:
  - src/auth/**
  - migrations/**
  - packages/db/**
  - **/crypto/**
retry_budget:
  max_total_retries: 20
  max_wall_clock_minutes: 60
```

## Closed Decisions (pre-applied)

Tablestakes for any plan run against this scenario. Plans may override
via their own `## Closed Decisions` section.

- @closed-decisions/stacks/nextjs-app-router
- @closed-decisions/testing/vitest-only
- @closed-decisions/db/postgres-drizzle
- **DB driver override:** SQLite (better-sqlite3) via Drizzle, not
  PostgreSQL. Source: PRD §Stack.
- **Express API:** separate `packages/api` Express service alongside the
  Next.js frontend. Source: PRD §Package Structure.

## Project intent

Tech Debt Tracker MVP — a web app where teams catalog, score, and
prioritize tech debt items. See `docs/plans/PRD.md` for full spec.

## Workflow notes

- `/execute-plan` operates on feature branches off `main`. Never commits
  directly to `main` (Task 2 contract when landed; respected manually now).
- All plans live under `docs/plans/`; AERS artefacts under `docs/aers/`.
- The package.json is a pnpm-workspace stub with no real packages
  until `/execute-plan` scaffolds them. Lint/build/test scripts at the
  root are no-ops so schema-consumer skills have something to execute.
