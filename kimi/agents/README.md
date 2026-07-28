# kimi/agents/

Custom agent YAML files for downstream Kimi installs. Empty by default.

## Why no per-skill agent YAML

Investigated during the Kimi port. The Claude `execute-plan/agents/{implementer,reviewer,fixer}.md` files are **not** independent agents — they are prompt templates with `{PLACEHOLDER}` substitution that the parent `execute-plan` skill performs at dispatch time. Wrapping them in Kimi `version: 1` agent YAML would ship a system-prompt file with raw `{TEAM_NAME}`, `{WORKTREE_PATH}`, `{PLAN_SHA}` placeholders, which is broken.

Kimi handles this correctly without porting: when `execute-plan` calls the `Agent` tool, it passes the substituted prompt as the `prompt` parameter and selects the right built-in subagent type. No custom Kimi agent file is needed.

## Subagent-type mapping

When porting a Claude skill that dispatches subagents, map Claude's subagent types to Kimi's built-ins:

| Claude `subagent_type` | Kimi `subagent_type` | Use for |
|---|---|---|
| `general-purpose` | `coder` | Implementer / fixer roles with write access |
| `Explore` | `explore` | Read-only investigation, code-search, file-read passes |
| `Plan` | `plan` | Architecture/design analysis without write access |

For `execute-plan` specifically:
- **Implementer** → `subagent_type: coder` (write access required)
- **Reviewer** Step 1 (read-only review) → `subagent_type: explore`
- **Reviewer** Step 2-3 (build/test commands) → `subagent_type: coder` (needs shell)
- **Fixer** → `subagent_type: coder` (write access required)

In practice the existing `execute-plan` skill already uses generic "subagent" language and lets the runtime pick the right type. No per-CLI fork is needed.

## When to add a YAML agent here

Add a `<name>.yaml` (plus optional `<name>-system.md` for the system prompt body) when:

1. You want a Kimi user to launch the agent directly via `kimi --agent-file ./.kimi/agents/<name>.yaml`, not just as a subagent.
2. You need to restrict tools beyond what the built-in `coder` / `explore` / `plan` types provide.
3. The agent has a stable, fully-specified system prompt with no placeholders.

If you find yourself wrapping a placeholder template — stop. That belongs in the parent skill, not as an agent.
