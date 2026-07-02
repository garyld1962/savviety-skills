# What Is an AI Skill?

## One-sentence definition

An **AI skill** is a reusable, versioned, on-demand software capability that packages intent, context, instructions, tools, constraints, model choice, and validation into a workflow an LLM can execute reliably.

Put another way:

> A prompt is a request. A skill is an engineered artifact.

A skill should not be treated as a clever paragraph of instructions. It should be treated like a small software module: it has a purpose, dependencies, inputs, outputs, runtime assumptions, guardrails, tests, and ownership.

---

## The talk-friendly version

A skill is the AI-era equivalent of a well-designed function, module, or service endpoint.

It should answer:

- What job does this do?
- When should it run?
- What context does it need?
- What tools may it use?
- What should the output look like?
- How do we know it worked?

The point is not to make prompts longer. The point is to make AI behavior **repeatable, scoped, reviewable, and testable**.

> Skills are not magic. They are packaged engineering judgment.

---

## The 12-part definition of an AI skill

### 1. Intent

The skill must have a clear reason to exist.

**Question it answers:** What problem does this skill solve?

**Good example:**  
“Review a pull request for correctness, security, maintainability, and test coverage.”

**Bad example:**  
“Help with code.”

If the intent is vague, the model will improvise. Improvisation is great for jazz, less great for production delivery pipelines.

---

### 2. Trigger or invocation

A skill should define when and how it is used.

**Question it answers:** When should this skill be loaded?

Examples:

- Slash command: `/code-review`
- Workflow event: “When a PR is opened”
- User request: “Review this implementation plan”
- Agent routing rule: “Use this skill for changelog generation”

This matters because skills should be **loaded on demand**, not dumped into the model’s context all the time.

---

### 3. Scope and boundaries

A skill should know what it owns and what it does not own.

**Question it answers:** What is inside and outside the skill’s responsibility?

Example boundaries:

- This skill reviews code but does not modify it.
- This skill proposes a plan but does not execute changes.
- This skill reads only the files included in the diff.
- This skill reports risks but does not approve releases.

Good scope prevents the model from wandering into adjacent work and burning context on side quests.

---

### 4. Required context

A skill should define the minimum useful context required to do the job.

**Question it answers:** What does the model need to know before acting?

Examples:

- PRD or user story
- Repository conventions
- Relevant source files
- API contracts
- Test results
- Error logs
- Architecture decision records

This is where context management becomes dependency management. The skill should load the right dependencies, not every dependency.

> The context window is not chat history. It is the build environment.

---

### 5. Workflow instructions

A skill should describe the process the model should follow.

**Question it answers:** What steps should the model take?

Example:

1. Identify the changed files.
2. Classify the change by domain.
3. Review only the relevant files.
4. Deduplicate findings.
5. Rank findings by severity.
6. Return concise, actionable feedback.

Workflow instructions turn vague prompting into repeatable execution.

---

### 6. Input contract

A skill should define what inputs it expects.

**Question it answers:** What must be provided for this skill to run correctly?

Examples:

- A PR number
- A story ID
- A diff summary
- A target branch
- A log file path
- A design document
- A JSON payload

A good input contract prevents the model from guessing, searching blindly, or inventing missing data.

---

### 7. Tool and interface contract

A skill should define what tools, APIs, files, or systems it may use.

**Question it answers:** What is the skill allowed to touch?

Examples:

- Read-only repository access
- Azure DevOps work items
- GitHub pull requests
- Test runner
- Static analysis tool
- Documentation server
- Ticketing system

This is the AI equivalent of dependency imports and service permissions. Tool access should follow least privilege.

> Do not give every skill every tool “just in case.” That is how you get expensive chaos with autocomplete.

---

### 8. Model and runtime profile

A skill should define the appropriate model and runtime expectations.

**Question it answers:** How much intelligence does this task actually need?

Examples:

- Low-cost model for repo status, changelogs, summaries, and simple reports
- Mid-tier model for implementation planning, validation, and code review
- Stronger model for adversarial review, triage, architecture judgment, and complex reasoning

Not every task deserves the most expensive model. Reads and reports usually do not need the same model as security review or architecture tradeoff analysis.

> Model assignment is part of skill design, not an afterthought.

---

### 9. Constraints and guardrails

A skill should define what the model must not do.

**Question it answers:** What behavior is unsafe, wasteful, or out of bounds?

Examples:

- Do not modify files unless explicitly instructed.
- Do not read entire large logs; sample and search first.
- Do not call external services without permission.
- Do not expose secrets.
- Do not invent APIs or requirements.
- Do not approve your own output.

Constraints are not bureaucracy. They are seatbelts for probabilistic systems.

---

### 10. Output contract

A skill should define the shape, length, and format of the response.

**Question it answers:** What should the result look like?

Examples:

- Markdown checklist
- JSON object matching a schema
- One-page review summary
- Findings grouped by severity
- Patch file
- Test plan
- Release note

Output contracts reduce ambiguity, make results easier to review, and prevent token bloat.

A useful default:

> The output should be as structured as necessary and as short as possible.

---

### 11. Examples and evals

A skill should include examples of good behavior and a way to test whether it still works.

**Question it answers:** How do we know the skill performs correctly over time?

Examples:

- Golden input/output examples
- Regression prompts
- Expected findings for known bad code
- Test cases for malformed input
- Evaluation rubrics
- Acceptance criteria

Without evals, a skill is just a hope with a nice filename.

---

### 12. Observability, versioning, and ownership

A skill should be maintainable.

**Question it answers:** Who owns this, what changed, and how do we debug it?

Examples:

- Version history
- Owner or team
- Change log
- Known limitations
- Usage logs
- Failure examples
- Review cadence
- Rollback path

If a skill influences software delivery, it deserves the same lifecycle discipline as other delivery assets.

---

## Compact checklist

Before calling something a skill, ask whether it has:

| # | Dimension | Key question |
|---:|---|---|
| 1 | Intent | What job does it do? |
| 2 | Trigger | When is it invoked? |
| 3 | Scope | What is in and out of bounds? |
| 4 | Context | What information does it need? |
| 5 | Workflow | What process should it follow? |
| 6 | Input contract | What inputs are required? |
| 7 | Tool contract | What tools may it use? |
| 8 | Model profile | What model/runtime does it need? |
| 9 | Guardrails | What must it avoid? |
| 10 | Output contract | What should it produce? |
| 11 | Evals | How is correctness tested? |
| 12 | Lifecycle | Who owns it and how does it evolve? |

---

## Why this matters for engineering teams

The skill model keeps teams from treating AI as a pile of ad hoc prompts. It turns AI usage into something closer to software architecture.

A mature skill is:

- **Reusable**: declared once, invoked many times
- **Scoped**: loaded only when needed
- **Composable**: can be combined with other skills and tools
- **Reviewable**: changes can be inspected like code changes
- **Testable**: behavior can be evaluated over time
- **Governable**: permissions, model choice, and output shape are explicit
- **Economical**: expensive context and expensive models are used deliberately

This is why skills matter for context management. A skill packages context so developers do not have to keep retyping, rediscovering, or reloading the same instructions.

> Declare once. Invoke cheaply. Reuse forever.

---

## Skill versus prompt

| Prompt | Skill |
|---|---|
| One-off request | Reusable capability |
| Often informal | Designed artifact |
| Usually unversioned | Versioned and owned |
| Context is improvised | Context is curated |
| Output may vary wildly | Output contract is defined |
| Hard to test | Can be evaluated |
| Easy to copy-paste badly | Easier to govern and improve |

A prompt asks the model to do something.  
A skill teaches the system how to do something repeatedly.

---

## Skill versus traditional code

| Traditional software concept | AI skill equivalent |
|---|---|
| Function | Skill invocation |
| Function signature | Input and output contract |
| Imports | Context and tools |
| Runtime configuration | Model and execution profile |
| Type system | Schemas and validators |
| Unit tests | Evals and golden examples |
| Logging | Traces and tool outputs |
| Code ownership | Skill ownership |
| Refactoring | Prompt, context, and workflow cleanup |

This is the heart of the argument:

> AI skills are an abstraction of coding, but not an abstraction of engineering.

---

## Example skill skeleton

This is not meant to be universal syntax. It is a pattern for thinking about the artifact.

```markdown
---
name: code-review
description: Review a pull request for correctness, security, maintainability, and test coverage.
model: sonnet
allowed_tools:
  - git diff
  - test runner
  - static analyzer
owner: engineering-platform
version: 1.3
---

# Intent
Review code changes and return concise, actionable findings.

# Trigger
Use when a developer asks for a PR review or when a pull request enters review.

# Scope
Review changed files and directly related dependencies only. Do not modify code.

# Required Context
- PR description
- Diff summary
- Relevant source files
- Test output, if available
- Repository conventions

# Workflow
1. Identify changed files.
2. Classify changes by domain.
3. Read only relevant file ranges.
4. Check correctness, security, maintainability, and test coverage.
5. Deduplicate findings.
6. Rank by severity.

# Constraints
- Do not invent requirements.
- Do not read unrelated files.
- Do not return low-value style nits unless they affect maintainability.
- Do not approve your own output.

# Output Contract
Return findings grouped by severity:

- Critical
- High
- Medium
- Low
- No findings

Each finding must include:

- File/location
- Issue
- Why it matters
- Suggested fix

# Evals
Run against known PR examples with seeded defects and compare expected findings.
```

---

## Soundbites for the talk

> A skill is not a bigger prompt. It is a smaller program.

> Skills turn prompting from conversation into architecture.

> Context is dependency management; skills are dependency packaging.

> A prompt is a request. A skill is a repeatable capability.

> Vibes are not a build system.

> AI does not remove engineering discipline. It moves that discipline upstream.

