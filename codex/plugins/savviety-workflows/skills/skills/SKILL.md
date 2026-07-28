---
name: skills
description: "Unified Codex skill-management workflow. List available Savviety skills, show detail for one skill, audit local skill/agent/hook/rule/plugin coverage, check custom skills for overlap with installed native skills, or find installable skills for a requested capability. Trigger phrases: 'what skills are available', 'show skill details', 'audit skills', 'native skill overlap', 'do these skills compete with Codex skills', 'find a skill for X'."
---

# Skills

Codex consolidation for skill detail, skill audit, and skill discovery workflows.

## Modes

- no flag: list available Savviety Codex skills.
- `<name>`: show concise detail for one skill.
- `--audit`: inspect local skill, agent, hook, rule, and plugin coverage.
- `--native-overlap [skill-name]`: audit this source repo's custom Codex skills against the current session's available-skills listing. Use the live session list as the catalog; do not invent installed skills.
- `--find <query>`: search available skill ecosystems or installed plugin catalogs.

Prefer local installed skills and plugins before recommending new installation.

## Native-Overlap Audit

Use this mode only in the savviety-skills Codex source tree, where `plugins/savviety-workflows/skills/` exists. If that structure is absent, refuse with:

```
skills --native-overlap must run in the savviety-skills Codex source tree.
```

Audit user-invocable skill descriptions against the current session's installed skills and plugins. Skip archival `references/legacy/` content and internal reference files. For each overlap, assign one verdict:

- `Tighten`: the Savviety description is too broad and may lose its trigger surface.
- `Cross-reference`: the Savviety skill is a stricter project-tailored version of an installed skill.
- `Integrate`: the Savviety skill should call or defer to an installed skill at a specific workflow step.
- `Hand off`: the installed skill is better for part of the described territory.
- `Redundant`: the Savviety skill has no meaningful value over an installed skill.

Default to report-only. If edits are requested, update descriptions, `When Not To Use` sections, or relationship blocks narrowly, then run the Codex asset validator.
