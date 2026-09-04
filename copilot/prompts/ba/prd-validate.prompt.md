---
description: >-
  Turn a rough story, BRD, AERS draft, or idea into an implementation-ready
  artifact by interviewing the author, closing ambiguity, and generating
  missing sections such as Closed Descision, example contracts, and a
  verification matrix.
argument-hint: "[path to artifact or plain-language ask]"
agent: "agent"
tools:
  - read
  - search
  - edit
  - codebase
---

# AERS Validator

Use this prompt **before** `/plan` when the requirements artifact is still ambiguous.

Follow the skill: `.github/skills/prd-readiness/SKILL.md`

## Copilot-native usage

- If the user references a document, prefer `@file` context or read the exact file.
- Use project instructions from `.github/copilot-instructions.md` if present.
- Keep the interaction one question at a time.
- Do not drift into implementation planning; that belongs in `/plan`.
- The prompt name may still reference `prd-validate` for compatibility, but the preferred artifact term is **AERS**: Agent-Executable Requirements Spec.

## Input → output contract

Treat these as valid inputs:

- business problem statement
- business-oriented PRD
- BRD
- story or epic
- rough engineering notes
- partial AERS draft

The target output is:

- an **AERS** that an engineer or coding agent can execute with minimal re-interpretation

## Output goals

Produce the lightest useful version of:

- gap report
- mandatory `Closed Descision`
- `Open Decisions`
- public API / interface section when relevant
- data models section when relevant
- example JSON or contract snippets where ambiguity exists
- execution preflight
- verification matrix
- UI behavior matrix when UI work is involved
- implementation readiness verdict

## CRITICAL: Do Not Guess

- Do NOT invent settled facts that the artifact or author already knows.
- Do NOT silently choose architecture-impacting defaults when the choice is still open.
- Do NOT overwrite an existing artifact wholesale without showing the proposed additions or changes.
- Do NOT mark the artifact ready if blocking ambiguity remains.
- Do NOT stop at a business-oriented PRD if the user needs an engineering-executable output; convert it into an AERS.

## Built-in-first rule

- Use this prompt to improve the artifact.
- Use `/plan` after the artifact is ready.
- Use `/review` or specialist agents later to challenge implementation, not requirements.
