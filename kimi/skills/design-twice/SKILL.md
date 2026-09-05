---
name: design-twice
description: 'Explore multiple radically different API/module designs using parallel
  agents before committing. Use when designing a new interface, module API, or public
  surface — phrases like ''design it twice'', ''explore the design space'', ''what
  are my options for this interface'', ''compare API shapes'', ''how should this module
  look''. When NOT to Use: implementation details inside an existing interface (use
  superpowers:writing-plans); evaluating existing code (use /code-review).'
whenToUse: 'Explore multiple radically different API/module designs using parallel
  agents before committing. Use when designing a new interface, module API, or public
  surface — phrases like ''design it twice'', ''explore the design space'', ''what
  are my options for this interface'', ''compare API shapes'', ''how should this module
  look''. When NOT to Use: implementation details inside an existing interface (use
  superpowers:writing-plans); evaluating existing code (use /code-review).'
---


# /skill:design-twice -- Explore the Design Space

**Purpose:** Generate 3+ radically different designs for a module's interface in parallel, then compare them on depth, simplicity, and fit. Based on the "Design It Twice" principle from *A Philosophy of Software Design*: your first design idea is rarely your best.

## When to Use

- Designing a new API, module, or public interface
- You have one idea but want to validate it against alternatives
- The team is debating between approaches and the trade-offs aren't clear
- Any time you say "how should this work?"

## When NOT to Use

- Implementation details inside an existing interface — use `superpowers:writing-plans`
- Evaluating existing code quality — use `/code-review`
- UI/visual layout — use `/review-design`

## Workflow

### 1. Gather Requirements

Before designing anything, understand:

- What problem does this module solve?
- Who are the callers? (other modules, external users, tests)
- What are the key operations?
- Any constraints? (performance, compatibility, existing patterns)
- What complexity should be hidden vs exposed?

Ask: "What does this need to do, and who will call it?"

### 2. Generate Designs (Parallel Agents)

Spawn 3 sub-agents simultaneously. Assign each a different design constraint — enforce radical difference.

```
Prompt per agent:

Design an interface for: [module description]
Requirements: [gathered requirements]

Constraint for this design:
  Agent 1: "Minimize surface area — aim for 1-3 methods maximum"
  Agent 2: "Maximize flexibility — support every plausible use case"
  Agent 3: "Optimize for the most common case — everything else secondary"

Output:
  1. Interface signature (types, methods, params)
  2. Caller usage example — how someone actually uses this
  3. What complexity this design hides internally
  4. Trade-offs: where this design wins and loses
```

### 3. Present Designs

Show each design sequentially — let the user absorb one before seeing the next:
- **Signature** — types, methods, params
- **Usage** — realistic caller example
- **Hides** — what complexity stays internal
- **Trade-offs** — honest wins and losses

### 4. Compare

Before presenting any comparison to the user, engage extended thinking to reason privately:
- Which axis creates the most consequential divergence between the three designs?
- Is any design clearly superior, or is the choice genuinely context-dependent?
- Are there elements from different designs that would combine cleanly without defeating either?
- What would a senior engineer maintaining this in three years wish had been chosen?

Use that reasoning to anchor the prose comparison — the thinking shapes what you surface, not just what the axes mechanically score.

Evaluate all designs against these axes:

| Axis | What to ask |
|------|-------------|
| **Depth** | Small interface hiding real complexity? (good) Large interface with thin internals? (bad) |
| **Simplicity** | Fewer methods, simpler params — easier to learn and harder to misuse |
| **Generality** | Handles future cases without changes? Beware over-generalizing. |
| **Implementation fit** | Does the interface shape allow efficient internals, or force awkward ones? |
| **Ease of correct use** | Can callers do the right thing without reading docs? |

Discuss trade-offs in prose. Highlight where designs diverge most — that's where the decision lives.

### 5. Synthesize

The best design often borrows from multiple options. Ask:
- "Which fits your primary use case best?"
- "Anything from the other designs worth incorporating?"

## Anti-Patterns

- Don't let agents produce similar designs — enforce the constraint difference
- Don't evaluate based on implementation effort (that comes later)
- Don't skip comparison — the value is the contrast, not the individual designs
- Don't implement — this skill is interface shape only
