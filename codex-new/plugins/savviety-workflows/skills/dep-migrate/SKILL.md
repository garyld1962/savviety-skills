---
name: dep-migrate
description: "Plan major dependency migrations. Analyze breaking changes, repo impact, sequencing, tests, rollback, and risk."
---

# Dependency Migrate

Plan a migration before editing code.

Read `references/migration-plan.md` for the report template. `references/legacy/` is archival only.

## Workflow

1. Identify current and target versions.
2. Verify upstream migration docs when current information matters.
3. Search the repo for affected APIs and configuration.
4. Produce staged migration tasks with verification and rollback.
5. Do not perform the migration unless the user asks for implementation.
