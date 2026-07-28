# Code Quality — Disposition Criteria

## Disposition Table

| Finding | Default Disposition | Override Conditions |
|---------|--------------------|--------------------|
| Single-letter variable | Non-blocking | Loop counter (`i/j/k`), obvious lambda param |
| Boolean missing prefix | Non-blocking | Name is already unambiguous question (`active` on a toggle component) |
| Magic number | Non-blocking | Test file, config file, `/ 100`, `[0]` first element |
| Function >40 lines | Non-blocking | Pure transformation, sequential pipeline, generated code |
| Nesting depth >3 | Non-blocking | Already has a TODO or guard clause in PR |
| Function >4 params | Non-blocking | All params required with no logical grouping |
| Commented-out code | Non-blocking | Has ticket reference, clearly temporary |
| TODO without reference | Non-blocking | — |
| Negated boolean name | Non-blocking | — |
| `else` after `return` | Non-blocking | Symmetric branches, same length |
| Deep inheritance | Discussion | — |
| Dead public method | Discussion | Confirmed public API surface |
| Copy-paste duplication | Discussion | Third occurrence not yet reached |

## Blocking Findings

No checks in this skill produce blocking findings by default. Code quality issues reduce readability; they rarely cause production failures. Escalate to Blocking only if a naming lie is found that could cause callers to misuse the function (e.g., a function named `validate` that silently mutates state).

## Scope Rules

- **Apply to**: `src/`, `lib/`, `app/`, `components/`, `services/` — production source code
- **Skip**: `*.test.*`, `*.spec.*`, `__tests__/`, `migrations/`, generated files (`*.generated.*`, `dist/`, `build/`)
- **Language notes**: All checks are language-agnostic unless marked `[js]`/`[ts]`/`[py]`. Apply the concept even if the exact grep syntax doesn't match.

## Judgment Notes

A 45-line function that reads top-to-bottom with no branching is better than 9 five-line functions that require jumping to understand. Use the "new team member" test: would someone unfamiliar with this codebase understand the function's purpose in 30 seconds? If yes, don't flag it.

Magic number exceptions are narrow: if the number requires a reader to look elsewhere to understand its meaning, it's a magic number.

When in doubt on Tier 2, note the finding as Discussion rather than Non-blocking.
