# Governed Workflow Config

This file tells the execute-workflow skill where to find process docs,
artifact templates, and where to write run artifacts for this project.

Copy to `<project>/.claude/workflow.config.md` and fill in the paths.

## Paths

```yaml
# Root directory for process documents (relative to project root)
process_docs_root: <FILL IN: e.g., docs/process>

# Root directory for artifact templates (relative to project root)
templates_root: <FILL IN: e.g., docs/templates>

# Root directory for run artifacts (relative to project root)
# Each run creates a timestamped subfolder: <runs_root>/yyyy-mm-dd-HHMMSS/
runs_root: <FILL IN: e.g., docs/runs>
```

## Process Docs Expected

The execute-workflow skill looks for these files under `process_docs_root`:

- `execute-workflow.md` — execution phase ordering
- `review-and-disposition.md` — review and disposition process
- `evidence-and-artifacts.md` — evidence standards
- `document-schema.md` — artifact schemas
- `postmortem-workflow.md` — postmortem trigger and process

If you haven't authored these yet, copy the reference templates:
```
cp -r claude/execute-workflow/process-docs.template/ <project>/docs/process/
```

## Artifact Templates Expected

The skill uses templates from `templates_root` to structure run artifacts:

- `execution-report.template.md`
- `review-plan.template.md`
- `review-code.template.md`
- `adversarial-review.template.md`
- `disposition-log.template.md`
- `postmortem.template.md`

If you haven't authored these yet, copy the reference templates:
```
cp -r claude/execute-workflow/artifact-templates.template/ <project>/docs/templates/
```
