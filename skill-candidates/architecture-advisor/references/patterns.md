# Architecture Advisor — Patterns

---

## Monolith First

**When**: Any new project. Almost always.

```
Phase 1: Well-structured monolith
/app
  /users       ← clear interface, could become service later
  /orders
  /payments
  /notifications
All share one database, one deployment.

Extract a service only when ALL true:
  1. Different scaling needs (10× more load than rest)
  2. Independent deployment cycle (different release cadence)
  3. Clear team ownership (dedicated team for this domain)
  4. Stable interface (no churn in how others call it)

Warning signs you extracted too early:
  - Constantly changing the service interface
  - Service and monolith deployed together anyway
  - Debugging requires reading logs from multiple systems
```

---

## Data Model Primacy

**When**: Starting any feature involving persistent data. Do this before writing code.

```sql
-- Step 1: Entities and relationships
User (1) ---< Order (*) ---< OrderItem (*) >--- Product (1)

-- Step 2: Fields with constraints
orders:
  id: uuid PRIMARY KEY
  user_id: uuid REFERENCES users NOT NULL
  status: enum('pending', 'paid', 'shipped', 'delivered')
  total_cents: integer NOT NULL   -- money as cents, always

-- Step 3: Query patterns drive indexes
-- "Get all orders for a user" → CREATE INDEX idx_orders_user_id
-- "Get orders by status" → CREATE INDEX idx_orders_status

-- Step 4: Data lifecycle
-- Soft delete or hard? GDPR deletion? Retention policy?
```

Design for the domain, not for the queries. An ORM can't save a wrong data model.

---

## API-First Design

**When**: Building services that others will consume.

```
1. Define resources and operations first (before code)
2. Write example request/response payloads
3. Define error responses (400/401/403/404/409/500)
4. Write OpenAPI spec
5. Implement against the spec

Anti-pattern: Designing API after implementation.
Result: implementation leaks into the interface.
```

---

## CAP Theorem Applied

**When**: Designing systems with multiple nodes or replicas.

You can have two of three: Consistency, Availability, Partition tolerance. Networks always partition — so you're really choosing between C and A when a partition occurs.

| Choice | When to use | Example |
|---|---|---|
| CP (consistency over availability) | Money, inventory, anything that can't be double-counted | Payment processing |
| AP (availability over consistency) | Read-heavy, stale-ok, user-facing | Product catalog, social feeds |

**For 99% of apps**: Use PostgreSQL with read replicas. You will never need to think about CAP again. CAP is for global distributed databases, not typical web services.

---

## Event-Driven vs Request-Response

**When**: Choosing integration pattern between components.

| Request-Response (sync) | Event-Driven (async) |
|---|---|
| Caller needs result immediately | Result not needed immediately |
| Operations must succeed together | Operations can succeed independently |
| Simple, easy to debug | Harder to trace, but decoupled |
| Tight coupling on availability | Resilient to downstream slowness |

```
Synchronous chain of doom (avoid):
  User request → Service A → Service B → Service C → Service D
  Any failure breaks the chain. Latency adds up. Distributed monolith.

Async candidates: email, notifications, report generation,
  data processing, third-party integrations, audit logging
```

---

## ADR (Architecture Decision Record)

**When**: Any one-way door decision (see decisions.md).

```markdown
# ADR-001: Use PostgreSQL for primary database

## Status
Accepted (2026-04-21)

## Context
[1-3 sentences: what forced this decision, what constraints exist]

## Decision
[One sentence: what we're doing]

## Rationale
[2-4 bullet points: why this over alternatives]

## Alternatives Considered
[Each rejected option: 1-2 sentences on why]

## Consequences
Positive: [what gets better]
Negative: [what gets worse / what we accept]

## Review Triggers
[Specific conditions that would cause us to revisit]
```

---

## Failure Mode Analysis

**When**: Designing any system that needs to be reliable.

```
For each external dependency, map:
  Component | Failure | Impact | Mitigation | Fallback

Example: Stripe
  Timeout     → High    → 10s timeout + retry + backoff → "try again"
  Error       → Medium  → Parse + specific message       → offer alternative
  Partial (charge ok, webhook failed) → High → idempotency keys + reconciliation job
  Full outage → Critical → circuit breaker               → queue + charge later

For each component: also model connection exhaustion, slow queries,
primary failure, replication lag.
```
