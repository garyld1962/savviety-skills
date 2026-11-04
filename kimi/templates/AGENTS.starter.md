# AGENTS.md

## Repository Expectations

- Use the installed Savviety Workflows skills for repeatable planning, review, checkpoint, and delivery work.
- Run the repository's documented lint, build, and test commands before opening a pull request.
- Keep project-specific decisions in this file or nearby `AGENTS.md` files close to the code they govern.
- Put personal preferences in your CLI user configuration (`~/.kimi/AGENTS.md` for Kimi, `~/.codex/AGENTS.md` for Codex), not in shared repository instructions.

## Commands

lint: <cmd>
build: <cmd>
test: <cmd>
default_branch: main
package_manager: <npm|pnpm|yarn|bun|pip|poetry|cargo|go|dotnet|...>

## Savviety Workflows

- Use `/skill:repo-status` before delivery or after a long break.
- Use `/skill:validate-plan` before executing implementation plans.
- Use `/skill:checkpoint` before push, PR creation, or release.
- When the `jev-gate` FastMCP server is connected (`Runtime Tool Args > ./.jev-gate.toml > ~/.config/jev-gate/config.toml`), route technical/SDK/hardware searches through `smart_search`, pre-triage multi-file tasks with `triage_coding_task`, audit diffs with `verify_code_invariants`, and gate non-trivial shell commands via `gate_shell_command`.
- Use project-scoped custom agents only when the task explicitly calls for subagent delegation.

## Cross-CLI Notes

This file is auto-injected into the Kimi system prompt as `${KIMI_AGENTS_MD}` and is also read by Codex. Keep contents CLI-neutral so both runtimes interpret it correctly. CLI-specific guidance belongs in the per-CLI user file (`~/.kimi/AGENTS.md`, `~/.codex/AGENTS.md`).
