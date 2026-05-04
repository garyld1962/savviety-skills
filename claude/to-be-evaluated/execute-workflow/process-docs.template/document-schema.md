# Document Schema

This document defines the required sections and structure for each governed workflow artifact. Edit sections to match your project's needs.

## Execution Report Schema

```markdown
# Execution Report

## Run Metadata
- Run ID: <timestamp>
- Requirements: <path to AERS/PRD>
- Date: <date>
- Gate verdict: completed | completed-with-accepted-risk | blocked | awaiting-human-decision

## Summary
<1-3 sentence summary of what was done>

## Phases Completed
<checklist of phases from execute-workflow.md>

## Finding Summary
- Total findings: <N>
- High: <N> (resolved: <N>, open: <N>)
- Medium: <N> (resolved: <N>, open: <N>)
- Low: <N>

## Accepted Risks
<list of accepted-risk items, or "None">

## Deferred Items
<list of deferred items with follow-up actions, or "None">

## Artifact Links
- [review-code.md](review-code.md)
- [adversarial-review.md](adversarial-review.md)
- [disposition-log.md](disposition-log.md)
```

## Review Code Schema

```markdown
# Code Review

## Scope
<files and packages reviewed>

## Proof Accounting
| Area | Classification | Evidence |
|---|---|---|
| <area> | proved / partially proved / unproved | <test/file reference> |

## Findings
### <ID>: <title>
- Severity: High | Medium | Low
- File: <path:line>
- Evidence: <what the code does>
- Impact: <why it matters>
- Recommendation: <how to fix>
- Status: open

## Elevation Recommendations
<items from the elevation pass, or "None">
```

## Adversarial Review Schema

```markdown
# Adversarial Review

## Reviewer Context
- Model/role: <what performed this review>
- Independence: <how this differs from the main implementation>

## Findings
### <ID>: <title>
- Severity: High | Medium | Low
- Challenges: <which code-review finding or implementation choice>
- Evidence: <what the adversary found>
- Status: open
```

## Disposition Log Schema

```markdown
# Disposition Log

## Rounds

### Round 1
| Finding ID | Source | Severity | Coder Response | Status |
|---|---|---|---|---|
| CR-01 | review-code | High | fixed | resolved |
| AR-01 | adversarial-review | Medium | disagree-with-evidence | <status> |

### Round 2
<same format>

## Final State
- Unresolved High: <N>
- Accepted risk: <list or "None">
- Deferred: <list with follow-up actions or "None">
- Human decisions: <list or "None">
```

## Postmortem Schema

```markdown
# Postmortem

## Run Reference
- Run ID: <timestamp>
- Gate verdict: <verdict>

## What Happened
<narrative summary>

## What Worked
<process strengths>

## What Broke Down
<process failures or near-misses>

## What the Process Missed
<gaps that only became visible after the run>

## Recommendations
<specific, actionable changes for next time>
```
