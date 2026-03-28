---
name: review-solution
description: Review a .NET solution (.sln) and write a versioned report to docs/code-reviews/
agent: "Code Review Orchestrator"
argument-hint: "slnPath=<path>"
---

Review a .NET solution.

Solution path (preferred: .sln):
${input:slnPath:Example: MyApp.sln (or leave blank and auto-detect if only one exists)}

Output subdirectory (optional, for batch grouping):
${input:outputSubdir:Example: pcrs, acs, or beqom (leave blank for root)}

Requirements:
- Do not modify product code.
- Create a new versioned report in docs/code-reviews/ (or docs/code-reviews/<outputSubdir>/ if provided)
- Update docs/code-reviews/index.md and docs/code-reviews/latest.md
- If outputSubdir is provided, also update docs/code-reviews/<outputSubdir>/index.md
- Treat solution review as code-level sampling across the solution (not every file).
