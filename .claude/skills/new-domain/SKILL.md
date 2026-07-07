---
name: new-domain
description: "Scaffold a new domain-review domain (concept, dialect, or platform) with correct frontmatter, and update the relevant profiles."
---

# /new-domain — Scaffold a Code Review Domain

**Purpose:** Create a new domain file for the domain-review system with correct frontmatter and structure, then update the profile YAML files that should include it.

## Arguments

- `<name>` — the domain name (required). Becomes the filename.
- `--type concept|dialect|platform` — which axis (required)

## Workflow

### 1. Determine the axis

If `--type` not provided, ask:

- **concept** — language- and platform-agnostic lens. Describes the shape of the problem universally. Owns the output format and severity scale.
- **dialect** — language-specific overlay that extends a concept. Additive only. Short.
- **platform** — framework/service-specific overlay that extends a concept. For non-obvious failure modes.

### 2. Gather metadata

Ask one at a time:

**For concept:**
- Title (e.g., "Correctness", "UI Design & Accessibility")
- Which profiles should include it? (competence, comprehensive, pre-merge, pre-production, security-focused)
- Mode in each profile: `always` or `conditional`
- If conditional: what triggers it? (path globs, import patterns, prose description)

**For dialect/platform:**
- Title
- Which concept does it extend? (must be an existing concept file)
- Trigger paths and/or imports
- Which profiles' overlay lists should include it?

### 3. Scaffold the file

**Concept** → `claude/domain-review/concept/<name>.md`:

```markdown
---
id: concept/<name>
type: concept
title: <title>
extends: null
triggers:
  paths: []
  imports: []
  always: <true|false>
  profiles: [<profile list>]
  conditional: "<prose trigger description>"
severity_owner: true
---

# <Title>

You are a senior engineer reviewing this change for <lens>. Your job is to find <what>.

Scope: <what's in scope>. Do not comment on <what's out of scope>.

Actively hunt for:

- **<Smell 1>.** <Description>
- **<Smell 2>.** <Description>

**Bar-raising instruction:** do not say "<positive claim>" without having <specific verification work>. Name what you checked.

## Output format

\```
## Findings
[severity] [file:line] — [problem] — [fix]

## Questions
[things the reviewer needs to know to finalize]

## Verdict
[block | revise | accept-with-notes | accept]
\```

## Severity scale

- **critical** — will cause incident, data loss, or security breach in production. Blocks.
- **major** — meaningful degradation under load, real maintenance burden, or latent bug. Revise before merge.
- **minor** — worth fixing but not blocking. Leave a note.
- **nit** — style or taste. Mention once, don't belabor.
```

**Dialect** → `claude/domain-review/dialect/<name>.md`:

```markdown
---
id: dialect/<name>
type: dialect
title: <title>
extends: concept/<parent>
triggers:
  paths: [<globs>]
  imports: [<patterns>]
  always: false
  conditional: "<prose>"
severity_owner: false
---

# <Title> — Dialect Overlay

Extends `concept/<parent>` with <language>-specific smells.

## Additional smells to hunt for

- **<Smell 1>.** <Description>
```

**Platform** → `claude/domain-review/platform/<name>.md` (same structure as dialect but `type: platform`).

### 4. Update profiles

For each profile the user selected, edit the YAML file:
- Add the domain ID to the `domains:` list with the correct `mode:`
- For overlays, add the ID to the `overlays:` list

Show the diff and ask for confirmation before writing.

### 5. Update README

Add the new domain to the "Current domains" list in `claude/domain-review/README.md` under the appropriate section.

### 6. Run validation

Run `bash claude/domain-review/tests/validate-structure.sh` and report the result. All tests should pass with the new domain included.

### 7. Confirm

Print:
```
Created: claude/domain-review/<axis>/<name>.md
Updated profiles: <list>
Updated: claude/domain-review/README.md
Validation: PASSED (N tests)

Next: fill in the "Actively hunt for" section with domain-specific smells.
```

## Rules

- **Concepts own the format.** Only concepts get `severity_owner: true`, output format section, and severity scale.
- **Overlays are additive.** Don't repeat the parent concept's hunt list or format. Only add smells the parent can't see.
- **Every concept needs a bar-raising instruction.** The scaffold includes a placeholder — the user MUST fill it in with a specific verification task.
- **Validate after creation.** The structural tests catch broken references immediately.
