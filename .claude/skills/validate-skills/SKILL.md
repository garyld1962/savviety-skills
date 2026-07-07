---
name: validate-skills
description: "Lint and validate all skill files in this repo: check frontmatter, cross-references, naming conventions, and structural integrity across both claude/ and copilot-native/ platforms."
---

# /validate-skills — Skill Library Linter

**Purpose:** Validate that all skill, prompt, agent, and domain files in this repo conform to their platform's conventions. Catches missing frontmatter, broken cross-references, naming drift, and structural issues before they ship.

## Arguments

- _(none)_ — validate everything
- `claude` — validate only `claude/` skills
- `copilot-native` — validate only `copilot-native/` assets
- `domain-review` — validate only `claude/domain-review/` domains and profiles
- `<path>` — validate a specific file or directory

## Checks

### Claude skills (`claude/*/SKILL.md`)

For each top-level skill directory (not `_rubrics/`, not nested specialists):

1. **SKILL.md exists** in the directory
2. **Frontmatter** has `name:` and `description:` fields
3. **`name:` matches directory name** — `claude/plan/SKILL.md` must have `name: plan`
4. **Description is quoted** and under 200 characters
5. **No orphan directories** — every `claude/*/` has a SKILL.md (except `_rubrics/`)

### Claude rubrics (`claude/_rubrics/*/SKILL.md`)

1. **SKILL.md exists**
2. **Frontmatter** has `name:` and `description:`
3. **Not user-invokable** — rubrics should not appear in skill-help categories

### Code review domains (`claude/domain-review/concept/*.md`)

Run the existing validation script: `bash claude/domain-review/tests/validate-structure.sh`

Report the result. If it fails, surface the specific failures.

### Copilot-native prompts (`copilot-native/prompts/**/*.prompt.md`)

1. **Frontmatter** has `description:` field
2. **File extension** is `.prompt.md`
3. **Path convention** — prompts live under `copilot-native/prompts/{category}/`

### Copilot-native agents (`copilot-native/agents/*.agent.md`)

1. **Frontmatter** has `description:` field
2. **Frontmatter** has `tools:` list
3. **File extension** is `.agent.md`

### Copilot-native skills (`copilot-native/skills/*/SKILL.md`)

1. **SKILL.md exists** in the directory
2. **Frontmatter** has `name:` and `description:` fields

### Cross-platform checks

1. **Asset catalog** — if `copilot-native/asset-catalog.md` exists, verify every file listed in it actually exists
2. **README references** — if `claude/domain-review/README.md` lists domains, verify they exist
3. **Profile references** — every domain ID in a profile YAML resolves to a file

## Output

```
=== Skill Library Validation ===

Claude skills: N checked, M issues
Copilot-native: N checked, M issues
Code review domains: N checked, M issues

Issues:
  [WARN] claude/foo/SKILL.md — name "bar" doesn't match directory "foo"
  [ERROR] copilot-native/agents/missing.agent.md — listed in asset-catalog but file not found
  [WARN] claude/baz/SKILL.md — description exceeds 200 characters

Summary: N errors, M warnings
```

## Rules

- **ERROR** = something is broken (missing file, broken reference, missing required field)
- **WARN** = convention violation (naming mismatch, long description, deprecated pattern)
- Report counts at the end. Exit with nonzero if any ERRORs.
