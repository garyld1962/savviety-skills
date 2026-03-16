# Severity rubric

Use these severities exactly:

- **Blocker**: Likely to cause production incident, data loss, broken builds, or a serious security issue.
- **High**: Serious bug risk, security weakness, major reliability/perf issue, hard-to-debug behavior.
- **Medium**: Real issue but with mitigations; maintainability/correctness risk in edge cases.
- **Low**: Minor maintainability/clarity improvement; should not block merges.
- **Info**: Observation, question, or suggestion without strong evidence.

Confidence:
- 0.90–1.00: Clear evidence in code
- 0.70–0.89: Strong signals, some assumptions
- 0.50–0.69: Plausible, needs confirmation
- <0.50: Don’t emit as a finding
