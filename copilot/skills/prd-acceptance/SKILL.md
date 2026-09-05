---
name: prd-acceptance
description: "Verify delivered behavior against PRD/AERS criteria with a per-criterion evidence scorecard. Use for acceptance validation, not implementation or a general code-quality review."
---

# PRD acceptance

1. Resolve one requirements source and extract every criterion with stable IDs.
   Detect repository commands, runtime, ports and test environment from actual code.
2. Map each criterion to an appropriate check: build/static, data, API, UI or tests.
   --dry-run returns this verification plan without running it. --recheck narrows a
   previous report to failed/unproved criteria plus checks affected by code changes.
3. Run declared build prerequisites, then checks in dependency order. Use an available
   browser for UI behavior when needed; code wiring is partial evidence of interaction.
   Do not substitute a weaker inspection for a required runtime check silently.
4. Mark criteria pass, fail, partial or unverifiable. Each pass needs actual output or
   a reproducible observation. Record expected versus actual on failure. A manual or
   unavailable check remains unproved until evidence arrives; it never counts as pass.
5. Track only the servers/processes this run starts and stop those specific processes
   afterward. Never kill all background processes. Preserve user data and shared services.
6. Save a scorecard under docs/prd-acceptance or the requested location: source, head
   commit, criteria, method, expected/actual, proof, blockers and next action.
   PASS means every criterion proved. PARTIAL means incomplete proof without a known
   failure. FAIL means any required criterion or prerequisite demonstrably fails.
   Missing proof blocks a successful execution-report gate even when this scorecard
   uses PARTIAL to distinguish it from a demonstrated defect.

## Examples
An interactive control verified only by reading its event handler is partial, not pass.
An API rejection criterion needs the expected status and response, not just a 2xx check.

## Closed decisions and open decisions
Verify the accepted source's behavior, including any deliberately allowed choice.
Flag an ambiguous criterion instead of inventing its expected result.

## Do not
Do not fix implementation during a validation-only request, invent evidence, count
manual checks as successes, or assume a specific framework/port from an example.
