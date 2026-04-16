# Fix: superpowers subagent-driven-development — SendMessage/same-subagent inconsistency

| Field | Value |
|-------|-------|
| **Date** | 2026-04-12T12:21:16Z |
| **Source repo** | [obra/superpowers](https://github.com/obra/superpowers) v5.0.7 |
| **Related issue** | [obra/superpowers#429](https://github.com/obra/superpowers/issues/429) |
| **Local cache path** | `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/` |

## Reason

The `subagent-driven-development` skill's flow diagram, example workflow, and prose instructions all implied that the **same implementer subagent** could be resumed to fix issues found during review (e.g., "Implementer (same subagent) fixes them"). This is not possible in Claude Code CLI — the `Agent` tool creates a fresh conversation each time, and the `SendMessage` tool referenced in the Agent tool's response footer is part of the experimental Agent Teams feature, not the standard subagent workflow.

This caused repeated errors during Phase 1 execution of the Baker Street services-pod plan (2026-04-10) where the orchestrator attempted to call `SendMessage` to resume implementer subagents, wasting cycles on a tool that doesn't exist in the current tool registry.

The correct pattern is to dispatch a **fresh fix subagent** with targeted instructions when a reviewer finds issues.

## Files affected

**Modified:** `skills/subagent-driven-development/SKILL.md`

### Changes

1. **Flow diagram nodes** (lines 54, 57): Renamed `"Implementer subagent fixes spec gaps"` and `"Implementer subagent fixes quality issues"` to `"Dispatch fix subagent for spec gaps"` and `"Dispatch fix subagent for quality issues"`

2. **Flow diagram edges** (lines 73–74, 77–78): Updated edge references to match renamed nodes

3. **"If reviewer finds issues" section** (line 268): Replaced `"Implementer (same subagent) fixes them"` with explicit fresh fix subagent instructions including scoping guidance

4. **Red flags section** (line 258): Changed `"implementer fixes"` to `"dispatch fix subagent"` in the review loop description

5. **Example workflow** (lines 189–190, 198–199): Replaced `"[Implementer fixes issues]"` / `"[Implementer fixes]"` with `"[Dispatch fix subagent with ...]"` / `"Fix subagent: ..."` pattern

6. **New section: "Fix Subagent Pattern"** (inserted before "Prompt Templates"): Added explicit documentation of the fix subagent pattern with the 5 required prompt elements, rationale, and link to obra/superpowers#429

### Files NOT modified (verified clean)

- `skills/subagent-driven-development/implementer-prompt.md` — no SendMessage/same-subagent references
- `skills/subagent-driven-development/spec-reviewer-prompt.md` — clean
- `skills/subagent-driven-development/code-quality-reviewer-prompt.md` — clean

## Re-application

These fixes are in the plugin **cache** and will be overwritten when the superpowers plugin updates. If obra/superpowers#429 has not been resolved when a new version is installed, re-apply these changes or verify the upstream version addresses the inconsistency.
