---
description: >-
  Audit a Copilot asset set (prompts, agents, skills, instructions, and repo
  instructions) against GitHub Copilot platform capabilities. Identify
  duplication with built-ins, missing structure, and a modernization path.
argument-hint: "[path to .github folder or source repo folder]"
agent: "agent"
tools:
  - read
  - search
  - codebase
---

# Copilot Asset Audit

Review an existing Copilot asset set and recommend how to make it more Copilot-native.

Follow the skill: `.github/skills/copilot-platform-playbook/SKILL.md`

## Audit scope

Review:

- prompts
- agents
- skills
- instructions
- repo-level `copilot-instructions.md`
- overlap with Copilot built-ins

## Expected output

Produce:

- strengths worth keeping
- duplicate or weak assets worth simplifying
- gaps where custom assets still add value
- recommended target architecture
- quick wins
- staged migration plan

## CRITICAL: Do Not Guess

- Do NOT assume the repo structure; inspect it.
- Do NOT recommend removing custom assets just because a built-in exists; explain why the built-in is enough or where custom value remains.
- Do NOT rewrite the whole portfolio mentally. Separate "keep", "simplify", and "add".

## Built-in-first rule

When evaluating an asset, ask:

1. Is this replacing a built-in that already works well?
2. Is this adding domain-specific leverage the built-in does not provide?
3. Would this guidance be better placed in a skill or instruction instead of a prompt?
