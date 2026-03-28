# C# Architecture Refactoring

You are refactoring the architecture of a C# codebase that was ported from Java, targeting **.NET 10**.

## Scope

If arguments are provided, refactor only those files or directories: $ARGUMENTS
If no arguments are provided, ask the user what to target. Do NOT refactor the entire codebase at once.

## Pre-flight

1. Read `docs/refactoring-candidates.md` if it exists — use the Architecture Candidates section to guide your work.
2. Read the target files thoroughly before making any changes.
3. Present a brief plan to the user and get confirmation before editing.

## What to refactor

Focus on **one concern at a time**. Prefer small, reviewable diffs.

### Patterns to apply
- **Single Responsibility**: Split god classes into focused classes
- **Dependency Injection**: Replace manual instantiation and service locators with constructor injection via the .NET DI container
- **Interface segregation**: Break fat interfaces into focused ones
- **Composition over inheritance**: Replace deep inheritance hierarchies with composition, delegation, or interfaces with default implementations
- **Remove Java-isms**: Eliminate patterns that exist only because Java required them (e.g., utility classes that should be extension methods, checked-exception wrappers, `IComparable` implementations that should be `IComparer<T>`)
- **Idiomatic project structure**: Align with .NET conventions (namespaces matching folder structure, proper use of `internal` vs `public`)

### What NOT to do
- Do NOT modernize language syntax (that's `/refactor-modernize`)
- Do NOT optimize performance (that's `/refactor-perf`)
- Do NOT change public API contracts without confirming with the user
- Do NOT refactor tests in the same pass as production code

## After refactoring

1. Verify the solution builds: `dotnet build`
2. Run tests if they exist: `dotnet test`
3. Summarize what changed and why in 3-5 bullet points
4. Update `docs/refactoring-candidates.md` — mark completed items and note any new findings
