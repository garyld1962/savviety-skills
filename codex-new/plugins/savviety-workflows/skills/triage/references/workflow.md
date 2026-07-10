# Triage Workflow

Use this for bug investigation and root cause analysis.

## Steps

1. Restate the symptom and expected behavior.
2. Collect repro steps, logs, stack traces, recent changes, and environment.
3. Form hypotheses tied to code paths.
4. Inspect code and tests with `rg` and targeted reads.
5. Reproduce or explain why reproduction is unavailable.
6. Identify root cause, blast radius, and minimal fix options.
7. Recommend verification.

Separate evidence from guesses. Mark confidence explicitly when evidence is incomplete.

