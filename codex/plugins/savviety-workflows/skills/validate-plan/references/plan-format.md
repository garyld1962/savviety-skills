# Task graph plan contract

This contract is shared by the native Codex and Copilot workflows. Its source
is `shared/workflow-contracts/`; the installer ships a complete copy with each
platform. Run `bin/sync-native-contracts` after changing the source.

An execution plan has required YAML frontmatter, an H1, a `**Source:**` line,
and unique, ascending `## Task N: Title` sections. The source can be a file or
ticket reference. Supported types are `bug`, `feature`, `refactor`, and `infra`.

````markdown
---
slug: add-export
source_prd: docs/plans/PRD-export.md
intent: Let users export their own saved items.
type: feature
---
# Add item export

**Source:** docs/plans/PRD-export.md

## Closed Decisions
- **Format:** CSV with a header. Source: PRD acceptance criterion AC-1.

## Task 1: Define the export contract
```yaml
depends_on: []
write_scope: [src/contracts/export.ts, tests/export-contract.test.ts]
milestone_end: false
```
Define fields and serialization rules without changing the public API.

**Acceptance:**
- `npm test -- export-contract` exits 0, including a quoted-comma fixture.

## Task 2: Implement export
```yaml
depends_on: [1]
write_scope: [src/export/**, tests/export.test.ts]
milestone_end: true
```
Implement AC-1 against the contract from Task 1.

**Acceptance:**
- `npm test -- export` exits 0; a two-item export has one header and two rows.
````

## Ownership and ordering

- The first nonblank content after each task heading is its YAML block.
  `depends_on` is a list of integer task IDs; `write_scope` is a nonempty list
  of repository-relative paths or globs; `milestone_end` is a boolean.
- Paths have no absolute roots, traversal, backslashes, brace expansion, or
  negation. Name a directory's descendants with `path/**`. Quote glob values
  beginning with `*` so YAML does not interpret them as aliases.
- Dependencies must exist, be acyclic, and include prerequisites such as
  contracts, migrations, or generated clients. Transitive dependencies count.
- Tasks that can run concurrently must have provably disjoint write scopes.
  Serialize overlapping tasks with a dependency, even when their current
  edits happen to touch different lines. Assign manifests, lockfiles, shared
  exports, migrations and generated files to an explicit owner at a time.
- The validator conservatively compares glob prefixes. If it cannot prove
  disjointness, narrow the scopes or serialize the tasks. It cannot discover
  undeclared writes: the executor must also check the actual changed files.
- `milestone_end: true` pauses dispatch for review after that task's group
  finishes. With no explicit milestones, the final task is the review boundary.
  Final repository gates always run, regardless of milestone placement.
- Dependencies are the scheduling authority. Do not also author `## Waves`,
  lane tables, `## Parallel Execution`, or wave markers. Migrate older plans
  explicitly, preserving requirements and dependencies, before executing them.

## Acceptance and decisions

Each task has an `**Acceptance:**` block with nonempty bullets specifying a
command and expected result, or an observable state with exact expected values.
Commands alone are not enough if they cannot prove the promised behavior.
The script checks structure; the reviewer checks relevance and sufficiency.

Retain requirement IDs, scope limits, rollback obligations and closed decisions.
Record the authority for each closed decision. Check referenced decision records
before changing governed files. Do not turn unresolved product choices into
assumptions. Explicitly list open decisions; block only those affecting execution.

`validate_plan.py` needs Python 3 and PyYAML. It only reads the plan and emits
diagnostics or JSON (`--json`), including a SHA-256 of the exact plan bytes.
It never executes acceptance commands. Missing prerequisites or malformed YAML
are failures, not permission to skip validation.
