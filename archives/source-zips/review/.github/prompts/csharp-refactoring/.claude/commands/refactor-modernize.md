# C# / .NET 10 Modernization

You are modernizing a C# codebase to leverage **C# 13 and .NET 10** features. The codebase was ported from Java and likely contains verbose, outdated patterns.

## Scope

If arguments are provided, modernize only those files or directories: $ARGUMENTS
If no arguments are provided, ask the user what to target. Do NOT modernize the entire codebase at once.

## Pre-flight

1. Read `docs/refactoring-candidates.md` if it exists — use the Modernization Candidates section to guide your work.
2. Read the target files thoroughly before making any changes.
3. Present a brief plan to the user and get confirmation before editing.

## Modernization checklist

Apply these transforms where appropriate, in order of impact:

### High Impact
- **Records**: Convert getter/setter DTOs and value objects to `record` or `record struct`
- **Nullable reference types**: Enable and annotate nullability; replace manual null checks with `?.`, `??`, `??=`, and `ArgumentNullException.ThrowIfNull`
- **Primary constructors**: Use on classes and structs where constructor just assigns to fields
- **async/await**: Replace `Task.ContinueWith`, `Task.Result`, `Task.Wait()` with proper async/await
- **Pattern matching**: Convert complex `if`/`else if` chains and `switch` statements to switch expressions with pattern matching

### Medium Impact
- **Collection expressions**: Use `[1, 2, 3]` syntax, spread operator `[..existing, newItem]`
- **File-scoped namespaces**: Convert block-scoped to file-scoped
- **Using declarations**: Convert `using` blocks to `using` declarations where scope allows
- **Raw string literals**: Replace escaped strings and verbatim strings with `"""`
- **Required properties**: Add `required` keyword to properties that must be set at construction
- **String interpolation**: Replace `string.Format` and concatenation

### Low Impact (batch-apply)
- **Target-typed new**: `List<string> items = new()` instead of `new List<string>()`
- **Global usings**: Move common usings to a `GlobalUsings.cs`
- **Implicit usings**: Enable in project file where appropriate
- **is not null**: Replace `!= null` checks
- **Simplified LINQ**: Use `Enumerable.TryGetNonEnumeratedCount`, `Order()` instead of `OrderBy(x => x)`

### What NOT to do
- Do NOT change architecture (that's `/refactor-arch`)
- Do NOT optimize algorithms or memory (that's `/refactor-perf`)
- Do NOT change behavior — these are syntax/API modernizations only
- Do NOT modernize test code in the same pass as production code
- Do NOT enable nullable reference types project-wide without confirming with the user first

## After modernizing

1. Verify the solution builds: `dotnet build`
2. Run tests if they exist: `dotnet test`
3. Summarize what changed in 3-5 bullet points
4. Update `docs/refactoring-candidates.md` — mark completed items and note any new findings
