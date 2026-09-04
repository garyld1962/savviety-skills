---
name: design-twice
description: "Compare at least three contrasting module or API interfaces before committing to architecture. Use for unresolved interface design in feature/refactor work; skip settled designs, small bug fixes, and implementation-only requests."
---

# Design twice

Despite the name, compare at least three designs before recommending one.

## Workflow
1. Inspect callers, data contracts, constraints, existing patterns and closed decisions.
   State the one interface decision and the behavior all alternatives must preserve.
2. Produce three substantially different designs:
   - minimal surface: one to three public operations hiding the complexity;
   - flexibility: broader composition and extension points;
   - common case: make the usual caller simple, documenting edge-case tradeoffs.
3. For each, give a signature or schema, a realistic caller example, hidden complexity,
   error behavior, tradeoffs and likely misuse. Compare simplicity, depth, generality,
   implementation cost and ease of correct use. Do not compare only names or styling.
4. Use independent agents only when delegation is authorized and exposed by the host.
   Send the same requirements with a different design constraint to each. Otherwise
   work through all three locally and identify that this was one agent's comparison.
5. Recommend a design or synthesis with reasons tied to actual callers. Honor a user's
   delegation of routine technical choices; ask only about a material unresolved choice.
   Record the selected interface, authority and rejected alternatives in the repo's
   established decision format when the task includes planning or persistence.

## Example
For a cache boundary, compare get/set, a configurable cache policy object, and a
single get-or-load operation using the same expiry and error requirements.

## Closed decisions and open decisions
Do not reopen a selected transport, persistence model or public contract. Compare only
the remaining design freedom; expose any requirement conflict before choosing.

## Do not
Do not implement the winning design unless requested, claim local passes are independent
reviewers, or invent tools, models or parallel execution support.

## Codex integration
Use `$design-twice` explicitly or let its description match the request. Resolve sibling
skills inside this plugin. Read AGENTS.md before repository edits; honor the current
host's tool access and delegation rules. Do not require another platform's runtime.
