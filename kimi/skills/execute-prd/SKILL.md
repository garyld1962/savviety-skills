---
name: execute-prd
description: Use when a written requirements source exists (PRD, RFC, prompt.md, spec
  file, or ADO/Linear ticket) and the user wants it planned and built — phrases like
  'build this PRD', 'execute prompt.md', 'turn this RFC into a plan and run it'. Not
  for vague ideas (use superpowers:brainstorming) or when a validated plan already
  exists (use /execute-plan).
whenToUse: Use when a written requirements source exists (PRD, RFC, prompt.md, spec
  file, or ADO/Linear ticket) and the user wants it planned and built — phrases like
  'build this PRD', 'execute prompt.md', 'turn this RFC into a plan and run it'. Not
  for vague ideas (use superpowers:brainstorming) or when a validated plan already
  exists (use /execute-plan).
type: flow
disableModelInvocation: false
arguments:
- source
---


# /skill:execute-prd — PRD to Plan Compiler

Converts a requirements source into a plan conforming to
`_internal/plan-format`, validates it, and hands off to
`/skill:execute-plan`. After the plan is written, the plan governs
execution; the PRD is used only for traceability.

Before the first user update, read [simplify](../simplify/SKILL.md). Apply its
output guidance to every assistant-written progress update, readiness or plan
summary, blocker, decision request, and handoff. Explain the actual gap and next
action before internal scores or labels. Keep technical artifacts unchanged.

## Arguments

- `<path>` — path to the requirements source. If not provided and no
  ticket flag is set, resolve it by the order in step 2.
- `--ado <id>` — fetch the requirements source from Azure DevOps via
  `/skill:work-item` instead of a file.
- `--linear <id>` — fetch the requirements source from Linear via
  `/skill:work-item` instead of a file.
- `--type <bug|feature|refactor|infra>` — force the plan type instead of
  inferring it in step 2.
- Pass-through flags — `--force`, `--accept-risk <category>`, and
  `--adversarial <auto|always|never>` are forwarded verbatim to
  `/skill:execute-plan` in step 10.

At most one of `<path>` / `--ado` / `--linear` may be set.

## Workflow

1. **Load repo contract** — `CLAUDE.md ## Commands` per
   `_internal/repo-delivery`; missing → halt (same message as
   /skill:execute-plan preflight gate 1).

2. **Load requirements source.**

   If `--ado <id>` or `--linear <id>` was supplied, invoke `/skill:work-item`
   to fetch the ticket. `/skill:work-item` returns the rendered markdown to
   stdout — it does **not** write to disk. **execute-prd** then persists
   that rendered markdown to `docs/prds/<source-slug>/PRD.md` (creating
   the directory if needed) so the rest of the flow has a stable file to
   reference. Extract title, description, acceptance criteria, and
   work-item type from the rendered markdown. The plan header carries
   `**Source:** ADO #<id> — <title>` (or `Linear <id> — <title>`).
   Reject if more than one of `<path>` / `--ado` / `--linear` is set.

   Otherwise resolve the requirements artifact from the filesystem.

   Resolution order — first match wins:

   1. The explicit `<path>` argument, if one was supplied.
   2. The most recently modified `docs/prds/*/AERS.md`.
   3. `./AERS.md` (legacy root location).
   4. The most recently modified `docs/prds/*/PRD.md`.
   5. `./PRD.md`.
   6. `./prompt.md`.

   If two or more candidates tie within the same tier, do not guess: ask the
   operator which is canonical (interactive) or emit a `plan-ambiguity` finding
   and stop (autonomous).

   Sibling artifacts — `ONTOLOGY.md`, `UBIQUITOUS_LANGUAGE.md`, and `PRD.md` —
   resolve relative to the directory of the resolved requirements file, not the
   repo root.

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

3. **Audit current state** — invoke `/skill:audit-existing`; never assume
   the source describes the repo accurately.

4. **Readiness gate.**

   Before extracting non-negotiables or drafting the plan, score the
   requirements source using the **Automated readiness check** in
   `_internal/aers-readiness/SKILL.md`. That check is a **composite**:
   structural points plus the ontology contribution produced by
   `_internal/ontology-readiness/SKILL.md` over the sibling
   `ONTOLOGY.md` resolved in step 2. Report both the structural verdict
   and the `Ontology:` line — the point values live in those rubrics and
   are not restated here. The audit from step 3 is an input — readiness
   is judged against *this repo*, not in the abstract.

   ```
   Readiness: Not ready / Partially ready / Ready
   Ontology: Ready / Partial / Absent

   Structural score: <n>
   Ontology contribution: <0 | +2 | +4>
   Composite: <n>

   Gaps:
   - ...
   ```

   Both lines are always emitted, even when the ontology contribution
   is 0. The structural verdict is the structural score read against the
   same bands (see `_internal/aers-readiness`).

   Behaviour by composite verdict:

   - **Ready:** proceed silently to step 5.
   - **Partially ready:**
     - Interactive operator → ask the gap questions inline (one at a
       time, via AskUserQuestion) and record answers as **closed
       decisions** in the generated plan (step 7). Do not invent
       answers. Suggest `/skill:prd-validate` if the operator prefers a
       structured interview.
     - Autonomous → proceed and log the gap list in the plan as a
       known risk under `## Open Decisions`. Do not auto-invoke
       `/skill:prd-validate`.
   - **Not ready:**
     - Interactive operator → halt; suggest `/skill:prd-validate` to close
       gaps. Do not invoke it automatically — it's an interview, not a
       gate.
     - Autonomous → abort with a `requirements-incomplete` finding
       listing the rubric points and the unresolved high-risk
       ambiguities. Do not draft a plan against an unready PRD.

   **Ontology halt.** Halt only when the ontology line is a bare
   `Ontology: Absent` **and** the structural verdict is
   `Partially ready` or worse. A structural verdict of `Ready` with a
   bare `Absent` proceeds and logs the missing ontology as a known
   risk. `Ontology: Absent (trivial domain)` never halts.

   On a halt: interactive operator → halt and suggest `/skill:prd-create`;
   autonomous → halt with a `requirements-incomplete` finding. Do not
   auto-invoke `/skill:prd-create` — it is an interview, the same interaction
   boundary as `/skill:prd-validate`. When the run proceeds on a bare
   `Absent`, log the missing ontology in the plan as a known risk under
   `## Open Decisions`.

   **Ontology revision halt.** The reopened-decision halt extends to
   the ontology. An `addition` entry in the `ONTOLOGY.md` Extension Log
   passes.

   A **revision** — one of exactly five kinds per
   `_internal/ontology-readiness` § *Completeness and Extension* Rule 4:
   changed reference scheme, homonym split, tightened constraint,
   reclassified modality, retrofitted temporality — is mode-dependent, and
   the mode is read from the `mode:` header of `ONTOLOGY.md`: in `feature`
   mode any `revision` entry in the Extension Log is a halt condition and
   halts with an `ontology-revision` finding; `refresh` mode follows the
   `feature` rule, so any `revision` entry halts the same way; in
   `greenfield` mode a `revision` entry is itself a defect — nothing
   existed to revise — and halts the same way; in `rewrite` mode a
   `revision` entry must be matched by a confirmed closed decision in the
   PRD, and is a halt — the same `ontology-revision` finding — only if it
   is not.

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

8. **Static plan checks** (author-side, before /skill:validate-plan):
   every depends_on references an existing task id; no two
   dependency-independent tasks share a write_scope glob; every
   acceptance bullet is mechanical. Fix violations before validating.

9. **Validate** — run `/skill:validate-plan`; fix-and-revalidate at most 3
   times, then surface the top blocking finding and ask the operator
   (escalate to readiness / manual override / abandon).

10. **Execute** — invoke `/skill:execute-plan <plan-path>` with any
    pass-through flags.

## Things you must not do

- Do not skip `/skill:audit-existing`. Greenfield assumptions on a populated
  repo are the most expensive failure mode this skill exists to prevent.
- Do not skip the readiness gate (step 4). Drafting a plan against
  an unready PRD is the second most expensive failure mode.
- Do not skip `/skill:validate-plan`. A bad plan silently guessed through is
  the third most expensive failure mode.
- Do not draft and execute in one shot — the staged validation is the
  point.
- Do not loop on `/skill:validate-plan` without bound. Three attempts then
  surface to the operator (see step 9).
- Do not invent product decisions to close ambiguity. Halt and ask.

## Contract

- **Inputs:** one requirements source — `<path>`, `--ado <id>`, or
  `--linear <id>` — resolved per step 2; optional `--type`; pass-through
  flags forwarded to `/skill:execute-plan`. Calls `/skill:work-item` (ticket fetch),
  `/skill:audit-existing` (repo audit), `_internal/aers-readiness` (composite
  readiness scoring), `_internal/ontology-readiness` (the `Ontology:`
  verdict line, reached through aers-readiness), the
  `workflows/design-it-twice.mjs` Workflow script (step 6,
  conditional), `/skill:validate-plan` (plan gate), and `/skill:execute-plan`
  (execution). Consults `_internal/plan-format` and
  `_internal/repo-delivery`.
- **Preconditions:** repo has a `CLAUDE.md ## Commands` section; the
  requirements source resolves to exactly one artifact; for `--ado` /
  `--linear`, the tracker integration `/skill:work-item` needs is configured;
  the Workflow tool is available if step 6 fires.
- **Outputs:** a plan file in the `_internal/plan-format` contract
  (frontmatter, Closed Decisions, `## Task N:` sections with dependency
  metadata and mechanical acceptance bullets); for a ticket source, the
  fetched work item persisted to `docs/prds/<source-slug>/PRD.md`; then
  whatever `/skill:execute-plan` produces (execution report, postmortem).
- **Postconditions:** `/skill:audit-existing`, the readiness gate, and
  `/skill:validate-plan` all ran before execution; every non-negotiable from the
  requirements source appears in a task acceptance block or the final
  traceability task; no product decision was invented to close ambiguity.
- **Failure modes:** missing `CLAUDE.md ## Commands` → halt with the same
  message as `/skill:execute-plan` preflight gate 1; more than one of `<path>` /
  `--ado` / `--linear` → reject; several plausible requirements sources and
  none named → ask the operator (interactive) or abort with a
  `plan-ambiguity` finding (autonomous); readiness `Not ready` → halt and
  suggest `/skill:prd-validate` (interactive) or abort with a
  `requirements-incomplete` finding (autonomous); a bare
  `Ontology: Absent` with a structural verdict of `Partially ready` or
  worse → halt and suggest `/skill:prd-create` (interactive) or halt with a
  `requirements-incomplete` finding (autonomous), never auto-invoke
  `/skill:prd-create` (a structural `Ready` with a bare `Absent` proceeds and
  logs a known risk under `## Open Decisions`, and
  `Absent (trivial domain)` never halts); an ontology revision — changed
  reference scheme, homonym split, tightened constraint, reclassified
  modality, retrofitted temporality — in `feature` mode → halt with an
  `ontology-revision` finding, and in `rewrite` mode → the same halt
  unless the `revision` entry is matched by a confirmed closed decision
  in the PRD (mode read from the `mode:` header of `ONTOLOGY.md`), while
  `addition` entries pass; `/skill:validate-plan` still
  failing after three fix cycles → surface the top blocking finding and ask
  the operator; no Workflow tool when step 6 fires → halt, never emulate
  the script with the Agent tool.

## When NOT to Use

- A validated plan already exists — `/skill:execute-plan` directly.
- One-or-two-file change — edit directly.
- The PRD is open-ended or the user wants to think interactively —
  `/skill:prd-validate` or superpowers:brainstorming first.
