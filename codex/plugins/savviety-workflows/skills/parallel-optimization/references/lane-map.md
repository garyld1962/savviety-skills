# Parallel Optimization Lane Map

Use this to decide whether a plan can safely run with parallel lanes.

## Analysis

For each task, identify:

- Write scope.
- Read-only context.
- Dependencies.
- Shared surfaces.
- Verification command.
- Contract produced or consumed.

## Safe Parallel Conditions

Parallel execution is safe only when:

- Write scopes are disjoint or one owner is named for shared files.
- Shared exports, lockfiles, manifests, migrations, generated files, and root config have a single owner.
- Contract-producing tasks complete before consumers.
- Each lane has focused verification.
- An integration lane owns final verification and conflict resolution.

## Required Plan Section

Add or update:

```markdown
## Parallel Execution

Mode: sequential | parallel

### Shared Context Packet
...

### Ownership
...

### Barriers
...

### Single-Owner Files
...

### Parallel Safety Checks
...
```

If safe parallelism is not proven, set `Mode: sequential` and state why.

