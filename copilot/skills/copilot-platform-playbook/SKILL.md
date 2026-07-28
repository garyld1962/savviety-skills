---
name: copilot-platform-playbook
description: Decision framework for designing GitHub Copilot prompts, agents, skills, and instructions in a built-in-first architecture.
---

# Copilot Platform Playbook

Use this skill when designing or reviewing GitHub Copilot assets.

## Core principle

> Do not recreate the platform in custom prompts.

GitHub Copilot already provides built-in workflow capabilities. Custom assets should extend them, not blindly duplicate them.

## Asset decision table

| Need | Best home | Why |
|------|-----------|-----|
| Implementation planning | Built-in `/plan` | Native workflow already exists |
| Default code review | Built-in `/review` | Native review path already exists |
| Broad repo/web investigation | Built-in `/research` | Native research mode already exists |
| Parallel specialist execution | Built-in `/fleet` + `/tasks` | Native worker orchestration and visibility already exist |
| Inspect changed scope | Built-in `/diff` | Native changed-scope inspection already exists |
| PR state and checks | Built-in `/pr` | Native PR workflow surface already exists |
| Background execution visibility | Built-in `/tasks` | Native task tracking already exists |
| Environment inspection | Built-in `/env` | Native environment snapshot already exists |
| Exporting a report or session | Built-in `/share` | Native export path already exists |
| Specialist bounded analysis | Agent | Best for focused role-based work |
| Durable rules / rubrics / heuristics | Skill | Keeps prompts thin |
| Passive always-on constraints | Instruction | Avoids prompt duplication |
| Repo-specific workflow gap | Prompt | Good only when built-ins are insufficient |

## What to keep custom

Good custom assets usually have one of these properties:

- they run a specialized interview
- they encode a domain-specific rubric
- they produce a repeatable artifact with a fixed shape
- they orchestrate a specialist agent set with a clear contract

## Examples

- AERS/story refinement
- structured asset audits
- domain-specific review rubrics
- architecture-specific quality gates

## What not to port one-for-one from Claude

Be suspicious of assets that:

- exist mainly because the Claude command existed
- merely rename a built-in Copilot flow
- duplicate generic planning or review steps without adding domain logic
- mix passive rules, durable knowledge, and orchestration into one giant prompt

## Built-in-aware authoring rules

### Prompts

Prompts should:

- stay thin
- orchestrate a workflow
- reference skills for durable guidance
- mention the relevant built-in next step when appropriate

Prompts should not:

- act like giant instruction dumps
- duplicate all project conventions inline
- replace built-ins without a clear reason

### Skills

Skills should contain:

- rubrics
- checklists
- heuristics
- definitions
- templates
- decision rules

### Agents

Agents should:

- have a bounded role
- produce a clear output shape
- avoid becoming another general assistant layer

### Instructions

Instructions should:

- hold passive, always-on constraints
- prevent repeated prompt boilerplate
- encode authoring discipline
- handle cross-shell execution rules when environment differences matter

## Copilot features to actively leverage

- `/plan` for planning
- `/review` for default review
- `/research` for broader discovery
- `/fleet` for parallel specialist passes
- `/diff` for changed-scope inspection
- `/pr` for PR state and checks
- `/tasks` for background work visibility
- `/agent` for specialist agent usage
- `/skills` for skill management
- `/instructions` to inspect active instruction layers
- `/env` for environment inspection
- `/share` for exporting a report or session
- `/model` for deliberate model switching
- `@file` mentions for precise context
- `/context` and `/compact` for context management

## Environment-aware authoring

When assets emit commands or shell guidance, design for:

- PowerShell usage
- WSL/Linux usage
- deliberate PowerShell-to-WSL routing when Linux tooling is required

Do not assume one terminal model for every user.

Prefer:

- a shared environment-detection skill
- a passive execution-environment instruction
- prompts that state the detected mode before giving commands

## Migration heuristic

When reviewing an existing asset:

### Keep

Keep it if it adds domain leverage or repeatable structure.

### Simplify

Simplify it if it mostly wraps a built-in.

### Split

Split it if one file is doing too much:

- prompt orchestration
- domain rules
- passive constraints
- agent contracts

### Remove

Remove it only if the built-in fully replaces it and the custom layer adds no clarity.

## Recommended portfolio shape

For most repos, prefer:

- a small number of high-value prompts
- strong domain skills
- a few specialist agents
- disciplined instructions
- heavy use of built-ins

## Do Nots

- Do not recreate built-in `/plan`, `/review`, or `/research` flows as custom
  prompts unless the custom layer adds real domain leverage.
- Do not mix prompt orchestration, durable domain rules, and passive
  instructions into one giant asset when they should be split.
- Do not assume one shell or terminal model for every user when an asset emits
  commands.

## Closed Decisions

- Built-in first is the default design posture for Copilot assets in this repo.
- Prompts stay thin, skills hold durable guidance, agents stay bounded, and
  instructions carry passive always-on constraints.
- When an asset mostly duplicates a built-in, simplify or retire it instead of
  preserving it for name parity.

## Output format for audits

When using this skill in an audit, organize recommendations as:

1. Keep
2. Simplify
3. Add
4. Retire later

That keeps migration work practical instead of theoretical.
