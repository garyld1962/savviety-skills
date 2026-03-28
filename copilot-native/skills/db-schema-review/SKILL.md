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

## Guardrails

- Read existing schema files before reviewing.
- Match the repo's ORM conventions, not a generic favorite ORM.
