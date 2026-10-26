# Universal Platform Config Rubrics (`shared/platforms/`)

This directory defines the canonical **Per-CLI Config & Capability Rubrics** (`<platform>.rubric.yaml`) and the **Universal Configure Target Registry** (`configure-registry.yaml`).

When authoring or porting a skill from the canonical baseline (`claude/` and `shared/`), each platform CLI follows its rubric so domain logic, verification gates, and artifact schemas stay 100% shared while CLI-specific mechanics are adapted deterministically.

## Platform Comparison Matrix

| Dimension | Claude Code (`claude`) | OpenAI Codex (`codex`) | GitHub Copilot (`copilot`) | Kimi Code (`kimi`) | Hermes Agent (`hermes`) |
|---|---|---|---|---|---|
| **Rubric File** | [`claude.rubric.yaml`](claude.rubric.yaml) | [`codex.rubric.yaml`](codex.rubric.yaml) | [`copilot.rubric.yaml`](copilot.rubric.yaml) | [`kimi.rubric.yaml`](kimi.rubric.yaml) | [`hermes.rubric.yaml`](hermes.rubric.yaml) |
| **Install Scope** | Project (`.claude/`) or Plugin (`savviety-workflows`) | Project (`.codex/`) + local plugin | Project (`.github/`) | Project (`.kimi/`) or Plugin (`savviety-workflows`) | Profile (`$HERMES_HOME/skills/`) |
| **Instruction & `## Commands` Source** | `CLAUDE.md` | `AGENTS.md` (fallback: `CLAUDE.md`) | `.github/copilot-instructions.md` (fallback: `AGENTS.md`, `CLAUDE.md`) | `AGENTS.md` (fallback: `CLAUDE.md`) | `AGENTS.md` / `CLAUDE.md` |
| **Personal Overrides** | `CLAUDE.local.md`, `.claude/settings.local.json` | `~/.codex/AGENTS.md`, `.codex/config.toml` | `.github/instructions/personal.instructions.md` | `~/.kimi/AGENTS.md`, `.kimi/config.toml` | Profile persona & config |
| **Skill Invocation** | `/<skill>` | `$<skill>` | `/<skill>` (skill or `.prompt.md`) | `/skill:<skill>` or `/savviety-workflows:<cmd>` | `/<skill>` |
| **Execution Runtime** | `claude-workflow` (`workflows/*.mjs`) | `native-task-graph` (`shared/workflow-contracts/`) | `native-task-graph` (`shared/workflow-contracts/`) | `native-task-graph` (`shared/workflow-contracts/`) | `native-task-graph` (`shared/workflow-contracts/`) |
| **Worker / Subagent Model** | Stateless `Agent` tool + nested skill resources | Sequential default; `.codex/agents/*.toml` when authorized | `.github/agents/*.agent.md` specialists | `Agent` tool (`coder`/`explore`/`plan`) + `type: flow` | Sequential default; native tools |
| **Model Pinning** | `model: opus` (reasoning), `model: haiku` (fast), or unpinned | Unpinned (session model + reasoning effort) | Unpinned or agent-level model selection | Unpinned (Kimi K2.5/K2.6) | Unpinned (profile model) |

## Universal `## Commands` Resolution Order

Skills that depend on the `repo-delivery` contract (`lint`, `build`, `test`, `default_branch`, `package_manager`) resolve the `## Commands` section in this order:

1. The active platform's primary instruction file (`CLAUDE.md` for Claude, `AGENTS.md` for Codex/Kimi, `.github/copilot-instructions.md` for Copilot).
2. Fallback repository instruction files present in the repo (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`) so multi-CLI repositories only have to declare `## Commands` once.
3. Halt with an actionable message naming the active platform's instruction file if no `## Commands` block is found.

## Validation & Synchronization

- `bin/sync-native-contracts` distributes shared contracts (`shared/workflow-contracts/`, `shared/simplify/`, `shared/drawio/`) into the platform trees.
- `bin/build-kimi-plugin` compiles `claude/` skills into `kimi/skills/` using the rules declared in `kimi.rubric.yaml` (including `_internal/` rubrics, shared validation contracts, and Kimi-native frontmatter/runtime rewrites).
- `bin/validate-native-parity` verifies that all platform rubrics, shared contracts, and skill entrypoints are valid and in sync.
