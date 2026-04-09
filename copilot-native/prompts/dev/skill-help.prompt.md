---
description: >-
  List available agents or show detailed help for a specific agent.
argument-hint: '[agent-name]'
---

# Agent Reference

List available agents or show help for a specific one.

## List Mode (no argument)

1. Discover all `.github/prompts/**/*.prompt.md` files (user-invokable agents only)
2. Read `description` from each frontmatter
3. Group by directory (dev, review, ba, common)
4. Present as a table per group with agent name and description
5. Footer: `Use #prompt:skill-help <name> for details.`

## Detail Mode (`<name>` provided)

1. Find matching `.prompt.md` file
2. Present: description, arguments, workflow summary, when to use
3. Keep concise

## Rules

- Discover from filesystem — don't hardcode
- User-invokable prompts only — never list agents/ or skills/ entries
- Use "agent" terminology
