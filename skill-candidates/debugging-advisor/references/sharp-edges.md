# Debugging Advisor — Sharp Edges

---

## "I Think I Know What It Is" (Skipping Observation)

**Severity**: Critical
**Situation**: You have a hunch. You start poking at the suspected location immediately, looking for evidence that confirms the theory. Two hours later, the bug was somewhere else entirely.

```
THE TRAP:
  Intuition says: "It's probably the auth middleware."
  You spend 2 hours in auth middleware.
  Bug was in the date formatting in the response serializer.

WHAT YOU SHOULD HAVE DONE:
  1. Observe the exact symptom (not your interpretation of it)
  2. Write down 3 candidate hypotheses
  3. Pick the most testable one (not the most likely-feeling one)
  4. Design an experiment to disprove it
```

**Fix**: Before touching any code, write down: "The symptom is exactly ___. My hypothesis is ___. I predict that if I do ___, I will see ___ if this hypothesis is correct." If you can't fill in the prediction, you don't have a hypothesis yet.

---

## Fixing Symptoms, Not Causes

**Severity**: High
**Situation**: Add a null check to prevent a crash. Crash gone. "Fixed." But WHY was it null? The null was produced upstream. Now you have a silent failure instead of a visible crash — which is worse.

```
WORKAROUND:  if (user?.name) { ... }     ← null check
FIX:         ensure user is never null   ← fix initialization
             (plus the null check as defense-in-depth)
```

**Fix**: Trace every bad value backward. Where was it produced? What produced the thing that produced it? Stop when you reach code that should have behaved differently. That's the root cause — fix it there first, then optionally add defensive checks downstream.

---

## Adding More Logging Without a Hypothesis

**Severity**: Medium
**Situation**: Something is wrong. Add logging everywhere. Redeploy. Sift through thousands of log lines. Still not sure what happened. Add more logging.

Logging without a hypothesis is noise generation. You're hoping the answer appears in the output rather than knowing what question you're asking.

**Fix**: Before adding any log, write the question: "I want to know if ___." Then add exactly one log that answers that question. If the answer is "yes": next hypothesis. If "no": ruled out, next hypothesis.

---

## Debugging on Production

**Severity**: High
**Situation**: Bug only happens in production. You SSH in. Start changing things. Run experiments directly on live data.

```
WHAT CAN GO WRONG:
  Experiment corrupts real user data
  Change causes cascade failure
  You forget to revert, inconsistency persists for days
  You add logging that exposes PII in log aggregators
```

**Fix**: Reproduce in staging with production-like data (anonymized). If you can't reproduce: add structured logging to production, deploy, let it happen again, analyze logs. Only touch production data as a last resort and with explicit rollback plan.

---

## Not Writing a Test After Finding the Bug

**Severity**: Medium
**Situation**: You found the bug. You fixed it. You move on. Six months later, someone's refactor reintroduces the same bug. It ships. The original investigation was wasted.

```
THE RULE:
  Every bug fix should be accompanied by a test that:
  1. Fails before the fix (proves you're testing the right thing)
  2. Passes after the fix (proves the fix works)
  3. Will fail again if the bug is reintroduced
```

**Fix**: Before merging any bug fix, write the regression test first. This also forces you to confirm your understanding of the root cause — if you can't write a test that reproduces it, you may not have actually fixed it.
