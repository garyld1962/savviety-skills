# Gamma Prompt — Token Management Deck

Paste the content below directly into Gamma's "Generate from outline" prompt box.

---

## PROMPT

Create a presentation deck for a software engineering audience titled **"Putting Your Context on a Diet"** with the subtitle **"Token & Context Management for AI-Assisted Development"**.

Tone: direct, technical, practitioner-level. No fluff. Use tables, code blocks, and bullet lists where they aid clarity. Avoid motivational language. This is for engineers who write production code.

---

### Slide 1 — Title Slide

**Title:** Putting Your Context on a Diet
**Subtitle:** Token & Context Management for AI-Assisted Development
**Tagline:** Using AI skills to develop software is an abstraction of coding, but not an abstraction of engineering.

---

### Slide 2 — Agenda

Three parts:
1. AI as an Abstraction of Coding — the new programming model
2. What Is an AI Skill — the engineered artifact
3. Token & Context Management — the discipline that keeps it working

---

## PART 1 — AI AS AN ABSTRACTION OF CODING

### Slide 3 — Part 1 Summary

**Heading:** AI as an Abstraction of Coding

We are still expressing intent in a machine-actionable form. The artifacts changed shape — from source code to prompts, context, skills, schemas, and evals. The engineering discipline did not change. It moved upstream.

Three ideas:
- AI-assisted development is still programming — just at a higher abstraction layer
- Context management is dependency management
- Engineering discipline matters more, not less

---

### Slide 4 — This Is Still Programming

**Heading:** This Is Still Programming

Traditional development:
```
Requirements → Source code → Compiler → Executable behavior
```

AI-assisted development:
```
Intent + context + constraints → LLM → generated code / actions
```

Table — The new programming layer:

| Traditional software | AI-assisted software |
|---|---|
| Source code | Prompts, context, examples, skills |
| Compiler | LLM |
| Imports / dependencies | Context window |
| Libraries | Tools, APIs, MCP servers, skills |
| Unit tests | Evals, regression prompts, validation |
| Code review | Review of prompts, generated code, and outputs |

> Prompts and skills are not a replacement for code. They are source files in a new layer of the stack.

---

### Slide 5 — Context Management Is Dependency Management

**Heading:** Context Management Is Dependency Management

The context window is not chat history. It is the build environment.

Table — Bad habits map directly:

| Bad software habit | Bad AI habit |
|---|---|
| Import everything | Dump everything into context |
| Use global state everywhere | Put every rule in global CLAUDE.md |
| Ignore dependency versions | Ignore stale or conflicting context |
| Skip interfaces | Use vague prompts and undefined outputs |
| No tests | Trust generated code without validation |

> Garbage context is like linking against the wrong library. The program may still run, but now you are debugging ghosts.

---

### Slide 6 — Engineering Discipline Moves Upstream

**Heading:** Engineering Discipline Moves Upstream

Table — Old principles, new application:

| Software engineering principle | AI-era equivalent |
|---|---|
| Modularity | Skills with narrow responsibilities |
| Least privilege | Scoped tools and limited context |
| Dependency hygiene | Context discipline |
| Type safety | Schemas and output contracts |
| Testing | Evals and validation |
| Performance tuning | Prompt cache, model routing, token budgets |
| Observability | Logs, traces, tool outputs |

> The danger is not that developers stop coding. The danger is that they stop engineering.

---

### Slide 7 — Part 1 Takeaways

**Heading:** Part 1 Takeaways

1. AI skills are a new programming layer — same engineering principles, higher-level artifacts
2. Context is the new dependency graph — manage it with the same discipline as imports and libraries
3. Engineering discipline matters more, not less — AI increases the speed of producing bad software too

---

## PART 2 — WHAT IS AN AI SKILL

### Slide 8 — Part 2 Summary

**Heading:** What Is an AI Skill?

> A prompt is a request. A skill is an engineered artifact.

An AI skill packages intent, context, instructions, tools, constraints, model choice, and validation into a workflow an LLM can execute reliably.

A skill answers six questions:
- What job does this do?
- When should it run?
- What context does it need?
- What tools may it use?
- What should the output look like?
- How do we know it worked?

> Skills are not magic. They are packaged engineering judgment.

---

### Slide 9 — The 12-Part Definition (Part A)

**Heading:** Anatomy of a Skill — Inputs & Process

1. **Intent** — clear reason to exist; vague intent means the model improvises
2. **Trigger** — slash command, workflow event, or routing rule; loaded on demand, not always
3. **Scope** — what the skill owns and does not own; prevents context side quests
4. **Required context** — minimum useful inputs: PRD, conventions, relevant files, contracts
5. **Workflow instructions** — explicit steps that turn vague prompting into repeatable execution
6. **Input contract** — defined required inputs; prevents the model from guessing or inventing data

---

### Slide 10 — The 12-Part Definition (Part B)

**Heading:** Anatomy of a Skill — Execution & Governance

7. **Tool contract** — what tools, APIs, files the skill may use; follow least privilege
8. **Model profile** — match model tier to task depth; model assignment is design, not afterthought
9. **Guardrails** — what the skill must not do; seatbelts for probabilistic systems
10. **Output contract** — defined shape, length, format; as structured as necessary, as short as possible
11. **Evals** — golden examples, regression prompts, rubrics; without evals it is just a hope with a nice filename
12. **Lifecycle** — version history, owner, change log; if it influences delivery, treat it like a delivery asset

---

### Slide 11 — Skill vs. Prompt

**Heading:** Skill vs. Prompt

| Prompt | Skill |
|---|---|
| One-off request | Reusable capability |
| Often informal | Designed artifact |
| Usually unversioned | Versioned and owned |
| Context is improvised | Context is curated |
| Output may vary wildly | Output contract is defined |
| Hard to test | Can be evaluated |

A prompt asks the model to do something.
A skill teaches the system how to do something repeatedly.

---

### Slide 12 — Skill vs. Traditional Code

**Heading:** Skill vs. Traditional Code

| Traditional software | AI skill equivalent |
|---|---|
| Function | Skill invocation |
| Function signature | Input and output contract |
| Imports | Context and tools |
| Runtime configuration | Model and execution profile |
| Type system | Schemas and validators |
| Unit tests | Evals and golden examples |
| Code ownership | Skill ownership |
| Refactoring | Prompt, context, and workflow cleanup |

> AI skills are an abstraction of coding, but not an abstraction of engineering.

---

### Slide 13 — Skill Checklist

**Heading:** Before You Call It a Skill

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

## PART 3 — TOKEN & CONTEXT MANAGEMENT

### Slide 14 — Part 3 Summary

**Heading:** Token & Context Management

Context is a finite resource. Every token consumed is a token unavailable for reasoning, synthesis, and output. Five categories of discipline:

1. Context Budget Management — govern consumption and discard
2. Cost-by-Capability Routing — right model for the right task
3. Tooling & Infrastructure — reduce consumption at the infrastructure level
4. Guardrails Against Runaway Spending — hard limits for loops and spirals
5. Review Quality vs. Token Tradeoff — maximize signal per token in reviews

---

### Slide 15 — CLAUDE.md Rules: Token Efficiency

**Heading:** Three-Axis Token Budget

**Input — what you read:**
- Targeted reads: `rg` + line-range views, not `cat` on whole files
- Don't re-read files already in context this session
- Sample logs — 20 lines usually tells you what 20,000 would

**Output — what you write:**
- No preamble, no narration of routine actions, no recap of the user's request
- Match reply length to question weight — one-line questions get one-line answers

**Context — what you reuse:**
- Never re-emit unchanged code — use targeted edits
- Don't repeat caveats across sections
- Compress summaries of prior work aggressively

> Test: if removing a sentence wouldn't change what the user can act on, remove it.

---

### Slide 16 — Context Window Hygiene

**Heading:** Clear Context at Phase Boundaries

Prior context becomes ballast when the phase changes. Suggest a fresh session at these boundaries:

| Boundary | Why clear |
|---|---|
| Plan → Execute | Exploration that produced the plan is dead weight once it's written |
| Research → Implement | Search queries don't help implementation |
| Review → Fix | Review framing biases toward the reviewer, not the code's reality |
| Long debugging → Clean attempt | 15+ turns pollutes context with wrong hypotheses |
| Multi-repo switch | Prior repo file contents waste context |

Also watch for **mid-session context drift** — when the current task has shifted so far that most existing tool output is irrelevant.

---

### Slide 17 — Context Budget Management

**Heading:** Group 1 — Context Budget Management

**Three-Axis Token Budget**
Input, output, and context each have explicit rules. Read targeted ranges. Write no preamble. Never re-emit unchanged code.

**Context Window Phase Clearing**
Clear context at plan/research/review phase boundaries. Start fresh so the next phase loads only what it needs.

**Cross-Session Memory Compression**
Rolling memory system compresses prior work into a digest. Fresh sessions read the digest — not raw tool output — eliminating session-start reconstruction cost.

---

### Slide 18 — Cost-by-Capability Routing

**Heading:** Group 2 — Cost-by-Capability Routing

**Model Tier Pinning**
- `haiku` — dispatcher and lookup skills (fast, cheap, high frequency)
- `opus` — deep-reasoning skills (triage, adversarial review, architecture judgment)
- Unpinned — inherits session model (everything else)

**Haiku-as-Router Pattern**
Routing skills fire at the entry point of every skill chain. They run constantly. Pinning them to Haiku is the highest-ROI tier decision in the policy.

> Model assignment is part of skill design, not an afterthought.

---

### Slide 19 — Tooling & Infrastructure

**Heading:** Group 3 — Tooling & Infrastructure

**RTK — Rust Token Killer**
Hook-based CLI proxy. Intercepts all shell commands and compresses output before it reaches the context window. Claimed 60–90% savings on common dev operations. Transparent — rewrites `git status` → `rtk git status` automatically.

**Parallel Execution Lanes**
Disjoint-write-scope lanes with milestone barriers replace sequential back-and-forth. Each lane gets a narrow shared context packet — not the full conversation history.

**WSL/Bash over Windows/PowerShell**
Unix commands emit compact, pipeable text. PowerShell serializes structured objects with verbose headers and type annotations that inflate context with low-signal content. Compounds across a long session.

---

### Slide 20 — Guardrails Against Runaway Spending

**Heading:** Group 4 — Guardrails Against Runaway Spending

**Token Guardrail in Scanning Skills**
Hard stop at ~30% context consumed during file scanning. The remaining 70% is reserved for synthesis. Prevents large codebases from crowding out the work that produces output.

**Retry Budget Circuit Breaker**
Configurable retry budget (default: 20 retries / 60 min). When exhausted, the executor surfaces the impasse instead of looping. Prevents token burn on a wrong mental model of the problem.

> After two failed attempts at the same fix — stop. Describe what you tried, what you observed, and what doesn't match your mental model. Don't try a third variant of the same idea.

---

### Slide 21 — Review Quality vs. Token Tradeoff

**Heading:** Group 5 — Review Quality vs. Token Tradeoff

**Separate-Pass Domain Reviews**
Each review domain — security, performance, data integrity, concurrency — gets its own isolated context window pass.

Why it matters:
- Combined prompt → shallow bullet-per-domain output
- Isolated passes → forced depth per domain
- Tradeoff: more total tokens spent, but higher signal per token
- Findings are actionable, not superficial

> The goal is not to minimize tokens spent on review. It is to maximize what each token produces.

---

### Slide 22 — Closing

**Heading:** The Code Changed Shape. The Engineering Did Not.

Key takeaways for engineers:
- Treat context like a dependency graph — scope it, version it, keep it clean
- Match model tier to task complexity — cost-by-capability is a design decision
- Use skills as packaged, reusable context — declare once, invoke cheaply
- Set hard limits — guardrails prevent loops, not just mistakes
- Clear context at phase boundaries — fresh sessions are faster than polluted ones

---

> Using AI skills to develop software is an abstraction of coding, not an abstraction of engineering.

> The future is not vibe-driven prompting. It is engineered context.

> Vibes are not a build system.
