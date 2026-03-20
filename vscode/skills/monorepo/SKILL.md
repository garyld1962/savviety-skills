---
name: monorepo
description: "Monorepo patterns — workspace structure, package boundaries, shared code, Turborepo, dependency management"
---

# Monorepo Patterns

Opinionated patterns for TypeScript/Node monorepos using pnpm workspaces (or npm/yarn). Applies to Turborepo and non-Turborepo setups.

## Workspace Structure

```
my-monorepo/
├── apps/                    # Deployable applications
│   ├── web/                 # Next.js frontend
│   ├── api/                 # Express/Fastify backend
│   └── worker/              # Background job processor
├── packages/                # Shared libraries
│   ├── shared/              # Types, constants, utilities shared by all
│   ├── db/                  # Database schema, migrations, client
│   ├── config/              # Shared ESLint, TypeScript, Tailwind configs
│   └── ui/                  # Shared UI components (if applicable)
├── pnpm-workspace.yaml      # Workspace definition
├── turbo.json               # Turborepo config (if using)
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
  - 'apps/*'
  - 'packages/*'
```

- **Root `package.json`**: Only devDependencies shared across all packages (TypeScript, ESLint, Prettier).
- **Package `package.json`**: Runtime dependencies specific to that package.
- **Workspace protocol**: Use `"@myapp/shared": "workspace:*"` for internal dependencies.
- **Never duplicate versions**: If two packages need the same dependency, keep versions aligned. Use `pnpm dedupe`.

## Turborepo Configuration

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

- `^build` means "build my dependencies first" — critical for type generation.
- `lint` has no `dependsOn` — it can run in parallel.
- `dev` is never cached — it's a long-running process.

## Scripts Pattern

```json
// Root package.json
{
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "dev": "turbo run dev"
  }
}
```

Run everything from root. Package-specific commands use `--filter`:

```bash
pnpm --filter @myapp/api build
pnpm --filter @myapp/web dev
turbo run test --filter=@myapp/shared
```

## TypeScript Configuration

```json
// packages/config/tsconfig.base.json — shared base
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "composite": true
  }
}

// apps/api/tsconfig.json — extends base
{
  "extends": "@myapp/config/tsconfig.base.json",
  "compilerOptions": { "outDir": "dist" },
  "include": ["src"],
  "references": [
    { "path": "../../packages/shared" },
    { "path": "../../packages/db" }
  ]
}
```

## Common Mistakes

- **Circular dependencies**: Package A imports from B which imports from A. The shared package breaks cycles.
- **Putting everything in shared**: Only types/constants used by 2+ packages belong there.
- **Root-level source code**: No application code at the repo root. It goes in `apps/` or `packages/`.
- **Mismatched TypeScript versions**: Pin one TS version in root, use it everywhere.
- **Missing `build` before `test`**: Types from other packages must be built first. Use `dependsOn: ["^build"]`.
