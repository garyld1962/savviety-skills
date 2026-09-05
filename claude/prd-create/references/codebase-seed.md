# Codebase seed: code signal → ontology category

Used by `/prd-create` **Step 1** in brownfield modes (`feature`, `refresh`,
`rewrite`). The scan **proposes**; the Step 3 interview **confirms**.

Every row this table produces enters `ONTOLOGY.md` as `unknown` with a
`code:<file:line>` source. Nothing seeded is written `settled` without a human
answer: a scan reports what the code does, which is not evidence of what the
domain requires. The category names and the item-state vocabulary are owned by
`_internal/ontology-readiness`; this file only maps code signals onto them.

## Signal table

| Code signal | Where to look | Proposed as |
|---|---|---|
| ORM model, table definition, exported domain type, aggregate root | `models/`, `entities/`, `schema.prisma`, migrations, `domain/` | **entity type** |
| Primary key, `@id`, unique index, unique constraint, natural-key lookup (`findBySku`) | migrations, schema, repository query methods | candidate **reference scheme** for that entity |
| Foreign key, join table, typed relation field, navigation property | schema, migrations, model associations | candidate **fact type**, verbalized, with cardinality read off the relation |
| Relation cardinality and nullability | `NOT NULL` on the FK, `1:N` vs `N:M` shape | Constraints cell: `mandatory: <Child>→<Parent>`, `unique: <Entity>.<field>` |
| `*Status` / `*State` enum plus a transition function, state machine, or `switch` on that enum | services, reducers, workflow code | candidate **lifecycle**; totality check = every enum member has an outgoing branch or is explicitly terminal |
| `NOT NULL`, unique, check constraint, non-nullable schema type, DB-enforced range | migrations, schema | **alethic** modality candidate (cannot be otherwise → type or schema constraint) |
| Validator, guard clause, policy or business-rule function, permission check, thrown domain error | `validators/`, `policies/`, service preconditions | **deontic** modality candidate (must not be otherwise → validation rule or alert) |
| Enum on a field, allowed-values list, range or regex check | schema, validators, constants | Constraints cell: `value domain: <values or range>` |
| `created_at`, `updated_at`, `valid_from`, `valid_to`, `effective_*`, history or audit tables, event log, `deleted_at` soft delete | migrations, base model mixins | **temporality** candidate — instant vs interval, and whether historisation is recorded at all |
| The same type name defined in two packages; two names bound to one table; a term used with two meanings across modules | package boundaries, `/audit-existing` § *Duplicated Or Divergent Contracts* | **homonym** candidate (one term, two meanings) or synonym candidate (two terms, one meaning) |

## Constraint-cell prefixes

Emit exactly these prefixes so `/prd-acceptance` and `/test-plan` can key on them:

- `unique:` — a uniqueness constraint. Becomes a duplicate-insert test.
- `mandatory:` — a mandatory role. Becomes a null-rejection test.
- `value domain:` — an enumerated or bounded domain. Becomes a boundary test.

A cell that has no constraint reads `[unconstrained]`. It is never blank.

## Ordering and guardrails

1. Run `/audit-existing` first — its `## Duplicated Or Divergent Contracts` is
   the strongest homonym signal in the repo, and its `## Existing State` supplies
   the AERS execution sections without a second scan.
2. Walk schema and migrations before application code: reference schemes and
   alethic constraints are declared there, not inferred.
3. In `refresh`, add `_internal/modernization-rubric` §1 shape detection and
   sample-read per its §3, stopping at the 30% context guardrail.
4. Do not read every file. The seed is a proposal to a human, not an inventory.
5. Entities the current release does not touch are proposed as **out of the UoD**
   in Step 2 rather than interviewed — that is what licenses deferring their
   fact types.
