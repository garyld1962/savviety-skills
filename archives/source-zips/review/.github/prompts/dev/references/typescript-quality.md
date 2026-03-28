# TypeScript Quality Specialist

**Domain:** `typescript-quality`

Reviews all TypeScript/TSX files for type safety, strict mode compliance, and import hygiene. These rules are universal to any TypeScript project.

## Scope

All `*.ts` and `*.tsx` files in source roots identified from:
- `pnpm-workspace.yaml` or `package.json` workspaces field
- Auto-detected source directories: `packages/*/src`, `services/*/src`, etc.

## Context Required Before Review

Read these files from repo root to understand project conventions:
- **`.github/copilot-instructions.md`** — project-specific import conventions, package boundaries, logging patterns
- **Workspace config** — to identify package boundaries and the shared package

## Review Checklist

### Rule 1: No `any` Type (High, 0.92+)

**What:** Avoid the `any` type; use `unknown` instead for unknown values.

**Violations:**
```typescript
const data: any = response;
function process(input: any): any { ... }
```

**Correct:**
```typescript
const data: unknown = response;
function process(input: unknown): ProcessedData { ... }
```

**Exception:** Third-party library types that genuinely require `any` (must have justifying comment).

---

### Rule 2: No `@ts-ignore` Without Justification (Medium, 0.90+)

**What:** Use `@ts-expect-error` with clear explanation instead of `@ts-ignore`.

**Violation:**
```typescript
// @ts-ignore
const value = obj.prop;
```

**Correct:**
```typescript
// @ts-expect-error — library types incompatible with current TS version, see issue #42
const value = obj.prop;
```

---

### Rule 3: No `console.log` in Production Code (Medium, 0.90)

**What:** Check `.github/copilot-instructions.md` for the project's logging convention. If a structured logger is configured, `console.log` is a violation in service code.

**Exception:** Test files, scripts, and CLI tools may use console.

---

### Rule 4: No Cross-Package Boundary Imports (High, 0.95)

**What:** Workspace packages must not import directly from each other's internals — only from the shared package or via public exports.

**Violations:**
```typescript
import { something } from '../../../other-package/src/internal';
import { internalType } from '@myapp/shared/src/internals';
```

**Allowed:**
```typescript
import { SharedType } from '@myapp/shared';
import { type AppRouter } from '@myapp/server';  // type-only
```

---

### Rule 5: ESM Import Extensions (Medium, 0.85)

**What:** For ESM projects (`"type": "module"` + `NodeNext`), relative imports require `.js` extensions.

**Violation:**
```typescript
import { createAgent } from './agent';
```

**Correct:**
```typescript
import { createAgent } from './agent.js';
```

**Skip if:** Project uses CommonJS or bundler module resolution.

---

### Rule 6: `noUncheckedIndexedAccess` Compliance (Medium, 0.80)

**What:** Guard against undefined when accessing array indices or dynamic object properties.

**Violation:**
```typescript
const first = items[0].toUpperCase();
```

**Correct:**
```typescript
return items[0]?.toUpperCase() ?? 'default';
```

**Apply only if:** tsconfig has `noUncheckedIndexedAccess: true`.

---

### Rule 7: Non-null Assertion Hiding Real Bugs (Medium, 0.75)

**What:** Non-null assertions (`!`) can hide real bugs. Prefer explicit guards.

**Suspicious:**
```typescript
const user = users.find(u => u.id === id)!;
```

**Better:**
```typescript
const user = users.find(u => u.id === id);
if (!user) throw new Error(`User ${id} not found`);
```

---

### Rule 8: Unused Imports and Variables (Low, 0.90)

**What:** Flag unused imports and variables. Only flag if no linter is configured.

## Output

Domain is always `"typescript-quality"`. Emit findings conforming to the schema in the main code-review prompt.
