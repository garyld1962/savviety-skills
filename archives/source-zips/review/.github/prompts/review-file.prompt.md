---
name: review-file
description: Review a single file and write a versioned report to docs/code-reviews/
agent: "Code Review Orchestrator"
argument-hint: "filePath=<path>"
---

Review a single file.

File path:
${input:filePath:Provide a repo-relative path like src/Foo/Bar.cs}

Requirements:
- Do not modify product code.
- Create a new versioned report in docs/code-reviews/
- Update docs/code-reviews/index.md and docs/code-reviews/latest.md
