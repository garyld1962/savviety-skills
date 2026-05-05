# AGENTS.md

## Repository Expectations

- Use the installed Savviety Workflows skills for repeatable planning, review, checkpoint, and delivery work.
- Run the repository's documented lint, build, and test commands before opening a pull request.
- Keep project-specific decisions in this file or nearby `AGENTS.md` files close to the code they govern.
- Put personal preferences in your CLI user configuration (`~/.kimi/AGENTS.md` for Kimi, `~/.codex/AGENTS.md` for Codex), not in shared repository instructions.

## Savviety Workflows

- Use `/skill:repo-status` before delivery or after a long break.
- Use `/skill:validate-plan` before executing implementation plans.
- Use `/skill:checkpoint` before push, PR creation, or release.
- Use project-scoped custom agents only when the task explicitly calls for subagent delegation.

## Cross-CLI Notes

This file is auto-injected into the Kimi system prompt as `${KIMI_AGENTS_MD}` and is also read by Codex. Keep contents CLI-neutral so both runtimes interpret it correctly. CLI-specific guidance belongs in the per-CLI user file (`~/.kimi/AGENTS.md`, `~/.codex/AGENTS.md`).
