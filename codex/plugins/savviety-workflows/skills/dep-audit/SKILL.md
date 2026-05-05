---
name: dep-audit
description: "Audit dependencies for vulnerabilities, outdated packages, unused dependencies, and license risk before release or major changes."
---

# Dependency Audit

Use existing project package managers and lockfiles. Read `references/reporting.md` for the report shape. `references/legacy/` is archival only.

## Workflow

1. Detect package ecosystems and lockfiles.
2. Prefer local audit commands already available in the repo.
3. Do not install new audit tools without approval.
4. Summarize critical/high vulnerabilities, license blockers, unused dependencies, and upgrade pressure.
5. Distinguish exploitable production risk from irrelevant dev-only noise.
