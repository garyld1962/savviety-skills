---
description: >-
  Database schema compliance check: primary keys, timestamps, indexes,
  relations, type exports, naming conventions. Reads project ORM conventions.
agent: 'ask'
tools:
  - read
  - search
  - codebase
---

# Database Schema Compliance Review

Quick review of database schema code (migrations, models, ORM definitions) for pattern compliance.

---

## CRITICAL: Do Not Guess

- **ORM in use**: DETECT which ORM the project uses (Prisma, Drizzle, TypeORM, Knex, Sequelize, raw SQL). Do NOT assume.
- **Naming convention**: Check existing tables/columns. Is it snake_case, camelCase, PascalCase? Match the project.
- **ID strategy**: Check existing tables. UUID? Auto-increment? CUID? Match the project.
- **Timestamp columns**: Check existing tables for `createdAt`/`updatedAt` naming and type.

---

## Step 1: Detect ORM and Conventions

```bash
# Check for ORM config files
ls prisma/ drizzle.config.* knexfile.* ormconfig.* 2>/dev/null

# Check package.json for ORM dependency
cat package.json | grep -E '"(prisma|drizzle-orm|typeorm|knex|sequelize)"'
```

Read 2-3 existing schema/model/migration files to learn:
- Column naming convention
- ID type and generation strategy
- Timestamp column names and types
- Soft delete pattern (if any)
- Index naming convention
- Foreign key naming convention

---

## Step 2: Check Each Pattern

### 2a. Primary Keys

| Check | Pass | Fail |
|-------|------|------|
| Every table has a primary key | `id` column present | No PK defined |
| PK type matches project convention | Same type as other tables | Different type |
| PK generation matches convention | Same strategy | Different strategy |

### 2b. Timestamps

| Check | Pass | Fail |
|-------|------|------|
| `createdAt` (or project equivalent) present | Column exists with correct type | Missing |
| `updatedAt` (or project equivalent) present | Column exists | Missing |
| Default values set correctly | `DEFAULT NOW()` or equivalent | No default |

### 2c. Indexes

| Check | Pass | Fail |
|-------|------|------|
| Foreign keys are indexed | Index on FK columns | FK without index |
| Frequently queried columns indexed | Based on usage patterns | Missing index on filtered columns |
| Index names follow convention | Match project pattern | Ad-hoc names |

### 2d. Relations

| Check | Pass | Fail |
|-------|------|------|
| FK constraints defined | `REFERENCES` present | Dangling FK |
| Cascade behavior explicit | `ON DELETE CASCADE/SET NULL/RESTRICT` | Default behavior (may surprise) |
| Relation types correct | 1:1, 1:N, N:M match domain | Wrong cardinality |

### 2e. Type Exports

| Check | Pass | Fail |
|-------|------|------|
| Schema types exported to shared package | Types available for import | Types only in DB package |
| Insert/select types distinct | Separate input vs output types | Same type for both |

### 2f. Naming

| Check | Pass | Fail |
|-------|------|------|
| Table names match convention | Same style as existing tables | Different style |
| Column names match convention | Same style as existing columns | Different style |
| No reserved words as column names | No conflicts | Uses `order`, `group`, `user`, etc. |

---

## Step 3: Report

```
## Schema Review: <file(s)>

**ORM:** <detected>
**Convention:** <column naming, ID type, timestamp names>

| Pattern | Verdict | Findings |
|---------|---------|----------|
| Primary Keys | PASS/WARN/FAIL | N issues |
| Timestamps | PASS/WARN/FAIL | N issues |
| Indexes | PASS/WARN/FAIL | N issues |
| Relations | PASS/WARN/FAIL | N issues |
| Type Exports | PASS/WARN/FAIL | N issues |
| Naming | PASS/WARN/FAIL | N issues |

### Findings
1. **[severity]** `file:line` — <description>
   - Convention: <what the project does>
   - Found: <what this code does>
   - Fix: <specific change>
```

---

## Rules

1. **Detect the ORM first.** Schema review without knowing the ORM is useless.
2. **Match the project.** Every check compares against the project's own conventions, not generic best practices.
3. **Read before reviewing.** You must read existing schema files to learn conventions before flagging violations.
