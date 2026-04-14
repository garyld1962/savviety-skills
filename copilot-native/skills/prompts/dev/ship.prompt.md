---
description: >-
  Ship completed work through the repo's actual delivery flow: checkpoint,
  commit, push, PR, CI, and release steps when the project supports them.
argument-hint: '[--skip-checkpoint] [--draft]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - edit
---

# Ship

Use this prompt when the work is done and the next job is release orchestration.

Follow the skills:

- `.github/skills/repo-delivery/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`

## Copilot-native usage

- Run `checkpoint` first unless the user intentionally skips it.
- Use the repo's actual PR and CI flow rather than assuming a standard release
  pipeline.
