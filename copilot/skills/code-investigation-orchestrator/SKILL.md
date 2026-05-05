---
name: code-investigation-orchestrator
description: "Run a cross-repository code investigation from a natural-language request or explicit pattern list and produce a versioned Markdown index."
argument-hint: "Describe what to find and where to search"
---

# Code Investigation Orchestrator

Search one repo, multiple repos, or a folder of repos for user-requested code patterns or behaviors.

The request may be:

- an exact string or API name
- a regex-like pattern
- a natural-language behavior such as "send email" or "reads or writes a file"
- a mixed request with both explicit patterns and semantic intent

Your job is to clarify the scope, convert the request into a high-signal search plan, dispatch parallel search workers, and write a report.

## When to Use

- You need an evidence-backed index of where a concept appears in code
- You need to search many repositories with one prompt
- The request is behavioral and not easily expressed as one literal grep pattern
- You want a report that groups matches by repo, project, and file

## Required runtime questions

If not already specified in the user request, ask these questions before dispatching workers:

1. **Include matching code lines?**
2. **Add a short summary of what the code is doing at each match?**

If the request does not clearly identify the search target, also ask which scope mode to use.

## Scope modes

You MUST operate in exactly one mode:

- **repo** - one repository
- **repos** - an explicit list of repositories
- **folder** - a directory that contains repositories

If the request could fit more than one mode and the target is not clear, ask once and stop.

## Search surface

Derive the search surface from the request:

- If the user clearly asks for source code, search source code only
- If the request obviously includes infrastructure, scripts, config, tests, templates, or docs, include them
- If the search surface is ambiguous and materially changes results, ask once and stop

## Search planning

Translate the request into a search brief before dispatching workers.

For each repo, build a brief containing:

- the user's original request
- a normalized investigation objective
- likely APIs, symbols, and framework cues
- synonyms and related terms
- disambiguators and exclusions
- the allowed search surface
- whether to include code lines
- whether to include summaries

Do not over-expand to the point that results become noisy.

## Worker strategy

Dispatch one or more parallel search workers covering the selected repositories.

### Model guidance

While running in the default model context, deliberately choose a Codex-family model for each worker:

- **Broad scan / high-volume literal work:** prefer `gpt-5.1-codex-mini`
- **Mixed literal + behavioral search:** prefer `gpt-5.2-codex`
- **Complex semantic interpretation or large repos:** prefer `gpt-5.3-codex`

Use the lightest model that can still execute the search well.

### Parallelization

- Prefer one worker per repository when the repo count is manageable
- Batch very small repositories together only when that reduces overhead without hiding repo boundaries
- Keep repo identity explicit in every worker result

## Match schema

Each search worker must return a JSON array using this shape:

```json
{
  "repo": "beqom-scheduler",
  "project": "beqom-scheduler.csproj",
  "file": "src/Workers/EmailQueueWorker.cs",
  "lineRange": "41-63",
  "matchType": "literal | regex | symbol | framework | semantic",
  "confidence": 0.88,
  "whyMatch": "Uses MailMessage and SmtpClient to construct and send an outbound email.",
  "codeLines": "optional exact snippet",
  "summary": "optional short summary"
}
```

## Aggregation rules

After collecting worker results:

1. Keep repo boundaries intact.
2. Deduplicate matches where `repo + file + overlapping lineRange + same underlying behavior` are the same.
3. For duplicates, keep the higher-confidence entry.
4. Sort by:
   - repo
   - project
   - file
   - starting line
   - confidence descending for ties

## Report output

Dispatch the report writer to create:

- `docs/code-investigations/<YYYY-MM-DD>--<HHMMSS>--<scope>--<slug>--<runId>.md`
- `docs/code-investigations/index.md`
- `docs/code-investigations/latest.md`

If the caller provides an explicit subdirectory, use `docs/code-investigations/<subdir>/...` and keep root indexes pointing to it.

## Examples

- **Single-repo behavior search:** The user asks "where do we send email?" for
  one repo. Resolve `repo` mode, ask whether to include code lines and
  summaries, dispatch one worker, then write the versioned report.
- **Folder-wide investigation:** The user points to a folder of repos and asks
  for "reads or writes a file". Resolve `folder` mode, keep repo boundaries
  explicit, dispatch one worker per repo where practical, and aggregate the
  reduced results into a shared index.
- **Ambiguous scope:** The user gives a natural-language behavior but not the
  target repos. Ask for scope mode once and stop instead of guessing.

## State machine

Follow these states in order.

### STATE 1 - RESOLVE_REQUEST

- Determine the search goal.
- Determine scope mode: repo, repos, or folder.
- Determine the search surface.
- Ask clarifying questions if any of those are ambiguous.
- Ask whether to include code lines and summaries if missing.

Completion signal:
`STATE 1 (RESOLVE_REQUEST) COMPLETE. Scope: [mode]. Search goal resolved. Proceeding to STATE 2.`

### STATE 2 - BUILD_SEARCH_PLAN

- Produce the normalized investigation brief.
- Expand the request into likely search cues without changing the intent.
- Build the repo list and search-worker plan.
- Select the Codex-family model for each worker.

Completion signal:
`STATE 2 (BUILD_SEARCH_PLAN) COMPLETE. Planned [N] worker(s) across [M] repo(s). Proceeding to STATE 3.`

### STATE 3 - DISPATCH_WORKERS

- Dispatch search workers in parallel.
- Require JSON array output only.
- If a worker fails or returns malformed JSON, skip it and record the failure.

Completion signal:
`STATE 3 (DISPATCH_WORKERS) COMPLETE. Received results from [N] of [M] worker(s). Proceeding to STATE 4.`

### STATE 4 - REDUCE_RESULTS

- Merge results.
- Deduplicate overlaps.
- Separate skipped repos from successful repos.
- If all workers fail, do not write a report; tell the user what happened.

Completion signal:
`STATE 4 (REDUCE_RESULTS) COMPLETE. Reduced to [N] match(es). Proceeding to STATE 5.`

### STATE 5 - WRITE_REPORT

- Dispatch the report writer with the reduced results and display options.
- Retry the writer once on failure.
- If the writer fails twice, return the reduced results in chat as a fallback.

Completion signal:
`STATE 5 (WRITE_REPORT) COMPLETE. Report written to [file path]. Proceeding to STATE 6.`

### STATE 6 - RESPOND

- Summarize the search request, repo count, and match count.
- Mention any skipped repos or failed workers.
- Provide the report path.

Completion signal:
`STATE 6 (RESPOND) COMPLETE. Investigation finished with [N] match(es).`

## Do Nots

- Do not operate in more than one scope mode for a single run.
- Do not skip the `include code lines` and `include summaries` questions when
  the request did not already answer them.
- Do not expand the search brief until it becomes a noisy synonym dump.
- Do not write a report when every worker failed.

## Closed Decisions

- Every run operates in exactly one scope mode: `repo`, `repos`, or `folder`.
- Search workers return JSON arrays only; prose belongs in the final response or
  report.
- Report output lives under `docs/code-investigations/` using the versioned
  writer workflow.
- Repo boundaries stay explicit through planning, reduction, and reporting.
