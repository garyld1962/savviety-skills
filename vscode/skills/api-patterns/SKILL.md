---
name: api-patterns
description: "Reviews backend/service code for architectural pattern compliance."
---

# API Patterns Specialist

**Domain:** `api-patterns`

Reviews backend/service code for architectural pattern compliance. Adapts to the project's framework and messaging system by reading `.github/copilot-instructions.md`.

## Scope

All `*.ts` files in service/API/backend packages. Excludes UI/frontend packages and test files.

> **What is a service package?** A package whose primary purpose is serving HTTP/RPC requests or handling async jobs (e.g., `services/auth`, `services/worker`). Identify by checking package.json scripts for `start` or `serve`, or by the presence of route/handler files.

## Context Required Before Review

- **`.github/copilot-instructions.md`** — framework (Express, Fastify, tRPC, etc.), messaging system, error handling patterns, shared package conventions
- **Workspace config** — shared package and service package boundaries

## Review Checklist

### Rule 1: Shared Types and Constants From Shared Package Only (Medium, 0.90)

**What:** Types and constants used across multiple packages must be defined in the shared package.

**Violation:**
```typescript
// in services/worker/src/types.ts — duplicates shared type
interface JobDispatch { jobId: string; type: string; }
```

**Correct:**
```typescript
import { JobDispatch } from '@myapp/shared';
```

---

### Rule 2: Error Handling on Async Route Handlers (High, 0.85)

**What:** All async HTTP route handlers must have error handling. Adapt to project framework (Express try-catch, Fastify error handler, tRPC auto-catch).

---

### Rule 3: Request Input Validation (High, 0.90)

**What:** User-facing endpoints must validate input before processing.

---

### Rule 4: Messaging Contract Compliance (Medium, 0.85)

**What:** If project uses messaging (NATS, Redis, RabbitMQ): subject/topic names from shared package, payloads use shared types, subscribers handle errors.

**Skip this rule if:** Project doesn't use messaging.

---

### Rule 5: Graceful Shutdown (Medium, 0.75)

**What:** Services in containers must handle SIGTERM/SIGINT for clean shutdown.

**Skip this rule if:** No Dockerfiles or K8s manifests exist.

---

### Rule 6: Connection/Subscription Cleanup (Medium, 0.80)

**What:** Database connections, message queue subscriptions, and other resources must be cleaned up on shutdown.

---

### Rule 7: Follow Project's Error Handling Convention (Medium, 0.80)

**What:** Check `.github/copilot-instructions.md` for custom error classes. If one exists, flag raw `throw new Error()` in service code.

## Output

Domain is always `"api-patterns"`. Emit findings conforming to the schema in the main code-review prompt.
