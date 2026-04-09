---
description: >-
  API/service pattern compliance check: shared types, error handling, logging,
  auth, input validation, messaging contracts. Quick manual check for backend code.
agent: 'ask'
tools:
  - read
  - search
  - codebase
---

# API Pattern Compliance Review

Quick review of backend/API code for pattern compliance. Reads project docs for conventions and checks against them.

---

## CRITICAL: Do Not Guess

- **Project patterns**: READ `.github/copilot-instructions.md` FIRST. The project's patterns are the standard — not generic best practices.
- **Shared types package**: DETECT it from workspace config. Do NOT assume it's called "shared."
- **Error handling convention**: Check how existing services handle errors. Is it try/catch? Result types? Error middleware? Match the project.
- **Auth pattern**: Read existing auth middleware before commenting on auth. The project may use tokens, sessions, or something custom.
- **Finding line numbers**: Search and verify. Do NOT cite approximate lines.

---

## Step 1: Load Project Conventions

```
Read: .github/copilot-instructions.md
Read: <shared-package>/src/ (find the types/schemas)
Read: One existing service file (as reference pattern)
```

Extract:
- How types are defined and shared
- Error handling patterns (Result types, exceptions, error codes)
- Logging conventions (structured? which logger?)
- Auth middleware pattern
- Input validation approach (Zod, Joi, manual, etc.)
- Response format (envelope, raw, JSON:API, etc.)

---

## Step 2: Check Each Pattern

For each file in scope (or currently open file):

### 2a. Shared Types Usage

| Check | Pass | Fail |
|-------|------|------|
| Types imported from shared package, not redefined locally | Uses `import { Type } from '<shared>'` | Redefines types inline |
| Request/response types match shared definitions | Types match | Types diverge |
| Enums come from shared package | Shared enums | Local string literals |

### 2b. Error Handling

| Check | Pass | Fail |
|-------|------|------|
| Async operations have error handling | try/catch or .catch() on all awaits | Unhandled promise |
| Errors include context (operation, entity, ID) | `new Error(\`Failed to create user ${id}\`)` | `throw new Error("failed")` |
| Error responses use consistent format | Matches project pattern | Ad-hoc error shape |
| No silent error swallowing | Errors logged or re-thrown | `catch (e) {}` |

### 2c. Input Validation

| Check | Pass | Fail |
|-------|------|------|
| External input validated at boundary | Schema validation on request body/params | Raw `req.body` used directly |
| Validation errors return 400 with details | Structured validation error | Generic 500 |
| Internal function calls trust validated input | No re-validation of already-validated data | Redundant validation deep in stack |

### 2d. Auth & Authorization

| Check | Pass | Fail |
|-------|------|------|
| Routes that need auth have middleware | Auth check present | Endpoint open |
| Authorization checked (not just authentication) | Role/permission check | Only token check |

### 2e. Logging

| Check | Pass | Fail |
|-------|------|------|
| Key operations logged | Create, update, delete logged | Silent operations |
| Uses project's logger (not console.log) | `logger.info(...)` | `console.log(...)` |
| Sensitive data not logged | IDs, metadata only | Passwords, tokens in logs |

---

## Step 3: Report

```
## API Pattern Review: <file(s)>

| Pattern | Verdict | Findings |
|---------|---------|----------|
| Shared Types | PASS/WARN/FAIL | N issues |
| Error Handling | PASS/WARN/FAIL | N issues |
| Input Validation | PASS/WARN/FAIL | N issues |
| Auth | PASS/WARN/FAIL/N/A | N issues |
| Logging | PASS/WARN/FAIL | N issues |

### Findings
1. **[severity]** `file:line` — <description>
   - Expected: <project pattern>
   - Found: <what the code does>
   - Fix: <specific change>
```

---

## Rules

1. **Project conventions are the standard.** Match the project, not textbook patterns.
2. **Read before reviewing.** You must read project docs and a reference implementation before checking any file.
3. **Findings need evidence.** Cite exact file:line and the specific convention being violated.
