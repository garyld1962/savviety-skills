# Tech Debt Advisor — Patterns

---

## Cunningham's Quadrant

**When**: Assessing and communicating about any technical debt item.

```
              PRUDENT                RECKLESS
DELIBERATE  "Ship now, address    "No time for design"
             consequences later"   (no plan to fix)
             ✓ Valid tool          ✗ Creates danger

INADVERTENT "Now we know how      "What's layering?"
             we should have done   (doesn't know it's debt)
             it" — plan it         ✗ Usually unrecognized
             ✓ Addressable
```

Only Deliberate+Prudent and Inadvertent+Prudent debt is manageable. Reckless debt needs honesty first — call it what it is.

---

## Debt Interest Calculation

**When**: Prioritizing debt or building a case for stakeholders.

```
Development velocity interest:
  Clean module: feature takes 2 days
  Debt-laden module: same feature takes 5 days
  Interest = 3 dev-days per feature × 10 features/quarter = 30 dev-days/quarter

Bug rate interest:
  Clean: 1 bug/month × 4 hrs = 4 hrs/month
  Debt: 5 bugs/month × 4 hrs = 20 hrs/month
  Interest = 16 hrs/month

Break-even calculation:
  Paydown cost: 2 weeks (80 hrs)
  Monthly interest: 16 hrs
  Break-even: 5 months
  → If you'll touch this code for 5+ more months: pay it
  → If not: leave it
```

If you can't quantify interest, it might not be real debt. "I don't like it" is not interest.

---

## The 3-Question Filter

**When**: Evaluating any item on the debt backlog.

```
1. Are we actively working in this area?
   No → Deprioritize. Debt isn't costing much if nobody's in there.

2. Is the debt causing measurable problems?
   No → May be hindsight, not real debt. Remove from backlog.

3. Is paydown cost less than 6-month interest?
   No → Accept the debt. Schedule a trigger for when this changes.
   Yes → Schedule paydown.
```

---

## Opportunistic Payment

**When**: Working in an area that has debt — scoped improvement, not full cleanup.

```
Task: Add email notification to order flow.

Option A: Just add email (2 days) — fast but adds to the mess
Option B: Refactor first, then add (5 days) — clean but 2.5× longer
Option C: Add email, refactor the touched parts only (3 days) — balanced ✓

Rule: Improve the specific area you're working in.
      Leave the rest for when it's touched.
      Don't let cleanup exceed feature time.
```

---

## Debt Communication (Interest Payments Metaphor)

**When**: Asking for time to address debt, or explaining velocity slowdowns.

| Audience | Framing |
|---|---|
| Product manager | "Features in this area take 3× longer and have more bugs. Here are the options." |
| Executive | "We borrowed time to ship faster. Now we pay interest. Here's the ROI to refinance." |
| Finance | "Like a loan — faster to market, now paying interest. Here are our options." |

```
BAD:  "We need 2 weeks to clean up tech debt."
GOOD: "The order system takes 2 weeks per feature instead of 3 days.
       Spending 2 weeks now makes the next 5 features cost 1.5 weeks each
       instead of 10 weeks total."

BAD:  "We MUST refactor before adding features."
GOOD: "Option A: ship now, 3× cost on future features.
       Option B: 2-week investment, then normal speed.
       Option C: 2 extra days per feature, paid down in 3 months."
```

---

## The 20% Rule

**When**: Negotiating ongoing debt maintenance into the sprint cadence.

Allocate 20% of sprint capacity to debt payment — not as a "debt sprint" but as a sustained allocation. This keeps interest from compounding while maintaining feature velocity. Debt sprints are an antipattern (see sharp-edges.md): they concentrate risk, create a stop-start pattern, and never finish the backlog.

---

## Debt Inventory (Keep It Short)

**When**: Tracking debt items.

| Priority | Criteria | Action |
|---|---|---|
| Now | Critical+blocking, safety/security | This sprint |
| Opportunistic | Active area, measurable interest | When in area |
| Trigger-based | Moderate interest, not active | "When we touch X" note |
| Delete | No measurable interest, never touched | Remove from backlog |

**Rule**: Maximum 10-20 tracked items. Items older than 6 months untouched get deleted. A 300-item backlog is a graveyard, not a plan.
