# Debugging Advisor — Patterns

---

## The Scientific Method Loop

The foundation. Apply after 10 minutes of ad-hoc hunting fails.

```
1. OBSERVE   — What exactly is the symptom? (not your theory, the actual output)
2. HYPOTHESIZE — What is the most likely cause? (pick one, the most testable)
3. PREDICT   — If this hypothesis is true, what should I see when I do X?
4. EXPERIMENT — Do X. Observe the result.
5. ANALYZE   — Did the prediction hold?
               Yes → hypothesis supported, continue
               No → hypothesis rejected, learn from what you saw
6. REPEAT    — New hypothesis informed by what you learned
```

The key discipline: form the prediction before running the experiment. If you can't predict what you'll see, you don't have a hypothesis — you have a guess.

Example:
```
OBSERVE: API returns 500 on POST /orders, GET works fine.

HYPOTHESIS: Request body validation is rejecting the payload.
PREDICT: If true, logging before validation will show invalid data.
EXPERIMENT: Add log, reproduce.
RESULT: Log shows valid data. Validation passes.
CONCLUSION: Not validation. (But now you know more.)

HYPOTHESIS: Database insert is failing.
PREDICT: If true, database error logs will show a constraint violation.
EXPERIMENT: Check DB logs during reproduction.
RESULT: "duplicate key constraint violation on email"
ROOT CAUSE: Missing upsert logic — plain INSERT fails when email exists.
```

---

## Binary Search (Wolf Fence)

When the bug is somewhere in a large pipeline, commit history, or codebase.

**Concept**: Put a fence across the middle. Check which side has the bug. Discard the other half. Repeat.

```python
# Bug: wrong output from a pipeline
def process(data):
    a = step_one(data)
    b = step_two(a)
    c = step_three(b)   # ← add checkpoint here first
    d = step_four(c)
    return d

# Checkpoint at the midpoint:
    c = step_three(b)
    print(f"CHECKPOINT: {c}")  # correct? bug is in step_four
                               # wrong? bug is in step_one/two/three
```

**For commit history** — `git bisect`:
```bash
git bisect start
git bisect bad HEAD        # current is broken
git bisect good abc123     # this commit worked
# Git checks out midpoint. Test, then:
git bisect good            # or: git bisect bad
# Repeat 6–7 times. Git identifies the exact guilty commit.
```

---

## Rubber Duck / Articulate First

Before running any experiment, describe the problem out loud (or in writing). Include:
1. What you expected to happen
2. What actually happened
3. What you've already tried
4. Why you ruled out each thing you tried

This forces you to confront your assumptions. Often the bug becomes obvious mid-sentence — not because someone answered, but because articulating the problem requires logical clarity that reveals the gap.

---

## Minimal Reproduction

When the bug is buried in a complex system, strip it down.

Goal: smallest possible code that still reproduces the bug.

```
Start with:          Remove (if bug persists):
Full app             → authentication
Real database        → replace with in-memory
All configuration    → hardcode values
Network services     → stub with constants
Related routes       → delete everything else
```

Stop removing when the next removal makes the bug disappear. What you removed last is likely load-bearing.

Benefits: Forces identification of actual dependencies. Makes the bug visible (less noise). Creates the regression test.

---

## Time-Travel Debugging

When "it was working yesterday":

```bash
# Code changes:
git log --oneline --since="2 days ago"
git diff HEAD~5         # what changed recently?

# Dependency changes:
git log -p package-lock.json   # when did deps change?

# Data changes: check created_at / updated_at on affected records
# Infrastructure: check deploy logs for the window when it broke
```

The question is never "why is it broken?" — it's "what changed since it worked?" Something always changed. Find the change.

---

## Strategic Print Debugging

Prints are not a lesser tool. They're flexible, portable, and don't affect timing.

```python
# BAD — random prints with no question
print("here")
print(data)  # massive dump

# GOOD — answer a specific question
# Question: "Is this function being called?"
print(f">>> process_order called: id={order.id}")

# Question: "Which branch runs?"
if condition_a:
    print(">>> branch A")
elif condition_b:
    print(">>> branch B")

# Question: "What changed?"
print(f">>> BEFORE: {state}")
result = transform(state)
print(f">>> AFTER: {result}")
```

Use a distinctive prefix (`>>>`) so you can grep your own prints in noisy output. Remove them after — they're investigation tools, not documentation.
