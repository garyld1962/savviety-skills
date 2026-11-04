# Execution proof and finding disposition

Use a unique run directory under the repo's configured `runs_root`, otherwise
`docs/runs/<plan-slug>/<UTC-run-id>/`. Respect an explicitly requested location.
The JSON is canonical; render the Markdown summary from the same data.

For assistant-written console output, apply
[the simplify output guidance](../../simplify/references/output.md). Lead with
the actual result, remaining risks or unverified behavior, and next action or
decision. Link the detailed report after explaining what matters. This wording
pass does not alter the JSON, audit tables, verdict rules, or required evidence.

Write `execution-report.json`, `execution-report.md`, and `disposition-log.md`.
JSON schema version 2 is the native contract; it is not wire-compatible with
the older Claude runtime's version 1. Record:

- `schema_version: 2`, `verdict`, `plan_file`, `plan_sha` (SHA-256), `base_sha`,
  `head_sha` (final code commit), `code_committed: true`, `branch`, `mode`, and `required_gates`;
- `tasks`: each plan ID, `status` (`done`, `blocked`, `pending`), changed files,
  commit if any, and `proof` items with `criterion`, `status`, `evidence`, and
  `verified_sha`; include every acceptance bullet, not just one check per task;
- `gates`: name, `status` (`passed`, `failed`, `unavailable`, `skipped`),
  `head_sha`, and `evidence`; alignment also has `all_tasks_implemented`;
- `findings`: stable ID, severity, status, evidence, rationale, plus fix
  verification / follow-up / user authorization as appropriate;
- `deviations`, `retry_stats`, `open_questions`, and `started_at` / `ended_at`.

Required gates always include `checkpoint`, `code-review`, `alignment`. Add
`professional-review` and `adversarial-review` when the plan, repository or
execution contract requires them. Keep the declaration made in preflight;
do not remove a failed gate to make the report validate.

## Terminal statuses

| Status | Evidence needed | Completion effect |
|---|---|---|
| `fixed` | `verification` from a check/review after the fix | Closed |
| `disagree-with-evidence` | `rationale` and `verification` supporting dismissal | Closed only after review agrees or recorded human arbitration |
| `defer` | `follow_up` with owner and issue/action | WARN for minor/nit; blocks critical/major |
| `accepted-risk` | `authorization` naming the user's decision and `rationale` | WARN; never inferred from silence |
| `open` | Unresolved finding | FAIL at the final boundary, at any severity |

Do not use ambiguous `resolved` to hide how a finding ended. A deviation records
what changed, why, its evidence, and whether the existing request or a specific
user decision authorized it. Never auto-accept solely from a category such as
lockfile or formatting. Unresolved deviations block; approved deviations warn.

`PASS` requires all tasks proved, all required gates passed on the final head,
alignment true, and every finding fixed or dismissed with evidence. `WARN`
requires the same completed work/gates but has explicit accepted risks, minor
deferrals, approved deviations, optional skipped gates or recorded limitations.
`FAIL` covers blocked/unproved tasks, any open finding, missing/failed required
gate, false alignment, exhausted execution, or unresolved material questions.
Lack of an environment for a required test is FAIL, not a successful completion.

Version 2 certifies committed code. Check that all scoped code changes are committed
before setting code_committed; run artifacts themselves may remain uncommitted.
If the user explicitly requests no commits, preserve that choice and return a draft
verification summary with the uncommitted changes identified. Do not emit an execution
PASS/WARN tied to an older commit; this contract's certification remains unavailable.

Run the sibling `scripts/validate_report.py <report.json> --plan <plan.md>` before
publishing a success claim. It verifies proof coverage and final-head gate
consistency, not the truth of fabricated evidence: inspect the referenced output.

## Postmortem and durable decisions

On WARN/FAIL, budget exhaustion, escalation or a workflow defect, write
`postmortem.md` and `postmortem.json`: timeline, symptoms, root cause with
evidence, impact, attempts, recovery, and concrete prevention actions. Identify
the reusable target (plan contract, command setup, disposition, review trigger,
decision rule, skill instructions, or tests); do not reduce every failure to
"agent error". Append a run reference to the existing postmortem index without
overwriting it. Propose shared-skill changes unless their application is already
authorized. Record durable architectural decisions in the repo's established
decision directory and update its index while preserving existing entries.
