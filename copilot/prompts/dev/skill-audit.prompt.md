---
description: >-
  Audit a Copilot asset set (prompts, agents, skills, instructions, and repo
  instructions) against GitHub Copilot platform capabilities. Identify
  duplication with built-ins, missing structure, and a modernization path.
argument-hint: "[path to .github folder or source repo folder]"
agent: "agent"
tools:
  - read
  - search
  - codebase
---

# Copilot Asset Audit

Review an existing Copilot asset set and recommend how to make it more Copilot-native.

Follow the skill: `.github/skills/copilot-platform-playbook/SKILL.md`

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
