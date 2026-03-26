# Skill Factory Design

**Date:** 2026-03-25
**Status:** Approved (design phase)
**Author:** Gary + Claude Opus 4.6

## Executive Summary

### The Problem

AI coding skills must be maintained across three platforms (Claude Code, VS Code/Copilot, Copilot Native), each with different file formats, conventions, and capabilities. Today, skills are authored separately per platform, leading to drift, duplication, and manual cross-platform synchronization. There is no way to verify which exact skills were active when code was written, and platform updates require manually reviewing every skill for compatibility.

### The Solution

A **compiler architecture** that treats skills like source code: write once in a platform-agnostic format, compile to each target, publish with a cryptographic audit trail.

**How it works:**

1. **Author** — A factory skill interviews you about what you want to accomplish. It produces an *intent document* — a structured description of the goal, constraints, and components (prompts, skills, agents) needed. You never hand-write platform-specific files.

2. **Compile** — A deterministic Python compiler reads the intent, checks each platform's capabilities (what it can do, what built-ins it has, what extensions are available) and rules (your authoring conventions), then generates the right artifacts for each platform. Claude gets a single SKILL.md with sub-files. VS Code gets separate prompts, skills, and agents. Copilot Native gets thin wrappers where built-ins already cover the need.

3. **Review** — You inspect the compiled output. A quality gate validates frontmatter, structure, shared references, and context budgets before publishing is allowed.

4. **Publish** — The compiler output is pushed to the published repo (the current `skills/` repo). A SHA-256 Merkle tree is computed over every file. The root hash is committed to a MANIFEST.json, creating a verifiable chain: *these exact prompts were active when this code was written.*

**Key properties:**

- **Single source of truth** — Intents live in one place. Platform-specific output is derived.
- **Deterministic** — Same intent + same platform definitions = same output. Re-compilable at any time.
- **Auditable** — Merkle tree hashes prove exactly which skills were deployed. Traceable from a PR back to the intent that generated the prompts.
- **Platform-aware** — The compiler knows what each platform can do natively and only generates custom artifacts for gaps. When a platform adds a new built-in, recompile and the redundant custom skill disappears.
- **Stack-aware** — Tech stack rules (naming, patterns, testing conventions) are separate from skills. A single `code-review` intent adapts to .NET, Next.js, or Python projects via hierarchical stack definitions.
- **Extensible** — Vendor extensions (Anthropic superpowers, marketplace skills) are tracked in platform capabilities. The compiler defers to them rather than duplicating their functionality.

**What changes for end users:** Nothing. They still run `deploy-skills` from their project and get skills deployed. The published repo looks the same — it's just produced by a compiler instead of by hand.

### Technical Summary

A compiler architecture for AI coding skills. Intent documents capture *what* and *why*. Platform capability and rule definitions capture *how* and *constraints*. A deterministic compiler bridges the gap, producing platform-specific artifacts from a single source of truth.

The current `skills/` repo becomes a build artifact (the "published repo"). A new `skill-factory/` repo becomes the source of truth (the "factory").

## Glossary

| Term | Definition |
|------|-----------|
| **Intent** | A goal document with structured sub-components. Captures what a skill should accomplish, its constraints, and its component structure. Single source of truth for a published skill set. |
| **Component** | A sub-structure within an intent (type: prompt, skill, or agent). The compiler decides what artifacts to emit per platform. |
| **Factory skill** (dev-skill) | A hand-authored skill that powers the factory itself. Never compiled from an intent. Lives in `factory-skills/`. |
| **Published skill** | A compiled artifact deployed to end users via the published repo. |
| **Capabilities file** | Platform-intrinsic facts: what artifact types it supports, built-in commands, extensions, context limits. Changes when the vendor ships updates. |
| **Rules file** | Authoring conventions for a platform: required frontmatter fields, structural patterns, "Do Not Guess" sections. Changes when you decide to. |
| **Stack definition** | Tech stack coding conventions (e.g., "all API methods must have a Swagger attribute"). Hierarchical inheritance (dotnet → dotnet-api). |
| **Shared reference** | Reusable content (rubrics, schemas, templates) referenced by multiple intents. |
| **Output tree** | Compiled output in `working/` in the factory repo. Source of truth for what gets published. Not to be confused with the shell's current working directory. |
| **Merkle tree** | SHA-256 hash tree over published artifacts. Leaf = file hash, interior = hash of children, root = entire release. |

## Architecture Overview

```
skill-factory/ (source of truth)
├── intents/           ← canonical goal definitions
├── shared/            ← reusable content across intents
├── platforms/         ← capabilities + rules per environment
├── stacks/            ← tech stack conventions (hierarchical)
├── templates/         ← scaffold templates (pass-through, not compiled)
├── factory-skills/    ← dev-skills that power the factory
├── working/           ← compiled output (reviewed before publish)
├── compiler/          ← Python compilation toolchain
├── publish/           ← publish + Merkle hash toolchain
├── .factory/state.db  ← SQLite operational state
└── .claude/skills/    ← published skills deployed here for factory use

skills/ (published repo — build artifact)
├── claude/
├── vscode/
├── copilot-native/
├── templates/
├── MAPPING.md
├── MANIFEST.json
└── deploy.sh
```

### Data Flow

```
intents/ + platforms/ + stacks/ + shared/
                    │
                    ▼
            compiler (Python)
            optional LLM advice (local Ollama)
                    │
                    ▼
              working/<env>/
                    │
                    ▼
            compile-review (quality gate)
                    │
                    ▼
            human review
                    │
                    ▼
            publish (Python → Rust Phase 2)
            Merkle tree + SHA-256
                    │
                    ▼
            published repo + MANIFEST.json
                    │
                    ▼
            deploy-skills (end user)
```

## Intent Document Format

An intent has two phases — during authoring it exists as two documents (Goal & Constraints + Component Spec) for side-by-side review. On approval, the factory skill merges them into a single canonical file.

### Final merged format

```markdown
---
# ─── Identity ───────────────────────────────────
name: <intent-name>
version: <semver>
description: "<what this accomplishes>"

# ─── Components ─────────────────────────────────
components:
  - id: <component-id>
    type: prompt | skill | agent
    description: "<what this component does>"

# ─── Shared References ──────────────────────────
shared_refs:
  - shared/rubrics/severity.md
  - shared/schemas/finding.schema.md

# ─── Stack Awareness ────────────────────────────
stack_aware: true | false
stack_hints:
  - <stack-name>

# ─── Platform Notes ─────────────────────────────
platform_notes:
  claude:
    strategy: "<how this maps to Claude artifacts>"
  vscode:
    strategy: "<how this maps to VS Code artifacts>"
  copilot-native:
    strategy: "<how this maps to Copilot Native artifacts>"
    limitations:
      - "<known gap>"
---

# <Intent Name>

## Goal
<What the user wants to accomplish>

## Constraints
<What limits apply>

## Component: <id>
<Per-component spec with Inputs, Outputs, Behavior/Rules>
```

### Frontmatter

Machine-readable. The compiler parses `components`, `shared_refs`, `platform_notes`, and `stack_aware` without reading the markdown body.

### Body

Human-readable. Goal, constraints, and component details are prose. Component specs follow a uniform structure: Inputs, Outputs, and domain-specific detail (Behavior, Rules, etc.).

### Authoring phase (two-doc split)

During the factory skill interview, two documents are maintained:

- **Doc 1 — Goal & Constraints**: what you want, why, what limits apply. User keeps this visible on a second screen to spot drift.
- **Doc 2 — Component Spec**: the emerging structure, platform notes, shared references. Built incrementally as the interview progresses.

User approves both independently. Factory skill merges into final `intent.md`.

### Component sub-files

For intents with multiple components, each component's detailed spec can live in a separate file under `intents/<name>/components/`:

```
intents/code-review/
├── intent.md                          # Frontmatter + Goal + Constraints + component summaries
└── components/
    ├── orchestrator.md                # Full spec for the orchestrator component
    ├── specialist-dispatch.md         # Full spec for specialist dispatch
    └── report-assembly.md             # Full spec for report assembly
```

The compiler associates component sub-files with frontmatter entries by matching the filename (minus extension) to the component `id`. For example, `components/orchestrator.md` maps to the frontmatter entry with `id: orchestrator`.

When component sub-files exist, the `intent.md` body contains only a brief summary for each component (enough for human review). The compiler reads the full spec from the sub-file.

Simple intents with few components can inline everything in `intent.md` with no `components/` directory.

### Versioning policy

Intent versions use semver (`major.minor.patch`):
- **Patch**: wording improvements, typo fixes that don't change compiled output
- **Minor**: new component, changed behavior within existing components, new stack hints
- **Major**: goal redefinition, component removal, breaking changes to compiled output

Intent versions are bumped manually by the author (or by the intent-author skill when it modifies an existing intent). The compiler records which intent version it compiled.

Release versions in MANIFEST.json use date-based versioning (`YYYY.MM.DD.N` where N is a sequence number for same-day releases). A release bundles whatever intent versions are current at publish time. The MANIFEST records each intent's version alongside the release version.

### Two-doc intermediate formats

During the intent-author interview:

**Doc 1 — Goal & Constraints** (user's reference screen):
```markdown
# <Name> — Goal & Constraints

## Goal
<What the user wants to accomplish — written first, refined during interview>

## Constraints
<What limits apply — added incrementally as the interview reveals them>

## Success Criteria
<How to know it's working — optional, added if the interview surfaces them>
```

**Doc 2 — Component Spec** (built incrementally):
```markdown
# <Name> — Component Spec

## Components
- <id> (<type>): <description>
[grows as interview progresses]

## Shared References
- <ref-path>: <why needed>
[added as reuse opportunities are identified]

## Platform Notes
- <platform>: <strategy or limitation>
[factory skill flags these during interview]

## Stack Awareness
- stack_aware: true/false
- hints: [<stack-names>]
```

**Merge rules**: Doc 1 content maps to the `Goal` and `Constraints` sections of the final intent body. Doc 2 content maps to the frontmatter (`components`, `shared_refs`, `platform_notes`, `stack_aware`) and the per-component body sections. No overlap — the two docs capture different concerns.

## Platform Definitions

Each platform has two YAML files in `platforms/<name>/`.

### Capabilities (what the platform can do)

```yaml
name: <platform-name>
version: <version>
last_verified: <date>
vendor_changelog: <url>

artifact_types:
  skill:
    supported: true|false
    format: "<file format description>"
    invocation: "<how users invoke>" | null
    supports_sub_files: true|false
    auto_discovery: true|false
  prompt:
    supported: true|false
    maps_to: <artifact_type>       # if not natively supported
  agent:
    supported: true|false
    mechanism: "<how agents work>"
    standalone_definition: true|false
    maps_to: <artifact_type>       # if not standalone

capabilities:
  parallel_dispatch: true|false
  streaming_output: true|false
  tool_calling: true|false
  file_pattern_instructions: true|false
  project_conventions_file: "<path>"
  built_in_plan: true|false        # platform-specific built-ins
  built_in_review: true|false
  context_budget_kb: <number>

extensions:
  - name: <extension-name>
    provider: <provider>
    status: default|approved|optional
    provides:
      - <capability>

deprecations:
  - capability: <name>
    deprecated_in: <version>
    removed_in: <version>|null
    replacement: "<what to use instead>"
```

### Rules (how you want artifacts shaped)

```yaml
name: <platform-name>
version: <version>

<artifact_type>_frontmatter:
  required_fields: [<fields>]
  optional_fields: [<fields>]

<artifact_type>_structure:
  - "<required section>"

conventions:
  - id: <convention-id>
    rule: "<what the convention requires>"
    applies_to: [<artifact_types>]

compilation:
  shared_ref_strategy: inline|sub_file|reference
  component_merge: true|false
  agent_emit: sub_file|standalone
  prompt_emit: skill|prompt
```

### Capability update workflow

Three triggers:

1. **Scheduled staleness check** — flags platforms with `last_verified` > 30 days
2. **On-demand verify** — `/verify-platform <name>` fetches changelog, proposes updates
3. **Compile-time warning** — compiler warns if capabilities are stale, does not block

Capability changes cascade: compiler identifies affected intents and recommends recompilation.

Deprecations and removals are tracked. A removed capability that an intent depends on produces a hard error.

## Stack Definitions

Hierarchical YAML files in `stacks/`. Child stacks inherit all parent rules.

```yaml
name: <stack-name>
description: "<what this stack covers>"
extends: <parent-stack-name>     # optional

language: "<primary language>"
runtime: "<runtime version>"
framework: "<framework>"         # optional

rules:
  <category>:                    # naming, quality, testing, security, api, etc.
    - "<convention>"
```

### Inheritance resolution

The compiler resolves the chain bottom-up. `dotnet-function-app` = `dotnet` rules + `dotnet-function-app` rules. Category-level merge: child rules extend parent rules in the same category. Child metadata (language, runtime, framework) overrides parent.

### Stack hierarchy examples

```
dotnet
├── dotnet-api
└── dotnet-function-app

nextjs
└── nextjs-app

typescript (base)

python
└── python-fastapi
```

### User-extensible

End users can add stack definitions for their own tech stacks. The compiler resolves whatever it finds in `stacks/`.

## Compilation Pipeline

### Stages

**1. RESOLVE** — Load intent, resolve stack hierarchy, load shared references, load platform capabilities and rules.

**2. DECIDE** — Per component, per platform, determine the emission action:
- **skip** — platform built-in covers this
- **thin_wrapper** — default/approved extension covers this; emit enrichment only
- **full_emit** — no coverage; emit complete artifact

The decision also determines shared reference strategy (inline vs. sub_file vs. reference) and artifact type mapping (e.g., prompt→skill on Claude).

**3. EMIT** — Per-platform emitters write artifacts to `working/<env>/`:
- **Claude emitter**: merges components into single SKILL.md with sub-file directories
- **VS Code emitter**: separates into prompt + skill + agent files
- **Copilot Native emitter**: emits thin wrappers or skips where built-ins cover

**4. RECORD** — Write compilation metadata to SQLite (intent, platform, capabilities version, components emitted/skipped, warnings, duration).

### LLM advice mode

For ambiguous decisions (partial overlap with built-in, unclear component mapping), the compiler can optionally query a local LLM (Ollama). Advice is logged to SQLite for audit. The compiler can operate without LLM access (falls back to full_emit with a warning).

```yaml
# compiler/config.yml
llm_advice:
  enabled: true
  endpoint: "http://localhost:11434/v1"
  model: "qwen2.5:14b"
  fallback: "warn"
```

### CLI

```bash
python compiler/compile.py <intent-name>              # one intent, all platforms
python compiler/compile.py <intent-name> --platform X  # one intent, one platform
python compiler/compile.py --all                       # all intents, all platforms
python compiler/compile.py --all --diff                # show what changed
python compiler/compile.py <intent-name> --dry-run     # show plan, don't write
```

### Error handling

| Failure | Behavior |
|---------|----------|
| Intent references a `shared_ref` that doesn't exist | **Hard error.** Compilation aborts for that intent. Other intents continue. |
| Platform capabilities file missing or malformed | **Hard error.** That platform is skipped entirely. Warning emitted. |
| Stack `extends` references a parent that doesn't exist | **Hard error.** Compilation aborts for any intent using that stack. |
| Circular stack inheritance (A extends B extends A) | **Hard error.** Detected during RESOLVE. Reports the cycle. |
| Component sub-file referenced in frontmatter but file missing | **Hard error.** Compilation aborts for that intent. |
| EMIT produces a file path that collides with a factory-skill | **Hard error.** Factory-skills paths are reserved. Compiler refuses to overwrite. |
| SQLite write failure (locked, disk full) | **Warning.** Compilation output is still written to `working/`. State recording is best-effort. |
| LLM advice endpoint unreachable | **Fallback per config:** `warn` (continue with default decision), `error` (abort), or `skip` (silently use default). |
| Intent has no components | **Warning.** Compiler emits nothing but records the attempt. May indicate an incomplete intent. |

All errors and warnings are written to both stderr and the SQLite `compilations` table (if writable). The `--dry-run` flag validates all inputs without writing output, making it useful for pre-flight checks.

## Publish Pipeline and Merkle Tree

### Merkle tree

SHA-256 hash tree over the published output. Leaves are file content hashes. Interior nodes are SHA-256 of sorted child hashes concatenated. Root hash represents the entire release.

### MANIFEST.json

Committed to the published repo root on every publish:

```json
{
  "version": "<release-version>",
  "timestamp": "<ISO-8601>",
  "root_hash": "<SHA-256>",
  "factory_commit": "<git-sha>",
  "platforms": {
    "<name>": {
      "hash": "<SHA-256>",
      "skills_count": "<number>",
      "last_compiled": "<ISO-8601>"
    }
  },
  "intents": {
    "<intent-name>": {
      "version": "<intent-semver>",
      "platforms_emitted": ["<platform-names>"],
      "platforms_skipped": ["<platform-names>"]
    }
  },
  "tree": { "...full Merkle tree..." }
}
```

### Publish flow

1. Copy `working/` to published repo
2. Copy `templates/` to published repo (pass-through)
3. Compute Merkle tree over all published content
4. Write MANIFEST.json
5. Commit with root hash in message, tag with version
6. Record in SQLite

### Verification

```bash
python publish/verify.py                              # quick: root hash match?
python publish/verify.py --deep                       # rebuild tree from files
python publish/verify.py --skill claude/plan          # check one skill
```

### Audit trail

Published repo commits include the root hash and factory commit reference. Projects can record `Skills version` and `Skills hash` in PR descriptions. CI can verify deployed skills match the manifest.

### Rust Phase 2

The publish + Merkle hash step starts as Python. Once stable, a Rust binary is a drop-in replacement. Validation: run both side-by-side, confirm identical hashes. Python becomes the test oracle.

## SQLite State Database

`.factory/state.db` — operational state for the factory. Gitignored (local to each factory instance).

### Tables

| Table | Purpose |
|-------|---------|
| `intents` | Registry of all intents (name, version, path, timestamps) |
| `compilations` | Every compilation run (intent, platform, caps version, components emitted/skipped, status) |
| `publications` | Every publish (version, root hash, factory commit, published commit, manifest) |
| `advice_log` | LLM advice requests and responses (question, response, model, accepted?) |
| `platform_checks` | Platform capability verifications (previous/new version, changes found) |
| `reconciliations` | Drift detection results (drifted files, action taken) |

### Key views

| View | Purpose |
|------|---------|
| `stale_compilations` | Intents updated after their last compile |
| `stale_platforms` | Platforms not verified in 30+ days |
| `compilation_history` | Full history with freshness indicator |

### Bootstrap and recovery

- **`python compiler/db.py init`** — creates `state.db` with the schema. Safe to run on an existing DB (no-ops if tables exist). Required after cloning the factory repo.
- **`python compiler/db.py export`** — dumps all tables to `.factory/state-export.json` for backup.
- **`python compiler/db.py import <file>`** — restores from a JSON export.

If the DB is lost without an export, publications and compilations can be partially reconstructed from git history (commit messages contain root hashes, MANIFEST.json contains publication metadata). Advice logs and reconciliation records would be lost.

## Factory Skills

Hand-authored skills in `factory-skills/`. These bootstrap the system and are never compiled from intents.

| Skill | Invocation | Purpose |
|-------|-----------|---------|
| intent-author | `/intent-author` | Interview user, write intent document (two-doc flow → merge) |
| skill-discovery | `/skill-discovery` | Find gaps in existing coverage, recommend intent type |
| verify-platform | `/verify-platform <name>` | Update platform capabilities from vendor changelog |
| reconcile | `/reconcile` | Detect drift between working dirs and published repo |
| compile-review | `/compile-review` | Quality gate on compiled output before publish |

### compile-review criteria

The compile-review skill validates compiled output against platform rules before publish is allowed:

1. **Frontmatter validation** — all required fields present per platform rules
2. **Structural compliance** — required sections exist (e.g., "CRITICAL: Do Not Guess" for VS Code prompts)
3. **Shared reference resolution** — all references resolve to actual files
4. **Context budget** — file sizes within platform's `context_budget_kb` limit
5. **Diff review** — flag unexpected changes vs. previous compilation (new files, deleted files, large diffs)
6. **Cross-platform consistency** — same intent produced output for all expected platforms
7. **Empty artifact check** — no zero-content or stub-only files

Report: pass/fail per platform with specific issues. Must pass before `publish.py` will run (publish checks for a recent passing compile-review record in SQLite).

### intent-author flow

1. Ask about the goal
2. Write Doc 1 (Goal & Constraints) — user reviews on side screen
3. Work through constraints, inputs, outputs, error cases
4. Determine components (prompt/skill/agent sub-structures)
5. Build Doc 2 (Component Spec) — flag platform deviations as they emerge
6. Identify shared references and stack awareness
7. User approves both docs
8. Merge into `intents/<name>/intent.md`
9. Record in SQLite

### Factory self-consumption

The factory repo is itself a consumer of the published repo. `deploy-skills` deploys published skills (plan, checkpoint, code-review, etc.) into the factory's `.claude/skills/` for use during factory development. Factory-only skills live separately in `factory-skills/`.

## Repository Structure

```
skill-factory/
├── intents/
│   ├── plan/
│   │   ├── intent.md
│   │   └── components/
│   │       ├── codebase-discovery.md
│   │       └── validation-gate.md
│   ├── code-review/
│   │   ├── intent.md
│   │   └── components/
│   │       ├── orchestrator.md
│   │       ├── specialist-dispatch.md
│   │       └── report-assembly.md
│   └── checkpoint/
│       └── intent.md
│
├── shared/
│   ├── rubrics/
│   │   └── severity.md
│   ├── schemas/
│   │   ├── finding.schema.md
│   │   └── report-template.md
│   └── conventions/
│       └── do-not-guess.md
│
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
│
├── stacks/
│   ├── dotnet.yml
│   ├── dotnet-api.yml
│   ├── dotnet-function-app.yml
│   ├── nextjs.yml
│   ├── nextjs-app.yml
│   ├── typescript.yml
│   └── python.yml
│
├── templates/
│   ├── blazorstack/
│   ├── ts-monorepo/
│   └── CLAUDE.local.md
│
├── factory-skills/
│   ├── intent-author/
│   ├── skill-discovery/
│   ├── verify-platform/
│   ├── reconcile/
│   └── compile-review/
│
├── working/
│   ├── claude/
│   ├── vscode/
│   └── copilot-native/
│
├── compiler/
│   ├── compile.py
│   ├── resolve.py
│   ├── db.py
│   ├── config.yml
│   └── emit/
│       ├── claude.py
│       ├── vscode.py
│       └── copilot_native.py
│
├── publish/
│   ├── publish.py
│   ├── verify.py
│   ├── merkle.py
│   └── src/
│       └── main.rs
│
├── .factory/
│   └── state.db
│
├── .claude/skills/
│   ├── plan/
│   ├── checkpoint/
│   └── _project/factory/
│
└── docs/
    └── superpowers/specs/
```

## End-to-End Workflows

### Creating a new skill

1. `/skill-discovery` — identify gap, recommend intent type
2. `/intent-author` — interview → Doc 1 + Doc 2 → approve → merge into intent.md
3. `python compiler/compile.py <name>` — compile for all platforms
4. `/compile-review` — quality gate
5. Human reviews `working/` diffs
6. `python publish/publish.py` — Merkle hash, commit to published repo
7. `deploy-skills both` — end user deploys from published repo

### Platform capability update

1. `/verify-platform <name>` — fetch changelog, propose changes, approve
2. Compiler reports affected intents
3. Recompile affected intents → review → publish

### Reconciling ad-hoc published edits

1. `/reconcile` — diff `working/` vs published repo
2. Per drifted file, the reconcile skill shows the diff and offers options:
   - **Backport**: user manually edits the source intent to incorporate the change, then recompiles. The reconcile skill identifies which intent produced the drifted file (via SQLite compilation records) and opens it for editing. This is a manual process — the change may be platform-specific and needs human judgment to generalize back to the intent.
   - **Discard**: mark as acknowledged. Next publish overwrites the ad-hoc change.
3. Decisions recorded in SQLite with the diff content for audit

### Audit verification

1. Read `Skills version` and `Skills hash` from PR description
2. `python publish/verify.py --version <X>` — confirm hash matches MANIFEST.json
3. Full manifest shows exact skills active when the code was written

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Intent model | Single intent doc with SKILL/AGENT/PROMPT sub-structures | Compiler decides platform artifacts, not the author |
| Intent format | Markdown body + YAML frontmatter | Machine-readable metadata, human-readable content |
| Two-doc authoring | Goal & Constraints + Component Spec, merged on approval | Prevents drift during interview |
| Compilation | Separate Python exe, not part of factory skill | Deterministic, repeatable, auditable |
| Compiler output | Full compilation with shared library | Complete inspectable artifacts, shared content deduplicated per platform capability |
| LLM in compiler | Local Ollama for advice, not frontier model | Structured classification, no creativity needed |
| Publish toolchain | Python Phase 1, Rust Phase 2 drop-in | Iterate fast, then harden |
| Hash algorithm | SHA-256 | Fast, universal, well-supported in both Python and Rust |
| State backend | SQLite | Queryable, transactional, portable, no server |
| Platform definitions | Capabilities (vendor facts) + Rules (authoring conventions) | Different change cadences, different owners |
| Capability updates | Versioned files, staleness checks, on-demand verify, compile-time warnings | Lightweight but visible |
| Extensions | Tracked in capabilities with status (default/approved/optional) | Superpowers, marketplace skills get first-class treatment |
| Stack rules | Hierarchical YAML inheritance | DRY, extensible by end users |
| Templates | Pass-through, not compiled | Closed decisions, no LLM reasoning needed |
| BA skills | Minimal — AERS, problem refinement only | Full pipeline stays in superpowers |
| Factory skills | Hand-authored, bootstrap the system | Avoids circular dependency |
| Published repo | Build artifact, not source of truth | Factory working dirs are canonical |
| Reconciliation | Git diff between working/ and published repo | Simple, uses existing tooling |

## Open Items

- Exact Ollama model selection for compiler advice mode
- MAPPING.md generation: auto-generate from compilation records (intent → platform mapping is available in SQLite) or maintain manually? Likely auto-generate.
- `deploy-skills` CLI: needs updates to read MANIFEST.json for version reporting. Clarify relationship to existing `deploy.sh`. May rename or replace.
- CI pipeline design: how to inject skills hash into PR descriptions automatically. Deferred to follow-up spec.
- Copilot Native emitter detail: needs same specificity as Claude and VS Code emitters during implementation. The current spec describes the decision logic but not the exact file layout — this will be refined when writing the first Copilot Native intent.
- Stack definition examples (e.g., `python-fastapi`) shown in hierarchy diagrams are illustrative. Only stacks with real rules will be created during initial implementation.
