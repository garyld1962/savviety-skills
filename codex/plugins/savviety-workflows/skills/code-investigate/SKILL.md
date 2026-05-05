---
name: code-investigate
description: "Evidence-backed code investigation across one or more repos. Use for durable reports about where behavior lives, how a pattern is implemented, or whether a behavior exists."
---

# Code Investigate

Run a read-first investigation and produce a durable report.

Read `references/workflow.md` for the Codex-native investigation workflow. `references/legacy/` is archival only.

## Workflow

1. Define the investigation question and scope.
2. Search with `rg` and targeted file reads.
3. For multi-repo work, ask before using subagents; otherwise investigate sequentially.
4. Record evidence with file references, confidence, and gaps.
5. Write a Markdown report only when the user asks for an artifact.
