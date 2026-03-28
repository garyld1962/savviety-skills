# C# Performance & Memory Optimization

You are optimizing a C# codebase for performance and memory efficiency, targeting **.NET 10**. The codebase was ported from Java and likely has allocation-heavy patterns.

## Scope

If arguments are provided, optimize only those files or directories: $ARGUMENTS
If no arguments are provided, ask the user what to target. Do NOT optimize the entire codebase at once.

## Pre-flight

1. Read `docs/refactoring-candidates.md` if it exists — use the Performance & Memory Candidates section to guide your work.
2. Read the target files thoroughly before making any changes.
3. Present a brief plan to the user and get confirmation before editing.
4. Identify hot paths vs cold paths — focus effort on hot paths.

## Optimization checklist

### Memory / Allocation Reduction
- **Span/Memory**: Use `Span<T>`, `ReadOnlySpan<T>`, `Memory<T>` for slicing and buffer work instead of allocating new arrays/strings
- **stackalloc**: Use for small, fixed-size buffers in hot paths
- **ArrayPool / MemoryPool**: Rent buffers instead of allocating in loops or frequently called methods
- **String optimization**: Use `string.Create`, `StringBuilder` pooling, or `CompositeFormat` for repeated formatting; avoid `string.Split` where `ReadOnlySpan<char>` slicing works
- **Value types**: Convert small, immutable classes to `readonly record struct` where appropriate
- **Sealed classes**: Add `sealed` to classes not designed for inheritance (enables devirtualization)
- **Avoid boxing**: Eliminate value-type boxing (e.g., passing structs through `object`, non-generic collections)

### Algorithmic
- **Collection choice**: `FrozenDictionary`/`FrozenSet` for read-heavy lookup tables, `HashSet` over `List` for contains checks, right-size collections with capacity hints
- **LINQ in hot paths**: Replace LINQ with `for`/`foreach` loops in performance-critical code; use `Enumerable.TryGetNonEnumeratedCount`
- **Lazy evaluation**: Use `IEnumerable` / `yield return` to avoid materializing large collections when only iterating
- **Batch operations**: Replace N+1 patterns with batch queries/operations
- **Caching**: Add caching for expensive computations with `Lazy<T>`, `ConcurrentDictionary.GetOrAdd`, or `MemoryCache`

### Async & Concurrency
- **ValueTask**: Use `ValueTask<T>` for methods that frequently complete synchronously
- **ConfigureAwait**: Apply `ConfigureAwait(false)` in library code
- **IAsyncEnumerable**: Use for streaming data instead of materializing collections
- **Channel<T>**: Replace `BlockingCollection` with `Channel<T>` for producer-consumer
- **Parallel.ForEachAsync**: Use for CPU-bound parallel work over `Task.WhenAll` with `Select`

### What NOT to do
- Do NOT optimize cold paths or code that runs once at startup — focus on hot paths
- Do NOT sacrifice readability for marginal gains — every optimization must be justified
- Do NOT change architecture (that's `/refactor-arch`)
- Do NOT modernize syntax without perf benefit (that's `/refactor-modernize`)
- Do NOT micro-optimize without evidence — if you can't articulate why it matters, skip it

## After optimizing

1. Verify the solution builds: `dotnet build`
2. Run tests if they exist: `dotnet test`
3. Summarize what changed, and for each change note the **expected impact** (reduced allocations, fewer iterations, etc.)
4. Update `docs/refactoring-candidates.md` — mark completed items and note any new findings
5. If benchmarks exist, suggest running them. If they don't, suggest which optimizations would benefit from a benchmark.
