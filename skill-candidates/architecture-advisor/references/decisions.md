# Architecture Advisor — Decisions

---

## Reversibility Analysis (One-Way vs Two-Way Doors)

The most important classification before any architectural decision.

**One-way doors** (reversal cost > 3-6 months, or creates business disruption to undo):
- Programming language, database engine, cloud provider
- Architectural style (monolith vs microservices)
- Data model schema once data is in it
- Public API contracts once adopted

**Two-way doors** (decide fast, expect to revisit):
- Monitoring/logging tool, internal API design (before widespread use)
- Testing framework, deployment schedule, feature flags, UI framework version

| Door type | Process |
|---|---|
| One-way | Broad stakeholder input, written analysis, ADR, review period |
| Two-way | Individual or small team decides, minimal doc, bias toward action |

**Anti-pattern**: Treating every decision as a one-way door. Velocity dies. Simple choices take weeks. The irony: your "careful" process is a worse meta-decision.

---

## Monolith vs Services Decision Matrix

| Signal | Monolith | Extract service |
|---|---|---|
| Team size | < 10 engineers | Dedicated team per domain |
| Domain understanding | Still learning | Well-understood, stable |
| Scaling needs | Uniform | One component needs 10× |
| Deployment cadence | Same for all | Components need independent release |
| Data coupling | Shared | Independent data stores feasible |

**Default**: Monolith. Always. Extract services when you have evidence, not theory.

---

## Synchronous vs Asynchronous

```
Does the caller need the result to complete its response?
├── Yes → Synchronous (but keep the chain short)
└── No → Async candidate

Is this a critical path operation?
├── Yes → Sync, with timeout + circuit breaker
└── No → Async queue + background worker

Will this slow the user's response?
├── Email / notification → Async
├── Report generation → Async
├── Third-party integrations → Async when result not needed immediately
└── Payment authorization → Sync (user needs to know it worked)
```

---

## Scale Decision

```
Is there a measured scaling bottleneck?
├── No → Do nothing. Premature scalability = premature optimization.
└── Yes: what is it?
    ├── Single server CPU/memory → Vertical scale first (bigger instance)
    │   └── If vertical limit reached → Horizontal (add instances + load balancer)
    ├── Database reads → Read replicas
    ├── Database writes → Shard or redesign write path
    └── Specific service → Extract and scale that service only
```

"Scalable" is not a feature — it's a hypothesis. You don't know what needs to scale until real users use the system.

---

## Build vs Buy

| Factor | Build | Buy |
|---|---|---|
| Core differentiation | ✓ Build — this is where your value lives | — |
| Commodity capability | — | ✓ Buy — don't compete with specialists |
| Integration complexity | Simple | — |
| Team expertise | Exists | — |
| Vendor lock-in risk | Low | Evaluate carefully |
| Time to market | — | ✓ Buy is faster |

**Framework**: Build when it's your core business logic. Buy everything else. The most impressive engineering is the infrastructure you don't have to maintain.

---

## Second-Order Effects Checklist

Before finalizing any one-way door decision, ask "and then what?" at least twice.

```
Decision: Add caching layer

First-order: API gets faster ✓
Second-order:
  - Cache invalidation complexity — who owns this?
  - Stale data bugs — how does user experience this?
  - New failure mode: cache outage — graceful degradation?
  - Debugging difficulty — how do we know if cache is the cause?
Third-order:
  - Team needs caching expertise
  - Every new feature must consider cache (velocity cost)
  - Cache becomes critical path needing monitoring/on-call
```

Stop when effects become speculative. But always get to second-order before deciding.

---

## Four Pillars Assessment

**When**: Designing or reviewing any system architecture.

| Pillar | Key question | Red flags |
|---|---|---|
| Scalability | Which component breaks first at 10× load? | Single write path, in-memory state in web servers |
| Availability | What are the single points of failure? | No redundancy on critical paths, no circuit breakers |
| Reliability | What happens when components disagree? | No idempotency for mutations, no data validation at boundaries |
| Performance | Where are the hot paths? What's the p99? | N+1 queries, synchronous chains of network calls |
