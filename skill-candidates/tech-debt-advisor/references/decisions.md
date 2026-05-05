# Tech Debt Advisor — Decisions

---

## Pay Debt vs Ship Features

Matrix: stability × change frequency

| Code stability | Change frequency | Action |
|---|---|---|
| Stable, rarely touched | Low | Leave it. No interest, no paydown. |
| Stable, rarely touched | High (new features planned) | Pay before the next feature touches it |
| Unstable, buggy | Low | Minimal stabilization only |
| Unstable, buggy | High | Pay down now — interest compounds fast |

**Default rule**: Pay debt when you're changing the code anyway. Don't pay debt on code that doesn't change.

---

## Debt Category Tiers

Not all debt is equal. Prioritize by risk × frequency.

| Tier | Type | Examples | Action |
|---|---|---|---|
| A | Security / data integrity | No auth tests, unvalidated inputs, race conditions | Pay immediately |
| B | Velocity-blocking | God class blocking 3 teams, no tests in high-change module | Pay this quarter |
| C | Slows development | Messy but workable, low-change module | Opportunistic |
| D | Aesthetic / hindsight | "I'd write this differently today" | Probably never pay |

Tier D items should be deleted from the backlog unless they cross into C when the area becomes active.

---

## When NOT to Pay Debt

| Situation | Reasoning |
|---|---|
| Code is stable and rarely touched | No interest accruing; paydown has zero ROI |
| Rewrite risk exceeds debt risk | Old code has institutional knowledge; rewrite reintroduces bugs |
| Break-even is > 12 months out | Capital is better deployed elsewhere |
| System is being deprecated | Debt dies with the system |
| You're in a production crisis | Minimal fix only; refactor after |

**The contrarian rule**: Never pay debt on code that doesn't change. It's not costing you anything.

---

## When to Take on Debt Deliberately

Valid reasons (Deliberate+Prudent quadrant only):
- Time-to-market pressure with real, quantified business value
- Prototype to validate before investing in quality
- Short-lived code that will be replaced
- Learning phase: build to understand the problem before building right

Required: you know specifically what's compromised, and you have an explicit plan (even if "never").

---

## Stakeholder Communication Flow

```
Velocity slowdown noticed?
└─ Quantify interest first (hours/sprint, bug rate)
   └─ Frame as investment decision, not complaint
      └─ Present three options (ship as-is / pay now / incremental)
         └─ Let them choose with full cost information
```

Never: "We have tech debt." Always: "Here's what it's costing us and here are the trade-offs."

---

## Debt Sprint vs Continuous Allocation

| Approach | Risk | Effectiveness |
|---|---|---|
| "Debt sprint" (periodic dedicated cleanup) | High — concentrated risk, hard to review, stop-start | Low — backlog never shrinks |
| 20% continuous allocation | Low — small changes, easy review | High — sustainable, visible progress |
| Opportunistic only (no allocation) | Medium — depends on discipline | Medium — can work with strong culture |

**Avoid debt sprints.** They feel productive and deliver concentrated risk with unmeasurable output. A 2-week "cleanup sprint" with no clear exit criteria is scope creep with a planning name.
