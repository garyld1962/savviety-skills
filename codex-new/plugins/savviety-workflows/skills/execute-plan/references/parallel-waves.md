# Execute Plan Parallel Waves

Use this reference only when the user has explicitly authorized subagents and the plan metadata proves parallel safety.

## Dispatch Contract

Each lane prompt must include:

- Plan path and plan SHA.
- Lane objective.
- Owned write scope.
- Read-only context scope.
- Dependencies and barriers.
- Focused verification command.
- Coordination warning: other agents may be editing the repo, so do not revert or overwrite files outside the assigned scope.

Default prompt templates live in `references/agent-prompts/`.

## Ownership Rules

- No two lanes may write the same file unless one lane is the named shared-surface owner.
- Lockfiles, root manifests, generated files, migrations, shared contracts, and public exports require a single owner.
- Contract-producing work must land before consumers.
- Integration owns final root gates and conflict resolution.

## Merge Order

1. Merge contract producers.
2. Merge shared-surface owners.
3. Merge independent implementation lanes.
4. Merge tests and integration lanes.
5. Run focused lane verification after each merge.
6. Run root verification after the wave is fully merged.

On merge failure, preserve all worktrees or branches and stop with the exact conflict scope.

