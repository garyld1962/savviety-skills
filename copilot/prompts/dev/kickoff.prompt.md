---
name: kickoff
description: "Start a requirement or story through audit, readiness, validated planning and requested implementation."
argument-hint: "[requirements path, otherwise AERS.md when unambiguous]"
agent: agent
---

Use [execute-prd](../../skills/execute-prd/SKILL.md) in lightweight kickoff mode.
If no source was supplied and AERS.md is the unambiguous requirements artifact, use it.
For a small direct edit whose scope is settled, do the edit with proportional checks.
A --skip-readiness request can reuse recorded readiness evidence; it never waives
unresolved material requirements or a malformed execution plan. Do not auto-start an
interview in batch mode or ask for implementation approval already given.
