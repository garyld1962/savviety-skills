# GraphQL — Patterns

## Schema-First Design

The schema is the contract. Write it before the resolvers. Nullability is a deliberate choice — non-null fields must always resolve or the entire parent nulls out.

```graphql
type Query {
  user(id: ID!): User!          # Non-null: throws on not-found
  userByEmail(email: String!): User  # Nullable: returns null if not found
  users(first: Int, after: String): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

# Payload types carry errors — don't throw for expected failures
type CreateUserPayload {
  user: User
  errors: [UserError!]!
}

union LoginResult = LoginSuccess | InvalidCredentials | AccountLocked
```

**Nullability rules**: Non-null if always present and failure should fail the query. Nullable if optional or partial success is acceptable.

---

## DataLoader — N+1 Solution

Without DataLoader, fetching 100 posts with authors fires 101 queries. DataLoader batches them into 2.

```ts
// Create per-request (scope matters — cache is per-request)
function createLoaders(db) {
  return {
    userLoader: new DataLoader(async (ids: readonly string[]) => {
      const users = await db.user.findMany({ where: { id: { in: ids } } });
      const map = new Map(users.map(u => [u.id, u]));
      return ids.map(id => map.get(id) ?? null); // must return in same order
    }),
  };
}

// Resolver — use .load(), never direct DB call
const resolvers = {
  Post: {
    author: (post, _, { loaders }) => loaders.userLoader.load(post.authorId),
  },
};
```

Key rules: new loaders per request, return results in input ID order, handle missing items with null (not by skipping).

---

## Query Depth + Complexity Limits

Circular schemas (`user → posts → author → posts → ...`) let clients craft exponentially expensive queries. Enforce limits at server startup.

```ts
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    depthLimit(10),
    createComplexityLimitRule(1000, { scalarCost: 1, objectCost: 2, listFactor: 10 }),
  ],
  introspection: process.env.NODE_ENV !== 'production',
});
```

---

## Cursor-Based Pagination

Offset pagination breaks under concurrent writes. Cursor pagination is stable.

```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}
type UserEdge { node: User!; cursor: String! }
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

Client fetches `users(first: 20, after: $cursor)`. Server returns `pageInfo.endCursor` for the next page.

---

## Federation for Microservices

Federation lets multiple services compose a single schema. Each service owns its types.

```ts
// users-service
import { buildSubgraphSchema } from '@apollo/subgraph';
const typeDefs = gql`
  extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@key"])
  type User @key(fields: "id") {
    id: ID!
    name: String!
    email: String!
  }
`;

// orders-service references User without owning it
const typeDefs = gql`
  type Order @key(fields: "id") {
    id: ID!
    user: User!  # Resolved via federation
  }
  extend type User @key(fields: "id") {
    id: ID! @external
  }
`;
```

---

## Error Handling — Partial Success

Use union types for expected failures. GraphQL errors (thrown exceptions) are for unexpected failures only.

```ts
// Resolver returns typed error instead of throwing
Mutation: {
  login: async (_, { email, password }, { db }) => {
    const user = await db.user.findByEmail(email);
    if (!user || !await verify(password, user.hash)) {
      return { __typename: 'InvalidCredentials', message: 'Invalid email or password' };
    }
    return { __typename: 'LoginSuccess', user, token: generateToken(user) };
  }
}
```

Client handles all cases with `... on TypeName` fragments.

---

## Persisted Queries

Register queries at deploy time. Production only executes pre-registered query hashes — unknown queries are rejected. Eliminates ad-hoc query DoS and leaks introspection data.
