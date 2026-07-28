---
name: db-schema-review
description: Database schema and migration review rubric covering ORM conventions, migration safety, indexes, relations, and exported types.
---

# Database Schema Review

Use this skill for migrations, ORM schemas, SQL files, and database model
definitions.

## Review focus

- detect the ORM or schema style first
- match the project's naming, ID, and timestamp conventions
- flag unsafe migrations such as destructive changes or not-null additions that
  ignore existing rows
- check foreign key indexes and multi-table transaction safety
- verify explicit relation behavior and type export boundaries
- avoid reserved words or ad-hoc naming that breaks project conventions

## High-signal checks

- raw SQL should be parameterized
- foreign keys should usually be indexed
- new tables should follow the project's timestamp convention
- irreversible drops deserve explicit attention

## Examples

- **Migration safety review:** A migration adds a non-null column to an existing
  table. Check whether it backfills or supplies a safe default before flagging
  it as migration-risky.
- **Schema convention review:** A new table uses ad-hoc timestamp or ID fields.
  Compare it to the repo's existing schema conventions before deciding whether
  the shape is actually inconsistent.

## Guardrails

- Read existing schema files before reviewing.
- Match the repo's ORM conventions, not a generic favorite ORM.

## Do Nots

- Do not recommend ORM patterns from a different stack than the one the repo
  uses.
- Do not call a destructive migration safe just because it passes syntax
  validation.
- Do not ignore existing-row impact when reviewing new required columns or data
  transformations.

## Closed Decisions

- Existing ORM, schema, naming, ID, and timestamp conventions are authoritative.
- Migration safety matters more than stylistic database preferences.
- Raw SQL must be parameterized.
- Irreversible or destructive changes require explicit scrutiny.
