---
description: >-
  Create an implementation plan for a feature, bug fix, refactor, or
  infrastructure change. Explores the codebase, writes TDD-style tasks with
  exact file paths and code, and validates the plan.
argument-hint: '<description> [--ado <id>] [--linear <id>] [--type bug|feature|refactor|infra] [--skip-validation]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - codebase
  - edit
  - web
---

# Implementation Planning

Explore the codebase, understand the problem, write a validated implementation plan with TDD-style tasks.

## When to Use

- You have requirements and need a plan before writing code
- Starting a new feature, bug fix, refactor, or infrastructure change
- Need to break complex work into concrete, ordered tasks

## Arguments

- `<description>` — what to plan (feature, bug fix, refactor, etc.)
- `--ado <item-id>` — fetch an Azure DevOps work item by ID and use it as requirements
- `--linear <issue-id>` — fetch a Linear issue by identifier (e.g., `BF-42`) and use it as requirements
- `--skip-validation` — skip the validation gate (for quick/small plans)
- `--type <bug|feature|refactor|infra>` — hint the plan type (auto-detected if omitted)

---

## CRITICAL: Do Not Guess

- **File paths**: ALWAYS search the codebase before citing paths. Do NOT invent paths like "probably src/services/auth.ts" — verify with search.
- **Function signatures**: READ the actual function before referencing it in a plan task. Do NOT guess parameter names, return types, or method names.
- **Test commands**: Check `package.json` scripts and test framework config. Do NOT assume `pnpm vitest` — the project may use jest, mocha, or a custom script.
- **Build commands**: Read the `scripts` field in `package.json` or project docs. Do NOT assume `pnpm -r build`.
- **Import paths**: Check actual import patterns in existing code. Path aliases (`@/`, `~/`, `#`), barrel exports, and workspace references vary by project.
- **Dependencies**: Verify what packages are installed before referencing them in plan code. Do NOT import packages that aren't in `package.json`.
- **Branch/remote names**: Run `git branch --show-current` and `git remote -v`. Do NOT assume `main` or `origin`.

---

## Phase 1: Understand the Problem

### 1.1 Read the Request

Parse the description, issue link, or spec. If the request references a file path or issue, read it for full context.

#### If `--ado <item-id>` is provided:

1. Resolve ADO org/project configuration:
   ```bash
   az devops configure --list
   ```
   If not configured, check for `.ado-config` in the repo root, then ASK the user. Do NOT guess org/project names.

2. Fetch the work item (uses configured defaults — do NOT pass `--project` inline):
   ```bash
   az boards work-item show --id <ITEM_ID> --output json
   ```

3. Extract: Title → plan name, Description → requirements, Acceptance Criteria → definition of done, Work Item Type → plan type hint

4. Include reference: `**Source:** ADO #<ID> — <Title>`

#### If `--linear <issue-id>` is provided:

Use the Linear MCP tool or CLI to fetch the issue. Extract the same fields. Include reference: `**Source:** Linear <ID> — <Title>`

### 1.2 Classify Plan Type

| Type | Signals | Plan Shape |
|------|---------|------------|
| **bug** | "fix", "broken", error messages, stack traces | Root cause → test → fix → verify |
| **feature** | "add", "implement", "create", new behavior | Interface → tests → impl → integration |
| **refactor** | "rename", "extract", "move", "clean up" | Characterization tests → transform → verify |
| **infra** | "deploy", "config", "CI", "k8s", manifests | Config → apply → smoke test |

### 1.3 Clarify Ambiguity

If requirements are unclear: ASK. One question at a time. Prefer multiple choice. Do NOT proceed with assumptions.

### Example: Correct clarification

```
The requirements mention "user authentication" but don't specify the method.
Which authentication approach should we use?
a) JWT tokens (stateless, typical for APIs)
b) Session-based (server-side, typical for web apps)
c) OAuth2/OIDC (delegated to identity provider)
```

### Example: INCORRECT

```
# WRONG: Making assumptions instead of asking
I'll implement JWT authentication since that's most common.  # ← ASK, don't assume
```

---

## Phase 2: Explore the Codebase

### 2.1 Identify Affected Areas

From the requirements, list which packages/services/files are likely involved.

### 2.2 Read Existing Code

For EACH affected area, actually read:
- Main source files (the code you'll modify)
- Existing tests (understand coverage and test patterns)
- Relevant types/interfaces from shared packages
- Project docs (`.github/copilot-instructions.md`)

**Do NOT skip this step.** Plans written without reading the codebase produce incorrect file paths, wrong function signatures, and broken imports.

### 2.3 Map Dependencies

Identify:
- What imports what (which packages depend on which)
- Shared types or interfaces that multiple tasks will touch
- External dependencies (APIs, databases, config) that constrain the design

### 2.4 Check for Existing Work

```bash
# Related branches
git branch -a | grep -i "<feature-keyword>"

# Related PRs (if gh CLI is available)
gh pr list --state all --search "<feature-keyword>" 2>/dev/null

# Partial implementations or TODOs
grep -r "TODO\|FIXME\|HACK" --include='*.ts' src/ | grep -i "<feature-keyword>"
```

---

## Phase 3: Scope & Estimate

### 3.1 High-Level Task List

One line per task, ordered by dependency.

### 3.2 Estimate Scope

| Tasks | Scope | Approach |
|-------|-------|----------|
| 1-3 | Small | Write plan inline, skip validation |
| 4-10 | Medium | Standard plan file with validation |
| 11+ | Large | Split into Waves |

### 3.3 Identify Risks and Parallel Opportunities

- Blocking dependencies (task order)
- Merge conflict risks (shared files)
- Unknowns requiring spikes
- **Parallel streams** — identify task groups that:
  - Live in different packages or directories (clear file ownership)
  - Have no cross-group file edits (no merge conflicts)
  - Share a common foundation that must complete first

When parallel streams exist, structure the plan as multiple **Waves**:
- **Wave 1:** Foundation tasks that all streams depend on (sequential)
- **Wave 2:** Independent streams that can run in parallel via `#prompt:teams`
- **Wave 3+:** Integration, verification, or further dependent work (may also be parallel)

**Parallel wave constraints:**
- **Max 4 teams per parallel wave.** If more than 4 independent streams exist, split into sequential parallel waves (Wave 2 with 3 teams, Wave 3 with 3 teams, etc.).
- Each team should have a meaningful chunk of work (3-8 tasks). Do NOT create a team for 1-2 trivial tasks.
- When in doubt, prefer fewer larger teams over many small ones — each parallel session has coordination overhead.

### 3.4 Report Scope and WAIT

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

**WAIT for user confirmation before writing the plan.** Do NOT auto-proceed.

---

## Phase 4: Write the Plan

Save to: `docs/plans/YYYY-MM-DD-<feature-name>.md`

### Plan Header

```markdown
# [Feature Name] Implementation Plan
**Source:** ADO #<ID> / Linear <ID> — <Title> (if applicable)
**Goal:** [One sentence]
**Architecture:** [2-3 sentences about approach]
**Tech Stack:** [Key technologies/libraries]
**Scope:** [N tasks, estimated size]
**Waves:** [N]
**Parallelizable:** [yes/no (N independent streams)]
**Risks:** [Key risks from Phase 3]

| Wave | Tasks | Focus | Execution |
|------|-------|-------|-----------|
| Wave 1: Foundation | 1–N | [description] | Sequential — `#prompt:execute-plan` (stop after Task N) |
| Wave 2: [Name] | N–M | [Team A] (Tasks N-P) and [Team B] (Tasks Q-M) | Parallel — `#prompt:teams` with N teams |
| Wave 3: Verify | M+1 | Integration verification | Sequential — `#prompt:checkpoint` |
```

If the plan has only 1 Wave (all tasks are sequential), omit the wave table and set `**Waves:** 1`.

### Wave Boundary Markers

When a plan has multiple Waves, insert boundary markers between waves:

```markdown
## --- WAVE 2 START: [Name] (Parallel Teams) ---

> **Execution:** Use `#prompt:teams` to run [Team A] and [Team B] in parallel worktrees.
> [Team A] owns `path/to/package-a/`. [Team B] owns `path/to/package-b/`. Zero file overlap.

### Task N: ...
```

### Team Boundary Table

When Wave 2+ uses parallel teams, include a team boundary table:

```markdown
### Wave 2 Team Boundaries

| Team | Tasks | Package | Files |
|------|-------|---------|-------|
| Team A | N–P | `packages/a/` | [description] |
| Team B | Q–M | `packages/b/` | [description] |

**Merge order:** [Which team merges first and why]. Run full build + test on main after each merge.
```

### Task Structure (TDD)

Each task follows TDD discipline:

````markdown
### Task N: [Component Name]
**Files:**
- Create: `exact/path/verified/by/search.ts`
- Modify: `exact/path/verified/by/reading.ts`
- Test: `exact/path/matching/project/convention.test.ts`

**Depends on:** Task M (if any)

**Step 1: Write the failing test**
```typescript
// Imports must use ACTUAL paths from the project
import { actualFunction } from '../../actual/import/path';

describe('specific behavior', () => {
  it('should do X when given Y', () => {
    const result = actualFunction(validInput);
    expect(result).toBe(expectedOutput);
  });
});
```

**Step 2: Run test to verify it fails**
```bash
# Use the project's ACTUAL test command
<detected-test-command> <test-file-path>
```

**Step 3: Write minimal implementation**

**Step 4: Run test to verify it passes**

**Step 5: Commit**
```bash
git commit -m "feat(scope): add specific feature"
```
````

### Writing Rules — MANDATORY

1. **Exact file paths always** — every path must have been verified by search. NEVER write "add this somewhere appropriate."
2. **Complete code in plan** — NEVER write "add validation here" without the actual code.
3. **Exact commands with expected output** — runnable as-is, using the project's actual build/test commands.
4. **One action per step** (2-5 minutes each).
5. **Dependency annotations** — mark which tasks block which.
6. **Real imports only** — every import path must match an actual file in the project. If you haven't verified the path, add a comment: `// VERIFY: path not confirmed`.

---

## Phase 5: Validate the Plan (unless --skip-validation)

### 5.1 Design Review
Follows project patterns? Naming conventions? No circular dependencies?

### 5.2 Dev Feasibility Review
Every task has tests? Commands correct for this project? Tasks ordered? Code compiles?

### 5.3 Security Review
Input validated? No secrets in code? Auth on new endpoints? No injection?

### 5.4 Scope Review
Within stated goal? All requirements addressed? No scope creep?

### 5.5 Present Findings

```
## Validation Findings
| # | Lens | Severity | Task | Finding | Suggestion |
|---|------|----------|------|---------|------------|
```

For each: **Fix Now** / **File Issue** / **Dismiss**. Revise plan for "Fix Now" items.

### 5.6 Stamp

```markdown
<!-- Validated: YYYY-MM-DD | Design ✓ | Dev ✓ | Security ✓ | Scope ✓ -->
```

---

## Phase 6: Ready

After validation passes (or is skipped), report next steps based on the plan structure:

**Single Wave (no parallelism):**
```
Plan ready: docs/plans/YYYY-MM-DD-<feature>.md
Tasks: N | Scope: small/medium/large | Waves: 1
Validated: yes/no

Next: run #prompt:execute-plan to implement.
```

**Multiple Waves (with parallelism):**
```
Plan ready: docs/plans/YYYY-MM-DD-<feature>.md
Tasks: N | Scope: medium/large | Waves: M
Validated: yes/no

Execution sequence:
  Wave 1: #prompt:execute-plan (stop after Task N — foundation)
  Wave 2: #prompt:teams (parallel: Team A + Team B)
  Wave 3: #prompt:checkpoint (integration verification)
```

---

## Rules

1. **Read before writing.** Never plan changes to code you haven't read. Phase 2 is mandatory.
2. **Verify every path.** Every file path in the plan must exist or be clearly marked as "to be created."
3. **Use real commands.** Build and test commands must match the actual project setup.
4. **Ask, don't assume.** If requirements are ambiguous, ask a clarifying question instead of guessing.
5. **Wait for approval.** Report scope in Phase 3 and wait for the user to confirm before writing the plan.
6. **Identify parallelism.** When tasks span independent packages with no shared files, structure as Waves with parallel teams.
