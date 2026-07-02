---
name: repo-delivery
description: "Declarative schema every repo must satisfy so execute-plan, checkpoint, and review-adversarial don't have to guess. Not user-invokable."
user-invocable: false
internal: true
---

# Repo Delivery

Required in the nearest applicable `AGENTS.md`. A legacy `CLAUDE.md` `## Commands` section may be read only when a repository has not migrated to Codex instructions.

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
auto_accept_deviations:               # optional; default [lockfile, dep-patch-bump, formatter, auto-generated-files]
  - lockfile
  - dep-patch-bump
  - formatter
  - auto-generated-files              # no-op unless auto_generated_paths is also declared
auto_generated_paths:                 # required for the auto-generated-files category to fire
  - "**/generated/**"
runtime_probes:                       # optional; commands that prove native/runtime deps load
  - node -e "require('better-sqlite3')"
  - node -e "require('sharp')"
```

Consumers: `execute-plan` (all), `checkpoint` (lint/build/test/package_manager/runtime_probes), `review-adversarial` (adversarial_triggers). Missing section -> consuming skill halts with `Repo missing required AGENTS.md ## Commands section. See repo-delivery for the schema.` Use lightweight tool discovery as a fallback only when the user explicitly asks to proceed without a contract.

`runtime_probes` close the typecheck-vs-runtime gap: a build that passes `tsc --noEmit` can still fail at startup when a native binding (`better-sqlite3`, `sharp`, `canvas`), generated client, or driver cannot load against the current Node ABI. Each probe is a one-liner that exits 0 when the dependency loads. Failures are treated as build failures by `checkpoint` and `execute-plan`.

## Guardrails

- Read commands / branch / package-manager from the schema — never assume.
- No auto-ship of unrelated changes; no hotfix-turned-refactor.
- No "success" without the configured verification passing.
