# Code Investigation Workflow

## Use

Use for evidence-backed answers about where behavior lives, how a pattern works, or whether behavior exists across one or more repositories.

## Steps

1. Restate the investigation question and scope.
2. Build a search plan with likely symbols, file patterns, config files, and runtime entrypoints.
3. Search with `rg` first, then read the smallest useful file ranges.
4. Track each match with repo, project, file, line, symbol, evidence type, and confidence.
5. Follow callers, callees, config bindings, and tests until the answer is supported or the gap is explicit.
6. Produce a concise answer unless the user asked for a durable report.

## Report Shape

- `Question`
- `Conclusion`
- `Evidence`
- `Matches by Repository`
- `Gaps and Confidence`
- `Next Checks`

Do not guess. If evidence is incomplete, say exactly what is missing.

