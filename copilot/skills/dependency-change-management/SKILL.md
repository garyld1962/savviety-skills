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

## Dependency Classification Taxonomy

A four-bucket taxonomy for classifying what your code depends on. The bucket
determines the right test strategy and drives audit judgments about mocking,
substitution, and coverage gaps.

| Category | Description | Test Strategy | Examples |
|---|---|---|---|
| **In-process** | Pure computation, no I/O. Same memory, same process. | Test directly — no mocks, no substitutes. | Validation logic, data transforms, calculations, state machines. |
| **Local-substitutable** | Crosses a boundary, but a real, fast, faithful local stand-in exists. | Use the substitute — faster than mocks, higher fidelity. | PGLite for Postgres, SQLite for SQL, in-memory filesystem, embedded Redis, testcontainers. |
| **Remote but owned** | Services you control across a network or process boundary. | Ports & Adapters — define an interface, inject a real adapter in integration tests and an in-memory adapter in unit tests. | Your own API services, internal message queues, your own cache layers, your own workers. |
| **True external** | Third-party systems you don't control, can't run locally with fidelity, and shouldn't hit in CI. | Mock at the boundary — this is the only category where mocking is the right default. Pair with a small contract test against the real service in a sandboxed lane. | Stripe API, SendGrid, AWS S3, external OAuth providers, third-party webhooks. |

### Mock vs. don't-mock per bucket

1. **Never mock in-process dependencies.** Mocking pure computation hides bugs
   and makes tests measure your mock, not your code.
2. **Never mock local-substitutable dependencies.** If PGLite exists for
   Postgres, use it. A handwritten DB mock will drift from real SQL behavior;
   the substitute won't.
3. **Mock remote-but-owned only at the unit-test boundary.** Integration tests
   must hit the real adapter. Only unit-test mocks here means zero integration
   coverage — flag this as a gap.
4. **Mock true-external — but pair with a contract test.** Pure mocks against
   third-party APIs go stale silently. A nightly or pre-release contract test
   against the real service catches schema drift.
5. **Re-classify when the world changes.** "Remote but owned" can become
   "local-substitutable" the moment someone ships a testcontainer or in-memory
   adapter.

### Common miscategorizations to flag during audits

- Postgres mocked instead of substituted with PGLite — tests pass but skip SQL
  semantics, constraints, and transactions.
- Internal services treated as true-external — if you own both sides, you have
  ports/adapters available; mocking is laziness, not pragmatism.
- External APIs treated as in-process — the boundary is the network call, not
  the function signature wrapping `fetch`.
- Filesystem treated as non-substitutable — `memfs` and tmpfs make most
  filesystem dependencies local-substitutable.

## Closed Decisions

- Dependency analysis is evidence-based and repo-specific, not generic advice.
- Official migration or release documentation is the source of truth for
  version-change claims.
- Built-in `/research` comes before vendor-doc discovery, and built-in `/plan`
  comes after the migration analysis is accepted.
