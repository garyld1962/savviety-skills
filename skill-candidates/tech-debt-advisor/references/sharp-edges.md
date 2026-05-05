# Tech Debt Advisor — Sharp Edges

---

## Paying Debt on Dead Code

**Severity**: High
**Situation**: Module sits untouched for 2 years. Team adds it to the debt backlog and periodically debates when to "pay it down."

```
2 years since last change.
0 bugs from this code this year.
0 features planned that touch it.
Interest paid: $0

Paydown cost: 2 weeks
ROI: negative
```

**Fix**: Remove from backlog. Document as trigger-based: "address when we need to change this." Spending time on non-changing code has zero ROI.

---

## The Refactor Sprint Antipattern

**Severity**: High
**Situation**: Team allocates a full sprint to "pay down tech debt." Two weeks pass. The backlog barely shrinks. Risk is concentrated. Output is unmeasurable. The next "debt sprint" is scheduled for six months from now.

```
Signals:
- "We'll do a cleanup sprint next quarter"
- Sprint has no clear exit criteria
- Large PRs touching unrelated areas
- Velocity dip with no measurable improvement afterward
```

**Fix**: 20% continuous allocation instead. Debt paid as part of normal work is easier to review, lower risk, and compounds over time. Debt sprints concentrate risk and create a stop-start cycle that never catches up.

---

## The Infinite Debt Backlog

**Severity**: Medium
**Situation**: Team created a backlog to track all code smells. It now has 300 items. Nobody looks at it. It creates guilt without action.

```
300-item debt backlog:
  Items from 3 years ago: still there
  Items addressed this quarter: 2
  Team morale impact: negative
  Actual debt paid: negligible
```

**Fix**: Keep the list under 20 items. Delete anything untouched for 6 months. Replace low-priority items with area-specific notes: "when we work in module X, address Y." A backlog that never shrinks is not management — it's avoidance.

---

## Old Code ≠ Debt

**Severity**: High
**Situation**: Developer looks at 5-year-old code and says "this is all tech debt, we need to rewrite it." The code works, is stable, and handles edge cases nobody else remembers.

```
"This code is so old."         ← not a debt measurement
"Nobody writes it this way."   ← not a debt measurement
"Every feature here takes 3×." ← actual interest
"5 bugs/month from this area." ← actual interest
```

**Fix**: Define debt by impact, not aesthetics. Age is not debt. Code that works, handles edge cases, and is rarely touched is an asset. Only track it as debt if you can answer: how much is this costing us per sprint?

---

## Treating All Debt Equally

**Severity**: Medium
**Situation**: Backlog lists "no tests in auth module" alongside "inconsistent variable names" with no priority difference. Team works on variable names first because it's easier.

```
Tier A (ignored): No tests in auth — security exposure
Tier D (addressed): Variable naming — zero user impact

Wrong order → real risk unaddressed, effort wasted on aesthetics.
```

**Fix**: Categorize debt by tier before tracking (see decisions.md). Critical+security issues are always Tier A regardless of age or aesthetics. Tier D items should rarely stay in the backlog.

---

## Boy Scout Scope Creep

**Severity**: High
**Situation**: Task is "add validation to user form." Developer notices debt in the user module. Three weeks later: 15,000-line PR across 40 files. Validation still isn't done.

```
"While I'm here" + no timebox = scope creep.
Each improvement looks small. Together they exceed the original task.
If something breaks: is it the feature or the cleanup? Nobody knows.
```

**Fix**: Improve only the specific area you're working in for your task. Timebox opportunistic improvements to a maximum of 20% of task time. Everything else goes into the backlog or area-specific notes — not into the current PR.
