---
slug: toy-greeter
source_prd: tests/fixtures/toy-prd.md
intent: Add a greet(name) helper and a CLI wrapper that prints it
type: feature
---

# Toy Greeter Plan

**Source:** tests/fixtures/toy-prd.md

## Closed Decisions

- Language: plain Node ESM, no dependencies.
- Output format: `Hello, <name>!` exactly.

## Task 1: greet helper

```yaml
depends_on: []
write_scope:
  - src/greet.mjs
  - test/greet.test.mjs
milestone_end: false
```

Create `src/greet.mjs` exporting `greet(name)` returning
`` `Hello, ${name}!` ``. Add `test/greet.test.mjs` using `node:test`.

**Acceptance:**
- `node --test test/greet.test.mjs` exits 0
- `node -e "import('./src/greet.mjs').then(m=>process.exit(m.greet('x')==='Hello, x!'?0:1))"` exits 0

## Task 2: CLI wrapper

```yaml
depends_on: [1]
write_scope:
  - bin/greet.mjs
milestone_end: false
```

Create `bin/greet.mjs` that prints `greet(process.argv[2])`.

**Acceptance:**
- `node bin/greet.mjs World` prints `Hello, World!`

## Task 3: README

```yaml
depends_on: [1]
write_scope:
  - README.md
milestone_end: true
```

Document usage in `README.md`.

**Acceptance:**
- `rg -q "greet" README.md` exits 0
