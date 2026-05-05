# Kimi Asset Authoring

These files are source assets for downstream Kimi Code CLI installs.

- Prefer Kimi-native terminology: skills, agents (YAML), subagents, hooks, `AGENTS.md`.
- Do not duplicate skill bodies that already live in `claude/`. Kimi auto-discovers `.claude/skills/` natively.
- Custom agents use the v1 YAML schema (`version: 1` + `agent:` block) with `extend: default` unless full replacement is required.
- Long system-prompt bodies live in sibling `*-system.md` files; the agent YAML references them via `system_prompt_path`.
- Subagent dispatch should map to Kimi's built-in `coder` / `explore` / `plan` types when possible. Only define a custom subagent when the role is genuinely different.
- `AGENTS.md` is shared with Codex (both CLIs read the project file). Keep it CLI-neutral.
- Validate agent YAML and hook JSON before shipping.
