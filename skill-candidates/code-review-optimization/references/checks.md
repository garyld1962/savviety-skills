# Code Review: Optimization — Checks

All checks run against added lines only (see SKILL.md Step 2 for extraction command).

---

## Tier 1 — Auto-Flag (High Confidence)

Run against all changed source files.

### Unbounded Cache

```bash
grep -n "new Map()\|new Set()\|cache\s*=\s*{}" <file> \
  | grep -v "LRU\|max:\|maxSize\|\.delete\|\.clear" | head -5
```

Flag if no LRU, max size, or TTL visible within ±5 lines of each match.

### Full Library Import

```bash
grep -n "from 'lodash'\|from \"lodash\"\|require('lodash')\|from 'moment'\|from \"moment\"" <file> | head -5
```

Always flag. Named imports (`from 'lodash/debounce'`) are fine.

### Console Interpolation in Production Code

```bash
grep -n "console\.log(.*\${.*}\|console\.log(.*+" <file> | head -5
```

Flag if file is under `src/`, `lib/`, or `app/`. Skip test files.

### DOM Query Inside Loop

```bash
grep -n "document\.querySelector\|document\.getElementById\|document\.getElements" <file> \
  | head -5
```

Check if the query appears inside a `for`, `forEach`, `map`, or `while` block. If so, flag.

### Regex Creation Inside Loop

```bash
grep -n "new RegExp(" <file> | head -5
```

Check if the `new RegExp` line is inside a loop construct. If so, flag.

### String Concatenation Inside Loop

```bash
grep -nE "(for|forEach|while).*\+=\s*['\"]|['\"].*\+=.*for" <file> | head -5
```

### Await in forEach

```bash
grep -n "\.forEach(async" <file> | head -5
```

Correctness bug — `async forEach` does not await. Use `for...of` or `Promise.all` instead.

---

## Tier 2 — Judgment Required

Apply to `src/`, `lib/`, `app/` files only. Check context before flagging.

### Sequential Await in Loop

```bash
grep -n "await " <file> | head -10
```

Flag only if the `await` appears inside a `for`, `for...of`, or `while` loop — not in `.forEach`. Skip if a comment like `// sequential required` or `// order matters` is within 3 lines.

### Event Listener Without Cleanup

```bash
grep -n "addEventListener(" <file> | head -5
```

Flag if no corresponding `removeEventListener` exists in the same file. Do not flag React `useEffect` patterns where a cleanup function is returned.

### Synchronous File Operations

```bash
grep -n "readFileSync\|writeFileSync\|readdirSync\|existsSync" <file> | head -5
```

Skip if file is a build script, CLI tool, or the match is inside a startup/init function.

### Nested Loop (O(n²) Risk)

```bash
grep -nE "\.forEach\(|\.map\(|for " <file> | head -10
```

Flag only if two loop constructs are visibly nested within the same function in the diff. Single loops are fine.

---

## Tier 3 — Architectural Concerns (Discussion Only)

### Premature Abstraction Signals

```bash
grep -n "options\?:\|config\?:\|settings\?:" <file> | head -5
```

Flag if the new code introduces a function with more than 5 optional parameters. Suggest applying Rule of Three.

### Direct DB/Raw Query Bypassing ORM

```bash
grep -n "db\.raw\|db\.query\|sql\`\|knex\.raw" <file> | head -5
```

Note as a tradeoff: performance gain vs. coupling. Not a blocker unless it crosses a module boundary it shouldn't.

### Dependency Version Unlock

```bash
grep -n "\"\\*\"\|\"latest\"\|\">=\|\">" package.json 2>/dev/null | head -5
```

Only applies if `package.json` is in the diff. Flag unlocked versions as a stability suggestion.
