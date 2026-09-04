---
name: refactor-brief
description: "Investigate a refactoring problem and produce an RFC with preserved behavior, interface decisions, characterization tests and small working commits. Use for refactor planning or an issue brief, not for applying a refactor that is already specified."
---

# Refactor brief

## Workflow
1. Clarify the pain, affected users/maintainers and desired outcome. Inspect the code,
   callers, tests and domain vocabulary. Ask only targeted questions the repository
   cannot answer. Distinguish current evidence from assumptions.
2. Identify invariants, public contracts, data behavior and boundaries that must remain
   stable. Compare plausible approaches; use design-twice when a substantial interface
   decision is still open. Preserve settled decisions.
3. Write an RFC with Problem, Proposed solution, Scope/non-goals, Commit sequence,
   Decision record, Testing decisions, Risks/rollback, and Further notes.
   The decision record covers modules/interfaces and any schema/API compatibility.
4. Make the sequence small and working after every commit: characterization first,
   introduce a seam, migrate callers incrementally, remove obsolete code, verify.
   Tie tests to preserved behavior and likely regression, not implementation structure.
5. Keep the issue's problem and sequence portable at the domain/behavior level.
   Put source-path evidence in an investigation appendix when it helps reviewers.
6. If the user requested a GitHub RFC issue, run gh-readiness, check duplicates and
   create it using the available connection/CLI. Otherwise return or save the brief
   as requested. Hand off to execute-prd only when implementation is requested.

## Example
"Write a refactor RFC for these duplicated pricing rules" → caller/behavior evidence,
characterization cases, incremental migration and an explicitly unchanged price contract.

## Closed decisions and open decisions
Record selected interfaces and authority. Expose unresolved compatibility decisions;
do not hide behavior changes inside a refactor.

## Do not
Do not edit production code during planning, invent a big-bang rewrite, or file an
issue when the request only asks for a draft.

## Copilot integration
This skill is the durable entrypoint for Copilot hosts that load agent skills.
The matching prompt file is an optional VS Code shortcut. Read repository instructions
before edits; use the tools actually exposed by the host, including connected GitHub
access when available. A prompt or skill does not itself grant additional permissions.
