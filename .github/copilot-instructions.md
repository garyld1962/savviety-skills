# Repository Copilot Instructions

> **This file is the repo-level source of truth for working in `skills/`.**
> It governs how Copilot should author, edit, review, and port assets in this
> repository itself.

## Repository purpose

This repository is not an application repo. It is the **source of truth for
skill authoring** across:

- `claude/` - Claude Code skills
- `copilot-native/` - source assets for Copilot prompts, agents, skills, and
  instructions

Treat this repository as an **authoring system**, not as a deployed `.github/`
workspace.

## Precedence and circular authoring rule

- These repo-level instructions apply when working anywhere in this repository.
- Files under `copilot-native/` are **source assets** that will later be
  deployed into `.github/` in downstream repos.
- `copilot-native/copilot-instructions.md` and
  `copilot-native/instructions/*.instructions.md` are themselves authoring
  artifacts/templates. They must align with this file rather than redefining the
  repo's top-level authoring rules.
- It is valid and expected for skills in this repository, including root-level
  and `claude/` authoring workflows, to create or refine assets under
  `copilot-native/`. That is not a circular mistake; it is the intended design
  of the repo.

## Copilot asset authoring rules for this repo

### Built-in first

- Prefer Copilot built-ins when the platform already provides the workflow well.
- Do not port or preserve a workflow only for Claude command-name parity.
- Keep prompts thin, keep durable knowledge in skills, and keep passive
  invariants in instructions.

### Guardrails required for non-trivial Copilot assets

Copilot, especially with high-reasoning models, performs better when the asset
author closes off predictable failure modes explicitly.

For non-trivial prompts, agents, and skills, prefer to include all three:

1. **Examples** - when the interaction shape, output shape, or boundary between
   valid choices is easy to misread.
2. **Do Nots** - when there are known failure modes to suppress, such as
   guessing facts, reopening settled choices, or claiming completion without the
   required evidence.
3. **Closed Decisions** - decisions already made by the repo, the asset author,
   or the source artifact that execution should inherit without reopening.

### Decision handling

- Keep **Closed Decisions** separate from **Open Decisions**.
- If a decision is closed, execute against it.
- If a decision is open and materially affects implementation or output, ask.
- Do not restate closed decisions as option sets unless the user explicitly
  wants to revisit them or the source material is contradictory.

### Example quality bar

- Prefer short, repo-shaped examples over abstract filler.
- Good examples use realistic file paths, command patterns, output skeletons,
  review findings, config snippets, or contract fragments from this repo's
  workflow style.
- One precise example is better than several generic ones.

## What to do when editing `copilot-native/`

- Treat `copilot-native/` as the canonical source tree for future Copilot
  assets, not as a live deployed `.github/` folder.
- When updating asset templates inside `copilot-native/`, make the asset itself
  follow the same rules this repo uses to author it.
- If `copilot-native/` instructions disagree with this file, update the
  `copilot-native/` file so it matches the repo-level rule unless there is a
  deliberate, documented exception.

## What to do when reviewing or porting assets

- Review for structure and behavior, not just wording.
- Look for missing guardrails before adding workflow complexity.
- When porting from Claude to Copilot, preserve domain leverage but strip
  command nostalgia and duplicated platform behavior.
- When in doubt, bias toward simpler assets with stronger guardrails.
