# Refactoring Advisor — Sharp Edges

---

## The Big Rewrite

**Severity**: Critical
**Situation**: Team decides to rewrite the legacy system "properly this time."

```
70% fail or are abandoned.
Average: 3× longer than estimated.
Month 4: morale destroyed, old system still accumulating patches the rewrite lacks.
Month 18: rewrite abandoned at 60% complete.
```

**Fix**: Strangler Fig. Replace one module at a time. Old system stays running throughout. Each phase is independently deployable. Exception: system is < 1 month to rewrite, team fully understands the domain, clear boundaries.

---

## Refactoring Without Tests

**Severity**: Critical
**Situation**: Code has no tests. Developer refactors carefully and ships. A week later, production breaks on an edge case nobody noticed.

```python
# Without tests, "preserving behavior" is hope.
# Write characterization tests first:
def test_characterization():
    assert calculate_discount(100, "SUMMER") == 15   # captured from actual run
    assert calculate_discount(-50, "SUMMER") == 0    # found this edge case!
```

**Fix**: No tests → no refactor. "I don't have time for tests" means "I don't have time to refactor." The only exception is IDE automated refactorings (rename, extract) which are mechanically safe.

---

## Mixed Commits: Refactoring + Feature Together

**Severity**: High
**Situation**: Developer adds a feature and "while there" cleans up the code. Something breaks. Nobody can tell if it's the feature or the cleanup.

```
Signal: "Refactoring" PR with new or modified test assertions.
→ Real refactoring never changes test assertions — behavior is preserved.
→ If tests changed, it's not refactoring.
```

**Fix**: Separate commits, always. Refactor first (tests unchanged), then feature (tests change). For large refactors: separate PR, merged before feature work starts.

---

## Premature Abstraction During Refactoring

**Severity**: High
**Situation**: Developer creates IFoo + FooImpl, factory classes, and generic interfaces "for flexibility" during a refactoring pass. Code is longer, harder to navigate, flexibility never used.

```
Before: OrderService (direct)
After: IOrderService + OrderServiceImpl + OrderServiceFactory
Implementations: 1
Times flexibility was used: 0
```

**Fix**: Refactor toward simplicity, not "proper architecture." Add abstraction only when you feel concrete pain. One implementation = no interface needed. YAGNI applies to refactoring too.

---

## Behavior Change Disguised as Refactoring

**Severity**: High
**Situation**: Developer "refactors" a function but silently changes how an edge case is handled. Bug is blamed on refactoring; root cause is the behavior change that slipped through without review.

```
Refactoring: change HOW code works, tests stay identical.
Behavior change: change WHAT code does, new/modified tests needed.

If your "refactoring" requires updating test assertions → not refactoring.
```

**Fix**: When you find a bug during refactoring, do not fix it in the same commit. File it, note it, fix it separately with a new test.

---

## Cleaning "Weird" Code Without Understanding Why

**Severity**: Medium
**Situation**: Developer removes code that "looks wrong." A month later, a vendor quirk, a regulatory edge case, or a customer-specific behavior breaks.

```
Legacy code often looks wrong and is right.
It accumulated fixes for real-world problems you haven't encountered yet.
```

**Fix**: Before removing anything that looks odd, ask: why might this have been written this way? Check git blame and linked issues. Write a characterization test capturing the behavior. Add a comment explaining the reason when you find it.

---

## Big Bang Refactoring (The Massive PR)

**Severity**: High
**Situation**: Three weeks of refactoring produces a 3,000-line PR touching 50 files. Review is cursory. Bugs trickle in for weeks after merge.

```
Signal: PR > 400 lines, touches > 10 files, "part 1 of 5" framing.
Each line has a small error probability. Multiply by thousands — errors guaranteed.
```

**Fix**: One refactoring type per PR (all renames, then all extractions). One area per PR. Each PR reviewable in one sitting. Use the Mikado Method to map dependencies and work leaf-to-root.
