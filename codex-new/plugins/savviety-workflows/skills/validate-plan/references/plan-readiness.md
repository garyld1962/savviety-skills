# Plan Readiness Standard

An executable plan must have:

- an H1 title after optional YAML frontmatter
- at least one discrete task
- acceptance criteria expressed as tests, commands, observable state, or schema/type checks
- no unresolved placeholders
- no task titles that begin with tentative openers such as "Consider", "Maybe", "Explore", or "Look into"
- well-formed closed decisions when a `## Closed Decisions` section is present
- a valid `## Parallel Execution` section when concurrency is declared

Acceptance criteria should let an executor know when a task is done without interpreting intent.

Passing examples:

- `test -f src/lib/cache.ts`
- `npm test -- cache.test.ts`
- `curl returns HTTP 200`
- `jq -e '.scripts.test' package.json`

Failing examples:

- "validation has been added"
- "errors are handled correctly"
- "the CLI behaves sensibly"
