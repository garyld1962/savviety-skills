# Execute Plan Review Gates

Use this reference at milestones and PR boundaries.

## Milestone Breakpoint

At each milestone:

1. Run the milestone verification command.
2. Run a checkpoint or focused review over the accumulated milestone diff.
3. Fix blocking findings before moving to the next milestone.
4. Record accepted risks explicitly.

Apply `references/loop-fuse.md` to every failed milestone verification. A repeated or malformed verification failure blocks the milestone report; do not continue to broader checks until the exact blocker is reported or fixed.

## PR Boundary

Before final report:

1. Run the repo checkpoint.
2. Compute the effective diff from the recorded base SHA.
3. Run full `code-review`.
4. Run `code-review-professional` when craft grading is part of the plan.
5. Check plan alignment against completed tasks, acceptance criteria, and deviations.
6. Run `review-adversarial` when requested or when automatic triggers apply.

## Effective Diff Manifest

Build a compact manifest for downstream review skills:

- Changed files.
- Language per file.
- File clusters by feature or layer.
- Flags for persistence, public surface, auth/security, concurrency, dependency manifests, migrations, generated files, and shared exports.
- Immediate context files needed by reviewers.

Pass this manifest to review skills when possible so they do not repeat triage.

## Disposition

Use `references/disposition.md` for accepting, rejecting, or escalating findings.

Rules:

- Critical and major findings block unless explicitly accepted by the user.
- Accepted risk must name the finding and rationale.
- Re-review fixes with the narrowest command that proves the issue is resolved.
