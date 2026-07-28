---
name: modernization-rubric
description: Calibration rubric for the `modernize` prompt. Encodes project-shape detection, sample-read strategy, admissible moves, per-theme finding patterns, and cull criteria.
---

# Modernization Rubric

Use this skill when running `#prompt:modernize`. It calibrates which
modernization moves are worth turning into a refactor plan.

## Purpose

Keep modernization work objective, within-stack, and execution-ready. This
skill exists so the prompt does not have to inline a giant rubric.

## Project shape detection

### Language detection

Read root manifests in this order; the first strong match identifies the
primary language:

| Manifest | Language |
|---|---|
| `package.json` | JavaScript / TypeScript |
| `Cargo.toml` | Rust |
| `pyproject.toml` / `setup.py` / `requirements.txt` | Python |
| `go.mod` | Go |
| `*.csproj` / `*.sln` / `*.slnx` | C# / .NET |
| `pom.xml` / `build.gradle*` | Java / Kotlin |
| `mix.exs` | Elixir |
| `Gemfile` | Ruby |

If multiple language manifests exist, pick the dominant language by source-file
extension count or package/workspace weight.

### Type classification

| Type | Signals |
|---|---|
| CLI | `bin` entry, argv parsing, no persistent server |
| Library | exported API, little or no top-level execution |
| App | UI framework imports, browser build pipeline |
| Service | HTTP framework imports, server start visible |
| Monorepo | workspace config such as `pnpm-workspace.yaml`, `turbo.json`, Cargo `[workspace]`, etc. |

Use the dominant shape and note any meaningful secondary shape.

### Size class

| Class | LOC range | Behaviour |
|---|---|---|
| Tiny | <500 | Refuse; recommend direct edits or a focused simplification |
| Small | 500-5,000 | Standard audit |
| Medium | 5,000-50,000 | Standard audit with token discipline |
| Large | 50,000-250,000 | Sample-read only; watch blast radius |
| Very large | >250,000 | Halt and recommend a per-package audit |

### Test coverage signal

| Signal | Heuristic |
|---|---|
| Strong | test:src LOC ratio >0.5; most public modules have tests |
| Present | ratio 0.2-0.5; meaningful but incomplete coverage |
| Thin | ratio <0.2 or mostly shallow tests |
| Absent | no usable test suite found |

If tests are thin or absent, characterization tests become a prerequisite for
behaviour-preserving refactors.

### Detected patterns

Look for explicit architectural signals:

- Layered
- Hexagonal
- MVC
- Functional core / imperative shell
- None detected

## Admissible moves by shape

Treat this matrix as a bias, not a license to force architecture.

| Move | CLI | Library | App | Service | Monorepo |
|---|---|---|---|---|---|
| Introduce DI container | rarely | sometimes | sometimes | often | often |
| Hexagonal architecture | no | rarely | sometimes | often | sometimes |
| Workspace splitting | no | sometimes | sometimes | sometimes | often |
| Branded / nominal types | sometimes | often | often | often | often |
| Top-level error boundary | sometimes | no | often | often | often |
| Module-per-feature reorganization | sometimes | sometimes | often | often | often |
| Replace stringly-typed enum with discriminated union | often | often | often | often | often |
| Extract config module | sometimes | sometimes | often | often | often |
| Introduce result/either type for error handling | sometimes | often | sometimes | often | often |
| Characterization tests for untested logic | often | often | often | often | often |

### Size-class admissibility

| Class | Max admissible blast radius in the primary plan |
|---|---|
| Small | up to 30% of files |
| Medium | up to 20% of files |
| Large | up to 10% of files |
| Very large | per-package only |

Moves above the admissible blast radius belong in the appendix, not the primary
plan.

## Sample-read strategy

Do not read every file. Sample by signal category:

| Category | What to read |
|---|---|
| Breadth | First file in every top-level directory |
| Depth | Top 5 modules by LOC, fully |
| Boundaries | Every `index.*`, `__init__.py`, `mod.rs`, or equivalent boundary file |
| Public surface | Files re-exported from the package entry point |
| Risk hotspots | Files >500 LOC and files matching `utils*`, `helpers*`, `common*`, `lib*`, `misc*` |
| Test parity | Spot-check 3 representative source files for matching tests |

**Token guardrail:** stop reading when the cumulative read would consume roughly
30% of the available context window.

## Per-theme finding patterns

### Abstraction

| Pattern | Default severity |
|---|---|
| Function >100 LOC without natural break | medium |
| Class with >10 public methods | medium |
| Conditional nesting depth >=3 | high |
| Forwarding-only `Manager` / `Handler` / `Service` class | medium |
| Inheritance chain >=3 levels | medium |
| Stringly-typed `switch` that wants a discriminated union | high |
| Function takes >5 positional args | medium |

### Separation of concerns

| Pattern | Default severity |
|---|---|
| Business logic in HTTP handler or UI component | high |
| File mixing >2 concerns | medium |
| Module imports another module's internal types | high |
| Circular dependency | high |
| Side effects at module top level | medium |
| Shared constants duplicated in feature modules | low |

### Types

| Pattern | Default severity |
|---|---|
| `any` / `unknown` cast away from an external boundary | high |
| Untyped dict / kwargs proliferation | medium |
| Repeated string literal that should be a typed enum | medium |
| Stale type comments instead of annotations | low |
| Type assertion instead of narrowing | medium |
| Optional / nullable everywhere "just in case" | medium |

### Errors

| Pattern | Default severity |
|---|---|
| Bare `catch` / `except` swallowing the error | high |
| Logged error with silent continuation | high |
| Error returned as `null` / `undefined` instead of a typed error | medium |
| Repeated error-message string handling | low |
| Error path untested | medium |
| Generic `Error` where a typed error exists | low |

### Tests

| Pattern | Default severity |
|---|---|
| Test file exists but only trivial cases | medium |
| Mocked-everything test | medium |
| Snapshot-only assertions on opaque output | low |
| Test names that only restate the function name | low |
| No edge-case tests on tricky modules | high |
| Tests import private helpers | medium |

### Infra

| Pattern | Default severity |
|---|---|
| Hardcoded URLs, keys, or paths in source | high |
| Settings scattered across files | medium |
| Build config has stale defaults or missing modern defaults | medium |
| No `.env.example` or config schema | low |
| CI YAML duplicates package scripts inline | low |
| Logging without structured fields | medium |

## Cull criteria

Apply these in order.

### Senior engineer test

Would a senior engineer with no codebase context, given a clear before/after,
agree the after is better? If no, cut it.

### Stylistic-preference test

Cut taste calls:

- variable renames for style only
- equivalent-loop rewrites
- whitespace-only cleanup
- quote-style churn

### Within-stack test

If the move implies a framework, language, database, or public API change, move
it to the out-of-scope appendix.

### Blast-radius vs. impact test

| Blast radius | Required impact |
|---|---|
| <5% of files | any impact tier |
| 5-15% | medium or high |
| 15-25% | high |
| >25% | high plus a verifiable benchmark |

### Cap test

Keep the top `--max-moves` by `impact x ease`; move the rest to
**Considered, not in primary plan**.

## Output contract

`#prompt:modernize` should express each move in this shape:

```yaml
move:
  theme: abstraction | separation | types | errors | tests | infra
  pattern: <one-line pattern name>
  examples:
    - file: src/example.ts
      line: 42
      excerpt: "..."
  proposed_state: "..."
  impact: high | medium | low
  ease: low | medium | high
  blast_radius: <integer file count>
  rationale: "..."
  scope_status: in-scope | out-of-scope | considered-not-primary
  acceptance:
    - "<mechanically verifiable criterion>"
```

Execution belongs to `#prompt:execute-prd --type=refactor`, not to this skill.

## Do Nots

- Do not turn style-only cleanup into modernization moves.
- Do not exhaustive-read large repos.
- Do not recommend stack switches in the primary plan.

## Closed Decisions

- Modernization stays within the current stack.
- `#prompt:modernize` produces a plan; `#prompt:execute-prd` executes it.
- A short list of high-confidence moves is better than a long list of taste
  calls.
