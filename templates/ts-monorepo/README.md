# TypeScript Monorepo Template

A full-stack TypeScript monorepo with pnpm workspaces.

## Stack

- **Shared**: Types, validation, business logic (zero runtime deps)
- **DB**: Drizzle ORM + SQLite via @libsql/client
- **API**: Express REST API with factory pattern
- **Web**: Next.js 15 (App Router, Turbopack) + Tailwind CSS

## Quick Start

```bash
# Copy template
npx degit garyld1962/savviety-skills/templates/ts-monorepo my-project
cd my-project

# Rename packages (find and replace @app/ with @myproject/)
# Update package names in all package.json files

# Install and verify
pnpm install
pnpm build
pnpm test
pnpm dev   # API on 3001, Web on 3000
```

## Package Structure

| Package | Purpose |
|---------|---------|
| `packages/shared` | Types, constants, scoring logic, validation |
| `packages/db` | Drizzle ORM schema, SQLite, migrations |
| `packages/api` | Express REST API with typed routes |
| `packages/web` | Next.js 15 frontend (App Router) |

## Architecture

- **Database**: Factory functions for connection (`createDatabaseContext()`), not singletons
- **Repository pattern**: Data access behind interfaces, injected into the API
- **API**: `createApp({ repository })` factory, testable with supertest
- **Shared logic**: Types, enums, validation in `packages/shared` — never duplicate
