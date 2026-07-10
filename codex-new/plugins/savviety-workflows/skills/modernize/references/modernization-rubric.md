# Modernization Rubric

Use this reference to calibrate `modernize` findings. The goal is a short list of objective, within-stack refactor moves that current Codex workflows can execute safely.

## 1. Project Shape Detection

### Language

Read root manifests first:

| Manifest | Language |
|---|---|
| `package.json` | JavaScript / TypeScript |
| `Cargo.toml` | Rust |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python |
| `go.mod` | Go |
| `*.csproj`, `*.sln`, `*.slnx` | C# / .NET |
| `pom.xml`, `build.gradle*` | Java / Kotlin |
| `mix.exs` | Elixir |
| `Gemfile` | Ruby |

If multiple manifests exist, pick the primary language by source LOC and report secondary languages.

### Project Type

| Type | Signals |
|---|---|
| CLI | `bin` field, argv parsing, no HTTP server import |
| Library | module API exports, no top-level execution, README API examples |
| App | UI framework import, `index.html`, client build output |
| Service | HTTP framework import, server start, routes or controllers |
| Monorepo | workspace config such as `pnpm-workspace.yaml`, `turbo.json`, Cargo `[workspace]`, or `lerna.json` |

Use the dominant type and note secondary roles.

### Size Class

| Class | LOC Range | Behavior |
|---|---|---|
| Tiny | under 500 | Refuse; recommend direct edits or simplification |
| Small | 500 to 5,000 | Standard audit |
| Medium | 5,000 to 50,000 | Standard audit with token discipline |
| Large | 50,000 to 250,000 | Mandatory sample-read |
| Very large | over 250,000 | Halt; recommend per-package audit |

### Test Coverage Signal

| Signal | Heuristic |
|---|---|
| Strong | test-to-source LOC ratio over 0.5; public modules have tests |
| Present | ratio 0.2 to 0.5; important modules tested |
| Thin | ratio under 0.2 or shallow tests dominate |
| Absent | no tests directory and no test files |

Refactors against thin or absent tests must include characterization tests before structural changes.

### Architecture Pattern

Look for layered, hexagonal, MVC, functional-core/imperative-shell, or no clear pattern. Do not impose a pattern that the project shape does not justify.

## 2. Admissible Moves

| Move | CLI | Library | App | Service | Monorepo |
|---|---|---|---|---|---|
| Introduce DI container | Rarely | Sometimes | Sometimes | Often | Often |
| Hexagonal architecture | No | Rarely | Sometimes | Often | Sometimes |
| Workspace splitting | No | Sometimes | Sometimes | Sometimes | Often |
| Branded or nominal types | Sometimes | Often | Often | Often | Often |
| Top-level error boundary | Sometimes | No | Often | Often | Often |
| Module-per-feature organization | Sometimes | Sometimes | Often | Often | Often |
| Replace string enums with discriminated unions | Often | Often | Often | Often | Often |
| Extract config module | Sometimes | Sometimes | Often | Often | Often |
| Introduce result/either error type | Sometimes | Often | Sometimes | Often | Often |
| Add characterization tests | Often | Often | Often | Often | Often |

A "no" is a hard cut from the primary plan. A "rarely" needs a strong rationale.

## 3. Blast-Radius Limits

| Class | Max Primary-Plan Blast Radius |
|---|---|
| Small | up to 30 percent of files |
| Medium | up to 20 percent of files |
| Large | up to 10 percent of files |
| Very large | per-package only |

Demote oversized moves to the considered appendix unless they have a clear benchmark and the user has asked to plan a broad refactor.

## 4. Sample-Read Strategy

Do not read every file. Sample by signal:

| Category | What To Read |
|---|---|
| Breadth | First file alphabetically in each top-level directory |
| Depth | Top five modules by LOC |
| Boundaries | `index.*`, `__init__.py`, `mod.rs`, and equivalent entry or re-export files |
| Public surface | Files exported from package or service entry points |
| Hotspots | Files over 500 LOC; files named `utils*`, `helpers*`, `common*`, `lib*`, or `misc*` |
| Test parity | Three representative source files and their matching tests, if any |

Stop reading when synthesis headroom is at risk. For monorepos, audit one workspace member at a time.

## 5. Finding Patterns

### Abstraction

- Function over 100 LOC without natural break: medium.
- Class with more than 10 public methods: medium.
- Conditional nesting depth of 3 or more: high.
- `Manager`, `Handler`, or `Service` object that only forwards state: medium.
- Inheritance chain of 3 or more levels: medium.
- Stringly-typed switch that should be a typed union: high.
- Function taking more than 5 positional args without an options object: medium.

### Separation

- Business logic in HTTP handler or UI component: high.
- File mixes more than 2 concerns: medium.
- Module imports another module's internal types: high.
- Circular dependency: high.
- Side effects at module top level outside entry/init: medium.
- Constants trapped in feature modules instead of a shared boundary: low.

### Types

- `any` or `unknown` cast away from an external boundary: high.
- Untyped dict/kwargs proliferation: medium.
- Repeated string literal that should be a typed enum or union: medium.
- Stale type comments instead of native annotations: low.
- Assertion where narrowing is possible: medium.
- Optional or nullable everywhere without domain reason: medium.

### Errors

- Bare catch/except swallowing errors: high.
- Error logged while execution silently continues: high.
- Error represented as `null` or `undefined` instead of a typed result: medium.
- Repeated string error messages used for control flow: low.
- Error path has no tests: medium.
- Generic error where domain error type exists: low.

### Tests

- Test file has only one or two trivial cases: medium.
- Everything mocked, no real boundary tested: medium.
- Opaque snapshot without shape assertions: low.
- Test names repeat function names without behavior: low.
- Tricky module lacks edge-case tests: high.
- Tests import private helpers as API: medium.

### Infra

- Hardcoded URLs, credentials, or paths in source: high.
- Settings scattered instead of one config module: medium.
- Build config has stale or missing modern defaults: medium.
- No `.env.example` or config schema: low.
- CI duplicates package scripts inline: low.
- Logging lacks structured fields where operations matter: medium.

## 6. Cull Criteria

Apply these in order:

1. Senior engineer test: would a senior engineer with no repo context agree the proposed state is better?
2. Taste-call test: cut style preferences, equivalent idiom swaps, formatting churn, and personal naming preferences.
3. Within-stack test: demote framework, language, API, package-manager, database, REST/GraphQL, or runtime switches to out-of-scope.
4. Blast-radius test: high blast radius requires high impact and verifiable evidence.
5. Cap test: keep the top `--max-moves` by impact times ease; move the rest to the appendix.

Impact scores: high 3, medium 2, low 1. Ease scores: low effort 3, medium effort 2, high effort 1.

## 7. Move Record

Capture each surviving move in this shape:

```yaml
move:
  theme: abstraction | separation | types | errors | tests | infra
  pattern: "<finding pattern>"
  examples:
    - file: src/lib/foo.ts
      line: 42
      excerpt: "short representative excerpt or paraphrase"
  proposed_state: "one paragraph"
  impact: high | medium | low
  ease: low | medium | high
  blast_radius: 3
  rationale: "one sentence"
  scope_status: in-scope | out-of-scope | considered-not-primary
  acceptance:
    - "mechanically verifiable criterion"
```
