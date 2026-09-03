# claude smoke test (run in the skills-test harness, fresh session)

1. Sync: `cli/skill.sh --claude --update ~/repos/skills-test-harness/claude-test`
   then manually copy `claude/execute-plan` and `claude/execute-prd`
   over the installed pair in the harness `.claude/skills/`
   (claude/execute-plan and claude/execute-prd are not yet in
   manifest.json).
2. In the harness repo, create `CLAUDE.md ## Commands` declaring
   install/lint/build/test for a toy Node project, and an empty git repo
   on a feature branch.
3. Copy `tests/fixtures/toy-plan.md` to `docs/plans/toy-plan.md`.
4. Fresh session: `/execute-plan docs/plans/toy-plan.md`.
   PASS criteria:
   - Preflight refuses on main, proceeds on a feature branch.
   - Workflow launches (visible in /workflows) with Parse → Tasks →
     Review Gates → Report phases.
   - Task 2 and Task 3 run as a parallel group in worktrees (both depend
     only on Task 1 and have disjoint write scopes).
   - A review gate fires after Task 3 (milestone_end: true).
   - execution-report.json is written with verdict PASS and 3 task rows.
5. Kill the run mid-Tasks once and resume with resumeFromRunId; verify
   completed agent calls replay from cache.
6. `/execute-prd tests/fixtures/toy-prd.md` (write a 5-line toy PRD):
   verify the emitted plan conforms to _internal/plan-format and that
   step 8's static checks reject a deliberately-overlapping write_scope.
