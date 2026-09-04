---
name: review-disposition-governance
description: "Reconcile plan, code and adversarial review findings with explicit proof, terminal dispositions and human risk acceptance. Use at governed review gates and execution closeout."
---

# Review disposition governance

Read [the canonical reporting/disposition contract](../validate-plan/references/reporting.md)
and [execution gates](../validate-plan/references/execution.md). Use the installed
process references and templates under .github/docs for governed run artifacts.

Gather all meaningful findings with stable ID, severity, affected scope, evidence,
impact and recommended remedy. Use critical, major, minor and nit; ambiguity/deviation
are finding categories, not extra severities. Focus senior engineering judgment on
contracts, ownership, error behavior, diagnosability and extension seams; avoid style
rewrites. Classify behavior as proved, partially proved or unproved from actual evidence.

Recheck fixes and disputed evidence. After at most three fix cycles or two unresolved
review rounds, report the blocker and seek arbitration only for a material decision.
Use a distinct reviewer when authorized and available; identify same-agent review
honestly when independent review is unavailable. Do not silently weaken a required
independence gate. Never infer risk acceptance or discard an inconvenient finding.

Reconcile JSON, Markdown and disposition counts at the final code head. Every finding
needs a terminal disposition; deferred minor/nit findings need a named follow-up.
Missing review output is failure. Validate the execution report before claiming success.

## Example
A fixer says a race is fixed but supplies no reproduction/check output → keep it open
until verified. A user explicitly accepts a named remaining risk → record WARN.

## Closed decisions and open decisions
Honor sourced architecture and accepted requirements. Arbitration addresses remaining
contradictions; it does not reopen settled choices.

## Do not
Do not count green tests as universal proof, use vague resolved/High labels, count a
manual check as pass, or label an unresolved disagreement accepted-risk.
