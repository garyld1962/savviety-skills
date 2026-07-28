---
applyTo: "**/*.{prompt,agent,instructions}.md"
description: "Author Copilot assets in a built-in-first style. Avoid duplicating platform capabilities and keep prompts thin, skills durable, agents narrow, and instructions passive."
---

# Copilot Asset Authoring Rules

These rules apply when writing or editing Copilot prompts, agents, and instructions.

## Built-in first

- Prefer Copilot built-ins when the platform already provides the workflow well.
- Do not create a custom prompt just because Claude had a similarly named command.
- Before creating a new prompt, ask whether `/plan`, `/review`, `/research`, `/tasks`, `/agent`, or `/delegate` already covers the need.

## Keep prompts thin

- Prompts should orchestrate a workflow, not contain all durable knowledge inline.
- Move rubrics, heuristics, and templates into skills.
- Point prompts to the relevant skill instead of repeating the whole checklist.

## Keep agents narrow

- Agents should have bounded specialist roles.
- Do not turn agents into generic orchestration layers unless there is a clear output contract.

## Keep instructions passive

- Instructions should hold always-on constraints and authoring discipline.
- Do not use instructions to recreate an entire workflow.

## Copilot-specific design rules

- Mention the right next built-in when appropriate, such as "use `/plan` after this."
- Prefer `@file` context and actual repo inspection over long speculative prompt text.
- Do not assume users need a custom asset when a built-in already creates a better UX.
- If an asset emits commands, detect whether the user is in PowerShell, WSL/Linux, or a mixed setup before giving shell-specific guidance.
- Do not hardcode "already in WSL" unless the environment has been detected.
- Prefer native-shell commands or explicit terminal switching over wrapper patterns like `wsl.exe -e bash -lc`.

## Guardrails for high-reasoning models

- Copilot, especially with high-reasoning models, performs better when assets
  constrain recurring failure modes instead of leaving them implicit.
- For non-trivial prompts, skills, and agents, prefer to include all three of
  these guardrail types:
  - **Examples** when the interaction shape, output shape, or classification
    boundary is easy to misread.
  - **Do Nots** when there are known bad behaviors to suppress, such as
    inventing facts, revisiting settled choices, or claiming success without
    evidence.
  - **Closed Decisions** when the asset author, repo, or source artifact has
    already made a choice that should not be reopened during execution.
- Keep **Closed Decisions** separate from **Open Decisions**. If a choice is
  closed, execute against it. If it is open, ask.
- Do not restate a closed decision as an option set unless the user explicitly
  asks to revisit it or the source artifact contradicts it.
- Prefer short, repo-shaped examples over abstract filler. One concrete example
  that locks in the intended behavior is better than several generic ones.
- If an asset has repeated model drift in practice, add guardrails before adding
  more workflow complexity.

## Migration rule

When porting from Claude:

- keep domain leverage
- remove command-name nostalgia
- split orchestration from durable knowledge
- simplify assets that only duplicate built-ins

## Ownership and preservation rules

- Treat repo-managed shared assets as the canonical layer. These should live in
  the standard shared namespaces:
  - `.github/prompts/ba/`
  - `.github/prompts/common/`
  - `.github/prompts/dev/`
  - `.github/prompts/review/`
  - `.github/skills/<shared-skill>/`
  - `.github/agents/`
  - `.github/instructions/*.instructions.md`
- Do not tell users to edit shared assets in place when the intent is a local or
  personal customization. Prefer a separate custom layer.
- Project-owned custom assets that should be committed with the repo should live
  in reserved project namespaces:
  - `.github/prompts/project/`
  - `.github/skills/project-<domain>/`
  - `.github/agents/project-<name>.agent.md`
  - `.github/instructions/project.instructions.md`
- User-local per-project assets that should survive syncs should live in
  reserved local namespaces:
  - `.github/prompts/local/`
  - `.github/skills/local-<user>/`
  - `.github/agents/local-<user>.agent.md`
  - `.github/instructions/personal.instructions.md`
- User-global preferences belong in:
  - `$HOME/.copilot/copilot-instructions.md`
  - additional instruction directories via `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`

## Deployment preservation rule

- Sync or deploy tooling should overwrite only the shared canonical layer.
- Sync or deploy tooling should never overwrite:
  - `.github/instructions/personal.instructions.md`
  - `.github/prompts/local/**`
  - `.github/skills/local-*/**`
  - `.github/agents/local-*.agent.md`
- If users need a shared asset changed for everyone, that should go through a PR
  to the shared repo, not a local override.
