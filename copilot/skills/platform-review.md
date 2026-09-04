# Copilot Platform Review and Optimization Direction

## What is already strong in this repo

The current `vscode/` tree is mature:

- clear split between prompts, agents, skills, and instructions
- prompts hardened with "Do Not Guess" guidance
- good domain skill coverage
- reusable review infrastructure
- project-level `copilot-instructions.md` as a single source of truth

That means the repo does **not** need a rewrite. It needs a more Copilot-native layer on top.

## Main optimization opportunity

The current VS Code assets still carry a lot of Claude workflow shape:

- many prompts mirror command-style skills from Claude
- some custom prompts duplicate Copilot built-ins conceptually
- orchestration logic often lives in prompts rather than being split across built-ins, skills, agents, and instructions

## Copilot-native design recommendation

### 1. Treat built-ins as the primary workflow layer

Prefer built-ins when they already provide strong platform support:

- `/plan` for implementation planning
- `/review` for default code review
- `/research` for broad investigation
- `/fleet` for parallel specialist execution
- `/tasks` for background work visibility
- `/diff` for changed-scope inspection
- `/pr` for PR state, checks, and merge readiness
- `/agent` and project agents for specialist roles
- `/instructions` to understand active rule layers
- `/env` for loaded environment inspection
- `/share` and `/compact` for long-running session export and context control
- `/model` for adversarial second-pass review

### 2. Reserve custom prompts for high-value gaps

Good candidates:

- interactive AERS/story refinement
- portfolio/asset audit
- repo-specific orchestration that cannot be expressed cleanly with built-ins alone

Weak candidates:

- thin wrappers around `/plan`
- thin wrappers around `/review`
- prompts that exist only because they used to be Claude slash commands

### 3. Move durable guidance into skills

Skills should hold:

- evaluation rubrics
- decision heuristics
- review criteria
- domain conventions
- handoff requirements

Prompts should mostly orchestrate the interview or workflow.

### 4. Keep passive guardrails in instructions

Instructions are the right place for:

- built-in-first authoring rules
- "do not duplicate platform features" rules
- conventions for prompt/agent/skill authoring

### 5. Narrow the role of agents

Agents are best for:

- bounded specialist review
- formatting/finalization roles
- focused analysis with clear output contracts

They should not become another layer of generic orchestration unless there is a real need.

## Built-in feature mapping

| Need | Prefer | Add custom asset only when... |
|------|--------|-------------------------------|
| Plan code changes | `/plan` | project needs special wave/team/test architecture |
| Review code | `/review` | you need structured multi-specialist review with custom rubrics |
| Research | `/research` | you need a repeatable domain-specific audit workflow |
| Parallel specialist work | `/fleet` + `/tasks` | you need custom worker selection, merge logic, or report contracts |
| Inspect changed scope | `/diff` | the repo needs a richer custom artifact than the built-in diff view |
| PR workflow | `/pr` | the repo needs additional governed delivery artifacts or disposition rules |
| Long-running work | `/tasks` | you need a project-specific coordination prompt |
| Environment inspection | `/env` | the repo needs shell-routing logic or config-aware command guidance |
| Context control | `@file`, `/instructions`, `/context`, `/compact` | the repo needs special handoff templates |
| Export/share | `/share` | you need a repo-persisted artifact with a fixed schema |
| Model disagreement | `/model` | you want a scripted adversarial review pattern |

## Recommended next-generation asset mix

### Keep strong

- domain review skills
- quality instructions
- specialist agents
- repo-level `copilot-instructions.md`

### Simplify over time

- duplicate wrappers around built-in planning/review workflows
- prompts whose only purpose is command-name parity with Claude

### Add now

- `prd-validate` (AERS validator)
- `copilot-asset-audit`
- a Copilot platform playbook skill
- an authoring instruction for future prompt/agent/skill design

## Immediate conclusion

The right move is **not** "port every Claude skill." The right move is:

1. keep the best existing Copilot assets
2. reduce duplication with built-ins
3. add only the highest-value custom workflows
4. use this folder as the staging area before deciding what merges into `vscode/`
