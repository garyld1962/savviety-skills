---
name: port-skill
description: "Port a skill between claude/ and copilot-native/ formats, applying platform conventions and stripping platform-specific bake-in."
---

# /port-skill — Cross-Platform Skill Porter

**Purpose:** Take a skill from one platform and create its counterpart on the other, applying the correct file format, frontmatter, and conventions for the target platform.

## Arguments

- `<source-path>` — path to the source skill file (required)
- `--to claude|copilot` — target platform (inferred from source if not specified)

## Workflow

### 1. Detect source platform

Read the source file and determine its platform from the path:
- `claude/*/SKILL.md` → Claude skill
- `copilot-native/prompts/**/*.prompt.md` → Copilot prompt
- `copilot-native/agents/*.agent.md` → Copilot agent
- `copilot-native/skills/*/SKILL.md` → Copilot skill (knowledge)

If `--to` is not specified, infer the target as the opposite platform.

### 2. Read source and extract content

Read the source file. Extract:
- **Name/ID** from frontmatter
- **Description** from frontmatter
- **Purpose** from the first paragraph
- **Workflow/steps** from the body
- **Rules/constraints** from any rules section
- **References** to other skills or assets

### 3. Map the asset type

| Source | Target | Notes |
|---|---|---|
| Claude skill (`claude/*/SKILL.md`) | Copilot prompt (`copilot-native/prompts/{cat}/<name>.prompt.md`) | User-invokable workflow → prompt |
| Claude rubric (`claude/_rubrics/*/SKILL.md`) | Copilot skill (`copilot-native/skills/<name>/SKILL.md`) | Knowledge/rubric → skill (knowledge) |
| Copilot prompt | Claude skill | Prompt → user-invokable skill |
| Copilot agent | Claude skill (with Agent tool notes) | Agent → skill that uses Agent tool dispatch |
| Copilot skill (knowledge) | Claude rubric or sub-file | Knowledge → rubric or embedded reference |

If the mapping is ambiguous, ask the user which target type to use.

### 4. Apply platform conventions

**Claude → Copilot-native:**

- Replace `name:` + `description:` frontmatter with `description:` (Copilot prompt format)
- Add `argument-hint:` if the skill has arguments
- Add `agent:` and `tools:` if the skill dispatches subagents or uses specific tools
- Replace Claude-specific references:
  - `superpowers:*` → describe the behavior inline (Copilot has no equivalent)
  - `Agent tool` → `@agent` or platform delegation
  - `TaskCreate/TaskUpdate` → remove or replace with prose
  - `CLAUDE.md` → `copilot-instructions.md` or `.github/copilot-instructions.md`
- Strip Claude Code-specific tool names (Read, Write, Edit, Glob, Grep) — Copilot uses `read`, `search`, `edit`, `codebase`
- Ask which prompt category: `ba/`, `dev/`, `review/`, `common/`

**Copilot-native → Claude:**

- Replace `description:` frontmatter with `name:` + `description:` (Claude skill format)
- Replace `tools:` list with prose about which Claude Code tools to use
- Replace `@agent` delegation with Agent tool dispatch
- Replace `copilot-instructions.md` references → `CLAUDE.md`
- Replace Copilot tool names (`read`, `search`, `edit`, `codebase`) with Claude equivalents (Read, Grep, Edit, Glob)
- Strip any `applyTo:` or `glob:` frontmatter (Claude uses skill invocation, not auto-apply)

### 5. Strip environment bake-in

**Critical rule from the parity plan:** Canonical skills never hardcode environmental specifics. During porting, strip:
- Specific shell names (PowerShell, WSL, bash) — replace with "detect the shell" or reference `env.config.md`
- Specific hostnames or machine names
- Specific project names, paths, or build commands
- Specific tool choices (npm/yarn/pnpm) — replace with "detect from project config"

If the source has environment-specific content that can't be generalized, note it as a "user must configure" item.

### 6. Create the target file

Write the ported file to the correct location. Show the full file to the user for review before writing.

### 7. Update indexes

- If porting to copilot-native and `asset-catalog.md` exists, add the new file
- If porting to claude, suggest the skill-help category
- If the source references other skills, note which cross-references need porting too

### 8. Confirm

Print:
```
Ported: <source-path>
    →   <target-path>

Platform adjustments:
  - Replaced N tool/platform references
  - Stripped M environment-specific items
  - <any warnings about manual follow-up>

Cross-references that may need porting:
  - <referenced skill 1>
  - <referenced skill 2>
```

## Rules

- **Don't blindly copy.** The port must read naturally on the target platform. A Claude skill that says "use the Agent tool with subagent_type=Explore" should become a Copilot prompt that says "use @agent to explore the codebase."
- **Preserve intent, not mechanics.** The workflow steps should achieve the same goal using the target platform's idioms.
- **Flag what can't be ported.** Some Claude features (confidence scores, verdict JSON, Agent tool dispatch) have no Copilot equivalent. Note these as "not ported — target platform handles this differently."
- **One skill at a time.** Don't batch-port. Each port is a conversation about what translates and what doesn't.
- **Environment-neutral.** The parity plan's env-neutral principle applies to all ports. No hardcoded shells, hosts, or paths.
