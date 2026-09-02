---
name: prd-acceptance
description: "Validate implementation against PRD acceptance criteria. Reads a PRD, extracts checkboxes, verifies each with evidence, produces a pass/fail scorecard."
---

# /prd-acceptance — PRD Acceptance Validation

**Purpose:** Compare finished implementation against the PRD's acceptance criteria. For each criterion, determine HOW to verify it, execute the check, and report pass/fail with evidence.

## When to Use

- Implementation is complete and you need to verify PRD criteria are met
- Before marking a story/PRD done, or before PR merge on acceptance-driven work
- Re-verifying after a fix via `--recheck`

## When NOT to Use

- PRD is still a draft — use `/prd-validate` first
- You need a general code review — use `/domain-review`
- No PRD/acceptance criteria exist — there's nothing to verify against

## Arguments

- `<path>` — path to the requirements artifact. If not provided, resolve it by the order below.
- `--recheck` — re-run only previously failed criteria
- `--dry-run` — show verification plan without executing

Resolution order — first match wins:

1. The explicit `<path>` argument, if one was supplied.
2. The most recently modified `docs/prds/*/AERS.md`.
3. `./AERS.md` (legacy root location).
4. The most recently modified `docs/prds/*/PRD.md`.
5. `./PRD.md`.
6. `./prompt.md`.

If two or more candidates tie within the same tier, do not guess: ask the
operator which is canonical (interactive) or emit a `plan-ambiguity` finding
and stop (autonomous).

Sibling artifacts — `ONTOLOGY.md`, `UBIQUITOUS_LANGUAGE.md`, and `PRD.md` —
resolve relative to the directory of the resolved requirements file, not the
repo root.

## Step 1: Load the PRD

Read the requirements artifact from the argument path, or resolve one by the
order under `## Arguments`. If nothing resolves, ask the user.

## Step 2: Extract Acceptance Criteria

Scan the PRD for acceptance criteria. These are identified by:
- Markdown checkboxes: `- [ ]` or `- [x]`
- Sections titled "Acceptance Criteria", "Requirements", "Done When", "Definition of Done"
- Numbered lists under those headings

For each criterion, extract:
- **ID**: Sequential (AC-01, AC-02, ...)
- **Text**: The criterion as written
- **Category**: Classify into one of: `build`, `code-structure`, `api`, `ui`, `data`, `test`, `behavior`

If the artifact declares no acceptance criteria at all, halt with a
`no-acceptance-criteria` finding and suggest `/prd-validate` — do not invoke
it, and do not invent criteria to verify against.

Display the extracted criteria and ask the user to confirm before proceeding:

```
Found 24 acceptance criteria in docs/prds/inventory-api/PRD.md:

  Build (4):        AC-01..AC-04
  Code Structure (3): AC-05..AC-07
  API (6):          AC-08..AC-13
  UI (6):           AC-14..AC-19
  Data (4):         AC-20..AC-23
  Test (1):         AC-24

Proceed with verification? [Y/n]
```

## Step 2.5: Extract Ontology Constraints

Locate `ONTOLOGY.md` beside the resolved requirements file, per the
sibling-artifact rule under `## Arguments` — it resolves relative to that file's
directory, not the repo root. `_internal/ontology-readiness` is the authority
for the table shapes read below and for the meaning of `settled` / `deferred` /
`unknown`.

If no sibling `ONTOLOGY.md` exists, skip this step and emit one note line:

```
Ontology: no ONTOLOGY.md beside <requirements-path> — ontology constraints not verified
```

Carry that line into the report. Do not hunt for an ontology elsewhere in the
repo, and do not reconstruct one from the schema.

When the file exists, read `## Entity Types`, `## Fact Types`, `## Lifecycles`,
`## Temporality`, `## Deferred (with re-entry condition)`, and `## Unknown`,
then triage every row by its `Status` cell (or by the section it sits in, for
Deferred and Unknown):

- **`settled`** → becomes an acceptance item, numbered `OC-01`, `OC-02`, … in
  file order across those sections. Record the verbalized constraint text
  verbatim and the constraint kind named in its `Constraints` or `Modality`
  cell.
- **`deferred`** → listed as SKIPPED (deferred), quoting its re-entry condition
  from the `Re-entry condition` column. Never verified — it is outside the UoD
  for this release, and testing it would fail correct code.
- **`unknown`** → listed as SKIPPED (unknown), quoting the `Why unknown` cell.
  An unknown row has no agreed behaviour to test against.

**Never invent a constraint that is not in a settled row.** If the schema
enforces a rule the ontology is silent about, that is not an `OC-` item — it is
at most a note in the verdict.

### Constraint → verification mapping

| Constraint kind | Verification | What the check does |
|---|---|---|
| uniqueness | duplicate-insert test | Insert a second record carrying the same value in the unique role; assert it is rejected (constraint violation, 409, or field-level validation error) and the first record is unchanged. |
| mandatory role | null-rejection test | Create the record with the mandatory role null or absent; assert rejection with a field-level error naming that role. |
| total state machine | exhaustive transition test | Drive every transition declared in the `## Lifecycles` table and assert each succeeds; assert every (state, event) pair *not* in the table is rejected; assert each terminal state has no exit. |
| value domain | boundary test | Exercise the lowest and highest legal values (accepted) and the value just outside each bound plus one ill-typed value (rejected). |
| alethic rule | schema or type-level check | Read the schema or type definition and assert the rule is enforced there — `NOT NULL`, `UNIQUE`, `CHECK`, enum, non-nullable type — not only in application code. |
| deontic rule | validation or alert check | Assert the rule is enforced on a validation path or raises an alert (request rejected with a message, or the alert/audit hook fires), and that it is deliberately *not* a schema constraint. |

A settled row too thin to derive a concrete check from — no named field, no
stated transition, no bound — is recorded as `UNVERIFIABLE` with the row quoted.
Do not guess the missing detail.

Report the triage before verification runs:

```
Ontology: docs/prds/inventory-api/ONTOLOGY.md
  Settled → OC-01..OC-09
  SKIPPED (deferred): 3    SKIPPED (unknown): 1
```

## Step 3: Plan Verification

For each criterion, determine the verification method. Do NOT guess — read the project first.

### Verification Methods

| Category | Method | How |
|----------|--------|-----|
| `build` | Run command | Execute the build/install/dev command and check exit code |
| `code-structure` | File/code search | Verify files exist, exports are present, imports are correct |
| `api` | HTTP request | Start the server, hit the endpoint, check response shape/status |
| `ui` | Code inspection | Read component code, verify elements/handlers exist |
| `data` | Schema + code check | Read schema, verify constraints, check mutation logic |
| `test` | Run tests | Execute test suite, check for specific test files |
| `behavior` | Combined | May need multiple methods — run code + inspect output |

### Detection Phase (MANDATORY before any execution)

Before running any verification:

1. **Detect package manager**: Read `package.json`, check for lockfiles
2. **Detect project scripts**: `pnpm run` / `npm run` — what's available?
3. **Detect API port**: Read the API entry point or config for the port number
4. **Detect web port**: Read Next.js config or package.json dev script for the port
5. **Detect test framework**: vitest, jest, mocha — check devDependencies
6. **Detect database**: Read schema files, check for migration scripts

Record all detected values before proceeding. Do NOT assume ports, commands, or paths.

### For `--dry-run`: Stop here and display the verification plan

```
AC-01: `pnpm install` succeeds
  Method: build
  Command: pnpm install
  Pass if: exit code 0

AC-08: POST /items with missing title returns 400
  Method: api
  Prereq: API server running on port <detected>
  Command: curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:<port>/api/v1/items -H 'Content-Type: application/json' -d '{}'
  Pass if: HTTP 400, response body contains "error" and "title"
```

## Step 4: Execute Verification

Run checks in dependency order:

### Phase 1: Build (must pass before anything else)
Run install, build, typecheck. If ANY fail, stop and report — no point checking API/UI if it doesn't compile.

### Phase 2: Code Structure
Verify file existence, exports, imports, shared package usage. These are static checks — no server needed.

### Phase 3: Data Integrity
Read schema definitions, check for computed vs stored fields, verify validation logic exists in code.

### Phase 3b: Ontology constraints
Verify each `OC-` item from Step 2.5 using the row for its constraint kind in
the **Constraint → verification mapping**. Reuse the Phase 3 reads (schema
files, migrations, validation modules) and the test framework detected in
Step 3; run an `OC-` check against the API in Phase 4 when it needs a live
endpoint. Record evidence in the same form as `AC-` items — the schema line, the
migration statement, the test name and exit code, or the rejected request's
status and body. Carry SKIPPED rows through unverified with their reason, and
`UNVERIFIABLE` rows with the ontology text quoted.

### Phase 4: API
Start the API server in background. Run endpoint checks. Kill the server when done.

**For each API check:**
1. Make the HTTP request
2. Capture status code AND response body
3. Compare against expected values from the PRD
4. Record evidence (actual status code, actual response snippet)

### Phase 5: UI
UI checks are primarily code inspection (does the component exist, does it have the right handlers, does it call the right API). For interactive behavior (live preview, click-to-sort), verify the code wiring — do NOT try to run a browser.

### Phase 6: Tests
Run the test suite. Check for specific test file existence if the PRD mentions it.

### Error Handling

- If a server won't start: record as FAIL with the error output, continue with non-server checks
- If a command times out (>30s): record as FAIL with "timeout", move on
- If a check is ambiguous: record as MANUAL with explanation of what to verify by hand
- Kill any background processes (servers) when verification is complete

## Step 5: Produce Report

Write the report to `docs/prd-acceptance/` with this format:

```
docs/prd-acceptance/<YYYY-MM-DD>--<PRD-filename>--acceptance.md
```

### Report Format

```markdown
# Acceptance Report

- **Date:** <YYYY-MM-DD HH:MM>
- **PRD:** <path to PRD file>
- **Ontology:** <path to ONTOLOGY.md | none — ontology constraints not verified>
- **Result:** <PASS | PARTIAL | FAIL>
- **Score:** <passed>/<total> (<percentage>%)

## Summary

| Category | Pass | Fail | Manual | Total |
|----------|------|------|--------|-------|
| Build | N | N | N | N |
| Code Structure | N | N | N | N |
| API | N | N | N | N |
| UI | N | N | N | N |
| Data | N | N | N | N |
| Test | N | N | N | N |
| Ontology | N | N | N | N |
| **Total** | **N** | **N** | **N** | **N** |

SKIPPED ontology rows (deferred, unknown) are listed below and excluded from
this table and from the percentage.

## Criteria Results

### PASS

- **AC-01** `pnpm install` succeeds
  - Evidence: exit code 0, 847 packages installed
- **OC-03** A **Product** is identified by `sku` (uniqueness)
  - Check: duplicate-insert test
  - Evidence: second insert of `sku='ABC-1'` rejected — `UNIQUE constraint failed: products.sku`; row count unchanged at 1

### FAIL

- **AC-08** POST /items with missing title returns 400
  - Expected: HTTP 400 with field-level error for "title"
  - Actual: HTTP 500 — unhandled validation error
  - Evidence: `{"error":"Internal Server Error"}`
- **OC-06** Every **Order** state has a defined exit; `Cancelled` is terminal (total state machine)
  - Check: exhaustive transition test
  - Expected: `Cancelled → Shipped` rejected
  - Actual: transition accepted; order moved to `Shipped`
  - Evidence: `PATCH /orders/7 {"state":"shipped"} → 200`

### SKIPPED (ontology)

- **Shipment lifecycle** — deferred
  - Re-entry condition: "When partial shipments enter scope"
- **Currency value domain** — unknown
  - Why unknown: "No decision on multi-currency pricing"

### UNVERIFIABLE (ontology)

- Settled row with no derivable check, quoted verbatim, and what is missing
  (named field, stated transition, or bound). Not guessed at.

### MANUAL

- **AC-15** Score selectors are interactive (not plain text inputs)
  - Reason: Requires visual/browser inspection
  - Guidance: Open /items/new and verify score fields are clickable selectors

## Verdict

<1-3 sentence assessment: what's working, what's broken, what's the critical path to PASS>
```

### Result Logic

Score `AC-` and `OC-` items together — one denominator, one percentage.

- **PASS**: all criteria pass (MANUAL counts as pass — they're noted for human spot-check)
- **PARTIAL**: ≥70% but not all pass, no build failures
- **FAIL**: <70% pass OR any build failure

SKIPPED ontology rows (deferred, unknown) are excluded from both numerator and
denominator — nothing was claimed, so nothing failed. `UNVERIFIABLE` rows stay
in the denominator and do not pass: a settled constraint no one can test is a
defect in the ontology, not a verification you may drop.

## Step 6: Response

```
Acceptance: <RESULT> — <passed>/<total> (<percentage>%)

PRD: <path>
Ontology: <path | none>
Report: <report-path>

Failed:
  AC-08: POST /items missing title → 500 instead of 400
  AC-12: GET /stats returns empty instead of counts
  OC-06: Cancelled → Shipped accepted (200); Cancelled must be terminal

Skipped (ontology, not verified):
  Shipment lifecycle — deferred: "When partial shipments enter scope"
  Currency value domain — unknown: "No decision on multi-currency pricing"

Manual (verify by hand):
  AC-15: Score selectors are interactive
  AC-17: Priority preview updates live

Next steps:
  1. Fix validation error handling in POST /items
  2. Implement /stats endpoint aggregation
  3. Run `/prd-acceptance --recheck` after fixes
```

## Rules

1. **Read the PRD exactly.** Verify what it says, not what you think it should say. If the PRD says "soft delete OR hard delete — your call", check that ONE of them is implemented and documented. Do not fail because you'd have chosen differently.
2. **Evidence required.** Every PASS needs evidence (exit code, response body, code snippet). Every FAIL needs expected vs actual. No bare pass/fail without proof.
3. **Do NOT fix code.** This is validation only. Report what's broken, do not repair it.
4. **Kill your processes.** Any background servers started during verification MUST be killed before the skill exits.
5. **Detect, don't assume.** Ports, commands, paths, frameworks — detect them from the project. The PRD might say port 3001 but the implementation might use 8080. Check the actual code.
6. **Build first.** If the project doesn't compile, stop early. API and UI checks are meaningless against broken code.

## Contract

- **Inputs:** path to the PRD/AERS to verify against (or the resolution order under `## Arguments`); optionally the sibling `ONTOLOGY.md`, whose `settled` rows become `OC-` items per Step 2.5 and whose table shapes and item states are defined by `_internal/ontology-readiness`; the built / running application. Calls `/domain-review` when defects warrant a structured list; it does not call `/prd-validate` — an artifact with no acceptance criteria halts with `no-acceptance-criteria` and suggests `/prd-validate` instead.
- **Preconditions:** project compiles; required services (DB, queue, etc.) are reachable; ports/paths detected from the actual implementation, not assumed from the PRD.
- **Outputs:** acceptance report with PASS/FAIL per `AC-` and `OC-` criterion plus evidence (exit code, response body, code snippet, screenshot reference); list of mismatches between PRD and implementation.
- **Postconditions:** all background processes started during verification are killed before exit; report attached to the PRD or the run report; no code edits are made; no `deferred` or `unknown` ontology row is verified or reported as passing.
- **Failure modes:** artifact declares no acceptance criteria → halt with `no-acceptance-criteria` and suggest `/prd-validate`; no sibling `ONTOLOGY.md` → skip Step 2.5 with one note line carried into the report, never reconstruct an ontology; ontology row without enough detail to derive a test → report as `UNVERIFIABLE`, do not guess; build fails → halt early; required service unreachable → fail with platform-specific setup instructions; PRD declares behaviour the implementation contradicts → report as `prd-implementation-mismatch`, do not assume the PRD is wrong.
