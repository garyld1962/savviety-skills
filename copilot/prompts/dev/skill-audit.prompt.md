---
description: >-
  Audit a Copilot asset set (prompts, agents, skills, instructions, and repo
  instructions) against GitHub Copilot platform capabilities. Identify
  duplication with built-ins, missing structure, and a modernization path. In
  `--native-overlap` mode, audit this source repo's custom Copilot prompts for
  description overlap with Copilot built-ins and installed skills.
argument-hint: "[path to .github folder or source repo folder] [--native-overlap [prompt-name]]"
agent: "agent"
tools:
  - read
  - search
  - codebase
---

# Copilot Asset Audit

Review an existing Copilot asset set and recommend how to make it more Copilot-native.

Follow the skill: `.github/skills/copilot-platform-playbook/SKILL.md`

## Modes

- Default mode: portfolio audit of prompts, agents, skills, instructions, and
  repo-level guidance.
- `--native-overlap [prompt-name]`: source-repo maintenance mode for checking
  whether custom Copilot prompts compete with Copilot built-ins or installed
  skills at the description level.

## Native-overlap mode

Use `--native-overlap` only in the savviety-skills source repo, where the
custom Copilot prompt library lives under `copilot/prompts/`.

### Purpose

Find custom prompts whose descriptions are too broad, duplicate a built-in, or
would benefit from an explicit built-in handoff or cross-reference.

### Catalog rule

Use the current session's available built-ins and skills as the native catalog.
Do not invent native capabilities that are not visible in the session.

### Scope

Audit user-invokable prompt files under `copilot/prompts/**/*.prompt.md`.
Ignore agents and internal knowledge skills for overlap scoring unless a prompt
explicitly delegates to them.

If `[prompt-name]` is supplied, restrict the audit to that one prompt.

### Verdicts

For each non-trivial overlap, assign exactly one verdict:

| Verdict | When | Recommended action |
|---|---|---|
| Tighten | The custom prompt is too broad and loses its trigger surface to a native | Sharpen the `description:` and trigger phrasing |
| Cross-reference | The prompt is a stricter repo-tailored version of a native capability | Add a built-in comparison block and say when to prefer the custom prompt |
| Integrate | The prompt should hand a specific step to a built-in | Add the built-in at the right workflow seam |
| Hand off | The built-in is better for part of the described territory | Expand `When NOT to Use` with the deferring condition |
| Redundant | The prompt adds no meaningful value over the native | Recommend retirement or consolidation |

### Output

Produce a short report with:

- prompt name
- current description
- overlapping native built-in or skill
- verdict
- concrete edit recommendation

Default to report-only. If the user asks for edits, update descriptions,
relationship text, and `When NOT to Use` sections narrowly rather than rewriting
the whole prompt.

## Audit scope

Review:

- prompts
- agents
- skills
- instructions
- repo-level `copilot-instructions.md`
- overlap with Copilot built-ins

## Expected output

Produce:

- strengths worth keeping
- duplicate or weak assets worth simplifying
- gaps where custom assets still add value
- recommended target architecture
- quick wins
- staged migration plan

## Gap Analysis

After completing the asset audit, identify capability gaps by cross-referencing
what the project actually needs against what the current asset set covers.

### Gap categories

1. **Missing capabilities** — workflows the project needs that no current prompt, agent, or skill addresses. Look for repeated ad-hoc patterns in copilot-instructions.md that should be promoted to a proper prompt or skill.
2. **Duplicate coverage** — multiple assets that do the same thing (e.g., two review prompts, two planning agents). Keep the one with more Copilot-native leverage; simplify or remove the other.
3. **Built-in duplicates** — assets that replicate behavior Copilot already provides natively (e.g., a "write unit tests" prompt when Copilot's built-in `/tests` covers it). Flag for simplification, not deletion — only remove if the custom asset adds no domain-specific value.
4. **Stale assets** — prompts or agents referencing old model names, deprecated tool calls, or workflows the team no longer uses.

> **Source-repo authors:** use `--native-overlap` when the question is
> description-level overlap between this repo's custom prompts and Copilot
> built-ins or installed skills. Default mode is for broader portfolio and
> architecture audits.

### Gap report format

```
## Gap Analysis

### Missing Capabilities
| Gap | Suggested asset type | Priority |
|-----|----------------------|---------- |
| ... | prompt / agent / skill / instruction | High/Med/Low |

### Duplicate Coverage
| Capability | Covered by | Recommendation |
|------------|------------|----------------|
| ... | asset A + asset B | keep A, simplify B |

### Built-in Duplicates (simplification candidates)
| Asset | Built-in equivalent | Custom value remaining? |
|-------|---------------------|-------------------------|
| ... | Copilot /tests | None — recommend removal |

### Stale Assets
| Asset | Issue |
|-------|-------|
| ... | References deprecated X |
```

## Marketplace Discovery

Check the awesome-copilot marketplace (github.com/github/awesome-copilot) for
Copilot plugins and skills that address identified gaps or upgrade existing assets.

1. Browse `github.com/github/awesome-copilot` for prompts, agents, and skills relevant to the project's languages, frameworks, and workflows.
2. For each candidate found, score relevance:

   | Signal | Score |
   |--------|-------|
   | Language/framework match | +3 |
   | Deployment target match | +2 |
   | Workflow pattern match | +2 |
   | Domain overlap | +1 |
   | No overlap | −5 (skip) |

3. Only recommend items with relevance score ≥ 3.
4. For each recommended item: state what gap it fills, where it lives in awesome-copilot, and what (if any) existing asset it would replace or simplify.

### Marketplace report format

```
## Marketplace Candidates

| Item | Source (awesome-copilot section) | Relevance | Gap filled | Replaces |
|------|----------------------------------|-----------|------------|---------|
| ... | ... | High/Med | ... | none / asset X |
```

## Modernization Path

Identify assets that should be simplified because Copilot built-ins now cover
the same ground, and produce a staged plan.

Stage 1 — Quick wins (no behavior change, just cleanup):
- Assets with zero custom value over a built-in → mark for removal
- Duplicate assets → consolidate to one

Stage 2 — Restructure (asset-type changes):
- Guidance buried in prompts that belongs in a skill or instruction → migrate
- Agents that are really just prompts → simplify to prompt

Stage 3 — Fill gaps (new assets):
- Create or install assets for identified missing capabilities (highest priority gaps first)

## CRITICAL: Do Not Guess

- Do NOT assume the repo structure; inspect it.
- Do NOT recommend removing custom assets just because a built-in exists; explain why the built-in is enough or where custom value remains.
- Do NOT rewrite the whole portfolio mentally. Separate "keep", "simplify", and "add".

## Built-in-first rule

When evaluating an asset, ask:

1. Is this replacing a built-in that already works well?
2. Is this adding domain-specific leverage the built-in does not provide?
3. Would this guidance be better placed in a skill or instruction instead of a prompt?
