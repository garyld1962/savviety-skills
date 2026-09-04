# Project Instructions

> **This file is the single source of truth for project conventions.**
> All prompts, agents, skills, and Copilot built-ins should treat this file as the project-level configuration source.

## Scope Boundaries

- This file is the authoritative project instruction file for GitHub Copilot in this repository.
- Do **not** read unrelated assistant-specific instruction files or non-Copilot runtime configuration when working in Copilot.
- Prompts live in `.github/prompts/`
- Agents live in `.github/agents/`
- Skills live in `.github/skills/`
- Passive rules live in `.github/instructions/`

## Project Overview

<!-- TODO: Replace with your actual project summary -->
This project is a [language/framework] codebase that [brief business or technical purpose].

## Tech Stack

<!-- TODO: Replace with your actual stack -->
- Language:
- Framework:
- Package manager / SDK:
- Test runner:
- Linter / formatter:

## Build and Test Commands

<!-- TODO: Replace with real commands -->
```bash
# Build

# Test

# Lint

# Format
```

## Environment Model

Describe how commands should be run in this repo.

<!-- TODO: Choose the correct model and delete the others -->
- This repo is primarily used from PowerShell
- This repo is primarily used from WSL/Linux
- This repo supports both PowerShell and WSL/Linux

### Environment rules

- Detect the current shell before giving shell-specific commands
- Prefer native-shell execution first
- If Linux tooling is required but the user is in PowerShell, prefer switching to a WSL terminal/session over wrapper-style command bridging
- Do **not** assume historical runners such as `run.sh` still exist unless they are present in the repo

## Repo Starting State

Describe what Copilot should assume before implementation begins.

<!-- TODO: Update for the repo -->
- Starting state: empty repo / scaffolded repo / existing production repo
- Solution/project format:
- Is scaffolding expected first?
- Are there existing packages/projects that must remain untouched?

## Tooling Assumptions

Document the concrete assumptions that should not be re-derived during execution.

<!-- TODO: Update for the repo -->
- Target framework / runtime version:
- Solution format (`.sln`, `.slnx`, workspace, monorepo, etc.):
- Package/project boundaries:
- Dependency management expectations:
- Integration test gating expectations:

## Copilot Asset Guardrails

In this repo, Copilot assets should bias toward explicit guardrails rather than
leaving important behavior to model interpretation, especially when using
high-reasoning models.

- Add **Examples** when the desired interaction pattern, output shape, or
  boundary between valid options is not obvious from the prompt alone.
- Add explicit **Do Nots** for the failure modes you already know about, such as
  guessing facts, reopening settled choices, or reporting success without the
  required evidence.
- Add **Closed Decisions** when the repo, asset author, or source artifact has
  already made a decision that execution should inherit without debate.
- Keep **Closed Decisions** and **Open Decisions** separate. Ask only about open
  decisions.
- Do not revisit a closed decision unless the user explicitly changes it or the
  source artifact is inconsistent.
- Prefer repo-shaped examples such as file paths, command patterns, output
  skeletons, and contract snippets over generic placeholder examples.

## Coding Conventions

### General

- Match existing patterns before introducing new ones
- Prefer minimal, surgical changes over broad refactors
- Do not add dependencies unless necessary and explicitly justified
- Keep code and tests readable and deterministic

### Error Handling

- Validate external input at boundaries
- Do not swallow exceptions silently
- Use project-standard error types and response patterns

### Testing

- Test core business behavior, not just happy paths
- Include validation and not-found/error-path coverage where applicable
- Use deterministic time control when time affects behavior
- Prefer test-created data over brittle seed-dependent assertions unless the AERS explicitly requires seed usage

## AERS Standard

When the input artifact is a story/spec/requirements document intended for execution, prefer an **AERS** — **Agent-Executable Requirements Spec**.

It should include:

- Closed Decisions
- Open Decisions
- Public API or public interface
- Data Models
- Test Strategy
- Repo Starting State
- Tooling Assumptions
- Definition of Done

If these are missing, use `#prompt:prd-validate` before `/plan`.

Treat the validator workflow as:

- input: business problem statement, business PRD, BRD, story, or rough spec
- output: AERS

Treat **Closed Decisions** as binding inputs for planning and implementation.
They are not brainstorming prompts and should not be reopened unless the user
or source artifact changes them.

## Execution Strategy

- Use built-in `/plan` for implementation planning once the artifact is ready
- Use custom prompts only where they add real domain value
- Build and test incrementally
- Prefer sequential execution when the dependency chain is linear

## Definition of Done

Work is only done when:

- implementation matches the approved artifact
- build passes
- tests pass
- important error paths are covered
- no unresolved blocker-level ambiguity remains

## Known Issues

<!-- TODO: Document any known failures or quirks so Copilot does not misclassify them as regressions -->
- None currently
