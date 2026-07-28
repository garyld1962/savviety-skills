---
name: repo-delivery
description: "Declarative schema every repo must satisfy so execute-plan, checkpoint, and review-adversarial don't have to guess. Not user-invokable."
---

# Repo Delivery

Required in the repo's `CLAUDE.md`:

```
## Commands
lint: <cmd>
build: <cmd>
test: <cmd>
default_branch: <name>
package_manager: <npm|pnpm|yarn|bun|pip|poetry|cargo|go|dotnet|...>
adversarial_triggers:                 # optional; default in execute-plan
  - src/auth/**
  - migrations/**
retry_budget:                         # optional; default 20 retries / 60 min
  max_total_retries: 20
  max_wall_clock_minutes: 60
auto_accept_deviations:               # optional; default [lockfile, dep-patch-bump, formatter]
  - lockfile
  - dep-patch-bump
  - formatter
auto_generated_paths:                 # used with auto-generated-files category
  - "**/generated/**"
```

Consumers: `execute-plan` (all), `checkpoint` (lint/build/test/package_manager), `review-adversarial` (adversarial_triggers). Missing section → consuming skill halts with `Repo missing required CLAUDE.md ## Commands section. See _rubrics/repo-delivery for the schema.` No heuristic detection, no manifest fallback.

## Guardrails

- Read commands / branch / package-manager from the schema — never assume.
- No auto-ship of unrelated changes; no hotfix-turned-refactor.
- No "success" without the configured verification passing.
