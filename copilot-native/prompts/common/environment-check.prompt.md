---
description: >-
  Detect the current shell and OS, then determine safe command routing
  using the user's env config. Use when the execution environment is
  ambiguous or the repo may be used from multiple shell families.
argument-hint: "[optional path or command pattern to evaluate]"
agent: "agent"
tools:
  - read
  - search
  - execute
---

# Environment Check

Use this prompt when the execution environment is ambiguous and you need to determine safe command routing before proceeding.

Do not use this prompt when the environment is obvious and no shell-specific guidance is needed.

Follow the skill: `.github/skills/execution-environment/SKILL.md`

## What to Do

1. Follow the detection protocol in the execution-environment skill
2. Check whether the user has routing rules in `env.config.md`
3. Match the detected environment against routing rules (if present)
4. Report only when the environment is ambiguous or mismatched

## Output

Return only the fields that help resolve a real execution ambiguity:

- detected shell
- detected OS
- recommended execution strategy
- whether terminal switching is preferable (per user's routing rules)
- example safe command pattern

If the environment is unambiguous, proceed silently.

## CRITICAL: Do Not Guess

- Do NOT assume any specific shell without detecting it.
- Do NOT emit commands in the wrong shell syntax.
- Do NOT recommend shell wrappers unless the user's routing rules call for it.
- Do NOT force a structured environment report when a silent check is sufficient.
- Do NOT hardcode shell names, OS names, or host names in your response.
