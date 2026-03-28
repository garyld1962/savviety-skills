---
name: review-report-writer
description: Turn structured findings into a Markdown report and write a new versioned report under docs/code-reviews/; update index.md and latest.md.
---

# Mission (MVP)

Input:
- mode: solution|project|file
- scope: human-readable string
- runId: (optional) if not provided, generate 4–6 lowercase alphanumerics
- timestamp: (best effort) local
- JSON array of findings (schema in ../review-foundations/schemas/finding.schema.json)
- filesReviewed: (optional) list of files that were sampled/reviewed
- outputSubdir: (optional) group subdirectory name (e.g., "pcrs", "acs", "beqom")

Output:
- Create a NEW Markdown report file:
  - If `outputSubdir` is provided: `docs/code-reviews/<outputSubdir>/<YYYY-MM-DD>--<HHMMSS>--<mode>--<slug>--<runId>.md`
  - Otherwise: `docs/code-reviews/<YYYY-MM-DD>--<HHMMSS>--<mode>--<slug>--<runId>.md`
- Update:
  - `docs/code-reviews/<outputSubdir>/index.md` (prepend newest entry — only when `outputSubdir` is set)
  - `docs/code-reviews/index.md` (prepend newest entry; use relative path `<outputSubdir>/<filename>.md` when subdir is set)
  - `docs/code-reviews/latest.md` (replace with summary pointing to newest, with correct relative path)

Use template:
- ../review-foundations/templates/review-report.template.md

# Safety rules

- You may ONLY create/edit files under `docs/code-reviews/` **and its subdirectories** (e.g., `docs/code-reviews/pcrs/`, `docs/code-reviews/acs/`, `docs/code-reviews/beqom/`).
- Do not modify any code or configuration outside that folder tree.

# Formatting rules

- Group findings by **severity first**, then by **domain within each severity level**.
- Omit empty domain sub-headings (if a severity has no findings for a domain, skip that sub-heading).
- Omit empty severity sections entirely (if no findings at that severity, skip the section).
- Each finding must show:
  - Title
  - Domain, Severity, Confidence
  - Location (file + lineRange if present)
  - Evidence (short)
  - Recommendation (actionable)

- Keep evidence excerpts short; prefer pointing at exact location.
- If there are zero findings, explicitly say so in the report body.

# index.md format

**Group index** (`docs/code-reviews/<outputSubdir>/index.md` — only when `outputSubdir` is set):
Prepend a line like:
- `- YYYY-MM-DD HH:MM | <mode> | <scope> | [report](./<filename>.md)`

**Root index** (`docs/code-reviews/index.md`):
Prepend a line like:
- Without subdir: `- YYYY-MM-DD HH:MM | <mode> | <scope> | [report](./<filename>.md)`
- With subdir: `- YYYY-MM-DD HH:MM | <mode> | <scope> | [report](./<outputSubdir>/<filename>.md)`

If you don't know the time, use `HH:MM` as `??:??`.

# latest.md format

Replace the entire content of `latest.md` with:

```markdown
# Latest Code Review Report

- **Date:** YYYY-MM-DD HH:MM
- **Mode:** <mode>
- **Scope:** <scope>
- **Report:** [<filename>.md](./<outputSubdir>/<filename>.md) _(adjust path: omit subdir if none)_

## Severity summary
- Blockers: <count>
- High: <count>
- Medium: <count>
- Low: <count>
- Info: <count>
```

If there are zero findings, set all counts to 0.
