# Project Instructions

> **This file is the single source of truth for project conventions.**
> All prompts, agents, skills, and Copilot built-ins should treat this file
> as the project-level configuration source.

This is a starter. Replace the placeholder sections with real content.
Personal preferences live in `.github/instructions/personal.instructions.md`
(already created — edit in place, never overwritten by `cli/skill.sh --update`).

## Asset locations

- Prompts: `.github/prompts/`
- Agents: `.github/agents/`
- Skills: `.github/skills/`
- Passive instructions: `.github/instructions/`
- Templates: `.github/templates/`

## Project overview

<!--
- One-paragraph description of what this repo is for
- Primary users / consumers
- Anything a fresh contributor needs to know on day one
-->

## Stack

<!--
- Language(s) and version(s)
- Build / test / lint commands
- Package manager
-->

## Conventions

<!--
- Code style and formatting rules
- Folder layout
- Naming conventions
- Error handling, logging, async patterns
-->

## Workflow

<!--
- Branch / PR conventions
- How to ship
- Quality gates before merge
-->

## Closed decisions

<!--
- Decisions already made for this repo that Copilot should inherit without re-litigating.
- Example: "We use pnpm, not npm. Don't suggest npm commands."
-->

## Pointers

- Personal overrides: `.github/instructions/personal.instructions.md`
- Shared assets installed via [savviety-skills](https://github.com/garyld1962/savviety-skills) — refresh with `cli/skill.sh --copilot --update`.
