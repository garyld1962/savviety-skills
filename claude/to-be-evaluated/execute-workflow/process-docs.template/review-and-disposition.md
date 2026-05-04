# Review and Disposition Process

This document defines how reviews are conducted and findings are dispositioned in this project. Edit the thresholds and escalation rules to match your needs.

## Review Types

| Review | Purpose | Required? |
|---|---|---|
| Plan review | Verify plan readiness and proof obligations | When a plan is produced |
| Code review | Evidence-based review of implementation | Always |
| Adversarial review | Independent challenge pass | Always |

## Evidence Standard

Every finding must include:
- **Severity:** High, Medium, Low
- **Evidence:** What the code does (cite file:line)
- **Impact:** Why it matters
- **Recommendation:** How to fix

Findings that lack evidence are not valid. Style-only commentary does not count.

## Disposition Status Vocabulary

| Status | Meaning |
|---|---|
| `open` | Finding raised, not yet addressed |
| `fixed` | Code changed to resolve the finding |
| `disagree-with-evidence` | Coder provides evidence that the finding is incorrect |
| `defer` | Real issue, not fixing in this run — record follow-up action |
| `accepted-risk` | Real issue, human explicitly accepts proceeding |
| `resolved` | Final state after agreement |

## Disposition Loop

1. Reviewer raises findings in the review artifact
2. Coder responds with one of: `fixed`, `disagree-with-evidence`, `defer`
3. Adversary re-checks unresolved, disputed, and recently-fixed items
4. All findings recorded in `disposition-log.md`
5. Repeat until convergence or escalation threshold

## Escalation Threshold

- **Default:** 2 review rounds before human arbitration
- **Edit this** to match your project's tolerance

## Blocking Rules

- Unresolved `High` findings block completion
- `accepted-risk` requires explicit human approval
- `defer` requires a named follow-up action

## Human Arbitration

Trigger when:
- Unresolved `High` findings remain after the escalation threshold
- Important `Medium` findings remain disputed
- Reviewer and coder cannot converge using evidence

Document the human decision in the disposition log.
