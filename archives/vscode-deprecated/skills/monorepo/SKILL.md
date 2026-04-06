---
name: monorepo
description: "Monorepo patterns — workspace structure, package boundaries, shared code, dependency management. Turborepo is optional and documented separately."
---

# Monorepo Patterns

Opinionated patterns for TypeScript/Node monorepos using pnpm workspaces (or npm/yarn).

## When to Use Turborepo

**Do NOT add Turborepo by default.** Plain pnpm scripts with `concurrently` are simpler and sufficient for most projects.

| Situation | Use |
|-----------|-----|
| ≤5 packages, <5k LoC, linear dependency chain | **pnpm scripts + concurrently** |
| >5 packages, parallel-safe tasks, CI remote caching needed | **Turborepo** |
| Template already includes Turborepo | **Keep it** |

If the project template or `package.json` uses `pnpm -r run build` and `concurrently`, do NOT replace them with Turborepo. Follow what exists.

## Default Scripts Pattern (No Turborepo)

```json
// Root package.json
{
  "scripts": {
    "build": "pnpm -r run build",
    "dev": "concurrently \"pnpm --filter @myapp/api dev\" \"pnpm --filter @myapp/web dev\"",
    "test": "pnpm -r run test",
    "lint": "pnpm -r run lint"
  }
}
```

Package-specific commands use `--filter`:

```bash
pnpm --filter @myapp/api build
pnpm --filter @myapp/shared test
```

## Workspace Structure

```
my-monorepo/
├── packages/                # All workspace packages
│   ├── shared/              # Types, constants, utilities shared by all
│   ├── db/                  # Database schema, migrations, client
│   ├── api/                 # Express/Fastify backend
│   └── web/                 # Next.js frontend
├── pnpm-workspace.yaml      # Workspace definition
└── package.json             # Root scripts, devDependencies
```

## Package Boundaries — The Cardinal Rule

**Packages import from each other's public exports only.** Never reach into another package's internals.

```typescript
// CORRECT — import from package's public API
import { JobStatus, SUBJECTS } from '@myapp/shared';
import { db } from '@myapp/db';

// WRONG — reaching into internals
import { JobStatus } from '@myapp/shared/src/types/job';
import { pool } from '@myapp/db/src/connection';
```

Every package must have an `index.ts` (or `exports` field in `package.json`) that defines its public API.

## Shared Package

The `shared` (or `common` or `core`) package is the only package that ALL other packages may import from. It contains:

- **Types and interfaces** used across multiple packages
- **Constants** (event subjects, error codes, status enums)
- **Utility functions** that are genuinely shared (not "might be useful someday")

Rules:
- If a type is used in only one package, it belongs in that package — NOT in shared.
- The shared package must have ZERO runtime dependencies on other workspace packages.
- Types from the database schema (`db`) package can be re-exported from shared.

## Dependency Management

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
```

- **Root `package.json`**: Only devDependencies shared across all packages (TypeScript, ESLint, Prettier).
- **Package `package.json`**: Runtime dependencies specific to that package.
- **Workspace protocol**: Use `"@myapp/shared": "workspace:*"` for internal dependencies.
- **Never duplicate versions**: If two packages need the same dependency, keep versions aligned. Use `pnpm dedupe`.

## TypeScript Configuration

```json
// tsconfig.json (root) — shared base
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "composite": true
  }
}

// packages/api/tsconfig.json — extends root
{
  "extends": "../../tsconfig.json",
  "compilerOptions": { "outDir": "dist", "rootDir": "src" },
  "include": ["src"],
  "exclude": ["__tests__", "dist"]
}
```

## Turborepo Configuration (When Opted In)

Only add this if the project explicitly needs Turborepo (>5 packages, CI remote caching, etc.):

```json
// turbo.json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["build"]
    },
    "lint": {},
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

When using Turborepo, root scripts change to:
```json
{
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "dev": "turbo run dev"
  }
}
```

## Common Mistakes

- **Circular dependencies**: Package A imports from B which imports from A. The shared package breaks cycles.
- **Putting everything in shared**: Only types/constants used by 2+ packages belong there.
- **Root-level source code**: No application code at the repo root. It goes in `packages/`.
- **Mismatched TypeScript versions**: Pin one TS version in root, use it everywhere.
- **Missing `build` before `test`**: Types from other packages must be built first. Build dependencies before running tests.
- **Adding Turborepo to small projects**: If the project has ≤5 packages and a linear dependency chain, plain pnpm scripts are simpler. Don't add complexity you don't need.
