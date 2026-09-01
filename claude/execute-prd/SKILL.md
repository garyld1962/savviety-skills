---
name: execute-prd
description: "Use when a written requirements source exists (PRD, RFC, prompt.md, spec file, or ADO/Linear ticket) and the user wants it planned and built — phrases like 'build this PRD', 'execute prompt.md', 'turn this RFC into a plan and run it'. Not for vague ideas (use superpowers:brainstorming) or when a validated plan already exists (use /execute-plan)."
---

# /execute-prd — PRD to Plan Compiler

Converts a requirements source into a plan conforming to
`_internal/plan-format`, validates it, and hands off to
`/execute-plan`. After the plan is written, the plan governs
execution; the PRD is used only for traceability.

## Workflow

1. **Load repo contract** — `CLAUDE.md ## Commands` per
   `_internal/repo-delivery`; missing → halt (same message as
   /execute-plan preflight gate 1).

2. **Load requirements source.**

   Resolution order:

   1. If `--ado <id>` or `--linear <id>` was supplied, invoke `/work-item`
      to fetch the ticket. `/work-item` returns the rendered markdown to
      stdout — it does **not** write to disk. **execute-prd** then
      persists that rendered markdown to
      `docs/plans/PRD-<source-slug>.md` (creating the directory if
      needed) so the rest of the flow has a stable file to reference.
      Extract title, description, acceptance criteria, and work-item type
      from the rendered markdown. The plan header carries
      `**Source:** ADO #<id> — <title>` (or `Linear <id> — <title>`).
      Reject if more than one of `<path>` / `--ado` / `--linear` is set.
   2. Otherwise, use the explicit `<path>` if provided.
   3. Otherwise, prefer `prompt.md`, `docs/plans/PRD.md`, `PRD.md`, then
      obvious RFC/spec files under `docs/`.

   If multiple plausible sources exist and none was named, pause and ask
   the operator which is canonical (interactive mode) or abort with a
   `plan-ambiguity` finding (autonomous mode).

   **Classify plan type.** Use `--type` if supplied. Otherwise infer
   from the requirements source:

   | Type | Signals |
   |---|---|
   | `bug` | "fix", "broken", error messages, stack traces; ADO/Linear `Bug` work-item type |
   | `feature` | "add", "implement", "create", new behaviour; ADO/Linear `User Story` / `Feature` types |
   | `refactor` | "rename", "extract", "move", "clean up", "restructure" with no new behaviour |
   | `infra` | "deploy", "config", "CI", "k8s", manifest paths, Dockerfiles, terraform |

   The classification governs plan shape in step 7. When the source
   spans types (e.g. a feature that includes a config change), pick the
   dominant type and represent the secondary as separate tasks.

3. **Audit current state** — invoke `/audit-existing`; never assume
   the source describes the repo accurately.

4. **Readiness gate.**

   Before extracting non-negotiables or drafting the plan, score the
   requirements source using the **Automated readiness check** in
   `_internal/aers-readiness/SKILL.md` (compute the points; verdict is
   `Ready` / `Partially ready` / `Not ready`). The audit from step 3 is
   an input — readiness is judged against *this repo*, not in the
   abstract.

   Behaviour by verdict:

   - **Ready (0–2 pts):** proceed silently to step 5.
   - **Partially ready (3–6 pts):**
     - Interactive operator → ask the gap questions inline (one at a
       time, via AskUserQuestion) and record answers as **closed
       decisions** in the generated plan (step 7). Do not invent
       answers. Suggest `/prd-validate` if the operator prefers a
       structured interview.
     - Autonomous → proceed and log the gap list in the plan as a
       known risk under `## Open Decisions`. Do not auto-invoke
       `/prd-validate`.
   - **Not ready (7+ pts):**
     - Interactive operator → halt; suggest `/prd-validate` to close
       gaps. Do not invoke it automatically — it's an interview, not a
       gate.
     - Autonomous → abort with a `requirements-incomplete` finding
       listing the rubric points and the unresolved high-risk
       ambiguities. Do not draft a plan against an unready PRD.

   The readiness gate's purpose is to refuse the most expensive failure
   mode this skill exists to prevent: a beautifully-validated plan built
   on top of an ambiguous PRD.

5. **Extract non-negotiables** — MUST/SHOULD requirements,
   invariants, acceptance criteria, forbidden behaviours; carry into
   task acceptance blocks and the final traceability task.

6. **Design-it-twice gate** — fire only when: type is
   feature/refactor AND the audit reveals a significant new
   architectural decision (service boundary, data model, public API,
   module interface) AND no closed decision resolves it. When it
   fires, invoke the Workflow tool with
   `scriptPath: <this-skill-dir>/workflows/design-it-twice.mjs`,
   `args: { decision, contextSummary, repoAuditPath }`. Record the
   returned recommendation as a Closed Decision in the plan,
   citing the rejected options.

   `<this-skill-dir>` is the `Base directory for this skill:` path
   printed when this skill loaded. The `.mjs` file is a Workflow-tool
   script, not a Node module: pass its absolute path as `scriptPath`
   and nothing else — do not run it with `node`, `import` it, or paste
   its contents into `script`. This step is the operator's opt-in to
   multi-agent orchestration; no further confirmation is needed. If
   the session has no Workflow tool, halt and say so — do not emulate
   the script with the Agent tool.

7. **Draft the plan** in the `_internal/plan-format` contract:
   frontmatter (slug/source_prd/intent/type), Closed Decisions,
   `## Task N:` sections each with the yaml metadata block
   (depends_on / write_scope / milestone_end) and mechanical
   `**Acceptance:**` bullets.

   **Shape the tasks by plan type** (from step 2):

   - **bug** — reproduce-with-failing-test → root-cause → minimal fix →
     regression tests → full-suite verify.
   - **feature** — interface/types → failing tests for each behaviour →
     implementation → integration → edge cases.
   - **refactor** — **characterization tests first** (capture current
     behaviour) → transform in small steps → verify existing +
     characterization tests still pass → clean up. Refactor plans without
     characterization tests will be flagged `unproved` by execute-plan's
     proof accounting; the plan must include them.
   - **infra** — config/manifest changes → apply to target env →
     smoke test end-to-end → documented rollback.

   **Plan Authoring Rules:**

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

   Dependency metadata replaces the old `## Waves` / lane tables
   entirely: contract-producing tasks are simply dependencies of their
   consumers, and single-owner surfaces appear in exactly one task's
   write_scope.

8. **Static plan checks** (author-side, before /validate-plan):
   every depends_on references an existing task id; no two
   dependency-independent tasks share a write_scope glob; every
   acceptance bullet is mechanical. Fix violations before validating.

9. **Validate** — run `/validate-plan`; fix-and-revalidate at most 3
   times, then surface the top blocking finding and ask the operator
   (escalate to readiness / manual override / abandon).

10. **Execute** — invoke `/execute-plan <plan-path>` with any
    pass-through flags.

## Things you must not do

- Do not skip `/audit-existing`. Greenfield assumptions on a populated
  repo are the most expensive failure mode this skill exists to prevent.
- Do not skip the readiness gate (step 4). Drafting a plan against
  an unready PRD is the second most expensive failure mode.
- Do not skip `/validate-plan`. A bad plan silently guessed through is
  the third most expensive failure mode.
- Do not draft and execute in one shot — the staged validation is the
  point.
- Do not loop on `/validate-plan` without bound. Three attempts then
  surface to the operator (see step 9).
- Do not invent product decisions to close ambiguity. Halt and ask.

## When NOT to Use

- A validated plan already exists — `/execute-plan` directly.
- One-or-two-file change — edit directly.
- The PRD is open-ended or the user wants to think interactively —
  `/prd-validate` or superpowers:brainstorming first.
