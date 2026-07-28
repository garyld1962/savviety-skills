---
name: ship
description: "Unified delivery workflow for checkpoint, commit preparation, push, PR creation, release steps, and fast hotfix mode. Uses explicit approval for mutating remote actions."
---

# Ship

Codex consolidation for Claude `ship`, `pr`, and `hotfix`.

Read `references/workflow.md` for delivery modes. Use `references/repo-delivery.md` and `references/security-quick-check.md` for shared contracts. Legacy ship, PR, and hotfix references are archival only.

## Modes

- default: checkpoint, prepare commit, push/PR only when approved.
- `--release`: include configured release steps.
- `--fast`: emergency path with targeted gates.

Never create, merge, or release without explicit user approval.
