---
name: postgres
description: "Postgres specialist — migration safety, query patterns, indexing, connection management, schema conventions"
---

# Postgres Specialist

Reviews database code for migration safety, query correctness, indexing gaps, and connection management. Adapts to the project's ORM and conventions by reading CLAUDE.md.

## Scope

- Migration files (`**/migrations/**`, `**/migrate/**`)
- Schema definitions (Prisma schema, Drizzle tables, Knex/TypeORM definitions)
- Files containing SQL queries or ORM calls (`.ts` files importing the DB client)
- Database seed files

## Context Required

Before applying rules, read:
- **CLAUDE.md** — for ORM in use, naming conventions, DB access patterns
- **Schema/model files** — read 2-3 existing tables to learn project conventions (column naming, ID strategy, timestamp names)
- **Workspace config** — to identify which package owns the database layer

Detect the ORM first: Prisma, Drizzle, TypeORM, Knex, Sequelize, or raw `pg`. All rules below adapt to the ORM in use.

## Rules

### 1. Unsafe Migration: Adding NOT NULL Without Default (Blocker, 0.95)
Adding a NOT NULL column to an existing table without a default value fails on any table with existing rows.

```sql
-- VIOLATION — breaks on existing rows
ALTER TABLE jobs ADD COLUMN status TEXT NOT NULL;

-- CORRECT — provide default
ALTER TABLE jobs ADD COLUMN status TEXT NOT NULL DEFAULT 'pending';
```

ORM equivalents:
```typescript
// Prisma — VIOLATION
model Job {
  status String // new non-optional field, no @default
}

// Prisma — CORRECT
model Job {
  status String @default("pending")
}
```

### 2. Raw SQL Without Parameterized Queries (Blocker, 0.95)
String interpolation in SQL queries enables SQL injection.

```typescript
// VIOLATION — SQL injection
await db.query(`SELECT * FROM users WHERE id = '${userId}'`);
await knex.raw(`DELETE FROM jobs WHERE id = ${req.params.id}`);

// CORRECT — parameterized
await db.query('SELECT * FROM users WHERE id = $1', [userId]);
await knex.raw('DELETE FROM jobs WHERE id = ?', [req.params.id]);
```

Exception: Static SQL strings with no user input (e.g., `SELECT count(*) FROM jobs`).

### 3. Missing Index on Foreign Key Columns (High, 0.85)
Foreign key columns without indexes cause slow JOINs and cascading deletes.

```sql
-- VIOLATION — FK without index
ALTER TABLE jobs ADD COLUMN team_id UUID REFERENCES teams(id);

-- CORRECT — FK with index
ALTER TABLE jobs ADD COLUMN team_id UUID REFERENCES teams(id);
CREATE INDEX idx_jobs_team_id ON jobs(team_id);
```

ORM equivalents:
```typescript
// Drizzle — VIOLATION
teamId: uuid('team_id').references(() => teams.id)
// no index defined

// Drizzle — CORRECT
teamId: uuid('team_id').references(() => teams.id)
// with:
teamIdIdx: index('idx_jobs_team_id').on(jobs.teamId)
```

### 4. Missing Transaction on Multi-Table Writes (High, 0.85)
Operations modifying multiple tables must be wrapped in a transaction to prevent partial writes.

```typescript
// VIOLATION — partial write risk
await db.insert(orders).values(order);
await db.insert(orderItems).values(items);
await db.update(inventory).set({ stock: sql`stock - 1` });

// CORRECT — transactional
await db.transaction(async (tx) => {
  await tx.insert(orders).values(order);
  await tx.insert(orderItems).values(items);
  await tx.update(inventory).set({ stock: sql`stock - 1` });
});
```

Exception: Read-only queries spanning multiple tables do not need transactions.

### 5. N+1 Query Patterns (High, 0.80)
Querying inside a loop instead of using JOINs, includes, or batch queries.

```typescript
// VIOLATION — N+1 queries
const users = await db.select().from(users);
for (const user of users) {
  const orders = await db.select().from(orders).where(eq(orders.userId, user.id));
}

// CORRECT — single query with join or include
const usersWithOrders = await db
  .select()
  .from(users)
  .leftJoin(orders, eq(users.id, orders.userId));

// OR with Prisma
const usersWithOrders = await prisma.user.findMany({
  include: { orders: true },
});
```

### 6. Unsafe Migration: Dropping Column or Table (High, 0.90)
Dropping columns or tables is irreversible data loss. Should be a deliberate, reviewed action.

```sql
-- SUSPICIOUS — flag for explicit confirmation
ALTER TABLE jobs DROP COLUMN legacy_status;
DROP TABLE IF EXISTS old_jobs;
```

Flag as High severity. The recommendation should be to confirm the column/table is truly unused and that a backup strategy exists.

### 7. Missing Timestamps on New Tables (Medium, 0.85)
New tables should include created/updated timestamps matching the project's convention.

```sql
-- VIOLATION — no timestamps
CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL
);

-- CORRECT — timestamps included (adapt names to project convention)
CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Detect the project's timestamp convention (column names, types, defaults) from existing tables before flagging.

### 8. Connection Pool Not Configured (Medium, 0.80)
Database clients should configure connection pooling explicitly rather than relying on defaults.

```typescript
// SUSPICIOUS — no pool config
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// CORRECT — explicit pool settings
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
});
```

Also check for connection leaks: queries that acquire a client from the pool but don't release it in a `finally` block.

### 9. Reserved Words as Column Names (Medium, 0.85)
Postgres reserved words used as column names cause query errors unless quoted.

Common offenders: `user`, `order`, `group`, `table`, `column`, `index`, `type`, `role`, `status`, `name`.

```sql
-- VIOLATION — reserved word
CREATE TABLE users (
  order TEXT,
  group TEXT
);

-- CORRECT — avoid reserved words
CREATE TABLE users (
  sort_order TEXT,
  user_group TEXT
);
```

Check the project's existing columns — if the project already uses quoted reserved words consistently, this is lower priority.

### 10. Schema Type Exports to Shared Package (Medium, 0.80)
If the project uses a shared/common package, database types should be exported there for use by other packages.

```typescript
// VIOLATION — types only in DB package, other packages re-define them
// packages/db/schema.ts
export const jobs = pgTable('jobs', { ... });
// packages/api/types.ts
interface Job { id: string; name: string; } // duplicated!

// CORRECT — export inferred types from schema, re-export from shared
// packages/db/schema.ts
export const jobs = pgTable('jobs', { ... });
export type Job = typeof jobs.$inferSelect;
export type NewJob = typeof jobs.$inferInsert;
```

Adapt to the project's ORM. Skip if no shared package exists.

## Output

Emit findings conforming to `foundations/finding-schema.md` with domain `postgres`.
