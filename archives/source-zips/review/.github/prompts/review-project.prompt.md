---
name: review-project
description: Review a .NET project (.csproj) and write a versioned report to docs/code-reviews/
agent: "Code Review Orchestrator"
argument-hint: "projectPath=<path>"
---

Review a .NET project.

Project path (preferred: .csproj):
${input:projectPath:Example: src/MyService/MyService.csproj (or leave blank and auto-detect if only one exists)}

Requirements:
- Do not modify product code.
- Create a new versioned report in docs/code-reviews/
- Update docs/code-reviews/index.md and docs/code-reviews/latest.md
- Treat project review as code-level sampling within the project (not every file).
