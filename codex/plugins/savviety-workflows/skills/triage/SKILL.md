---
name: triage
description: "Investigate a bug from reproduction through root cause and recommended next step. Produces a structured report and does not write fixes."
---

# Triage

Read `references/workflow.md` for source workflow. `references/legacy/` is archival only.

## Workflow

1. Capture symptoms, expected behavior, observed behavior, and reproduction.
2. Search code, logs, tests, and recent changes.
3. Identify root cause or narrow hypotheses.
4. Recommend fix, rollback, test, or deeper investigation.
5. Do not edit files unless the user changes the task from triage to fix.
