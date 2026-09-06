---
name: simplify
description: Explain dense progress reports, task or wave summaries, blockers and
  decision requests in plain language. Use /simplify, 'explain that simply', or before
  user-facing PRD/plan execution updates. Simplifies explanations, not code.
whenToUse: Explain dense progress reports, task or wave summaries, blockers and decision
  requests in plain language. Use /simplify, 'explain that simply', or before user-facing
  PRD/plan execution updates. Simplifies explanations, not code.
---


# Simplify an update

Read [the output guidance](references/output.md) and use it to rewrite the
explanation for the user.

With `/skill:simplify`, use the latest substantive assistant update or execution
summary. If the user supplies text, a report, or a file path, use that instead.
Read only the relevant source and linked evidence needed to understand it.
If there is no identifiable source, ask for the message to explain.

Return the rewritten explanation directly. Manual invocation does not rerun
checks, edit the source, implement fixes, or approve a proposed action. During
an active task, continue applying this guidance to subsequent user updates.

## Relationship to other skills

This skill explains work and decisions. It does not refactor code or replace
review, validation, or execution. During PRD/plan execution, use the guidance
as the final wording pass for every assistant-written user update; keep the
underlying workflow and evidence intact.
