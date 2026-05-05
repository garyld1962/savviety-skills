# GraphQL — Review Criteria

## Disposition Table

| Finding | Tier | Default Disposition | Override Condition |
|---------|------|--------------------|--------------------|
| `introspection: true` without env check | 1 | Blocking | None — always flag |
| No depth limit on server config change | 1 | Blocking | Pre-existing config confirmed unchanged |
| No complexity limit on server config | 1 | Blocking | Pre-existing config confirmed unchanged |
| Sensitive field resolver, no auth check | 1 | Blocking | Field explicitly intended to be public (e.g., `name`, `avatarUrl`) |
| Direct DB call in list-field resolver | 2 | Non-blocking | DataLoader present in same file or context |
| Mutation without input validation | 2 | Non-blocking | Input type has no user-controlled fields |
| Unhandled async resolver | 2 | Non-blocking | Global error handler confirmed in server config |
| Schema depth > 4 levels | 3 | Discussion | Author has documented the tradeoff |
| Heavy computation in field resolver | 3 | Discussion | Data set provably small and bounded |
| List field without pagination | 3 | Discussion | Field accesses a bounded collection (e.g., user roles) |

## Scope Rules

- Review only changed files. Do not flag pre-existing issues unless they are directly adjacent to a change.
- Resolver files: `*.resolver.ts`, `*.resolvers.ts`, `**/resolvers/**/*.ts`
- Schema files: `*.graphql`, `*.gql`
- Server config: files containing `ApolloServer`, `createServer`, `graphql-yoga`, `mercurius`
- Client files (`*.tsx`, `*.jsx`) are out of scope for security checks; apply only Tier 3 UX checks if included.

## Praise Criteria

Flag genuinely good decisions:
- DataLoader used correctly (new instance per request, ordered return)
- Union types used for expected error cases instead of throwing
- Persisted queries configured for production
- Field-level auth checks on sensitive resolver fields
