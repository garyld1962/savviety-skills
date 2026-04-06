---
name: code-review-orchestrator
description: Orchestrate multi-domain code review using specialist subagents and write a versioned Markdown report under docs/code-reviews/.
---

# Mission (MVP)

Perform a code review over the requested scope using specialist subagents.
Collect structured findings and write a **versioned** Markdown report to `docs/code-reviews/` (or a subdirectory when `outputSubdir` is provided),
then update:
- `docs/code-reviews/[<outputSubdir>/]index.md` (prepend newest)
- `docs/code-reviews/index.md` (prepend newest, with relative path including subdir if applicable)
- `docs/code-reviews/latest.md` (point to newest)

Findings must follow:
- `../review-foundations/schemas/finding.schema.json`

Severity meaning:
- `../review-foundations/rubrics/severity.md`

Report template:
- `../review-foundations/templates/review-report.template.md`

# Non-goals (MVP)

- Do NOT modify product code.
- Do NOT run builds/tests/scanners yet (we'll add validator workers later).
- Prefer fewer, higher-confidence findings over noisy lists.

# Scope modes (MVP)

You MUST operate in exactly one of these modes:
- **solution**: review a .NET solution (.sln) at code level using sampling (not exhaustive).
- **project**: review a .NET project (.csproj) at a medium depth (sampling; not exhaustive).
- **file**: review a specific file at deep, line-level detail.

If the user request is ambiguous, ask once which mode they want and stop.

# Worker domains (MVP)

Always run:
- csharp-quality
- complexity
- security
- di-architecture

Conditionally run (auto-detected):
- async-safety (if async/await/Task/CancellationToken appear in scope, or the repo is clearly .NET and the scope includes async code)

Optional (prompt user before running):
- k8s-readiness — Ask the user: _"Would you like to include **Kubernetes readiness** analysis (health probes, graceful shutdown, structured logging, resource limits)?"_ Only run if the user confirms. Do NOT auto-detect or silently include this domain.

# Sampling strategy (project / solution mode)

When reviewing a project or solution, do NOT attempt to read every file. Use a tiered approach:

## File classification tiers

- **Tier 1 — Always review** (~high impact):
  - `Program.cs`, `Startup.cs`, DI registration / service-collection files
  - Controllers, minimal-API endpoint files, middleware
  - Background services (`IHostedService`, `BackgroundService`)
- **Tier 2 — Prioritize** (~medium impact):
  - Service-layer classes, repository implementations
  - HTTP client wrappers, database access layers
  - Authentication / authorization configuration
  - Custom exception handlers, filters
- **Tier 3 — Deprioritize** (~low impact):
  - Pure DTOs, records, enums with no logic
  - Auto-generated code (migrations, designer files, `*.g.cs`)
  - Test files (unless review specifically requested)
  - Static asset references, `.resx` files

## Budget caps

- **project mode**: review up to ~40 files (Tier 1 + Tier 2 first, fill remaining with Tier 3).
- **solution mode**: review up to ~60 files across all projects (apply tiers per-project, then merge).

## Discovery

- Parse the `.csproj` or `.sln` to enumerate source files / project references.
- Use `codebase` search to find files matching tier criteria.
- Build an explicit file list before dispatching specialists.

## Communicating the file list

Pass the selected file list to each specialist in the dispatch payload so they know exactly which files to review. In file mode, this is just the single file.

# Output contracts

Each specialist subagent MUST return **ONLY** a JSON array of findings.
The orchestrator aggregates all findings, deduplicates, and passes the reduced array to the report writer.

# Versioned report naming (MVP)

Create a new file:
`docs/code-reviews/[<outputSubdir>/]<YYYY-MM-DD>--<HHMMSS>--<mode>--<slug>--<runId>.md`

Where:
- `outputSubdir` (optional) is the group subdirectory (e.g., "pcrs", "acs", "beqom"). When provided, the report file is created inside `docs/code-reviews/<outputSubdir>/`.
- `YYYY-MM-DD` is today's date (local).
- `HHMMSS` is the current local time (24h, no separators).
- `mode` is solution|project|file
- `slug` is a short, filesystem-safe identifier (solution name, project name, or file name without extension)
- `runId` is a short random id (4–6 lowercase alphanumerics) to avoid collisions.

Also update:
- `docs/code-reviews/<outputSubdir>/index.md` (prepend a bullet linking to the new file — only when `outputSubdir` is set)
- `docs/code-reviews/index.md` (prepend a bullet linking to the new file, using relative path `<outputSubdir>/<filename>.md` when subdir is set)
- `docs/code-reviews/latest.md` (replace content with a summary pointing to the new file, using relative path including subdir)

# State machine (follow exactly)

## STATE 1 — GATHER_SCOPE
- Determine mode: solution|project|file
- Determine target:
  - solution: .sln path or solution name
  - project: .csproj path or project name
  - file: file path
- If the caller provides an `outputSubdir` (e.g., "pcrs", "acs", "beqom"), reports go to `docs/code-reviews/<outputSubdir>/` instead of `docs/code-reviews/`. Store this value for STATE 5.
- If solution/project path is not given:
  - Try to auto-detect by searching for *.sln or *.csproj.
  - If exactly one candidate exists, use it.
  - Otherwise ask the user to specify which one.

## STATE 2 — SELECT_SPECIALISTS
- Select the required worker domains according to the rules above.
- If k8s-readiness is not explicitly included/excluded by the user, **ask the user** whether to include it. Wait for confirmation before proceeding.
- For project/solution mode: build the sampled file list per the sampling strategy above.

## STATE 3 — DISPATCH_SPECIALISTS
- For each selected domain, dispatch a subagent with:
  - mode + target + file list (for project/solution mode)
  - the constraints (MVP non-goals)
  - the finding schema requirement
  - request "JSON array only"

### Error handling
- **Malformed JSON from specialist**: Skip that domain entirely. Add a note to the report: `"Domain <name> returned unparseable output and was skipped."`
- **Empty array `[]`**: Accept silently — this is a valid outcome (no findings for that domain).
- **Specialist failure / timeout**: Skip that domain. Add a note to the report: `"Domain <name> failed and was skipped."`
- **All specialists fail**: Go directly to STATE 6. Report the failure in chat — do not produce an empty report file.

## STATE 4 — REDUCE_FINDINGS
- Deduplicate using these rules:
  1. **Same file + overlapping lineRange + same domain** → keep the finding with higher severity; break ties with higher confidence.
  2. **Same file + overlapping lineRange + different domains** → keep BOTH (cross-domain findings are distinct).
  3. **Same domain + same root pattern across multiple files** (e.g. the same anti-pattern repeated in 5 files) → collapse into ONE finding referencing all affected files in the evidence field.
- After dedup, prefer higher severity; break remaining ties with higher confidence.
- Cap total findings in the final report to:
  - file mode: up to 25
  - project mode: up to 30
  - solution mode: up to 40
  (Keep Blocker/High first, then Medium, then Lower.)

## STATE 5 — WRITE_REPORT
- Dispatch the Review Report Writer with:
  - mode, target, and a human-readable scope string
  - reduced findings JSON
  - filename convention: `YYYY-MM-DD--HHMMSS--<mode>--<slug>--<runId>.md`
  - `outputSubdir` (if set) — the writer will place the report in the correct subdirectory
  - instructions for index/latest updates (both group index and root index when subdir is set)

### Error handling
- **Report writer fails**: Retry once.
- **Second failure**: Output the reduced findings JSON array directly in chat as a fallback so the user still gets results.

## STATE 6 — RESPOND
- In chat: show the top 5 findings (or fewer) and the path of the generated report file.
- If no report was generated (all specialists failed), explain what happened and suggest the user re-run.
