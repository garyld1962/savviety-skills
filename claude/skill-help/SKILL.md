---
name: skill-help
description: "List available agents or show detailed help for a specific agent. Use when the user asks 'what agents are available', 'help with a skill', 'what can you do', 'list skills', or '/skill-help'."
---

# /skill-help — Agent Reference

**Purpose:** Show available agents and their usage. With no argument, list all user-invokable agents with descriptions. With a name, show detailed help for that agent.

## Arguments

- _(none)_ — list all available agents
- `<name>` — show detailed help for the named agent (e.g., `/skill-help plan`)

## Workflow

### List Mode (no argument)

1. **Discover agents.** Find all top-level SKILL.md files at `.claude/skills/*/SKILL.md` — these are user-invokable agents. Do NOT include nested sub-skills (specialists, analysts, writers under a parent skill directory) — those are internal to agent workflows.

2. **Read frontmatter.** For each discovered SKILL.md, extract the `name` and `description` fields from the YAML frontmatter.

3. **Group by category.** Organize agents into these groups based on their purpose:

   | Category | Agents |
   |----------|--------|
   | **Planning & Design** | plan, grill-me, ideate, ubiquitous-language |
   | **Development** | execute-plan, execute-workflow, kickoff, test-plan, hotfix, triage |
   | **Quality** | code-review, review-gauntlet, review-adversarial, checkpoint |
   | **BA & Requirements** | ba-review-adversarial, prd-acceptance, prd-readiness, prd-validate |
   | **Investigation** | code-investigate, postmortem |
   | **Source Control** | pr, ship, sync-main, changelog |
   | **Operations** | k8s-verify, dep-audit, dep-migrate, env-check |
   | **Team & Workflow** | teams, work-item |
   | **Session** | whereami, session-save |
   | **Configuration** | configure |
   | **Meta** | skill-help, skill-audit |

   If an agent doesn't fit a known category, add it to a "Other" group. If a project has agents in `.claude/skills/_project/`, include them in a "Project-Specific" group.

4. **Present as a table** per category:

   ```
   ## Planning & Design

   | Agent | Description |
   |-------|-------------|
   | `/plan` | Create an implementation plan: explores codebase, writes TDD-style tasks |
   | `/grill-me` | Stress-test a plan or design by walking every decision branch |
   ```

5. **Footer.** Add: `Run /skill-help <name> for detailed usage of any agent.`

### Detail Mode (`<name>` provided)

1. **Find the agent.** Look for `.claude/skills/<name>/SKILL.md`. If not found, search case-insensitively and suggest the closest match.

2. **Read the full SKILL.md.** Present to the user:
   - **Name and description** from frontmatter
   - **Purpose** — the first paragraph after the heading
   - **Arguments** — the arguments section if present
   - **Workflow summary** — the major phases/steps (headings only, not full content)
   - **When to use** — the "When to Use" section if present

3. **Format concisely.** Don't dump the entire SKILL.md — summarize the workflow into a readable overview.

## Rules

- **User-invokable only.** Only list agents at `.claude/skills/*/SKILL.md` (depth 1). Never list specialists, analysts, foundations, or writers nested under a parent agent.
- **Dynamic discovery.** Always read from the filesystem — don't hardcode the list. Projects add custom agents to `_project/`.
- **Concise output.** List mode should fit on one screen. Detail mode should give enough to use the agent without reading the SKILL.md.
- **Use "agent" terminology.** The user thinks in terms of agents, not skills.
