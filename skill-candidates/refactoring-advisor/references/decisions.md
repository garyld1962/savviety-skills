# Refactoring Advisor — Decisions

---

## Refactor vs Rewrite

| Factor | Refactor | Rewrite |
|---|---|---|
| System size | Any | < 1 month to rewrite |
| Domain understanding | Team knows it | Team fully understands domain |
| Boundaries | Can be incrementally improved | System is isolated, clear boundaries |
| Tests exist? | Not required (write characterization) | Required — you'll reintroduce bugs |
| Default | **Always start here** | Only when all three rewrite conditions are met |

**The rule**: 70% of rewrites fail or are abandoned. Average 3× longer than estimated. Strangler Fig first — always.

---

## When to Add Tests vs Trust Existing Coverage

```
Has tests that run and pass?
├── Yes → Are they characterization-level (cover edge cases)?
│   ├── Yes → Proceed with refactoring cycle
│   └── No → Add edge case coverage first for areas you'll touch
└── No → Write characterization tests before touching anything
         └── No time for tests = no time to refactor (skip it)
```

IDE automated refactorings (rename, extract method) are the only exception — they are mechanically proven safe. Use them without tests only for mechanical operations.

---

## How to Timebox a Refactor

Before starting, answer three questions:
1. **What is the goal?** (One specific improvement, named)
2. **What is done?** (Exit condition you can verify)
3. **What is the time limit?** (Stop when reached, even if not perfect)

| Scope | Timebox |
|---|---|
| Extract method / rename | 30 min |
| Refactor one class | Half day |
| Refactor one module | 1 sprint |
| Replace subsystem (Strangler Fig) | Multiple sprints, each independently shippable |

If you're still refactoring at the limit, ship what's done and create a follow-up task. Do not merge open-ended refactoring.

---

## When to Stop

Stop refactoring when any of these are true:

- The goal is met — the specific improvement is done
- Tests are failing and you can't see why (undo, restart smaller)
- The next extraction doesn't have a clear name (you've hit natural size)
- You're adding abstraction "just in case" — that's a new feature, not refactoring
- Scope has grown beyond the original goal — ship what's done, log the rest

**Perfect is the enemy of shipped.** "Good enough" code you can deliver is worth more than ideal code still in progress.

---

## Separating Refactoring from Feature Work

The test: Would tests change?
- **Refactoring only**: Tests run the same, behavior identical. Separate commit.
- **Feature work**: Tests change to cover new behavior. Separate commit.
- **Both in one PR**: You can't tell what broke. This is a debugging nightmare.

| Rule | Rationale |
|---|---|
| Separate commits | Git blame works; rollback is surgical |
| Separate PRs for large changes | Review is possible |
| Refactor first, then feature | Clean base means feature bugs are feature bugs |
| Never refactor during crisis | Minimal fix under pressure; refactor after |
