# C# Refactoring Inspector

You are inspecting a C# codebase that was ported from Java. Your job is to perform a **cursory first-pass review** and produce a markdown document identifying candidates for refactoring.

## Scope

If arguments are provided, inspect only those files or directories: $ARGUMENTS
If no arguments are provided, inspect the entire codebase.

## What to look for

Scan each file and categorize findings into these buckets:

### 1. Architecture Candidates
- God classes / classes with too many responsibilities
- Missing or misused interfaces and abstractions
- Tight coupling between components
- Java-style patterns that don't translate well to C# (e.g., factory classes where generics or DI suffice, excessive use of inheritance over composition)
- Service locator or manual DI where framework DI should be used
- Layering violations (e.g., data access in controllers)

### 2. C# / .NET 10 Modernization Candidates
- Getter/setter-only classes that should be `record` types
- Manual null checks replaceable with nullable reference types
- Verbose LINQ or loops replaceable with modern collection expressions
- Missing use of `Span<T>`, `Memory<T>`, or `ReadOnlySpan<T>` for buffer/string work
- `IEnumerable` chains that should be `IAsyncEnumerable`
- String concatenation instead of interpolation or `CompositeFormat`
- Old-style `Task.Run` / `Task.ContinueWith` instead of `async/await`
- Missing `using` declarations (non-block form)
- Classes that should leverage primary constructors
- `switch` statements convertible to switch expressions
- Missing file-scoped namespaces
- Missing `required` keyword on properties
- Java-style `equals`/`hashCode` patterns instead of records or `IEquatable<T>`

### 3. Performance & Memory Candidates
- Excessive allocations in hot paths (string concat in loops, LINQ in tight loops)
- Boxing of value types
- Missing `stackalloc` or `ArrayPool<T>` usage
- Synchronous I/O where async should be used
- Unbounded collections or caches
- N+1 query patterns or repeated enumeration of `IEnumerable`
- Large struct copies (should pass by `ref` or `in`)
- Missing `sealed` on classes not designed for inheritance
- `Dictionary` lookups that could use `FrozenDictionary` or `FrozenSet`
- Inefficient exception-driven control flow

## Output

Write the results to `docs/refactoring-candidates.md` with this structure:

```markdown
# Refactoring Candidates

> Generated: [date] | Scope: [files/dirs inspected or "full codebase"]

## Summary

| Category | Files Affected | Candidates Found |
|----------|---------------|-----------------|
| Architecture | N | N |
| Modernization (.NET 10) | N | N |
| Performance & Memory | N | N |

## Critical (High Impact)

[List items that are both easy to identify and high-impact. These are the "low-hanging fruit" plus the "this will bite you" items.]

## Architecture Candidates

### [filename:line] — Short description
- **Issue**: What the problem is
- **Suggestion**: What to consider
- **Effort**: Low / Medium / High

[Repeat for each finding]

## Modernization Candidates

### [filename:line] — Short description
- **Issue**: What the problem is
- **Modern alternative**: The C# 13 / .NET 10 way
- **Effort**: Low / Medium / High

[Repeat for each finding]

## Performance & Memory Candidates

### [filename:line] — Short description
- **Issue**: What the problem is
- **Suggestion**: What to consider
- **Estimated impact**: Low / Medium / High
- **Effort**: Low / Medium / High

## Boilerplate / Quick Wins

[Items that are mechanical and could be batch-applied: file-scoped namespaces, using declarations, sealed classes, etc. Group these by type rather than listing individually.]

## Notes & Open Questions

[Anything ambiguous that needs human judgement before proceeding.]
```

## Important guidelines

- This is a **cursory** review — flag candidates, don't solve them. Keep descriptions brief.
- When in doubt, include it. False positives are acceptable at this stage; false negatives are not.
- Do NOT modify any source code. This skill is read-only.
- Use the Explore agent to efficiently scan the codebase. Parallelize where possible.
- For large codebases, prioritize breadth over depth — touch every file but don't deep-dive.
