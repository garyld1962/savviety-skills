---
name: goal
description: "Turn a rough idea into a clear outcome, problem statement, success measures and scope before requirements work. Use for goal discovery, not an already written PRD or an implementation request whose outcome is clear."
---

# Goal discovery

Options: --append [path] (default goals.md), --linear <team-or-project>, --no-persist.
Reject conflicting persistence options rather than guessing where to write.

## Workflow
1. Capture the user's desired change in plain language: who benefits, their current
   difficulty, and what observable outcome would be better.
2. Separate an outcome from a proposed solution without discarding a solution the
   user has deliberately chosen. Ask at most three focused questions, one at a time,
   and only for gaps that materially affect the goal.
3. Produce: Goal; Problem; Beneficiaries; Success measures; In scope; Out of scope;
   Constraints; Assumptions/Open decisions. Make success observable without inventing
   arbitrary metrics. Mark a missing baseline or target as open.
4. If persistence was requested, --append appends an identified goal to the chosen
   file without replacing prior content. Check for an existing equivalent first.
   --linear creates a goal issue through an available connection after the team/project
   is resolved, then returns its real link. On uncertain response, check before retry.
   --no-persist and ordinary discovery return the result without writing.
5. Hand off to ideate or requirements refinement when requested; do not automatically
   begin implementation, create more tickets or run a long interview.

## Examples
- "I want an analytics dashboard" → clarify the decision it should help someone make,
  while preserving a dashboard if the user has settled on it.
- "Append this goal to our planning file" → inspect and append within that authorization.

## Closed decisions and open decisions
Keep settled constraints and solution choices visible. Ask about missing outcomes,
beneficiaries or measures, not preferences already supplied.

## Do not
Do not force this interview into batch execution, reframe a precise build request as
an unsolicited discovery session, or claim a Linear issue was created without evidence.

## Codex integration
Use `$goal` explicitly or let its description match the request. Resolve sibling
skills inside this plugin. Read AGENTS.md before repository edits; honor the current
host's tool access and delegation rules. Do not require another platform's runtime.
