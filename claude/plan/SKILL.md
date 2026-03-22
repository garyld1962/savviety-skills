---
name: plan
description: "Create an implementation plan: explores the codebase, estimates scope, writes a TDD-style task plan, and validates it. Use when you have requirements and need a plan before writing code."
---

# /plan — Implementation Planning

**Purpose:** Explore the codebase, understand the problem, write a validated implementation plan. Enriches the superpowers planning pipeline with codebase discovery and scope estimation.

## Arguments

- `<description>` — what to plan (feature, bug fix, refactor, etc.)
- `--ado <item-id>` — fetch an Azure DevOps work item by ID and use it as requirements input
- `--linear <issue-id>` — fetch a Linear issue by identifier (e.g., `BF-42`) and use it as requirements input
- `--skip-validation` — skip the validation gate (for quick/small plans)
- `--type <bug|feature|refactor|infra>` — hint the plan type (auto-detected if omitted)

## Workflow

### Phase 1: Understand the Problem

1. **Read the request.** Parse the description, issue link, or spec. If an argument references a file path, Linear issue, or GitHub issue, read it.

   If `--ado <item-id>` or `--linear <issue-id>` was provided, use `/work-item` to fetch the full details. Extract title, description, acceptance criteria, and work item type. Use the title as the plan name, description as requirements, acceptance criteria as definition of done, and work item type to hint plan type (User Story → feature, Bug → bug). Include the reference in the plan header:
   ```
   **Source:** ADO #<ID> — <Title>
   **Source:** Linear <ID> — <Title>
   ```

2. **Classify the plan type** (if not provided via `--type`):

   | Type | Signals | Plan Shape |
   |------|---------|------------|
   | **bug** | "fix", "broken", error messages, stack traces | Root cause → test → fix → verify |
   | **feature** | "add", "implement", "create", new behavior | Interface → tests → impl → integration |
   | **refactor** | "rename", "extract", "move", "clean up" | Characterization tests → transform → verify |
   | **infra** | "deploy", "config", "CI", "k8s", manifests | Config → apply → smoke test |

3. **Ask clarifying questions** if requirements are ambiguous. One question at a time, prefer multiple choice. Don't proceed with assumptions — ask.

### Phase 2: Explore the Codebase

4. **Identify affected areas.** From the requirements, determine which packages/services/files are likely involved.

5. **Read existing code.** For each affected area:
   - Read the main source files
   - Read existing tests (understand current coverage and test patterns)
   - Read relevant types/interfaces from shared packages
   - Check `CLAUDE.md` for project conventions

6. **Map dependencies.** Identify:
   - What imports what (which packages depend on which)
   - Shared types or interfaces that multiple tasks will touch
   - External dependencies (APIs, databases, config) that constrain the design

7. **Check for existing work.** Search for:
   - Related PRs or branches (`gh pr list`, `git branch -a`)
   - Partial implementations or TODOs in the codebase
   - Similar patterns already solved elsewhere in the project

### Phase 3: Scope & Estimate

8. **List the tasks** at a high level (not detailed yet). One line per task.

9. **Estimate scope:**

   | Tasks | Scope | Approach |
   |-------|-------|----------|
   | 1-3 | Small | Write plan inline, skip validation |
   | 4-10 | Medium | Standard plan file with validation |
   | 11+ | Large | Split into Waves |

10. **Identify risks and parallel opportunities:**
    - Tasks that block other tasks (dependency order)
    - Tasks that touch shared files (merge conflict risk)
    - Unknowns that need spiking first
    - **Parallel streams** — identify task groups that:
      - Live in different packages or directories (clear file ownership)
      - Have no cross-group file edits (no merge conflicts)
      - Share a common foundation that must complete first

    When parallel streams exist, structure the plan as multiple **Waves**:
    - **Wave 1:** Foundation tasks that all streams depend on (sequential via `/execute-plan`)
    - **Wave 2:** Independent streams that can run in parallel via `/teams`
    - **Wave 3+:** Integration, verification, or further dependent work (may also be parallel)

    **Parallel wave constraints:**
    - **Max 4 teams per parallel wave.** If more than 4 independent streams exist, split into sequential parallel waves (Wave 2 with 3 teams, Wave 3 with 3 teams, etc.).
    - Each team should have a meaningful chunk of work (3-8 tasks). Do NOT create a team for 1-2 trivial tasks.
    - When in doubt, prefer fewer larger teams over many small ones — each parallel agent has coordination overhead.

11. **Report scope to user** before writing the detailed plan:
    ```
    Scope: M tasks across N packages
    Type: feature/bug/refactor/infra
    Waves: N
      Wave 1: <focus> (sequential)
      Wave 2: <focus> (parallel: N teams) ← if applicable
      Wave 3: <focus> (sequential)
    Risks: [list]
    Parallelizable: yes/no (N independent streams)

    Proceed with detailed plan?
    ```

### Phase 4: Write the Plan

12. **Invoke `superpowers:writing-plans`** to write the detailed plan.

    Provide it with everything gathered in Phases 1-3:
    - Requirements and clarifications
    - Affected files and existing code context
    - Dependency map
    - Scope estimate and task ordering
    - Risk notes
    - **Wave structure and team boundaries** (if parallelizable)

    The writing-plans skill will produce the full TDD-style plan with exact code, paths, and test commands.

    **If the plan has multiple Waves**, ensure the output includes:
    - A wave table in the header (Wave, Tasks, Focus, Execution method)
    - Team boundary table for parallel waves (Team, Tasks, Package, Files)
    - `## --- WAVE N START ---` markers between waves
    - Merge order guidance (dependency providers first)

### Phase 5: Validate (unless --skip-validation)

13. **Invoke `superpowers:validating-plans`** to run the 4-specialist validation gate.

    This dispatches design, dev, security, and backlog reviewers in parallel, then presents findings for triage.

### Phase 6: Ready

14. After validation passes (or is skipped), report next steps based on plan structure:

    **Single Wave (no parallelism):**
    ```
    Plan ready: docs/plans/YYYY-MM-DD-<feature>.md
    Tasks: N | Scope: small/medium/large | Waves: 1
    Validated: yes/no

    Next: run /execute-plan to implement.
    ```

    **Multiple Waves (with parallelism):**
    ```
    Plan ready: docs/plans/YYYY-MM-DD-<feature>.md
    Tasks: N | Scope: medium/large | Waves: M
    Validated: yes/no

    Execution sequence:
      Wave 1: /execute-plan (stop after Task N — foundation)
      Wave 2: /teams (parallel: Team A + Team B)
      Wave 3: /checkpoint (integration verification)
    ```

## Plan Type Templates

### Bug Fix
```
1. Reproduce: write a failing test that demonstrates the bug
2. Root cause: trace the failure to the source
3. Fix: minimal change to make the test pass
4. Regression: add edge case tests
5. Verify: run full test suite
```

### Feature
```
1. Interface: define types/schemas
2. Tests: write failing tests for each behavior
3. Implementation: make tests pass (one component at a time)
4. Integration: wire components together
5. Edge cases: error handling, validation, boundary conditions
```

### Refactor
```
1. Characterization: write tests that capture current behavior
2. Transform: apply the refactor in small steps
3. Verify: existing + characterization tests still pass
4. Clean up: remove dead code, update imports
```

### Infrastructure
```
1. Config: write/modify manifests, configs, scripts
2. Apply: deploy to target environment
3. Smoke test: verify the change works end-to-end
4. Rollback plan: document how to undo if needed
```

## Notes

- This skill orchestrates — it delegates the heavy lifting to `superpowers:writing-plans` and `superpowers:validating-plans`.
- For small plans (1-3 tasks), `--skip-validation` is reasonable.
- For large plans (11+ tasks), suggest splitting into phases before writing.
- The plan file is the contract. `/execute-plan` reads it literally.
