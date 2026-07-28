---
name: investigation-report-writer
description: "Write structured investigation matches to a versioned Markdown report under docs/code-investigations/ and update report pointers."
argument-hint: "Structured investigation results JSON"
---

# Investigation Report Writer

Input:

- search request summary
- scope mode: repo | repos | folder
- human-readable scope string
- includeCodeLines: yes/no
- includeSummary: yes/no
- repo list searched
- skipped repo list (optional)
- JSON array of structured matches
- outputSubdir (optional)
- runId (optional)

Output:

- Create a NEW Markdown report file:
  - default: `docs/code-investigations/<YYYY-MM-DD>--<HHMMSS>--<scope>--<slug>--<runId>.md`
  - with subdir: `docs/code-investigations/<outputSubdir>/<YYYY-MM-DD>--<HHMMSS>--<scope>--<slug>--<runId>.md`
- Update:
  - `docs/code-investigations/index.md`
  - `docs/code-investigations/latest.md`
  - `docs/code-investigations/<outputSubdir>/index.md` when subdir is used

# Safety rules

- You may ONLY create or edit files under `docs/code-investigations/` and its subdirectories
- Do not modify code, prompts, skills, or agent definitions

# Report structure

Use this shape:

```markdown
# Code Investigation Report

- **Date:** YYYY-MM-DD HH:MM
- **Scope mode:** repo | repos | folder
- **Scope:** <human-readable scope>
- **Request:** <search request summary>
- **Repos searched:** <count>
- **Matches found:** <count>
- **Include code lines:** yes | no
- **Include summaries:** yes | no

## Searched Repositories
- `repo-a`
- `repo-b`

## Skipped Repositories
- `repo-x` - <reason>

## Matches by Repository

### `repo-a`

#### `<project>`

| Confidence | File | Lines | Match Type |
|------------|------|-------|------------|
| 0.92 | `src/Foo.cs` | `41-52` | `framework` |

##### `src/Foo.cs` - `41-52`
- **Confidence:** 0.92
- **Why it matches:** <whyMatch>
- **Code lines:** fenced code block only when enabled
- **Summary:** only when enabled
```

# Formatting rules

- Group results by repository, then by project, then by file
- Keep repo and project names prominent so the report reads like an index
- Always show confidence with two decimal places
- If code lines are disabled, omit that subsection entirely
- If summaries are disabled, omit that subsection entirely
- If there are no matches, explicitly say: `No matches were found for the requested investigation.`

# Index format

Prepend to `docs/code-investigations/index.md`:

- Without subdir: `- YYYY-MM-DD HH:MM | <scope mode> | <scope> | [report](./<filename>.md)`
- With subdir: `- YYYY-MM-DD HH:MM | <scope mode> | <scope> | [report](./<outputSubdir>/<filename>.md)`

If subdir is used, also prepend to `docs/code-investigations/<outputSubdir>/index.md`:

- `- YYYY-MM-DD HH:MM | <scope mode> | <scope> | [report](./<filename>.md)`

# latest.md format

Replace the entire content with:

```markdown
# Latest Code Investigation Report

- **Date:** YYYY-MM-DD HH:MM
- **Scope mode:** <scope mode>
- **Scope:** <scope>
- **Request:** <search request summary>
- **Report:** [<filename>.md](./<outputSubdir>/<filename>.md)
- **Matches:** <count>
```

Adjust the report path to omit the subdirectory when none is used.

# Examples

- **Root report:** Write a new report under `docs/code-investigations/`,
  prepend its link to `index.md`, and replace `latest.md` with the new pointer.
- **Subdirectory report:** Write the report under
  `docs/code-investigations/<outputSubdir>/`, update the root index, update the
  subdirectory index, and point `latest.md` at the subdirectory report.

# Do Nots

- Do not edit files outside `docs/code-investigations/`.
- Do not overwrite an existing investigation report instead of creating a new
  versioned file.
- Do not include code lines or summaries when the caller disabled them.

# Closed Decisions

- This writer may only create or edit files under `docs/code-investigations/`.
- Report, index, and `latest.md` formats are fixed by this skill.
- Every run creates a new versioned report file rather than mutating historical
  reports in place.
