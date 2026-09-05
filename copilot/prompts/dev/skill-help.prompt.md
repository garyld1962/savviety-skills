---
name: skill-help
description: "List installed Copilot skills and prompt shortcuts, or explain one workflow and its arguments."
argument-hint: "[skill or prompt name]"
---

# Skill and prompt help

Discover actual SKILL.md files under .github/skills and prompt files under
.github/prompts. Read names/descriptions first; show workflow, purpose and available
entrypoint in a concise table. For a named item, read its full instructions and
explain inputs, outputs, boundaries and examples. Include newly installed assets
without relying on a hardcoded list.

Host command availability differs. Inspect the current host before recommending a
built-in command; do not claim /skills discovers VS Code prompt files. Agent skills
are the durable workflows; prompt shortcuts require a host that supports prompt files.
