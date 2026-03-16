---
description: "Create an implementation plan for a feature, bug fix, refactor, or infrastructure change. Explores the codebase, writes TDD-style tasks with exact file paths and code, and validates the plan through design, dev feasibility, security, and scope reviews."
argument-hint: "Describe what to plan..."
---

# Implementation Planning

Explore the codebase, understand the problem, write a validated implementation plan with TDD-style tasks.

## When to Use

- You have requirements and need a plan before writing code
- Starting a new feature, bug fix, refactor, or infrastructure change
- Need to break complex work into concrete, ordered tasks

## Arguments

- `<description>` — what to plan (feature, bug fix, refactor, etc.)
- `--ado <item-id>` — fetch an Azure DevOps work item by ID and use it as the requirements input
- `--skip-validation` — skip the validation gate (for quick/small plans)
- `--type <bug|feature|refactor|infra>` — hint the plan type (auto-detected if omitted)

---

## Phase 1: Understand the Problem

### 1.1 Read the Request
Parse the description, issue link, or spec. If the request references a file path or GitHub issue, read it for full context.

#### If `--ado <item-id>` is provided:

Fetch the work item from Azure DevOps using the `ado-item` skill workflow:

1. Resolve ADO org/project configuration:
   ```bash
   az devops configure --list
   ```
   If not configured, check for `.ado-config` in the repo root, then ask the user.
   Once known, set them as defaults:
   ```bash
   az devops configure --defaults organization=<ADO_ORG> project="<ADO_PROJECT>"
   ```

2. Fetch the work item (uses configured defaults — do NOT pass `--project` inline):
   ```bash
   az boards work-item show --id <ITEM_ID> --output json
   ```

3. Extract requirements from the response:
   - **Title** → use as the plan name
   - **Description** → use as the primary requirements
   - **Acceptance Criteria** → use as the definition of done / test criteria
   - **Work Item Type** → use to hint plan type (User Story → feature, Bug → bug)
   - **Tags** → note for context
   - **Parent** → fetch parent item if needed for broader context

4. Include the ADO reference in the plan header:
   ```markdown
   **Source:** ADO #<ID> — <Title>
   ```

Then continue with the parsed requirements as if they were provided inline.

### 1.2 Classify Plan Type

| Type | Signals | Plan Shape |
|------|---------|------------|
| **bug** | "fix", "broken", error messages, stack traces | Root cause → test → fix → verify |
| **feature** | "add", "implement", "create", new behavior | Interface → tests → impl → integration |
| **refactor** | "rename", "extract", "move", "clean up" | Characterization tests → transform → verify |
| **infra** | "deploy", "config", "CI", "k8s", manifests | Config → apply → smoke test |

### 1.3 Clarify Ambiguity
If requirements are unclear, ask clarifying questions. One question at a time. Prefer multiple choice. Don't proceed with assumptions.

---

## Phase 2: Explore the Codebase

### 2.1 Identify Affected Areas
### 2.2 Read Existing Code
For each affected area: main source files, existing tests, relevant types/interfaces, project docs.

### 2.3 Map Dependencies
What imports what, shared types, external dependencies.

### 2.4 Check for Existing Work
Related PRs or branches, partial implementations, similar patterns.

---

## Phase 3: Scope & Estimate

### 3.1 High-Level Task List
### 3.2 Estimate Scope

| Tasks | Scope | Approach |
|-------|-------|----------|
| 1-3 | Small | Write plan inline, skip validation |
| 4-10 | Medium | Standard plan file with validation |
| 11+ | Large | Split into Waves |

### 3.3 Identify Risks
Blocking dependencies, merge conflict risks, parallel streams, unknowns, need for multiple Waves.

### 3.4 Report Scope
```
Scope: M tasks across N packages
Type: feature/bug/refactor/infra
Waves: 1 (or N if large)
Risks: [list]
Parallelizable: yes/no (N independent streams)

Proceed with detailed plan?
```
Wait for confirmation.

---

## Phase 4: Write the Plan

Save plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md`

### Plan Header

```markdown
# [Feature Name] Implementation Plan
**Source:** ADO #<ID> — <Title> (if --ado was used)
**Goal:** [One sentence]
**Architecture:** [2-3 sentences about approach]
**Tech Stack:** [Key technologies/libraries]
**Scope:** [N tasks, estimated size]
**Waves:** [N — list focus of each Wave if more than one]
**Risks:** [Key risks from Phase 3]
```

### Task Structure (TDD)

Each task follows TDD discipline — test first, then implement:

````markdown
### Task N: [Component Name]
**Files:**
- Create: `exact/path/to/file.ts`
- Modify: `exact/path/to/existing.ts`
- Test: `tests/exact/path/to/test.ts`

**Depends on:** Task M (if any)

**Step 1: Write the failing test**
```typescript
describe('specific behavior', () => {
  it('should do X when given Y', () => {
    const result = functionUnderTest(input);
    expect(result).toBe(expected);
  });
});
```

**Step 2: Run test to verify it fails**
```bash
npx vitest run tests/path/test.ts
```

**Step 3: Write minimal implementation**

**Step 4: Run test to verify it passes**

**Step 5: Commit**
```bash
git commit -m "feat(scope): add specific feature"
```
````

### Writing Rules
- **Exact file paths always** — never "add this somewhere appropriate"
- **Complete code in plan** — never "add validation here" without the actual code
- **Exact commands with expected output** — runnable as-is
- **One action per step** (2-5 minutes each)
- **DRY, YAGNI, TDD, frequent commits**
- **Dependency annotations** — mark which tasks block which

---

## Phase 5: Validate the Plan (unless --skip-validation)

Run through 4 review lenses:

### 5.1 Design Review
Follows project patterns? Naming conventions? No circular dependencies?

### 5.2 Dev Feasibility Review
Every task has tests? Commands are correct? Tasks ordered? Code compiles?

### 5.3 Security Review
Input validated? No secrets? Auth on new endpoints? No injection?

### 5.4 Scope Review
Stays within stated goal? All requirements addressed? No scope creep?

### 5.5 Present Findings

```
## Validation Findings
| # | Lens | Severity | Task | Finding | Suggestion |
|---|------|----------|------|---------|------------|
```

For each: **Fix Now** / **File Issue** / **Dismiss**. Revise the plan for any "Fix Now" items.

### 5.6 Stamp
```markdown
<!-- Validated: YYYY-MM-DD | Design ✅ | Dev ✅ | Security ✅ | Scope ✅ -->
```
