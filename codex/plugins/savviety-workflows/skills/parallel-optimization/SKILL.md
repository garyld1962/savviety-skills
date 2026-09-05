---
name: parallel-optimization
description: "Optimize a draft task graph's dependencies and file ownership for safe optional concurrency. Use before execution when scheduling needs work; do not change requirements or create a second lane/wave plan."
---

# Parallel optimization

Read the sibling validate-plan skill's [plan contract](../validate-plan/references/plan-format.md).
Inspect actual code, shared exports, lockfiles, migrations, generated files and test
boundaries. Assign concrete write scopes, add producer/consumer dependencies, and
serialize overlapping owners. Read-only investigation can be concurrent without write
ownership. Shared surfaces still need one writer at a time.

Edit the existing task graph; preserve all acceptance and requirement IDs. Emit the
ready task groups, dependency rationale, milestone boundaries and expected benefit.
These groups are an explanation, not a separate scheduling registry. A sequential
request adds ordering edges; an unsafe split stays sequential. Re-run validate-plan.

## Examples
A shared contract task precedes independent API and UI tasks, then an integration
task depends on both. Two tasks editing one lockfile must be ordered.

## Closed decisions and open decisions
The plan's scope is settled. Resolve ownership uncertainty from code; ask only when
it exposes a material scope choice. Graph optimization does not authorize delegation.

## Do not
Do not claim /fleet automatically consumes a custom table, create parallel workers
without authorization, mandate four lanes regardless of host capacity, or retain
legacy Waves/Parallel Execution metadata beside dependencies.
