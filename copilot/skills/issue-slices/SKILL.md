---
name: issue-slices
description: "Break a PRD or parent issue into demonstrable vertical GitHub issues with acceptance and dependency links. Use to create an implementation backlog; use execute-prd for a local execution plan and bug-session for unrelated bug reports."
---

# Issue slices

## Workflow
1. Resolve the canonical PRD from a file or parent issue and the target repository.
   Read the PRD, existing issues, code, tests and closed decisions before decomposing.
2. Propose the smallest end-to-end slices that demonstrate user-visible behavior.
   Include every needed layer in a slice; avoid separate database/API/UI tickets that
   cannot demonstrate value alone. Start with a tracer bullet through the system.
3. For each slice record title, intended behavior, covered requirement/user-story IDs,
   mechanical acceptance, dependencies, and HITL or AFK:
   HITL needs a named material human decision; AFK is sufficiently specified to execute.
   Do not invent stakeholder decisions to label a slice AFK.
4. Check coverage against the entire PRD, dependency cycles and duplicate tickets.
   Review the breakdown with the user only when scope or decisions remain unresolved.
   A clear request to create the backlog already authorizes filing the scoped issues.
5. Run gh-readiness, create blockers first, then replace dependency placeholders with
   returned issue numbers. Each issue contains parent PRD link/source, What to build,
   Acceptance, Blocked by, User stories, and decision needs if any.
6. Return a table of real links, dependencies, mode and coverage. Keep a creation ledger;
   after partial failure, search/reconcile before retrying. Do not change the parent
   issue unless that update was requested.

## Example
"Create issues from this export PRD" → a working single-format export first, followed
by separately demonstrable filtering and authorization behavior with real dependencies.

## Closed decisions and open decisions
Preserve PRD scope and architecture. Name unresolved decisions in HITL slices; only
ask now when they prevent a useful breakdown.

## Do not
Do not implement the issues, split solely by technical layer, drop acceptance criteria,
fabricate dependency IDs or duplicate successfully created slices on retry.

## Copilot integration
This skill is the durable entrypoint for Copilot hosts that load agent skills.
The matching prompt file is an optional VS Code shortcut. Read repository instructions
before edits; use the tools actually exposed by the host, including connected GitHub
access when available. A prompt or skill does not itself grant additional permissions.
