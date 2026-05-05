# Lean Skill — Directives

The canonical rules enforced by `/lean-skill`. Organized by target file.

---

## SKILL.md Directives

### Silent Execution (Active Audit + Review Sub-agent only)
Every non-Advisory skill must include all three:

```
Do not emit any text between tool calls during execution phases.
Accumulate findings internally. The report is the only output.
```
```
If a check produces no findings, record it as passed and move on. Do not narrate absence.
```
```
Combine related commands into a single shell invocation. Do not make a tool call to explain
what you are about to run.
```

### Dispatcher Contract (Review Sub-agent only)
Must have a "When Dispatched as Sub-Agent" table (see `archetypes.md`).
Must use `git merge-base HEAD main` not `HEAD~1`.

### Persona Length
3–5 sentences max. Trim to the distinctive/contrarian insight + core principles. Generic filler adds no value.

### Scope Limits
Must include a "Does not cover" or "Does not own" statement naming handoff targets.

---

## checks.md / Procedure File Directives

### Output Bounding
Every bash command that can produce unbounded output **must** be capped:

```bash
<command> | head -20
git log --oneline --since="30 days ago" | head -20
grep -rn "pattern" . | head -10
```

Without `| head -N`: a match on a 10,000-line file floods context.

### Filter-Before-Display
Emit only flagged lines. Do not print full file output.

```bash
# Bad: prints full file, reader must scan
cat file | head -50

# Good: emit only matches
grep -n "pattern" file | head -10
```

### One Command Per Check
Combine related patterns into a single invocation:

```bash
# Bad: two separate tool calls
grep -n "new Map()" file | head -5
grep -n "new Set()" file | head -5

# Good: one call
grep -n "new Map()\|new Set()\|cache\s*=\s*{}" file | head -5
```

### No Restating Comments in Bash Blocks
Comments inside a bash block that restate the heading above are waste:

```bash
# Bad
### Unbounded Cache
# This checks for unbounded cache patterns  ← redundant
grep -n "new Map()" file | head -5

# Good
### Unbounded Cache
grep -n "new Map()\|new Set()" file | grep -v "LRU\|max:\|maxSize" | head -5
```

### No Duplicate Extraction Commands
If `SKILL.md` defines the diff extraction command, `checks.md` must not repeat it.

---

## report.md / Output File Directives

### No Preamble
Report starts with the output header. Not with "I've completed the audit..." or "Here are the findings...".

### No Command Echo
Show findings, not the command that produced them.

```
# Bad
Running: grep -n "pattern" src/utils.ts
Found: match at line 42

# Good
`src/utils.ts:42` — match content here
```

### Evidence Truncation
Max 3 lines of evidence per finding. If more exist, append `(N total — showing 3)`.

### Collapse Passed Checks
More than 8 checks passed → emit one line: `All 12 remaining checks passed.`
Do not list each individually.

### No Template Placeholder Lines
Remove lines like `[repeat for each finding]`, `[add more findings here]`. Structure speaks for itself.

### Tighten Discussion Entries

```
# Bad
**Discussion**: This approach trades X for Y. It may or may not be appropriate depending
on your team's priorities and scale requirements. Consider carefully before proceeding.

# Good
**Tradeoff**: X vs Y. Worth it here?
```

---

## Advisory File Directives (patterns.md, decisions.md, sharp-edges.md)

### Bullet List Condensation
Short multi-item bullets → inline form:

```
# Bad
- Option A
- Option B
- Option C

# Good
Option A, Option B, or Option C — pick one.
```

### No Dangling Callout Lines
Lines after a code block that restate what the block shows → fold into the block or cut:

```
# Bad
    cache = LRUCache(max=500, ttl=300_000)

**Remember**: always set a max size and TTL.

# Good
    cache = LRUCache(max=500, ttl=300_000)  # max + TTL always required
```

### Cut "If you see X, do Y" Closers
Closing sentences after warning-signs lists that restate the list → cut. The list implies the action.

### Sharp Edge Format
Every sharp edge must follow this structure:

```markdown
## Edge Title
**Severity**: Critical / High / Medium
**Situation**: One sentence.

  code or illustration showing the trap

**Fix**: 1–3 sentences max.
```

---

## Tier Integrity (criteria.md)

### Blocking vs Non-blocking Mismatch
Check in Tier 1 that criteria.md classifies as Non-blocking → move to Tier 2.
Check in Tier 2 that criteria.md classifies as Blocking → move to Tier 1.

### Missing False Positive Exemptions
Tier 2 checks need at least one caveat: when NOT to flag.

### Optional Scoring Sections
Remove severity-score tables unless the dispatcher explicitly requires a numeric output.
