---
name: dependency-change-management
description: Heuristics for auditing dependency health and planning major-version migrations in a repo-specific, evidence-based way.
---

# Dependency Change Management

Use this skill for:

- `#prompt:dependency-audit`
- `#prompt:migration-guide`

## Relationship to Copilot built-ins

- Use built-in `/research` first when official migration guides or vendor docs
  are needed.
- Use built-in `/plan` after the migration analysis is accepted and ready to be
  executed.

## Dependency audit contract

- detect the ecosystem and package manager first
- separate security, outdated, unused, and license checks clearly
- report the actual severity from tool output rather than reclassifying it
- distinguish direct from transitive issues
- treat build-tool and type-only dependencies carefully before calling them
  unused

## Migration guide contract

- verify the current installed version before planning a migration
- read official migration or release documentation, not memory
- map breaking changes only to actual code usage in the repo
- exclude documented changes that do not affect this codebase
- call out plugin and peer-dependency compatibility explicitly

## Output expectations

For audits:

- ecosystem detected
- checks run and skipped
- concrete findings with severity and next actions

For migration plans:

- source documentation
- impact matrix
- ordered migration tasks
- compatibility blockers
- verification and rollback guidance

## Guardrails

- Do not invent breaking changes.
- Do not flag a dependency as unused before checking config and scripts.
- Do not recommend auto-fixes that the repo tooling cannot actually perform.
