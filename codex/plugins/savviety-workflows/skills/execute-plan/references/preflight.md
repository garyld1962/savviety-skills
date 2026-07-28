# Execute Plan Preflight

Use this reference before editing files.

## Required Inputs

- A written plan path, or the newest markdown file under `docs/plans/`.
- A repo delivery contract. Prefer `AGENTS.md` for Codex repos. If the repo still uses the legacy contract in `CLAUDE.md`, read only the `## Commands` section.
- The current branch, default branch, base SHA, and plan SHA.

## Gates

1. Run `validate-plan` against the plan.
2. If validation returns `FAIL`, refuse to execute unless the user explicitly asked to override the failure.
3. Probe declared commands before execution. Use `scripts/toolchain_probe.py` when the command list is available.
4. Refuse to run directly on the default branch unless the user explicitly asked to create or use a working branch.
5. Record the starting branch, base SHA, plan SHA, and verification commands in the execution log.

## Parallel Metadata

If the plan contains `## Parallel Execution`, treat it as executable metadata.

Required fields:

- `Mode`
- `Ownership`
- `Barriers`
- `Single-Owner Files`
- `Parallel Safety Checks`

For `Mode: sequential`, run a normal sequential task loop and report the stated rationale.

For `Mode: parallel`, verify before any dispatch:

- Every lane has a concrete write scope, dependency list, and focused verification command.
- Shared surfaces such as manifests, lockfiles, migrations, generated files, exported contracts, and root config have one owner.
- Contract-producing lanes finish before contract-consuming lanes.
- The integration lane owns conflict resolution and root verification.
- Worker prompts include the warning that other agents may be editing disjoint files.

If the metadata is absent, default to sequential execution and report: `Parallel Execution: absent; using sequential task loop.`

## Failure Safety

Never destroy work during this skill.

- Do not run `git reset --hard`.
- Do not run `git clean -f`.
- Do not force-delete branches or tags.
- Do not overwrite user changes unrelated to the current plan.
- On unrecoverable failure, preserve the branch and report the last successful commit.

