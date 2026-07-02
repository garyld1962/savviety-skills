# Using AI Skills to Develop Software Is an Abstraction of Coding

**Talk frame:** 3 slides, short format  
**Working title:** *Putting Your Context on a Diet*  
**Core thesis:**

> Using AI skills to develop software is an abstraction of coding, but not an abstraction of engineering.

Or, even tighter:

> The code changed shape. The engineering did not.

---

## 30-Second Opening

We keep talking about AI-assisted coding as though it is a totally new thing. It is new in capability, but not in principle.

At the core, we are still doing what programmers have always done: expressing intent in a machine-actionable form.

The difference is that the source artifacts are changing. They are no longer just `.cs`, `.java`, `.ts`, or `.py` files. They now include prompts, context, examples, schemas, tool contracts, skills, memory, and evals.

That means the engineering discipline does not go away. It moves up the stack.

---

# Slide 1 — This Is Still Programming

## Main Point

AI-assisted development moves programming up one abstraction layer.

## Slide Bullets

**Traditional development:**

```text
Requirements → Source code → Compiler/interpreter → Executable behavior
```

**AI-assisted development:**

```text
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

## Speaker Notes

The metaphor is imperfect, and that is fine. An LLM is not a deterministic compiler. A normal compiler is strict, formal, and predictable. An LLM is probabilistic and context-sensitive.

So the LLM is not exactly `javac`. It is more like a compiler, interpreter, autocomplete engine, junior developer, and raccoon in a trench coat.

But the point holds: we are still telling a machine what behavior we want. We are just doing it with higher-level artifacts.

Prompts and skills are not magic. They are source artifacts in a higher-level programming model.

## Key Line

> Prompts and skills are not a replacement for code. They are source files in a new layer of the stack.

---

# Slide 2 — Context Management Is Dependency Management

## Main Point

The context window is not chat history. It is the build environment.

## Slide Bullets

**Bad context management looks like bad dependency management:**

| Bad software habit | Bad AI habit |
|---|---|
| Import everything | Dump everything into context |
| Use global state everywhere | Put every rule in global `CLAUDE.md` |
| Ignore dependency versions | Ignore stale or conflicting context |
| Skip interfaces | Use vague prompts and undefined outputs |
| No tests | Trust generated code without validation |

**Better model:**

> Context should be scoped, intentional, reusable, and testable.

## Speaker Notes

This is where *Putting Your Context on a Diet* comes in.

We are not saving tokens just to save money. We are protecting the signal.

Every irrelevant file, stale instruction, bloated prompt, unnecessary tool schema, or repeated explanation competes with the useful context. The model may still produce an answer, but now you are making it reason through noise.

In traditional software, we learned not to casually import everything, rely on global state, or link against random versions of libraries. The same thinking applies here.

Context is a dependency graph. The model's output depends on what we load, what we omit, what we repeat, and what we accidentally pollute.

## Claude Code Examples

- Keep global `CLAUDE.md` lean because it is loaded every session.
- Move workflow-specific instructions into skills.
- Use prompt cache stability instead of constantly changing the prefix.
- Avoid exploratory reads when targeted reads will do.
- Route work to the right model for the task.
- Use skills as packaged, reusable context.

## Key Line

> Garbage context is like linking against the wrong library. The program may still run, but now you are debugging ghosts.

---

# Slide 3 — Engineering Discipline Moves Upstream

## Main Point

AI does not remove best practices. It changes where we apply them.

## Slide Bullets

**Old discipline still applies:**

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

**Practical behaviors:**

- Use `CLAUDE.md` only for rules that truly apply every turn.
- Move conditional or workflow-specific rules into skills.
- Assign cheaper models to simple read/report tasks.
- Reserve stronger models for judgment-heavy work.
- Use evals, tests, and review before trusting generated code.
- Treat context changes like code changes: review them, version them, and test the results.

## Speaker Notes

The dangerous mindset is: “AI writes the code, so we can relax the process.”

That is exactly backward.

AI makes it easier to produce more software faster. That includes bad software. So the engineering guardrails matter more, not less.

The last 40 years of software engineering taught us how to manage complexity. LLMs increase complexity; they do not repeal it.

The developer may write fewer implementation details by hand, but they still need to define intent, manage dependencies, constrain behavior, test outputs, review changes, and operate the system safely.

## Key Line

> The danger is not that developers stop coding. The danger is that they stop engineering.

---

# Three-Point Summary

## 1. AI skills are a new programming layer

We are still expressing intent in a machine-actionable form. The artifacts have changed from only code to prompts, context, skills, schemas, examples, tool contracts, memory, and evals.

## 2. Context is the new dependency graph

The model's output depends heavily on what we load, omit, repeat, or pollute. Context must be managed like dependencies: scoped, versioned, minimal, intentional, and reviewed.

## 3. Engineering discipline matters more, not less

The practices we learned over decades still apply: modularity, testing, review, least privilege, observability, reuse, and cost/performance management. AI does not repeal software engineering. It raises the abstraction layer where software engineering has to operate.

---

# Optional Closing Lines

Use one of these depending on the tone of the room:

> Using AI skills to develop software is an abstraction of coding, but not an abstraction of engineering.

> The future is not vibe-driven prompting. It is engineered context.

> AI does not remove the need for engineering discipline. It punishes the absence of it faster.

> Vibes are not a build system.

> The code changed shape. The engineering did not.

---

# Optional Transition Lines

## From Slide 1 to Slide 2

So if prompts and skills are source artifacts, then the next question is obvious: what are they compiled with? Context. And context is not free-form conversation. It is the dependency graph.

## From Slide 2 to Slide 3

Once we accept that context is dependency management, the conclusion gets uncomfortable but useful: AI does not reduce the need for engineering discipline. It moves that discipline upstream.

---

# Very Short Version

Use this if time gets tight:

> AI-assisted development is still programming because we are still expressing intent in a machine-actionable form. The artifacts are just higher-level now: prompts, context, skills, tools, schemas, and evals.
>
> Context management is dependency management. What we load into the context window shapes the output the same way imports, libraries, and build configuration shape traditional software.
>
> So AI does not let us throw away software engineering practices. It makes practices like modularity, testing, review, least privilege, observability, and versioning even more important.

Final line:

> Using AI skills is an abstraction of coding, not an abstraction of engineering.
