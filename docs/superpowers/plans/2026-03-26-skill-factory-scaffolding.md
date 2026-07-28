# Skill Factory Scaffolding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the skill-factory repository with its directory structure, platform capability/rules definitions, stack definitions, and initial intent structure — the foundation that the compiler, publish toolchain, and factory skills all build on.

**Architecture:** A new git repo (`~/repos/skill-factory`) with YAML-based platform and stack definitions, markdown intent templates, and Python project scaffolding for the compiler and publish toolchain. No executable code in this plan — just structure and definitions that can be validated by a linter.

**Tech Stack:** YAML (platform/stack definitions), Markdown (intents, shared references), Python project layout (pyproject.toml for compiler/publish), yamllint for validation.

**Spec:** `~/repos/skills/docs/superpowers/specs/2026-03-25-skill-factory-design.md`

**Plan series:**
1. **This plan** — Repository scaffolding + platform definitions + stack definitions
2. SQLite state DB schema + tooling
3. Compiler core (resolve, decide, emit)
4. Publish toolchain (Merkle tree, MANIFEST, verify)
5. Factory skills (intent-author, skill-discovery, verify-platform, reconcile, compile-review)

---

## File Structure

```
~/repos/skill-factory/
├── pyproject.toml                              # Python project config (compiler + publish deps)
├── .gitignore                                  # .factory/, __pycache__, *.pyc, .env
├── README.md                                   # Factory repo overview pointing to spec
├── intents/                                    # (empty dir with .gitkeep)
│   └── .gitkeep
├── shared/                                     # Reusable content referenced by intents
│   ├── rubrics/
│   │   └── severity.md                         # Severity rubric (from existing code-review)
│   ├── schemas/
│   │   ├── finding.schema.md                   # Finding schema (from existing code-review)
│   │   └── report-template.md                  # Report template (from existing code-review)
│   └── conventions/
│       └── do-not-guess.md                     # VS Code "Do Not Guess" convention
├── platforms/
│   ├── claude/
│   │   ├── capabilities.yml
│   │   └── rules.yml
│   ├── vscode/
│   │   ├── capabilities.yml
│   │   └── rules.yml
│   └── copilot-native/
│       ├── capabilities.yml
│       └── rules.yml
├── stacks/
│   ├── dotnet.yml
│   ├── dotnet-api.yml
│   ├── dotnet-function-app.yml
│   ├── nextjs.yml
│   ├── nextjs-app.yml
│   ├── typescript.yml
│   └── python.yml
├── templates/                                  # (copied from published repo)
│   ├── blazorstack/
│   ├── ts-monorepo/
│   └── CLAUDE.local.md
├── factory-skills/                             # (empty dirs with .gitkeep for future plans)
│   ├── intent-author/
│   │   └── .gitkeep
│   ├── skill-discovery/
│   │   └── .gitkeep
│   ├── verify-platform/
│   │   └── .gitkeep
│   ├── reconcile/
│   │   └── .gitkeep
│   └── compile-review/
│       └── .gitkeep
├── working/
│   ├── claude/
│   │   └── .gitkeep
│   ├── vscode/
│   │   └── .gitkeep
│   └── copilot-native/
│       └── .gitkeep
├── compiler/                                   # (empty scaffolding for future plans)
│   ├── __init__.py
│   ├── emit/
│   │   └── __init__.py
│   └── config.yml
├── publish/                                    # (empty scaffolding for future plans)
│   └── __init__.py
├── .factory/
│   └── .gitkeep                                # state.db created at runtime
├── .claude/skills/                             # Populated by deploy-skills, not scaffolded
│   └── .gitkeep                                # (deploy-skills fills this at runtime)
└── docs/
    └── superpowers/
        ├── specs/                              # Spec copied from published repo
        └── plans/                              # Implementation plans
```

**Note:** `.claude/skills/` is populated at runtime by `deploy-skills`, not by the factory compiler. It exists so the factory repo can consume published skills for its own development workflows. The `python-fastapi` stack shown in the spec's hierarchy examples is intentionally deferred — only stacks with real rules are created in this plan.

---

### Task 1: Initialize the repository

**Files:**
- Create: `~/repos/skill-factory/.gitignore`
- Create: `~/repos/skill-factory/pyproject.toml`
- Create: `~/repos/skill-factory/README.md`

- [ ] **Step 1: Create the repo and initialize git**

```bash
mkdir -p ~/repos/skill-factory
cd ~/repos/skill-factory
git init
```

- [ ] **Step 2: Write .gitignore**

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.venv/

# Factory runtime state
.factory/state.db
.factory/state-export.json

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
*:Zone.Identifier
```

- [ ] **Step 3: Write pyproject.toml**

```toml
[project]
name = "skill-factory"
version = "0.1.0"
description = "Compiler architecture for cross-platform AI coding skills"
requires-python = ">=3.12"
dependencies = [
    "pyyaml>=6.0",
    "python-frontmatter>=1.1",
]

[project.optional-dependencies]
dev = [
    "yamllint>=1.35",
    "pytest>=8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: Write README.md**

```markdown
# Skill Factory

Compiler architecture for cross-platform AI coding skills. Produces platform-specific
artifacts (Claude Code, VS Code/Copilot, Copilot Native) from platform-agnostic
intent documents.

See [design spec](docs/superpowers/specs/2026-03-25-skill-factory-design.md) for
full architecture documentation.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Initialize the state database
python compiler/db.py init

# Compile an intent
python compiler/compile.py <intent-name>

# Publish to the published repo
python publish/publish.py
```

## Repository Structure

- `intents/` — Source of truth: one directory per intent
- `shared/` — Reusable content referenced by multiple intents
- `platforms/` — Platform capability and rule definitions
- `stacks/` — Tech stack coding conventions (hierarchical)
- `templates/` — Scaffold templates (pass-through, not compiled)
- `factory-skills/` — Dev-skills that power the factory itself
- `working/` — Compiled output (reviewed before publish)
- `compiler/` — Python compilation toolchain
- `publish/` — Publish + Merkle hash toolchain
- `.factory/` — SQLite operational state (gitignored)
```

- [ ] **Step 5: Commit**

```bash
git add .gitignore pyproject.toml README.md
git commit -m "feat: initialize skill-factory repository"
```

---

### Task 2: Create directory structure with .gitkeep files

**Files:**
- Create: multiple `.gitkeep` files across the directory tree

- [ ] **Step 1: Create all directories**

```bash
mkdir -p intents
mkdir -p shared/rubrics shared/schemas shared/conventions
mkdir -p platforms/claude platforms/vscode platforms/copilot-native
mkdir -p stacks
mkdir -p templates
mkdir -p factory-skills/intent-author factory-skills/skill-discovery
mkdir -p factory-skills/verify-platform factory-skills/reconcile factory-skills/compile-review
mkdir -p working/claude working/vscode working/copilot-native
mkdir -p compiler/emit
mkdir -p publish
mkdir -p .factory
mkdir -p .claude/skills
mkdir -p docs/superpowers/specs docs/superpowers/plans
```

- [ ] **Step 2: Add .gitkeep files for empty directories**

```bash
touch intents/.gitkeep
touch factory-skills/intent-author/.gitkeep
touch factory-skills/skill-discovery/.gitkeep
touch factory-skills/verify-platform/.gitkeep
touch factory-skills/reconcile/.gitkeep
touch factory-skills/compile-review/.gitkeep
touch working/claude/.gitkeep
touch working/vscode/.gitkeep
touch working/copilot-native/.gitkeep
touch .factory/.gitkeep
touch .claude/skills/.gitkeep
```

- [ ] **Step 3: Create Python package markers**

```bash
touch compiler/__init__.py
touch compiler/emit/__init__.py
touch publish/__init__.py
```

- [ ] **Step 4: Commit**

```bash
git add intents/ shared/ platforms/ stacks/ templates/ factory-skills/ \
       working/ compiler/ publish/ .factory/ .claude/ docs/
git commit -m "feat: create directory structure"
```

---

### Task 3: Write Claude Code platform definitions

**Files:**
- Create: `platforms/claude/capabilities.yml`
- Create: `platforms/claude/rules.yml`

- [ ] **Step 1: Write capabilities.yml**

Source: The spec's Platform Definitions section + current knowledge of Claude Code.

```yaml
# platforms/claude/capabilities.yml
name: claude-code
version: 2026.03.1
last_verified: "2026-03-26"
vendor_changelog: https://github.com/anthropics/claude-code/releases

artifact_types:
  skill:
    supported: true
    format: "SKILL.md with YAML frontmatter"
    invocation: "/name"
    supports_sub_files: true
    auto_discovery: true
  prompt:
    supported: false
    maps_to: skill
  agent:
    supported: true
    mechanism: "Agent tool with subagent_type"
    standalone_definition: false
    maps_to: skill_sub_file

capabilities:
  parallel_dispatch: true
  streaming_output: true
  tool_calling: true
  file_pattern_instructions: false
  project_conventions_file: "CLAUDE.md"
  max_skill_depth: 3
  context_budget_kb: 200

extensions:
  - name: superpowers
    provider: anthropic
    status: default
    provides:
      - planning
      - brainstorming
      - tdd
      - debugging
      - ba-pipeline
  - name: rtk
    provider: user
    status: default
    provides:
      - token-optimized-cli

deprecations: []
```

- [ ] **Step 2: Write rules.yml**

```yaml
# platforms/claude/rules.yml
name: claude-code
version: 2026.03.1

skill_frontmatter:
  required_fields:
    - name
    - description
  optional_fields:
    - version
    - tags

skill_structure:
  - "# /name — Title"
  - "## Arguments (if applicable)"
  - "## Workflow"
  - "## Guardrails"

conventions:
  - id: extension-first
    rule: >
      If a default/approved extension provides the capability, emit a thin
      skill that enriches it rather than reimplementing.
    applies_to:
      - skill

  - id: sub-file-organization
    rule: >
      Multi-component skills use sub-directories: foundations/ for shared
      schemas, specialists/ for domain agents.
    applies_to:
      - skill

  - id: no-hardcoded-paths
    rule: >
      Skills must detect project structure, never hardcode paths or tool names.
    applies_to:
      - skill

  - id: guardrails-section
    rule: >
      Every skill must have a Guardrails section listing what it must NOT do.
    applies_to:
      - skill

compilation:
  shared_ref_strategy: sub_file
  component_merge: true
  agent_emit: sub_file
  prompt_emit: skill
```

- [ ] **Step 3: Validate YAML**

```bash
yamllint platforms/claude/capabilities.yml platforms/claude/rules.yml
```

Expected: no errors (warnings about line length are acceptable).

- [ ] **Step 4: Commit**

```bash
git add platforms/claude/
git commit -m "feat: add Claude Code platform definitions"
```

---

### Task 4: Write VS Code platform definitions

**Files:**
- Create: `platforms/vscode/capabilities.yml`
- Create: `platforms/vscode/rules.yml`

- [ ] **Step 1: Write capabilities.yml**

```yaml
# platforms/vscode/capabilities.yml
name: vscode-copilot
version: 2026.03.1
last_verified: "2026-03-26"
vendor_changelog: https://github.blog/changelog/label/copilot/

artifact_types:
  skill:
    supported: true
    format: "SKILL.md with YAML frontmatter in .github/skills/<name>/"
    invocation: null
    supports_sub_files: true
    auto_discovery: true
  prompt:
    supported: true
    format: ".prompt.md with YAML frontmatter in .github/prompts/<category>/"
    invocation: "#prompt:name"
    supports_sub_files: false
  agent:
    supported: true
    format: ".agent.md in .github/agents/"
    invocation: "@name"
    standalone_definition: true

capabilities:
  parallel_dispatch: false
  streaming_output: true
  tool_calling: true
  tool_frontmatter: true
  file_pattern_instructions: true
  project_conventions_file: ".github/copilot-instructions.md"
  max_skill_depth: 2
  context_budget_kb: 128

extensions: []

deprecations: []
```

- [ ] **Step 2: Write rules.yml**

```yaml
# platforms/vscode/rules.yml
name: vscode-copilot
version: 2026.03.1

skill_frontmatter:
  required_fields:
    - name
    - description
  optional_fields: []

prompt_frontmatter:
  required_fields:
    - description
    - agent
    - tools
  optional_fields:
    - argument-hint

agent_frontmatter:
  required_fields:
    - description
    - tools
  optional_fields: []

conventions:
  - id: do-not-guess
    rule: >
      Every prompt must include a '## CRITICAL: Do Not Guess' section listing
      what must be detected from the project, not assumed.
    applies_to:
      - prompt

  - id: correct-incorrect-examples
    rule: >
      Prompts should include Correct/Incorrect examples to anchor non-Claude
      models (GPT 5.4, Gemini Pro).
    applies_to:
      - prompt

  - id: bounded-agents
    rule: >
      Agents must have crisp roles with bounded output — not generic
      replacements for the base model.
    applies_to:
      - agent

  - id: skill-as-reference
    rule: >
      Skills are passive reference material read by prompts/agents — they do
      not contain workflow logic.
    applies_to:
      - skill

compilation:
  shared_ref_strategy: reference
  component_merge: false
  agent_emit: standalone
  prompt_emit: prompt
```

- [ ] **Step 3: Validate YAML**

```bash
yamllint platforms/vscode/capabilities.yml platforms/vscode/rules.yml
```

- [ ] **Step 4: Commit**

```bash
git add platforms/vscode/
git commit -m "feat: add VS Code Copilot platform definitions"
```

---

### Task 5: Write Copilot Native platform definitions

**Files:**
- Create: `platforms/copilot-native/capabilities.yml`
- Create: `platforms/copilot-native/rules.yml`

- [ ] **Step 1: Write capabilities.yml**

```yaml
# platforms/copilot-native/capabilities.yml
name: copilot-native
version: 2026.03.1
last_verified: "2026-03-26"
vendor_changelog: https://github.blog/changelog/label/copilot/

artifact_types:
  skill:
    supported: true
    format: "SKILL.md with YAML frontmatter in .github/skills/<name>/"
    invocation: null
    supports_sub_files: true
    auto_discovery: true
  prompt:
    supported: true
    format: ".prompt.md with YAML frontmatter in .github/prompts/<category>/"
    invocation: "#prompt:name"
    supports_sub_files: false
  agent:
    supported: true
    format: ".agent.md in .github/agents/"
    invocation: "@name"
    standalone_definition: true

capabilities:
  parallel_dispatch: false
  streaming_output: true
  tool_calling: true
  tool_frontmatter: true
  file_pattern_instructions: true
  project_conventions_file: ".github/copilot-instructions.md"
  built_in_plan: true
  built_in_review: true
  built_in_research: true
  built_in_delegate: true
  built_in_tasks: true
  max_skill_depth: 2
  context_budget_kb: 128

extensions: []

deprecations: []
```

- [ ] **Step 2: Write rules.yml**

```yaml
# platforms/copilot-native/rules.yml
name: copilot-native
version: 2026.03.1

skill_frontmatter:
  required_fields:
    - name
    - description
  optional_fields: []

prompt_frontmatter:
  required_fields:
    - description
    - agent
    - tools
  optional_fields:
    - argument-hint

agent_frontmatter:
  required_fields:
    - description
    - tools
  optional_fields: []

conventions:
  - id: builtin-first
    rule: >
      Prefer Copilot built-in commands (/plan, /review, /research, /delegate,
      /tasks) over custom prompts. Only emit custom prompts when they add
      value beyond the built-in.
    applies_to:
      - prompt

  - id: do-not-guess
    rule: >
      Every prompt must include a '## CRITICAL: Do Not Guess' section listing
      what must be detected from the project, not assumed.
    applies_to:
      - prompt

  - id: bounded-agents
    rule: >
      Agents must have crisp roles with bounded output — not generic
      replacements for the base model.
    applies_to:
      - agent

  - id: thin-wrappers
    rule: >
      When a built-in covers the base case, emit only a thin wrapper that
      adds domain-specific value (e.g., custom rubrics, specialist dispatch).
    applies_to:
      - prompt

compilation:
  shared_ref_strategy: reference
  component_merge: false
  agent_emit: standalone
  prompt_emit: prompt
```

- [ ] **Step 3: Validate YAML**

```bash
yamllint platforms/copilot-native/capabilities.yml platforms/copilot-native/rules.yml
```

- [ ] **Step 4: Commit**

```bash
git add platforms/copilot-native/
git commit -m "feat: add Copilot Native platform definitions"
```

---

### Task 6: Write stack definitions

**Files:**
- Create: `stacks/dotnet.yml`
- Create: `stacks/dotnet-api.yml`
- Create: `stacks/dotnet-function-app.yml`
- Create: `stacks/nextjs.yml`
- Create: `stacks/nextjs-app.yml`
- Create: `stacks/typescript.yml`
- Create: `stacks/python.yml`

- [ ] **Step 1: Write dotnet.yml (base)**

```yaml
name: dotnet
description: "Base .NET conventions shared across all .NET project types"
version: 2026.03.1

language: "C#"
runtime: ".NET 9"

rules:
  naming:
    - "PascalCase for public members, _camelCase for private fields"
    - "Async methods suffixed with Async"
    - "Interfaces prefixed with I"
  quality:
    - "Nullable reference types enabled project-wide"
    - "Use ILogger<T>, never Console.Write or Debug.WriteLine"
    - "Prefer records for immutable data types"
    - "Use CancellationToken on all async public APIs"
  testing:
    - "xUnit over NUnit or MSTest"
    - "FluentAssertions for assertions"
    - "Arrange-Act-Assert pattern"
  security:
    - "No hardcoded connection strings or secrets"
    - "Use IConfiguration + user-secrets in dev, Key Vault in prod"
```

- [ ] **Step 2: Write dotnet-api.yml**

```yaml
name: dotnet-api
description: "ASP.NET Web API conventions"
extends: dotnet
version: 2026.03.1

framework: "ASP.NET Core Minimal APIs"

rules:
  api:
    - "All API methods must have a Swagger/OpenAPI attribute"
    - "Use ProblemDetails for all error responses"
    - "Minimal APIs preferred over controllers for new endpoints"
    - "Use TypedResults for compile-time response type checking"
  patterns:
    - "Thin endpoints — business logic in services, not handlers"
    - "Use FluentValidation for request validation"
    - "Health checks at /healthz (liveness) and /readyz (readiness)"
  data:
    - "EF Core with explicit migrations"
    - "Repository pattern optional — DbContext in services is fine"
    - "Always parameterize queries, never string interpolation"
```

- [ ] **Step 3: Write dotnet-function-app.yml**

```yaml
name: dotnet-function-app
description: "Azure Functions conventions (isolated worker)"
extends: dotnet
version: 2026.03.1

framework: "Azure Functions v4 (isolated worker model)"

rules:
  functions:
    - "Isolated worker model only — never in-process"
    - "Functions are thin orchestrators, logic in injected services"
    - "One function class per trigger type"
    - "Configure retries and timeout in host.json"
  bindings:
    - "Prefer strongly-typed bindings over dynamic"
    - "Use DI for all service dependencies"
    - "Queue triggers: batch size and visibility timeout in host.json"
  deployment:
    - "Consumption plan for event-driven, Premium for VNet/long-running"
```

- [ ] **Step 4: Write typescript.yml (base)**

```yaml
name: typescript
description: "Base TypeScript conventions"
version: 2026.03.1

language: "TypeScript"
runtime: "Node.js 24 LTS"

rules:
  quality:
    - "Strict mode enabled (strict: true in tsconfig)"
    - "No any types without justification"
    - "No @ts-ignore — use @ts-expect-error with explanation"
    - "ESM imports only"
  naming:
    - "camelCase for variables and functions"
    - "PascalCase for types, interfaces, classes, and components"
    - "SCREAMING_SNAKE_CASE for constants"
  testing:
    - "Vitest preferred for unit tests"
    - "Tests co-located with source or in __tests__/ directory"
```

- [ ] **Step 5: Write nextjs.yml (base)**

```yaml
name: nextjs
description: "Base Next.js conventions"
extends: typescript
version: 2026.03.1

framework: "Next.js 16"

rules:
  rendering:
    - "Server Components by default"
    - "Push 'use client' boundaries as far down the component tree as possible"
    - "Use Server Actions for data mutations, not Route Handlers"
  routing:
    - "All request APIs are async: await cookies(), await headers(), await params"
    - "Use proxy.ts instead of middleware.ts (Next.js 16 rename)"
  performance:
    - "next/image for images, next/font for fonts"
    - "Cache Components ('use cache') for mixing static and dynamic"
```

- [ ] **Step 6: Write nextjs-app.yml**

```yaml
name: nextjs-app
description: "Next.js App Router application conventions"
extends: nextjs
version: 2026.03.1

rules:
  structure:
    - "App Router file conventions: page.tsx, layout.tsx, loading.tsx, error.tsx"
    - "Collocate components with their routes when route-specific"
    - "Shared components in /components at the package root"
  data:
    - "Use server-side data fetching in Server Components, not useEffect"
    - "revalidatePath/revalidateTag for cache invalidation"
  styling:
    - "Tailwind CSS with cn() utility (clsx + tailwind-merge)"
    - "CSS variables for theming"
```

- [ ] **Step 7: Write python.yml**

```yaml
name: python
description: "Base Python conventions"
version: 2026.03.1

language: "Python"
runtime: "Python 3.12+"

rules:
  quality:
    - "Type hints on all function signatures"
    - "Pydantic for data validation and settings"
    - "Use pathlib over os.path"
  naming:
    - "snake_case for functions and variables"
    - "PascalCase for classes"
    - "SCREAMING_SNAKE_CASE for constants"
  testing:
    - "pytest as test runner"
    - "fixtures over setUp/tearDown"
  tooling:
    - "ruff for linting and formatting"
    - "mypy for type checking"
```

- [ ] **Step 8: Validate all stack YAML**

```bash
yamllint stacks/*.yml
```

- [ ] **Step 9: Commit**

```bash
git add stacks/
git commit -m "feat: add tech stack definitions with inheritance"
```

---

### Task 7: Seed shared reference content

**Files:**
- Create: `shared/rubrics/severity.md`
- Create: `shared/schemas/finding.schema.md`
- Create: `shared/schemas/report-template.md`
- Create: `shared/conventions/do-not-guess.md`

Source: Extract from existing published skills in `~/repos/skills/`.

- [ ] **Step 1: Extract severity rubric from existing code-review skill**

Read `~/repos/skills/claude/code-review/foundations/severity.md` and copy to `shared/rubrics/severity.md`.

- [ ] **Step 2: Extract finding schema from existing code-review skill**

Read `~/repos/skills/claude/code-review/foundations/finding-schema.md` and copy to `shared/schemas/finding.schema.md` (intentional rename: hyphen to dot notation for the shared ref convention).

- [ ] **Step 3: Extract report template from existing code-review skill**

Read `~/repos/skills/claude/code-review/foundations/report-template.md` and copy to `shared/schemas/report-template.md`.

- [ ] **Step 4: Create the "Do Not Guess" convention document**

Extract the pattern from existing VS Code prompts. The document should define:
- What the convention requires (a `## CRITICAL: Do Not Guess` section)
- Why it exists (non-Claude models hallucinate without explicit detection instructions)
- Template content the compiler should inject

- [ ] **Step 5: Verify all files were created with content**

```bash
ls -la shared/rubrics/ shared/schemas/ shared/conventions/
wc -l shared/rubrics/severity.md shared/schemas/finding.schema.md \
      shared/schemas/report-template.md shared/conventions/do-not-guess.md
```

Expected: 4 files, each with non-zero line counts.

- [ ] **Step 6: Commit**

```bash
git add shared/
git commit -m "feat: seed shared reference content from existing skills"
```

---

### Task 8: Copy templates and spec from published repo

**Files:**
- Create: `templates/` contents (from `~/repos/skills/templates/`)
- Create: `docs/superpowers/specs/2026-03-25-skill-factory-design.md` (from published repo)

- [ ] **Step 1: Copy templates directory**

```bash
cp -r ~/repos/skills/templates/* ~/repos/skill-factory/templates/
```

- [ ] **Step 2: Copy the design spec**

```bash
cp ~/repos/skills/docs/superpowers/specs/2026-03-25-skill-factory-design.md \
   ~/repos/skill-factory/docs/superpowers/specs/
```

- [ ] **Step 3: Commit**

```bash
git add templates/ docs/
git commit -m "feat: copy templates and design spec from published repo"
```

---

### Task 9: Create compiler config scaffold

**Files:**
- Create: `compiler/config.yml`

- [ ] **Step 1: Write compiler/config.yml**

```yaml
# compiler/config.yml
# Configuration for the skill-factory compiler.

# Paths (relative to repo root)
paths:
  intents: intents
  shared: shared
  platforms: platforms
  stacks: stacks
  working: working

# LLM advice mode (optional, for ambiguous compilation decisions)
llm_advice:
  enabled: false
  endpoint: "http://localhost:11434/v1"
  model: "qwen2.5:14b"
  fallback: "warn"   # warn | error | skip

# Publish target
publish:
  repo: "~/repos/skills"
  include_templates: true
```

- [ ] **Step 2: Commit**

```bash
git add compiler/config.yml
git commit -m "feat: add compiler configuration scaffold"
```

---

### Task 10: Validate the complete structure and create initial tag

- [ ] **Step 1: Verify directory tree matches spec**

```bash
find . -not -path './.git/*' | sort
```

Compare against the spec's Repository Structure section. Verify all expected directories and files exist.

- [ ] **Step 2: Validate all YAML files**

```bash
pip install yamllint
yamllint platforms/**/*.yml stacks/*.yml compiler/config.yml
```

- [ ] **Step 3: Verify stack inheritance references**

Check that every `extends:` field in stack files references an existing stack:

```bash
grep -h "^extends:" stacks/*.yml | awk '{print $2}' | while read parent; do
  test -f "stacks/${parent}.yml" || echo "MISSING: stacks/${parent}.yml"
done
```

Expected: no output (all parents exist).

- [ ] **Step 4: Final commit and tag**

```bash
git add -A
git status  # verify nothing unexpected
git commit -m "chore: validate complete scaffolding structure" --allow-empty
git tag v0.1.0-scaffold -m "Repository scaffolding complete"
```
