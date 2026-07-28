# Code Optimization — Decisions

---

## Refactor vs. Rewrite

| Signal | Recommendation |
|--------|---------------|
| Code works but is hard to change | Refactor |
| Structure is sound, tests exist | Refactor |
| Technology is obsolete | Consider rewrite |
| Team cannot understand the code at all | Consider rewrite |
| System > 3 months to rewrite | Strangler Fig |
| System < 1 month, clear boundaries | Rewrite may be viable |

**Rewrite estimation rule**: Take your estimate. Multiply by 3. If that exceeds 3 months, do not rewrite — use Strangler Fig.

**Risk score** (+1 each): >10k LOC, business logic untested, external integrations, team unfamiliar with domain, deadline pressure. Score ≤3: rewrite viable. Score 4+: incremental only.

---

## When to Optimize

```
OPTIMIZE NOW:
  - Users are complaining about speed
  - SLA is violated
  - Cost/resource budget exceeded
  - Bottleneck confirmed by profiling

OPTIMIZE SOON:
  - Performance trending down over weeks
  - Approaching capacity limit
  - New feature needs headroom

OPTIMIZE LATER:
  - Performance is acceptable
  - No measured data yet
  - System is actively changing

DO NOT OPTIMIZE:
  - "Might be slow someday"
  - "I know a faster way"
  - "Best practice says so"
  - No profiling data
```

**ROI test**: Hours spent optimizing < hours saved over 1 year.
`Requests/day × latency_saved_seconds × 365 / 3600 > dev_hours_spent`

---

## Abstraction Level (Rule of Three)

```
1st occurrence: Write it inline. Do not abstract.
2nd occurrence: Note the duplication. Still do not abstract.
3rd occurrence: NOW extract the pattern.

"Duplication is far cheaper than the wrong abstraction." — Sandi Metz
```

| Level | When |
|-------|------|
| Inline | Default. Always start here. |
| Extract function | 3+ uses, or logic > 10 lines |
| Extract class/module | Related functions share state |
| Define interface | Multiple implementations exist, or need to mock |
| Internal framework | Almost never — only for large stable patterns |

**Warning signs of wrong abstraction**: options list keeps growing; conditionals inside for "different cases"; callers working around it; no one can explain it. Inline it back.

---

## Technical Debt Prioritization

```
Category A — Fix now:
  Security vulnerabilities, data corruption risk,
  production outages, blocked deployments

Category B — Fix soon:
  Slowing developer velocity, flaky CI,
  performance degradation, hard onboarding

Category C — Fix when convenient:
  Duplication, missing tests, unclear naming

Category D — Maybe never:
  Style preferences, "I'd have done it differently",
  minor inconsistencies with no velocity impact
```

**Prioritization matrix**:

```
              High Impact   Low Impact
High Effort       B              D
Low Effort        A              C
```

**Budget**: 20% per sprint, every 4th sprint, or boy scout rule — pick one, stick with it. Debt register: ID, description, category, owner, created date. Review monthly. Never track Category D.
