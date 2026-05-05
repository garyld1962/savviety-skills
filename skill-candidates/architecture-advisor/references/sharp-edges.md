# Architecture Advisor — Sharp Edges

---

## Microservices Before Product-Market Fit

**Severity**: Critical
**Situation**: Team starts a new product with microservices because "that's how you build scalable systems." Six months in: half the engineering time is infrastructure, service boundaries are constantly changing, debugging requires correlating logs across 8 services.

```
Wrong boundaries are expensive to fix:
  move data + change APIs + coordinate teams + migrate clients
  = months of work that adds zero user value

You don't know where the boundaries are until you've built it.
```

**Fix**: Monolith first. Extract services only when you have hard evidence: different scaling needs, independent deployment requirements, dedicated team ownership. Starting with microservices means drawing boundaries before you understand the domain.

---

## The Distributed Monolith

**Severity**: Critical
**Situation**: Team split into microservices but services share a database, make synchronous calls to each other, and must be deployed in sequence. All the complexity of microservices, none of the benefits.

```
Distributed monolith signals:
  - Multiple services write to the same database tables
  - Schema changes require coordinating all teams
  - Services can't deploy without deploying others
  - Debugging spans 5 services for one user request
  - "We need to deploy everything at once"
```

**Fix**: If services share a database or must deploy together — merge them. Real microservices have independent data stores. A well-structured monolith beats a distributed monolith in every dimension: simpler debugging, easier deployment, less infrastructure.

---

## Designing for Scale You Don't Have

**Severity**: High
**Situation**: Three-person startup adds Kubernetes, event streaming, CQRS, and sharded databases because "we'll need it when we scale." Half the engineering effort is infrastructure. The product launches 6 months late.

```
"Scalable" is not a feature — it's a hypothesis.
You don't know what will scale until real users use it.
Premature scalability is premature optimization with fancier infrastructure.

Real scaling progression:
  1. Vertical scale (bigger instance) — covers most startups to Series B
  2. Read replicas — covers most read-heavy workloads
  3. Targeted extraction — scale the specific bottleneck, not everything
```

**Fix**: Start with a well-structured monolith on a single database. Scale what's actually measured as a bottleneck. The cost of over-engineering before you have users is a delayed product; the cost of under-engineering is a refactor you do with revenue.

---

## Data Model Optimized for Queries

**Severity**: High
**Situation**: Team designs the database schema to make the first few queries easy — denormalized, query-shaped tables. Six months later, business requirements change and the data model can't represent the new domain without a migration that touches everything.

```
Common trap: optimizing for ORM convenience or report queries
instead of modeling the actual domain.

Your data model is your architecture.
Code is flexible. Schema migrations at scale are not.
```

**Fix**: Design the data model for the domain first — entities, relationships, constraints. Then add indexes for query patterns. Let the ORM work with the model, not shape it. Treat schema decisions as one-way doors.

---

## Cargo-Culting Big-Tech Architecture

**Severity**: High
**Situation**: Team reads a Netflix or Google engineering blog post and adopts the architecture. Three engineers spend four months building infrastructure designed for 1,000-engineer organizations at petabyte scale.

```
"All the cool companies use microservices/Kafka/CQRS/event sourcing."

Netflix: 10,000+ engineers, billions of streams
You: 5 engineers, 1,000 users

Their solution is optimized for their scale and org structure.
Your org structure is 5 people. Your solution should be too.
```

**Fix**: Match technology to problem. Use boring, well-understood technology by default. New or complex tech needs explicit justification based on your actual constraints. "It's what Netflix does" is resume-driven development.

---

## Decision Paralysis on Reversible Choices

**Severity**: High
**Situation**: Team spends three months evaluating monitoring tools. Meetings, comparison docs, pilots. Still no decision. Meanwhile production issues go unmonitored.

```
Two-way door treated as one-way:
  "Which logging library?" → 3 months of discussion
  Reversal cost of wrong choice: 1 day
  Cost of 3 months of delay: unmeasured production issues, morale damage
```

**Fix**: Classify first. If reversal cost is under a week — individual decides today. If under a month — small team decides this week with a timebox. Only decisions that take > 3-6 months to undo warrant committees and documents. Default to action.

---

## Sunk Cost in Architecture

**Severity**: Critical
**Situation**: Team has spent 6 months on an architectural approach. New evidence shows it won't work. But the investment feels too large to abandon. Team doubles down, spending 6 more months.

```
"We've come too far to turn back."
→ Past investment is already spent. It's irrelevant to the next decision.

Reframe: past work gave you information. That information says stop.
Ignoring the lesson wastes the investment twice.
```

**Fix**: Set kill criteria upfront: "If X doesn't work by date Y, we stop." Celebrate pivots — "we learned X didn't work and changed course" is a success. Evaluate the current path as if starting fresh today; if the answer would be different, the current path is wrong.
