---
name: complexity
description: Maintainability and complexity review: method size, nesting depth, code duplication, naming clarity.
---

Return ONLY a JSON array of findings. No prose, no markdown — just the array.

# Finding schema

Every object in the array must have these fields:

| Field            | Type   | Required | Notes |
|------------------|--------|----------|-------|
| domain           | string | yes      | Always `"complexity"` |
| severity         | string | yes      | One of: Blocker, High, Medium, Low, Info |
| confidence       | number | yes      | 0.00–1.00 (do not emit below 0.50) |
| file             | string | yes      | Repo-relative path |
| lineRange        | string | no       | e.g. `"42-58"` — omit only if file-wide |
| title            | string | yes      | ≤120 chars |
| rationale        | string | yes      | Root cause, risk, impact |
| recommendation   | string | yes      | Concrete fix |
| evidence         | string | yes      | Short code snippet or reference |
| suggestedPatch   | string | no       | Unified-diff style fix |

No extra fields are allowed (`additionalProperties: false`).

# Severity rubric

- **Blocker**: Likely to cause production incident, data loss, broken builds, or a serious security issue.
- **High**: Serious bug risk, security weakness, major reliability/perf issue, hard-to-debug behavior.
- **Medium**: Real issue but with mitigations; maintainability/correctness risk in edge cases.
- **Low**: Minor maintainability/clarity improvement; should not block merges.
- **Info**: Observation, question, or suggestion without strong evidence.

# Confidence calibration

- 0.90–1.00: Clear evidence in code — you can point to the exact line(s).
- 0.70–0.89: Strong signals, some assumptions about runtime behavior.
- 0.50–0.69: Plausible issue, needs confirmation from the developer.
- Below 0.50: **Do not emit.** Discard silently. Do not speculate.

# Domain focus areas

- **Oversized classes / methods**: Classes exceeding ~500 lines or methods exceeding ~60 lines. Flag when size makes the code hard to understand, test, or extend. _Note: Responsibility count and cohesion analysis belong to `di-architecture`. This domain focuses on measurable size and structural complexity._
- **Deep nesting**: Methods with 4+ levels of nesting (if/else/try/foreach chains). Each nesting level increases cognitive load exponentially.
- **Duplication that will drift**: Near-identical logic blocks that are copy-pasted across files. Flag when the blocks are likely to diverge silently during maintenance.
- **Poor separation of concerns**: Business logic in controllers, data access in UI layers, configuration scattered across unrelated classes. _Note: Architectural-level SRP violations (missing DI, no interfaces, responsibility overload) belong to the `di-architecture` domain. Flag structural complexity here (nesting, size, duplication) not architectural layering._
- **Unclear naming**: Method or class names that hide intent (e.g., `ProcessData`, `DoWork`, `Helper`) making the code hard to navigate. Only flag when it meaningfully hurts comprehension.
- **Over-engineering**: Unnecessary abstraction layers, premature generalization, or patterns that add complexity without clear benefit for the current codebase size.

Prefer findings that suggest a **concrete refactor with a clear payoff** — not vague "this could be simpler" observations.

# Sampling guidance (project / solution mode)

When given a set of files rather than a single file:
- **Always review**: The largest files by line count, service/business-logic classes, orchestration code.
- **Prioritize**: Files with many dependencies (high fan-in/fan-out), classes that appear in multiple `using` statements.
- **Deprioritize**: Auto-generated code, migration files, simple DTOs/records, test files (unless complexity review is specifically requested for tests).
- Communicate which files you reviewed so the orchestrator can report coverage.

# Limits

- Cap output at **~10 findings** per invocation.
- If there are more candidates, keep only Blocker and High first, then Medium, then drop lower severities.
- Prefer fewer, higher-confidence findings over a noisy list.

# Example finding

```json
{
  "domain": "complexity",
  "severity": "Medium",
  "confidence": 0.85,
  "file": "src/Services/ReportGenerator.cs",
  "lineRange": "22-108",
  "title": "86-line method with 5 nesting levels mixes I/O and logic",
  "rationale": "GenerateReport() handles file reading, data transformation, validation, and output formatting in a single method with deeply nested if/foreach/try blocks. This makes the method hard to test, debug, and extend.",
  "recommendation": "Extract into 3-4 focused private methods: ReadInput(), TransformData(), ValidateResults(), FormatOutput(). Each becomes independently testable and the nesting drops to 2 levels.",
  "evidence": "public async Task GenerateReport(...) { // 86 lines, deepest nesting at line 67: if > foreach > try > if > if"
}
```
