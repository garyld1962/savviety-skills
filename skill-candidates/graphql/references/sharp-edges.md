# GraphQL — Sharp Edges

---

## N+1 Without DataLoader

**Severity**: Critical
**Situation**: A resolver fetches a related entity by ID on every list item.

```ts
// TRAP: 100 posts = 101 queries
Post: {
  author: async (post, _, { db }) =>
    db.user.findUnique({ where: { id: post.authorId } })
}

// FIX
Post: {
  author: (post, _, { loaders }) => loaders.userLoader.load(post.authorId)
}
```

**Fix**: Use DataLoader for any resolver that accesses a relationship field. Detection: enable query logging — if query count scales with list length, you have N+1.

---

## Introspection Enabled in Production

**Severity**: Critical
**Situation**: `introspection: true` (or default) deployed to production.

```ts
// TRAP: Full schema exposed — attacker roadmap
const server = new ApolloServer({ typeDefs, resolvers });

// FIX
const server = new ApolloServer({
  typeDefs, resolvers,
  introspection: process.env.NODE_ENV !== 'production',
});
```

**Fix**: Disable introspection in production. Use persisted queries instead. Introspection exposes admin mutations, deprecated-but-live fields, and your entire data model.

---

## Missing Query Depth and Complexity Limits

**Severity**: Critical
**Situation**: Schema has circular relationships; no depth or complexity limit configured.

```
user → posts → author → posts → author → posts ... (depth 20)
Result: exponential resolver fan-out, server OOM or timeout
```

**Fix**: Add `depthLimit(10)` and `createComplexityLimitRule(1000)` to `validationRules`. Start conservative — you can raise limits, but production DoS incidents are hard to recover from.

---

## Authorization Only in Schema Directives

**Severity**: High
**Situation**: All authorization is handled via `@auth` directives; resolver-level checks are absent.

```ts
// TRAP: Directive-only — complex business rules don't fit, directive logic can be bypassed
type Mutation { deleteUser(id: ID!): User @auth(requires: ADMIN) }

// FIX: resolver enforces the rule in code
Mutation: {
  deleteUser: async (_, { id }, { user, db }) => {
    if (!user) throw new AuthenticationError('Not logged in');
    if (user.role !== 'ADMIN' && user.id !== id) throw new ForbiddenError('Not authorized');
    return db.user.delete({ where: { id } });
  }
}
```

**Fix**: Use directives for documentation; enforce authorization in resolver logic. Particularly important for field-level access (showing private email only to self/admin).

---

## Over-Fetching via Deeply Nested Queries

**Severity**: High
**Situation**: No pagination on list fields that can grow unbounded. `users { posts { comments { ... } } }` returns everything.

```graphql
# TRAP: No limit, no pagination
type User { posts: [Post!]! }

# FIX: Paginated with sane default
type User { posts(limit: Int = 10, after: String): PostConnection! }
```

**Fix**: Every list field that accesses a data store should have pagination arguments. Combine with complexity limits.

---

## Under-Fetching Leading to Client-Side Joins

**Severity**: Medium
**Situation**: Schema returns IDs instead of objects for relationships. Client fetches the object separately, re-implementing the join in JavaScript.

```graphql
# TRAP: authorId forces a second round-trip
type Post { id: ID!; title: String!; authorId: ID! }

# FIX: Resolve the relationship
type Post { id: ID!; title: String!; author: User! }
```

**Fix**: Model relationships as typed fields, not foreign key IDs. Use DataLoader to make resolution efficient.

---

## Mutation Side Effects Breaking Optimistic UI

**Severity**: Medium
**Situation**: Mutation returns a bare type or no data; client cannot update Apollo cache optimistically.

```ts
// TRAP: No id returned — Apollo can't normalize
mutation DeletePost($id: ID!) { deletePost(id: $id) }

// FIX: Return enough to update the cache
type DeletePostPayload { deletedId: ID!; errors: [UserError!]! }
```

**Fix**: Mutations should always return the affected entity (with `id`) or a payload type that includes it. Optimistic UI and cache consistency depend on it.
