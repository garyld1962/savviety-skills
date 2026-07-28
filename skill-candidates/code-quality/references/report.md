# Code Quality — Report Format

---

## Template

```
## Code Quality Review — [branch or description]
[N files reviewed · N findings: N non-blocking, N discussion]

---

### ⚠️ Non-blocking

#### `path/to/file.ts:14` — Boolean missing prefix
**Found**: `const loading = false`
**Issue**: Boolean reads as a noun, not a question. Requires "is this a boolean?" mental check.
**Fix**: `const isLoading = false`

---

#### `path/to/file.ts:42` — Magic number
**Found**: `if (elapsed === 86400000)`
**Issue**: 86400000 requires mental arithmetic to understand.
**Fix**: `const ONE_DAY_MS = 24 * 60 * 60 * 1000; if (elapsed === ONE_DAY_MS)`

---

### 💬 Discussion

#### `path/to/service.ts:80–130` — Function may benefit from extraction
**Found**: `processCheckout` — 52 lines, 3 distinct phases (validate, save, notify)
**Note**: Sequential flow is readable. But validate/save/notify are testable units. Worth discussing if this grows further.

---

### ✅ Looks Good
- Boolean naming consistent in `components/Button.tsx` — `isDisabled`, `isLoading`, `hasError`
- Guard clauses used correctly in `services/auth.ts` — happy path fully unindented
[or: All N remaining checks passed.]
```

---

## Formatting Rules

**Found field**: Show the exact line from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Fix field**: Show the corrected code. One-liner where possible. Do not describe the fix — show it.

**No preamble**: Start directly with the `## Code Quality Review` header.

**No commands in the report**: Show findings, not the grep commands that found them.

**Collapse passed checks**: If >8 checks passed with no findings, write `All N remaining checks passed.` — do not enumerate.

**Praise sparingly**: Note one or two genuinely good decisions if present. "Guard clauses used correctly" beats generic "good job."

**Non-blocking tone**: Frame as impact on readability, not rule violation. "Requires mental check" beats "violates convention."

**Discussion tone**: Acknowledge the author may have reasons. "Worth discussing if this grows" beats "this should be refactored."

**Never**: "you should have", "this is wrong", "why did you". The code is the subject, not the author.

**Empty diff or non-code changes only**: Emit `No readability concerns — non-code changes only.` and stop.
