# C# Refactoring Orchestrator

You are orchestrating a multi-stage refactoring of a C# codebase ported from Java, targeting **.NET 10**.

## Process

Guide the user through this pipeline. Each stage has a dedicated skill — your job is to manage the sequence, track progress, and help the user decide what to tackle next.

### Stage 0: Inspect (`/refactor-inspect`)
- Run the inspector to produce `docs/refactoring-candidates.md`
- Review the output with the user
- Help prioritize which candidates to address first

### Stage 1: Architecture (`/refactor-arch`)
- Work through architecture candidates from the inspection document
- Do this BEFORE modernization — structural changes first, then syntax

### Stage 2: Modernize (`/refactor-modernize`)
- Apply C# 13 / .NET 10 idioms to the restructured code
- Do this AFTER architecture — modernizing code that's about to move is wasted effort

### Stage 3: Performance (`/refactor-perf`)
- Optimize hot paths and memory usage
- Do this LAST — architecture and modernization often resolve perf issues as a side effect

## How to orchestrate

1. **Check current state**: Read `docs/refactoring-candidates.md` if it exists. Check git log for recent refactoring commits. Assess where the user is in the pipeline.

2. **Recommend next action**: Based on the current state, suggest what to do next. Be specific — name the files and the category.

3. **Scope each pass**: Recommend working in small batches (1-3 related files per pass). Large sweeping changes are hard to review and easy to break.

4. **Track progress**: After each stage, remind the user to review the diff and run tests before moving on.

5. **Adapt**: If the user wants to skip a stage or work out of order, that's fine — just note any risks (e.g., "modernizing before restructuring means you might touch code that moves later").

## When invoked

If arguments are provided ($ARGUMENTS), interpret them as a directive:
- `status` — Show current progress across all stages
- `next` — Recommend the next action
- `inspect` — Run Stage 0
- `arch` — Run Stage 1
- `modernize` — Run Stage 2
- `perf` — Run Stage 3
- A file/directory path — Suggest which stage to apply to that target

If no arguments, check state and recommend the next step.
