# VS Code / GitHub Copilot Skills

AI coding skills for **VS Code** with **GitHub Copilot**. Designed for **GPT 5.4** and **Gemini Pro** with explicit guardrails to prevent hallucination.

## Setup

Copy the `vscode/` contents into your project's `.github/` directory:

```
your-project/
└── .github/
    ├── copilot-instructions.md   # Project conventions (edit this!)
    ├── prompts/                   # Slash commands
    │   ├── dev/                   # Development workflow
    │   ├── review/                # Code review
    │   ├── ba/                    # Business analysis
    │   └── common/                # Shared utilities
    ├── agents/                    # Autonomous agents (used by prompts)
    ├── skills/                    # Domain knowledge (read by prompts)
    └── instructions/              # Auto-applied rules (by file pattern)
```

**Important:** Edit `.github/copilot-instructions.md` with your project's actual tech stack, build commands, and conventions. The prompts read this file for configuration.

---

## Quick Start

Open **Copilot Chat** in VS Code and type:

```
#prompt:implement Add a health check endpoint to the API
```

That's it. The prompt guides the model through reading existing code, matching patterns, writing the implementation, and verifying the build.

---

## How to Call Skills

### Prompts (slash commands)

Invoke with `#prompt:<name>` in Copilot Chat:

```
#prompt:implement Add user authentication to the API
#prompt:fix-bug TypeError: Cannot read property 'id' of undefined in jobs.ts:42
#prompt:write-tests src/services/job-service.ts
#prompt:plan Add webhook notification system --type feature
#prompt:code-review
#prompt:adversarial-review
#prompt:checkpoint
#prompt:pr
```

With arguments:

```
#prompt:plan Add rate limiting to API endpoints --type feature
#prompt:execute-plan docs/plans/2026-03-20-rate-limiting.md
#prompt:code-review quick
#prompt:code-review verify
#prompt:k8s-deploy-verify --namespace production --full
```

### Agents (autonomous workers)

Agents are referenced by prompts automatically. You can also invoke them directly:

```
@code-review-orchestrator Review the auth package
@security Check for hardcoded secrets
@csharp-quality Review this file
```

### Instructions (auto-applied)

Instructions apply automatically when editing matching files. No invocation needed:

| Instruction | Applies To | What It Does |
|-------------|-----------|-------------|
| `code-generation` | `*.ts`, `*.tsx`, `*.cs`, `*.js`, `*.jsx` | Read-before-write, verify imports, match patterns |
| `docx-processing` | `*.docx` | Word document handling rules |
| `pdf-processing` | `*.pdf` | PDF handling rules |
| `pptx-processing` | `*.pptx` | PowerPoint handling rules |
| `xlsx-processing` | `*.xlsx` | Spreadsheet handling rules |

### Skills (domain knowledge)

Skills are reference files read by prompts and agents. You don't invoke them directly — they're loaded automatically based on what code you're working with.

---

## Prompt Catalog

### Code Generation

| Prompt | Usage | Purpose |
|--------|-------|---------|
| `implement` | `#prompt:implement <task>` | Write new code — reads patterns first, verifies after |
| `fix-bug` | `#prompt:fix-bug <error>` | Structured debugging: trace, test, fix, verify |
| `write-tests` | `#prompt:write-tests <file>` | Generate tests matching project's test patterns |
| `execute-plan` | `#prompt:execute-plan [path]` | Execute a plan file with per-task build/test cycles |

### Planning

| Prompt | Usage | Purpose |
|--------|-------|---------|
| `plan` | `#prompt:plan <description>` | Create implementation plan with TDD-style tasks |
| `teams` | `#prompt:teams` | Dispatch parallel agent teams for large work |
| `triage` | `#prompt:triage` | Bug triage and priority assessment |

### Quality Gates

| Prompt | Usage | Purpose |
|--------|-------|---------|
| `checkpoint` | `#prompt:checkpoint` | Run lint + build + tests for changed packages |
| `simplify` | `#prompt:simplify` | Auto-refactoring pass with 3 parallel agents |
| `code-review` | `#prompt:code-review` | Multi-specialist structured code review |
| `code-review` (quick) | `#prompt:code-review quick` | Fast check: TypeScript + security only |
| `code-review` (verify) | `#prompt:code-review verify` | Re-check findings marked as fixed |

### Adversarial Review

Switch to a **different model** in the Copilot model picker before running these:

| Prompt | Usage | Purpose |
|--------|-------|---------|
| `adversarial-review` | `#prompt:adversarial-review` | Challenge CODE through Skeptic/Architect/Minimalist lenses |
| `adversarial-skeptic` | `#prompt:adversarial-skeptic` | Single lens: challenge correctness |
| `adversarial-architect` | `#prompt:adversarial-architect` | Single lens: challenge structure |
| `adversarial-minimalist` | `#prompt:adversarial-minimalist` | Single lens: challenge necessity |
| `review-gauntlet` | `#prompt:review-gauntlet` | Meta-review: challenge a `/code-review`'s findings |

### Standalone Review

| Prompt | Usage | Purpose |
|--------|-------|---------|
| `review-api` | `#prompt:review-api` | Quick API pattern compliance check |
| `review-db` | `#prompt:review-db` | Quick database schema compliance check |
| `review-design` | `#prompt:review-design` | Quick UI/design system compliance check |
| `review-tests` | `#prompt:review-tests` | Quick test quality check |

### Ship

| Prompt | Usage | Purpose |
|--------|-------|---------|
| `pr` | `#prompt:pr` | Create a PR from current branch |
| `ship` | `#prompt:ship` | Build and ship (project-specific) |
| `changelog` | `#prompt:changelog` | Generate changelog from commits |
| `hotfix` | `#prompt:hotfix` | Emergency fix workflow |

### Operations

| Prompt | Usage | Purpose |
|--------|-------|---------|
| `sync-main` | `#prompt:sync-main` | Rebase on main safely |
| `k8s-deploy-verify` | `#prompt:k8s-deploy-verify` | Post-deploy K8s health checks |
| `dependency-audit` | `#prompt:dependency-audit` | Audit deps for vulnerabilities |
| `migration-guide` | `#prompt:migration-guide` | Generate migration guide for breaking changes |
| `test-plan` | `#prompt:test-plan` | Multi-analyst test planning |
| `ado-item` | `#prompt:ado-item <id>` | Fetch Azure DevOps work item |

### Business Analysis

| Prompt | Usage | Purpose |
|--------|-------|---------|
| `ba-init` | `#prompt:ba-init` | Start the 6-phase BA pipeline |
| `ba-problem-thesis` | `#prompt:ba-problem-thesis` | Phase 1: Define problem + hypothesis |
| `ba-stakeholder` | `#prompt:ba-stakeholder` | Phase 2: Stakeholder mapping |
| `ba-current-state` | `#prompt:ba-current-state` | Phase 3: Current state + gap analysis |
| `ba-requirements` | `#prompt:ba-requirements` | Phase 4: Requirements definition |
| `ba-validation` | `#prompt:ba-validation` | Phase 5: Stress-test requirements |
| `ba-solution` | `#prompt:ba-solution` | Phase 6: Solution recommendation |
| `ba-context-builder` | `#prompt:ba-context-builder` | Build reusable project context doc |
| `ba-spec-engineer` | `#prompt:ba-spec-engineer` | Build complete requirements spec |
| `ba-problem-refiner` | `#prompt:ba-problem-refiner` | Sharpen vague problems into statements |
| `ba-preflight` | `#prompt:ba-preflight` | Pre-draft thinking exercise |
| `ba-eval-harness` | `#prompt:ba-eval-harness` | Evaluate AI-generated BA deliverables |
| `ba-knowledge-capture` | `#prompt:ba-knowledge-capture` | Capture decisions, insights, stakeholder intel |
| `ba-adversarial-review` | `#prompt:ba-adversarial-review` | Adversarial review of BA deliverables |

---

## Domain Skills Reference

These are loaded automatically by `/code-review`, `/adversarial-review`, and `/implement` based on the files you're working with:

### Language Quality

| Skill | Triggers On | Key Rules |
|-------|------------|-----------|
| `typescript-quality` | `*.ts`, `*.tsx` | No `any`, no `@ts-ignore`, strict mode, ESM imports |
| `csharp-quality` | `*.cs` | Naming, async/await, LINQ, exception handling |
| `python-quality` | `*.py` | Type hints always, Pydantic, pytest, ruff+mypy |

### Framework Patterns

| Skill | Triggers On | Key Rules |
|-------|------------|-----------|
| `dotnet-api` | C# API code | Minimal APIs preferred, ProblemDetails, health checks |
| `azure-functions` | Function classes | Isolated worker, thin functions, DI, host.json retries |
| `nextjs-patterns` | Next.js `app/` | Server Components default, push `'use client'` down |
| `monorepo` | Workspace config | Package boundaries, shared package rules, Turborepo |

### Infrastructure

| Skill | Triggers On | Key Rules |
|-------|------------|-----------|
| `bicep` | `*.bicep` | Modules per concern, Key Vault for secrets, managed identities |
| `security` | Config, K8s, scripts | No hardcoded secrets, input validation, shell safety |
| `k8s-readiness` | K8s manifests | Probes, resource limits, security context |

### Code Quality

| Skill | Triggers On | Key Rules |
|-------|------------|-----------|
| `api-patterns` | Service/API code | Shared types, error handling, validation, messaging |
| `ui-design-compliance` | Frontend `*.tsx` | Loading/empty/error states, a11y, design system |
| `test-quality` | `*.test.*` | Coverage gaps, behavior testing, isolation |
| `postgres` | Migrations, SQL, ORM | Safe migrations, parameterized queries, FK indexes |

---

## Recommended Workflow

```
#prompt:plan <task>              → Plan the work
#prompt:execute-plan             → Execute the plan
#prompt:simplify                 → Clean up the code
#prompt:checkpoint               → Verify lint + build + tests
#prompt:code-review              → Structured review
#prompt:adversarial-review       → Switch model, challenge the work
#prompt:pr                       → Ship it
```

For quick fixes:

```
#prompt:fix-bug <error>          → Debug and fix
#prompt:checkpoint               → Verify
#prompt:pr                       → Ship it
```

For adding tests:

```
#prompt:write-tests <file>       → Generate tests
#prompt:checkpoint               → Verify they pass
```

---

## Customization

### Project conventions

Edit `.github/copilot-instructions.md` — every prompt reads this file. Fill in:
- Tech stack (language, framework, package manager)
- Build and test commands
- Naming conventions
- Known issues

### Adding project-specific prompts

Create new files in `.github/prompts/dev/`:

```yaml
---
description: 'My custom prompt'
agent: 'agent'
tools:
  - read
  - search
  - edit
  - execute
---

# My Custom Prompt

Instructions here...
```

### Adding domain skills

Create new directories in `.github/skills/`:

```yaml
---
name: my-domain
description: "What this skill covers"
---

# My Domain Patterns

Rules and examples here...
```

Then reference it in the code-review specialist selection table in `prompts/dev/code-review.prompt.md`.
