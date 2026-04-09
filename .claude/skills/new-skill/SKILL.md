---
name: new-skill
description: "Scaffold a new skill with correct structure and frontmatter for both claude/ and copilot-native/ platforms."
---

# /new-skill — Scaffold a New Skill

**Purpose:** Create a new skill with the correct directory structure, frontmatter, and boilerplate for one or both platforms. Ensures naming conventions, file placement, and cross-platform parity from the start.

## Arguments

- `<name>` — the skill name (required). Used as directory name and `name:` frontmatter field.
- `--platform claude|copilot|both` — which platform(s) to scaffold (default: `both`)
- `--type skill|rubric` — whether this is a user-invokable skill or a non-invokable rubric (default: `skill`)

## Workflow

### 1. Validate the name

- Must be lowercase, kebab-case, no special characters: `[a-z0-9-]+`
- Must not conflict with an existing directory in `claude/` or `copilot-native/skills/`
- If it conflicts, list the existing skill and ask the user: rename, replace, or abort

### 2. Ask for description

Ask the user for a one-line description (under 200 characters). This becomes the `description:` frontmatter field on both platforms. The description should:
- Start with a verb or noun, not "A skill that..."
- Say what it does and when to use it
- Fit in a table cell

### 3. Ask for purpose

Ask the user for a 1-2 sentence purpose statement. This becomes the first paragraph after the heading.

### 4. Scaffold Claude skill

**For `--type skill`:** Create `claude/<name>/SKILL.md`:

```markdown
---
name: <name>
description: "<description>"
---

# /<name> — <Title Case Name>

**Purpose:** <purpose statement>

## Arguments

- _(none)_ — <default behavior>

## Workflow

### 1. <First step>

<step content>

## Rules

- <rule 1>
```

**For `--type rubric`:** Create `claude/_rubrics/<name>/SKILL.md`:

```markdown
---
name: <name>
description: "<description>"
---

# <Title Case Name>

<purpose statement>

## <Section 1>

<content>
```

### 5. Scaffold copilot-native prompt (if `--platform copilot` or `both`)

Create `copilot-native/prompts/<category>/<name>.prompt.md`:

Ask which category (`ba/`, `dev/`, `review/`, `common/`) the prompt belongs to.

```markdown
---
description: >-
  <description>
argument-hint: "<optional argument hint>"
---

<prompt content mirroring the claude skill's workflow>
```

### 6. Update asset catalog

If `copilot-native/asset-catalog.md` exists, append the new prompt to the appropriate section.

### 7. Update skill-help categories

Read `claude/skill-help/SKILL.md` and suggest which category the new skill belongs to. Do NOT auto-edit — show the suggested line and ask for confirmation.

### 8. Confirm

Print:
```
Created:
  claude/<name>/SKILL.md
  copilot-native/prompts/<category>/<name>.prompt.md  (if applicable)

Next: edit the SKILL.md to add your workflow steps.
```

## Rules

- **One question at a time.** Don't batch prompts. Ask name, then description, then purpose, then category.
- **Don't generate workflow content.** The scaffold creates the structure with placeholder sections. The user fills in the workflow — that's the creative work.
- **Respect existing patterns.** Read 2-3 existing skills to match the current style before scaffolding.
