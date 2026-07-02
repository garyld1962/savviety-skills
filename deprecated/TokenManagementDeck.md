# Putting Your Context on a Diet

> Using AI skills to develop software is an abstraction of coding, but not an abstraction of engineering.

---

## Part 1 — AI as an Abstraction of Coding

We keep talking about AI-assisted coding as though it is a totally new thing. It is new in capability, but not in principle.

At the core, we are still doing what programmers have always done: expressing intent in a machine-actionable form.

The difference is that the source artifacts are changing. They are no longer just `.cs`, `.java`, `.ts`, or `.py` files. They now include prompts, context, examples, schemas, tool contracts, skills, memory, and evals.

That means the engineering discipline does not go away. It moves up the stack.

---

### This Is Still Programming

AI-assisted development moves programming up one abstraction layer.

**Traditional development:**

```
Requirements → Source code → Compiler/interpreter → Executable behavior
```

**AI-assisted development:**

```
Intent + context + constraints → LLM → generated code / actions
```

**The new programming layer:**

| Traditional software | AI-assisted software |
|---|---|
| PRD / requirements | Source of truth |
| Source code | Prompts, context, examples, skills |
| Compiler | LLM |
| Imports / dependencies | Context window |
| Libraries | Tools, APIs, MCP servers, skills |
| Unit tests | Evals, regression prompts, validation |
| Code review | Review of prompts, generated code, and outputs |

> Prompts and skills are not a replacement for code. They are source files in a new layer of the stack.

---

### Context Management Is Dependency Management

The context window is not chat history. It is the build environment.

**Bad context management looks like bad dependency management:**

| Bad software habit | Bad AI habit |
|---|---|
| Import everything | Dump everything into context |
| Use global state everywhere | Put every rule in global `CLAUDE.md` |
| Ignore dependency versions | Ignore stale or conflicting context |
| Skip interfaces | Use vague prompts and undefined outputs |
| No tests | Trust generated code without validation |

> Context should be scoped, intentional, reusable, and testable.

We are not saving tokens just to save money. We are protecting the signal. Every irrelevant file, stale instruction, bloated prompt, or repeated explanation competes with the useful context. The model may still produce an answer, but now you are making it reason through noise.

> Garbage context is like linking against the wrong library. The program may still run, but now you are debugging ghosts.

---

### Engineering Discipline Moves Upstream

AI does not remove best practices. It changes where we apply them.

| Software engineering principle | AI-era equivalent |
|---|---|
| Modularity | Skills with narrow responsibilities |
| Least privilege | Scoped tools and limited context |
| Dependency hygiene | Context discipline |
| Type safety | Schemas and output contracts |
| Testing | Evals and validation |
| Code review | Review generated code and prompt changes |
| Performance tuning | Prompt cache, model routing, token budgets |
| Observability | Logs, traces, tool outputs |

The dangerous mindset is: "AI writes the code, so we can relax the process." That is exactly backward. AI makes it easier to produce more software faster — including bad software. The engineering guardrails matter more, not less.

> The danger is not that developers stop coding. The danger is that they stop engineering.

---

### Three-Point Summary

**1. AI skills are a new programming layer.**
We are still expressing intent in a machine-actionable form. The artifacts have changed from only code to prompts, context, skills, schemas, examples, tool contracts, memory, and evals.

**2. Context is the new dependency graph.**
The model's output depends heavily on what we load, omit, repeat, or pollute. Context must be managed like dependencies: scoped, versioned, minimal, intentional, and reviewed.

**3. Engineering discipline matters more, not less.**
The practices we learned over decades still apply: modularity, testing, review, least privilege, observability, reuse, and cost/performance management. AI does not repeal software engineering. It raises the abstraction layer where it has to operate.

---

## Part 2 — What Is an AI Skill

> A prompt is a request. A skill is an engineered artifact.

An AI skill is a reusable, versioned, on-demand software capability that packages intent, context, instructions, tools, constraints, model choice, and validation into a workflow an LLM can execute reliably.

A skill should not be treated as a clever paragraph of instructions. It should be treated like a small software module: it has a purpose, dependencies, inputs, outputs, runtime assumptions, guardrails, tests, and ownership.

A skill should answer:

- What job does this do?
- When should it run?
- What context does it need?
- What tools may it use?
- What should the output look like?
- How do we know it worked?

The point is not to make prompts longer. The point is to make AI behavior **repeatable, scoped, reviewable, and testable**.

> Skills are not magic. They are packaged engineering judgment.

---

### The 12-Part Definition

**1. Intent** — What problem does this skill solve?
A clear reason to exist. If the intent is vague, the model will improvise. Improvisation is great for jazz, less great for production delivery pipelines.

**2. Trigger or invocation** — When should this skill be loaded?
A slash command, workflow event, user request, or agent routing rule. Skills should be loaded on demand, not dumped into context all the time.

**3. Scope and boundaries** — What is inside and outside the skill's responsibility?
This skill reviews code but does not modify it. This skill proposes a plan but does not execute changes. Good scope prevents the model from wandering into adjacent work and burning context on side quests.

**4. Required context** — What does the model need to know before acting?
The minimum useful context: PRD, repo conventions, relevant source files, API contracts, test results, error logs. This is where context management becomes dependency management — load the right dependencies, not every dependency.

> The context window is not chat history. It is the build environment.

**5. Workflow instructions** — What steps should the model take?
Explicit process turns vague prompting into repeatable execution.

**6. Input contract** — What must be provided for this skill to run correctly?
A PR number, story ID, diff summary, target branch, log file path. A good input contract prevents the model from guessing, searching blindly, or inventing missing data.

**7. Tool and interface contract** — What is the skill allowed to touch?
Read-only repository access, specific APIs, test runner, static analysis. Tool access should follow least privilege.

> Do not give every skill every tool "just in case." That is how you get expensive chaos with autocomplete.

**8. Model and runtime profile** — How much intelligence does this task actually need?
Low-cost model for repo status, changelogs, summaries. Mid-tier for planning and code review. Stronger model for adversarial review, architecture judgment, and complex reasoning.

> Model assignment is part of skill design, not an afterthought.

**9. Constraints and guardrails** — What behavior is unsafe, wasteful, or out of bounds?
Do not modify files unless instructed. Do not read entire large logs. Do not expose secrets. Do not invent APIs. Constraints are not bureaucracy — they are seatbelts for probabilistic systems.

**10. Output contract** — What should the result look like?
Markdown checklist, JSON schema, one-page summary, findings by severity. Output contracts reduce ambiguity and prevent token bloat.

> The output should be as structured as necessary and as short as possible.

**11. Examples and evals** — How do we know the skill performs correctly over time?
Golden input/output examples, regression prompts, expected findings for known bad code, evaluation rubrics. Without evals, a skill is just a hope with a nice filename.

**12. Observability, versioning, and ownership** — Who owns this, what changed, and how do we debug it?
Version history, owner, change log, known limitations, usage logs, rollback path. If a skill influences software delivery, it deserves the same lifecycle discipline as other delivery assets.

---

### Compact Checklist

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

### Skill vs. Prompt

| Prompt | Skill |
|---|---|
| One-off request | Reusable capability |
| Often informal | Designed artifact |
| Usually unversioned | Versioned and owned |
| Context is improvised | Context is curated |
| Output may vary wildly | Output contract is defined |
| Hard to test | Can be evaluated |

A prompt asks the model to do something. A skill teaches the system how to do something repeatedly.

---

### Skill vs. Traditional Code

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

> AI skills are an abstraction of coding, but not an abstraction of engineering.

---

## Part 3 — Token & Context Management

Context is a finite resource. Every token consumed is a token unavailable for reasoning, synthesis, and output. The features and rules below are drawn from `~/.claude/CLAUDE.md`, `claude/MODEL-POLICY.md`, and the `claude/` skills tree.

---

### CLAUDE.md Rules: Token Efficiency (§2)

Three dimensions, each with explicit rules.

#### Input (what you read)
- Targeted reads over broad exploration — `rg` + line-range views, not `cat` on whole files
- Don't re-read files already in context this session
- Don't enumerate a directory tree when you need one file
- Sample, don't exhaust — 20 lines of a log usually tells you what 20,000 would
- Prefer `--help`/`man`/focused grep over reading a whole doc for a specific question

#### Output (what you write)
- No preamble, no "I'll help you with that", no narration of routine actions
- No recap of the user's request back to them
- No closing reassurance
- Prose over bullets for continuous content; bullets only for genuinely enumerable items
- Match reply length to question weight — one-line questions get one-line answers

#### Context (what you reuse)
- Don't re-emit unchanged code — use `str_replace` and targeted edits, not full-file rewrites
- Don't repeat the same caveat across multiple sections of a reply
- Don't restate the plan after executing it unless execution deviated
- Compress summaries of prior work aggressively

**Test:** if removing a sentence wouldn't change what the user can act on, remove it.

---

### CLAUDE.md Rules: Context Window Hygiene (§10)

Suggest a fresh session (`/exit`) at phase boundaries where prior context becomes ballast:

| Boundary | Why clear |
|---|---|
| Plan → Execute | Once written to a file, the exploration that produced it is dead weight |
| Research → Implement | Findings are captured; search queries don't help implementation |
| Review → Fix | Review context biases toward reviewer framing, not code reality |
| Long debugging → Clean attempt | 15+ turns pollutes context with wrong hypotheses |
| Multi-repo switch | Prior repo file contents waste context unless the dependency is the point |

Also flags **mid-session context drift** — when the current task has shifted far enough that most existing tool output is irrelevant to what's being worked on now.

---

### Top Ten Token Management Features

#### Group 1 — Context Budget Management

Rules and mechanisms that govern how much context is consumed and when to discard it.

**Three-Axis Token Budget (CLAUDE.md §2)**
Input, output, and context are each governed by explicit rules. Read targeted line ranges, not whole files. Write no preamble or recap. Never re-emit unchanged code — use targeted edits. If removing a sentence wouldn't change what the user can act on, remove it.

**Context Window Phase Clearing (CLAUDE.md §10)**
At natural phase boundaries — plan → execute, research → implement, review → fix, long debugging → clean attempt — prior tool outputs become dead weight. Suggest `/exit` and a fresh session so the next phase starts with only the artifact it needs, not the exploration that produced it.

**Cross-Session Memory Compression (`.remember/` + ccx)**
A rolling memory system (`now.md`, `today-*.md`, `recent.md`, `archive.md`) and a structured ccx event log (plan/intent/status) compress prior work into a digest. Fresh sessions read the digest instead of replaying raw tool output, eliminating the "reconstruct prior work" token cost at session start.

---

#### Group 2 — Cost-by-Capability Routing

Matching model tier to task complexity so expensive models are only used where they add value.

**Model Tier Pinning (MODEL-POLICY.md)**
Three tiers with explicit policy: `haiku` for dispatcher/lookup skills, `opus` for deep-reasoning skills, and unpinned (session-inherited) for everything else. Prevents over-using expensive models on cheap work and under-using capable models where reasoning headroom matters.

**Haiku-as-Router Pattern**
High-frequency routing skills (`find-skills`, `configure`, `repo-status`, `skill-help`, `env-check`) are pinned to Haiku specifically because they fire at the entry point of every skill invocation chain. Each invocation is cheap, but they run constantly — pinning here is the highest-ROI tier decision in the policy.

---

#### Group 3 — Tooling & Infrastructure

External tools and structural patterns that reduce token consumption at the infrastructure level.

**RTK — Rust Token Killer**
A hook-based CLI proxy installed globally. Intercepts all shell commands and strips/compresses output before it reaches the context window, with claimed 60–90% savings on common dev operations. Transparent to the user — the hook rewrites `git status` → `rtk git status` automatically.

**Parallel Execution Lanes (`/parallel-optimization`)**
Replaces sequential back-and-forth with disjoint-write-scope lanes and milestone barriers. Each lane receives a narrow shared context packet instead of the full conversation history, and fewer coordination round-trips means fewer tokens spent re-stating context between steps.

**WSL/Bash over Windows/PowerShell**
Running in WSL with Bash produces significantly terser tool output than PowerShell. Unix commands (`git`, `rg`, `ls`, `grep`) emit compact, pipeable text. PowerShell serializes structured objects with verbose headers, type annotations, and formatting that inflate context with low-signal content. Shorter command output means less context consumed per tool call — compounding across a long session.

---

#### Group 4 — Guardrails Against Runaway Spending

Hard limits that stop token burn when a task loops or spirals.

**Token Guardrail in Scanning Skills**
Skills like `security-quick-check` and `modernization-rubric` embed a hard stop: halt file reading once cumulative reads consume ~30% of the available context window. The remaining 70% is reserved for synthesis phases. Prevents runaway scanning on large codebases from crowding out the work that actually produces output.

**Retry Budget Circuit Breaker (`/execute-plan`)**
A configurable `retry_budget` (default: 20 retries / 60 min) enforces CLAUDE.md §6 (impasse handling) as a hard limit. When exhausted, the executor surfaces the impasse rather than attempting another variant of the same broken fix. Prevents token burn on wrong-model-of-the-problem loops.

---

#### Group 5 — Review Quality vs. Token Tradeoff

Structuring review passes to maximize depth without inflating context.

**Separate-Pass Domain Reviews (`/code-review-professional`)**
Each review domain (security, performance, data integrity, concurrency, etc.) gets its own isolated context window pass. The explicit rationale: a combined prompt produces shallow bullet-per-domain output, while isolation forces depth per domain. The tradeoff is more total tokens spent, but higher signal per token — findings are actionable rather than superficial.

---

## Closing Lines

> Using AI skills to develop software is an abstraction of coding, not an abstraction of engineering.

> The future is not vibe-driven prompting. It is engineered context.

> AI does not remove the need for engineering discipline. It punishes the absence of it faster.

> Vibes are not a build system.

> The code changed shape. The engineering did not.
