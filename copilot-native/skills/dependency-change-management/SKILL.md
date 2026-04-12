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

## Examples

- **Dependency audit:** Detect the package manager, separate security findings
  from outdated and unused packages, and report direct versus transitive issues
  without reclassifying tool output.
- **Migration guide:** Verify the currently installed version, read the official
  upgrade docs, map only the breaking changes that affect real repo usage, and
  produce an ordered migration plan with rollback notes.

## Guardrails

- Do not invent breaking changes.
- Do not flag a dependency as unused before checking config and scripts.
- Do not recommend auto-fixes that the repo tooling cannot actually perform.

## Do Nots

- Do not present vendor documentation from memory when official docs can be
  checked.
- Do not include documented breaking changes that do not touch this codebase.
- Do not blur security, outdated, unused, and license findings into one
  undifferentiated list.

## Closed Decisions

- Dependency analysis is evidence-based and repo-specific, not generic advice.
- Official migration or release documentation is the source of truth for
  version-change claims.
- Built-in `/research` comes before vendor-doc discovery, and built-in `/plan`
  comes after the migration analysis is accepted.
