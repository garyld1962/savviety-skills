---
description: >-
  Validate implementation against PRD acceptance criteria. Reads a PRD,
  extracts checkboxes, verifies each with evidence, produces a pass/fail
  scorecard.
argument-hint: '<path-to-prd> [--recheck] [--dry-run]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - codebase
  - edit
---

# Acceptance Validation

Compare finished implementation against a PRD's acceptance criteria. For each criterion, determine HOW to verify it, execute the check, and report pass/fail with evidence.

---

## CRITICAL: Do Not Guess

- **PRD location**: The user provides the path. If not, check `test_prd.md`, `PRD.md`, `docs/plans/*.md`. Do NOT invent a PRD path.
- **Package manager**: DETECT from lockfiles (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `bun.lockb`). Do NOT assume `npm`.
- **Ports**: READ the API and web entry points or config files to find ports. The PRD may say 3001 but the code may use 8080. Check the ACTUAL code.
- **Commands**: READ `package.json` scripts before running anything. Do NOT assume `npm run dev` or `pnpm dev` exists.
- **Test framework**: CHECK `devDependencies` for vitest, jest, mocha. Do NOT assume vitest.
- **Acceptance criteria**: Extract EXACTLY what the PRD says. Do NOT add criteria the PRD doesn't list. Do NOT reinterpret "soft delete OR hard delete" as requiring both.
- **Evidence**: Every PASS and FAIL needs proof. A bare checkmark with no evidence is not acceptable.

### CORRECT

```
Detecting port...
Read: packages/api/src/index.ts
Found: app.listen(3001)
API port: 3001
```

### INCORRECT

```
# WRONG: Guessing port from PRD without checking code
API port: 3001 (from PRD)  # <- The implementation might use a different port. READ THE CODE.
```

---

## Step 1: Load the PRD

Read the PRD file from the user's argument. If no path given, search in order:
1. `test_prd.md` in project root
2. Most recently modified `docs/plans/*.md`
3. `PRD.md` or `prd.md` in project root

If nothing found, ask the user.

---

## Step 2: Extract Acceptance Criteria

Scan the PRD for acceptance criteria. Identify them by:
- Markdown checkboxes: `- [ ]` or `- [x]`
- Sections titled "Acceptance Criteria", "Requirements", "Done When", "Definition of Done"
- Numbered lists under those headings

For each criterion extract:
- **ID**: Sequential (AC-01, AC-02, ...)
- **Text**: The criterion exactly as written
- **Category**: Classify as `build`, `code-structure`, `api`, `ui`, `data`, `test`, `behavior`

Show the extracted list and ask the user to confirm before proceeding.

---

## Step 3: Detect Project Tooling (MANDATORY)

Before running ANY verification, detect:

```
1. Package manager:   <read lockfiles>
2. Install command:   <from package.json or detected PM>
3. Build command:     <from package.json scripts>
4. Dev command:       <from package.json scripts>
5. Test command:      <from package.json scripts>
6. API port:          <read API entry point / config>
7. Web port:          <read Next.js config or dev script>
8. Test framework:    <from devDependencies>
9. Database:          <from schema files / dependencies>
```

### CORRECT detection

```
Read: pnpm-lock.yaml exists -> package manager is pnpm
Read: package.json scripts -> "dev": "turbo dev", "build": "turbo build", "test": "turbo test"
Read: packages/api/src/index.ts -> app.listen(process.env.PORT || 3001)
Read: packages/web/package.json -> "dev": "next dev --turbopack -p 3000"
Read: packages/api/package.json devDependencies -> vitest
Read: packages/db/src/schema.ts -> SQLite via drizzle-orm
```

### INCORRECT detection

```
# WRONG: Not reading, just assuming
Package manager: pnpm (monorepo so probably pnpm)  # <- READ the lockfile
API port: 3001 (PRD says so)  # <- READ the code
Test framework: vitest (common choice)  # <- READ devDependencies
```

Record all detected values. Display them. Proceed only after detection is complete.

---

## Step 4: Plan Verification

For each criterion, determine the verification method:

| Category | Method | How |
|----------|--------|-----|
| `build` | Run command | Execute and check exit code |
| `code-structure` | File/code search | Verify files exist, exports present, imports correct |
| `api` | HTTP request | Start server, hit endpoint, check response status + body |
| `ui` | Code inspection | Read components, verify elements/handlers/API calls exist |
| `data` | Schema + code check | Read schema, verify constraints and mutation logic |
| `test` | Run tests | Execute test suite, check for specific test files |
| `behavior` | Combined | Multiple methods as needed |

**For `--dry-run`:** Stop here. Display the verification plan showing each criterion, its method, the command or check, and the pass condition.

---

## Step 5: Execute Verification

Run checks in dependency order. If an earlier phase fails critically, later phases may be skipped.

### Phase 1: Build

Run install, build, typecheck. If ANY fail, record them and continue with what you can — code-structure and data checks don't need a running build.

### Phase 2: Code Structure

Verify file existence, exports, imports, shared package usage. Static checks — no server needed.

### Phase 3: Data Integrity

Read schema definitions. Check computed vs stored fields. Verify validation logic exists.

### Phase 4: API

1. Start the API server in background
2. Wait for it to be ready (poll the health endpoint or check for listening message in output)
3. Run endpoint checks — capture status code AND response body for each
4. Kill the server when done

**IMPORTANT:** If the server won't start, record as FAIL with the error output and continue with non-server checks. Do NOT retry indefinitely.

### Phase 5: UI

Code inspection only. Verify components exist, have correct handlers, call correct APIs. For interactive behavior (live preview, click-to-sort), verify the code wiring exists. Do NOT try to run a browser.

### Phase 6: Tests

Run the test suite. Check for specific test files if the PRD requires them.

### Cleanup

Kill ALL background processes (servers, watchers) before finishing. This is mandatory.

---

## Step 6: Write Report

Write to `docs/acceptance/<YYYY-MM-DD>--<prd-filename>--acceptance.md`.

### Report Format

```markdown
# Acceptance Report

- **Date:** <YYYY-MM-DD HH:MM>
- **PRD:** <path to PRD file>
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
| **Total** | **N** | **N** | **N** | **N** |

## Criteria Results

### PASS

- **AC-01** `pnpm install` succeeds
  - Evidence: exit code 0, 847 packages installed in 12.3s

### FAIL

- **AC-08** POST /items with missing title returns 400
  - Expected: HTTP 400 with field-level error for "title"
  - Actual: HTTP 500 with generic error
  - Evidence: `curl -s -X POST http://localhost:3001/api/v1/items -H 'Content-Type: application/json' -d '{}'` returned `{"error":"Internal Server Error"}`

### MANUAL

- **AC-15** Score selectors are interactive (not plain text inputs)
  - Reason: Requires visual/browser inspection
  - Guidance: Open /items/new in a browser and verify score fields are clickable selectors, not text inputs

## Verdict

<1-3 sentence assessment: what's working, what's broken, what's the critical path to PASS>
```

**IMPORTANT:** You MUST write this file. Do not just display results in chat. The report must be persisted.

### Result Logic

- **PASS**: All criteria pass (MANUAL counts as pass for scoring)
- **PARTIAL**: >70% pass, no build failures
- **FAIL**: <70% pass OR any build failure

---

## Step 7: Response

```
Acceptance: <RESULT> -- <passed>/<total> (<percentage>%)

PRD: <path>
Report: <report-path>

Failed:
  AC-08: POST /items missing title -> 500 instead of 400
  AC-12: GET /stats returns empty object

Manual (verify by hand):
  AC-15: Score selectors are interactive
  AC-17: Priority preview updates live

Next steps:
  1. Fix validation error handling in POST /items
  2. Implement /stats aggregation
  3. Run `/acceptance --recheck` after fixes
```

---

## Rules

1. **Read the PRD exactly.** Verify what it SAYS, not what you think it should say. If the PRD says "your choice", check that ONE option is implemented. Do NOT fail because you'd choose differently.
2. **Evidence required.** Every PASS needs proof (exit code, response body, code snippet). Every FAIL needs expected vs actual. No bare checkmarks.
3. **Do NOT fix code.** This is validation only. Report what's broken, do not repair it.
4. **Kill your processes.** Any background servers started during verification MUST be killed before the skill exits. Use process cleanup as the final step.
5. **Detect, don't assume.** Ports, commands, paths, frameworks — detect from the project. The PRD might say one thing; the code might do another. Trust the code for "what it does", trust the PRD for "what it should do."
6. **Build first.** If install/build/typecheck fails, report it and skip phases that need a running server. Code-structure and data checks can still run.
7. **Timeout and move on.** If a command hangs for >30 seconds, kill it, record FAIL with "timeout", continue to the next criterion.
8. **MANUAL is OK.** Some criteria (visual behavior, interactive UX) cannot be verified from code alone. Mark them MANUAL with clear guidance on what to check by hand. Do NOT fake a pass.
