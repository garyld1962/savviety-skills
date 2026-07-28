# GraphQL — Review Checks

All checks run against changed lines only. Extract with:
```bash
git diff <base_ref> -- <files> | grep '^+' | grep -v '^+++' > /tmp/gql-diff.txt
```

---

## Tier 1 — Blocking (Security / DoS)

### Introspection Enabled Without Env Guard

```bash
grep -nE "introspection\s*:\s*true" /tmp/gql-diff.txt | head -5
```

Flag if `introspection: true` appears without a conditional. Safe form: `introspection: process.env.NODE_ENV !== 'production'`.

### Missing Query Depth Limit

```bash
grep -nE "new ApolloServer|createServer|buildASTSchema" /tmp/gql-diff.txt | head -5
```

If a server instantiation is added or changed, check that `validationRules` includes `depthLimit(...)`. Flag if absent.

### Missing Query Complexity Limit

```bash
grep -nE "validationRules\s*:" /tmp/gql-diff.txt | head -5
```

Flag server config changes where `validationRules` is missing or doesn't include a complexity rule (`createComplexityLimitRule` or equivalent).

### Sensitive Fields Without Auth Check in Resolver

```bash
grep -nE "(email|phone|ssn|password|secret|token|privateKey|creditCard)\s*:" /tmp/gql-diff.txt | head -10
```

For each match in a resolver file: verify that the resolver function checks `currentUser` or `context.user` before returning the value. Flag if the field resolver body contains no auth check.

---

## Tier 2 — Judgment Required

### Direct DB Call in List-Field Resolver (N+1 Risk)

```bash
grep -nE "(findUnique|findOne|findById|findFirst)\s*\(\s*\{" /tmp/gql-diff.txt | head -10
```

Flag matches inside resolver files (`*.resolver.ts`, `**/resolvers/**`) when the resolver is for a field on a type that appears in a list (e.g., `Post.author`, `Comment.user`). No flag if the same file imports or uses DataLoader.

### Mutation Input Without Validation

```bash
grep -nE "input\s*:\s*\w+Input\b" /tmp/gql-diff.txt | head -10
```

For each Input type referenced in a new mutation resolver, check that the resolver body validates or uses a schema validation library (`zod`, `joi`, `class-validator`). Flag if absent.

### Unhandled Resolver Exception

```bash
grep -nE "async\s*\([^)]*\)\s*=>\s*\{" /tmp/gql-diff.txt | head -10
```

Flag resolver functions in which the body contains `await` but no `try`/`catch`. Unhandled exceptions propagate as opaque GraphQL errors and may leak stack traces.

---

## Tier 3 — Discussion

### Schema Depth Greater Than 4 Levels

```bash
grep -nE "^\+\s+\w+\s*:\s*\w+\s*\{" /tmp/gql-diff.txt | head -20
```

Manually scan new type definitions for nesting beyond 4 levels (e.g., `Post { comments { author { posts { ... } } } }`). Flag for discussion — deep nesting compounds query complexity.

### Field Resolver with Heavy Computation

```bash
grep -nE "(sort|filter|reduce|map)\s*\(" /tmp/gql-diff.txt | head -10
```

Flag field resolvers doing in-process data transformation on large collections. These should be deferred to service layer or computed at write time.

### List Field Without Pagination Arguments

```bash
grep -nE ":\s*\[\w+!?\]!?\s*$" /tmp/gql-diff.txt | head -10
```

Flag list return types on Query fields or type relationships that have no `limit`, `first`, or `after` argument. Note as discussion: unbounded lists become a problem at scale.
