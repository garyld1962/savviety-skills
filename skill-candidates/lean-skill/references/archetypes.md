# Lean Skill — Archetypes

---

## Three Archetypes

| Type | Speaks during execution | Drives tool calls | Scope |
|------|------------------------|-------------------|-------|
| Advisory | Yes — answers questions | No | Conversational |
| Active Audit | No — silent | Yes — whole repo | Whole codebase |
| Review Sub-agent | No — silent | Yes — diff only | PR diff |

---

## Detection Rules

Read `SKILL.md` and classify:

```
contains "git merge-base" or grep "^+" → Review Sub-agent
contains checks.md in references/, no diff pattern → Active Audit
has patterns.md + decisions.md, no checks.md → Advisory
```

When ambiguous: prefer the archetype whose required files are present.

---

## Expected Files by Archetype

### Advisory
```
SKILL.md
references/
  patterns.md       required
  decisions.md      required (if decision-heavy content exists)
  sharp-edges.md    required
```

Missing `sharp-edges.md` → **Flag**: Advisory without sharp edges loses its most actionable content.
Extra `checks.md` in Advisory → **Flag**: Advisory skills do not drive tool calls; checks.md implies execution behavior.

---

### Active Audit
```
SKILL.md
references/
  checks.md         required  (audit procedure — bash commands against whole repo)
  criteria.md       required  (severity levels, scoring thresholds)
  report.md         required  (output template)
```

Missing `criteria.md` → **Flag**: Without severity definitions, checks have no pass/fail threshold.

---

### Review Sub-agent
```
SKILL.md
references/
  checks.md         required  (Tier 1 / Tier 2 / Tier 3 with grep commands on added lines)
  criteria.md       required  (disposition table: blocking/non-blocking/discussion/praise)
  report.md         required  (output template)
```

Missing dispatcher contract in `SKILL.md` → **Flag**: Sub-agent without input contract falls back to asking the user — unusable in automated workflows.

---

## Dispatcher Contract (Review Sub-agent only)

`SKILL.md` must include a table with these inputs:

| Input | Source |
|-------|--------|
| `files` | List of changed files |
| `base_ref` | Base commit for diff |
| `context` | PR description / feature being built |

And a diff extraction pattern using `git merge-base`, not `HEAD~1`:

```bash
BASE=$(git merge-base HEAD main 2>/dev/null || echo "HEAD~1")
git diff $BASE -- <file> | grep "^+" | grep -v "^+++"
```

`HEAD~1` only covers the last commit — misses all prior commits in a multi-commit PR.
