# Security Review — Report Format

---

## Template

```
## Security Review — [branch or PR description]
[N files reviewed · N findings: N blocking, N non-blocking, N discussion]

---

### Blocking

#### `path/to/file.ts:42` — Hardcoded API key
**Found**: `const STRIPE_KEY = 'sk_live_abc123xyz'`
**Risk**: Secret visible in git history permanently. Anyone with repo access can use it.
**Fix**: `const STRIPE_KEY = process.env.STRIPE_SECRET_KEY`

---

#### `path/to/route.ts:88` — SQL injection via template literal
**Found**: `` const q = `SELECT * FROM users WHERE email = '${email}'` ``
**Risk**: Attacker input `' OR '1'='1` dumps entire table.
**Fix**: `const result = await db.query('SELECT * FROM users WHERE email = $1', [email])`

---

### Non-blocking

#### `path/to/auth.ts:34` — Cookie missing httpOnly flag
**Found**: `res.cookie('session', token, { secure: true })`
**Impact**: Cookie accessible to JavaScript — any XSS vulnerability can steal sessions.
**Fix**: Add `httpOnly: true, sameSite: 'lax'` to cookie options.

---

### Discussion

#### `path/to/api.ts:15` — No rate limiting on /login
**Found**: `app.post('/login', loginHandler)`
**Consideration**: No rate limiter visible. Enables credential stuffing at scale. Worth adding `express-rate-limit` here?

---

### Passed
- Input validated with Zod schema in `api/users.ts` — correct placement at boundary
- Parameterized queries throughout `db/queries.ts`
All 8 remaining checks passed.
```

---

## Formatting Rules

**Found field**: the exact line(s) from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Fix field** (blocking and non-blocking): show corrected code, not a description of it. One-liner where possible.

**No commands in the report**: show findings, not the grep commands that found them.

**No preamble**: start directly with the `## Security Review` header.

**Collapse passed checks**: if all checks pass on more than 8 files, write `All N remaining checks passed.` Do not list each file individually.

**Praise sparingly**: note one or two genuinely good security decisions if present. Omit if there are blocking findings.

**Empty diff**: emit `No security concerns — non-code changes only.` and stop.

---

## Comment Style

- **Blocking**: state the exploit, not just the rule. "Attacker sends `' OR 1=1--` and gets all rows" beats "parameterized queries required."
- **Non-blocking**: frame as risk, not violation. "Cookie accessible to XSS" beats "httpOnly missing."
- **Discussion**: acknowledge the author may have good reasons. "Worth adding rate limiting?" beats "you must add rate limiting."
- **Never**: "you should have", "this is wrong", "why didn't you". The code is the subject, not the author.
- **Test files with secrets**: be direct — "Secrets in test files are committed to git history and equally exposed as production secrets."
