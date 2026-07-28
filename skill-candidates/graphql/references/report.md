# GraphQL — Review Report Format

## Formatting Rules

- No preamble. No "I reviewed..." opener. Start directly with findings or the pass summary.
- No command echo. Do not repeat the grep commands run.
- Max 3 evidence lines per finding (file path, line number, offending code).
- Collapse passed checks: if more than 8 checks passed with no findings, emit `All N remaining checks passed.`
- Separate blocking, non-blocking, discussion, and praise sections.

---

## Output Template

```
## GraphQL Review

### Blocking

**[Finding Title]** — `path/to/file.ts:42`
> `introspection: true`
Introspection is enabled unconditionally. Exposes full schema in production. Change to `introspection: process.env.NODE_ENV !== 'production'`.

### Non-blocking

**[Finding Title]** — `resolvers/Post.resolver.ts:18`
> `author: async (post, _, { db }) => db.user.findUnique(...)`
Direct DB call in a list-field resolver. If Post appears in list queries, this is an N+1 source. Wrap with DataLoader.

### Discussion

**[Finding Title]** — `schema/types.graphql:55`
List field `User.activityLog` has no pagination arguments. Fine if the collection stays bounded; add `limit`/`after` if it can grow.

### Praise

**DataLoader correctly scoped** — `context/loaders.ts`
Loaders are created per-request in the context factory. Correct — prevents cross-request cache pollution.

---

All 6 remaining checks passed.
```

---

## Severity Labels

- **Blocking**: correctness bug, security vulnerability, will cause production failure
- **Non-blocking**: should fix before merge, doesn't block
- **Discussion**: tradeoff; author may have good reasons
- **Praise**: genuinely good decision worth noting
