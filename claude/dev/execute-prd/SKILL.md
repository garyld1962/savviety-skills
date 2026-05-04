---
name: execute-prd
description: "Read a PRD, prompt, RFC, or requirements document; audit the current repo; create a validated execution plan optimized for LLM code generation; embed a parallel-agent execution map; and then execute that plan as the governing source of truth. Use for requests like '/execute prd', 'execute prompt.md', 'build this PRD', 'turn this RFC into an execution plan and run it', or when no implementation plan exists yet."
---

# /execute-prd — PRD to Plan to Execution

**Purpose:** convert a requirements source into a mechanically verifiable
execution plan, optimize it for safe LLM execution, validate it, then
hand off to `/execute-plan`. After the plan is written, the plan
governs execution.

## When to Use

- A PRD, prompt, RFC, or requirements document exists but no
  implementation plan does.
- The user says "build this PRD" or "execute prompt.md" or "turn this
  RFC into a plan and run it."

## When NOT to Use

- A validated plan already exists — invoke `/execute-plan` directly.
- The change is one or two files — make the edit directly.
- The PRD is incomplete or open-ended — close it before planning.

## Arguments

| Argument | Description |
|---|---|
| `<path>` | Path to the requirements source (optional; if omitted, prefers `prompt.md`, `docs/plans/PRD.md`, `PRD.md`, then obvious RFC/spec files under `docs/`). |
| `--plan-path=<path>` | Where to write the generated plan. Default: `docs/plans/execute-plan-<source-slug>.md`. |
| `--parallel=<auto\|sequential>` | Force a parallel mode for the generated plan. Default: `auto` (let `/parallel-optimization` decide). |
| Pass-through | Any flag not recognised here is forwarded to `/execute-plan` (e.g. `--interactive=no`, `--adversarial=always`). |

## Workflow

### 1. Load repo contract

Read `CLAUDE.md` and the `## Commands` delivery schema. If the command
contract is missing, halt with the same failure used by `/execute-plan`:

```
Repo missing required CLAUDE.md ## Commands section.
See _rubrics/repo-delivery for the schema.
```

### 2. Load requirements source

Use the explicit path if provided. Otherwise prefer `prompt.md`,
`docs/plans/PRD.md`, `PRD.md`, then obvious RFC/spec files under
`docs/`.

If multiple plausible sources exist and none was named, pause and ask
the operator which is canonical (interactive mode) or abort with a
`plan-ambiguity` finding (autonomous mode).

### 3. Audit current state

Invoke `/audit-existing`. Determine whether the repo is greenfield,
partially implemented, or mature. Do not assume the source describes
current state accurately. Summarise existing packages, implemented
surfaces, missing pieces, duplicated contracts/constants, and relevant
tests before drafting the plan.

### 4. Extract non-negotiables

From the requirements source, list explicit MUST/SHOULD requirements,
invariants, acceptance criteria, forbidden behaviours, command
requirements, and final reporting requirements. Carry these into plan
tasks or final traceability checks.

### 5. Draft the plan

Create the plan at the configured path with closed decisions,
milestones, discrete tasks, and mechanical acceptance criteria.

### 6. Run /parallel-optimization

Embed its output as `## Parallel Execution` in the plan. If parallelism
is unsafe or `--parallel=sequential` was set, set `Mode: sequential` and
explain why.

### 7. Validate

Run `/validate-plan` against the generated plan. If it fails, fix the
plan and revalidate; do not execute a failing plan.

### 8. Execute

Invoke `/execute-plan <generated-plan>` with any pass-through flags.
Use the generated plan as the sole execution authority.

## Plan Authoring Rules

- Make every task independently understandable, with explicit
  file/package ownership.
- Put shared contracts, schemas, generated clients, and root workspace
  setup before consumers.
- Use package/module ownership so worker write scopes are disjoint
  where possible.
- Keep root manifests, lockfiles, shared exports, migrations, and
  public API contracts single-owner.
- Include focused verification commands per task or lane, plus final
  repo gates.
- Preserve all source acceptance criteria and non-negotiables; add
  tests before implementation when a task names behaviour not currently
  covered.
- Prefer contract-first tasks: shared public types/constants, API
  response mapping, generated clients, schemas, and migrations should
  precede consumers.
- Require explicit JSON/runtime boundary mapping where server values
  differ from wire values, such as `Date` objects becoming ISO strings.
- Record open product decisions as closed decisions only when the PRD
  or user has resolved them. Otherwise include a clear question and
  stop before execution.

## Generated Plan Minimum Structure

The plan must include:

- YAML frontmatter with `slug`, `source_prd`, and `intent`.
- H1 title.
- `## Closed Decisions` when product or technical choices are fixed.
- One or more `## Milestone:` sections.
- Numbered `## Task N:` sections.
- For each task: concrete description and `**Acceptance:**` bullets
  that can exit 0 or be directly observed.
- `## Parallel Execution` using the format from
  `/parallel-optimization`.
- Final verification task with the repo's declared lint/build/test
  commands.
- Final traceability task mapping source requirements and
  non-negotiables to implementation files and verification.

## Execution Boundary

Once validation passes, do not keep using the PRD as the active
instruction source for implementation choices. Use the PRD only for
traceability checks. If execution reveals a mismatch between PRD and
plan, halt as a `plan-ambiguity` or `plan-deviation` instead of
silently changing scope.

## Things you must not do

- Do not skip `/audit-existing`. Greenfield assumptions on a populated
  repo are the most expensive failure mode this skill exists to prevent.
- Do not skip `/validate-plan`. A bad plan silently guessed through is
  the second most expensive failure mode.
- Do not draft and execute in one shot — the staged validation is the
  point.
- Do not invent product decisions to close ambiguity. Halt and ask.
