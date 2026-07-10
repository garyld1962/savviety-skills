---
name: parallel-optimization
description: "Analyze a PRD or plan for safe parallel execution. Produces lanes, ownership, barriers, shared-surface owners, and verification gates."
---

# Parallel Optimization

Use this before parallel implementation.

Read `references/lane-map.md` for the lane-map standard. `references/legacy/` is archival only.

Only propose parallel lanes when write scopes are disjoint or an explicit owner protects shared surfaces. Cap a wave at four lanes and make dependency barriers explicit.
