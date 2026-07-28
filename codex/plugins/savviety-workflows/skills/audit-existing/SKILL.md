---
name: audit-existing
description: "Read-only audit of an existing implementation before planning or extending it. Produces implemented, missing, duplicated, broken, and risky findings without editing files."
---

# Audit Existing

Use this before extending a repo or replacing behavior that may already exist.

## Workflow

1. Restate the requested capability or expected behavior.
2. Search for existing implementations, tests, routes, commands, schema, docs, and configuration.
3. Classify evidence as implemented, missing, duplicated, broken, risky, or unknown.
4. Report file references and confidence.
5. Do not edit files.

## Output

Return:

- `Implemented`
- `Missing`
- `Duplicated`
- `Broken or Risky`
- `Recommended next step`

Every concrete claim should cite a file path or command result.
