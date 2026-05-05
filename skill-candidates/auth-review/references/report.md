# Auth Review — Report Format

---

## Template

```
## Auth Review — [branch or PR description]
[N files reviewed · N findings: N blocking, N non-blocking, N discussion]

---

### Blocking

#### `src/auth/jwt.ts:23` — jwt.decode() used for authentication
**Found**: `const payload = jwt.decode(token); req.user = payload;`
**Risk**: decode() does not verify the signature. Any forged payload is accepted as valid.
**Fix**: `const payload = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] });`

---

#### `src/api/orders.ts:67` — IDOR: order fetched without ownership check
**Found**: `const order = await db.order.findUnique({ where: { id: req.params.id } })`
**Risk**: Any authenticated user can access any order by guessing or enumerating IDs.
**Fix**: Add `userId: req.user.id` to the where clause.

---

### Non-blocking

#### `src/auth/session.ts:41` — Session not regenerated after login
**Found**: `req.session.userId = user.id;`
**Impact**: Session fixation: attacker sets session ID before login, then uses it after.
**Fix**: Call `req.session.regenerate()` before setting `userId`.

---

### Discussion

#### `src/auth/login.ts:88` — No account lockout on failed attempts
**Found**: `app.post('/login', loginHandler)`
**Consideration**: Rate limiting slows brute force, but no lockout means a slow attack over hours is still viable. Worth adding failed-attempt tracking per email?

---

### Passed
- Argon2id used for password hashing in `auth/register.ts` — correct algorithm
- Refresh token rotated on each use in `auth/refresh.ts`
All 6 remaining checks passed.
```

---

## Formatting Rules

**Found field**: exact line(s) from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Fix field** (blocking and non-blocking): show corrected code, not a description. One-liner where possible.

**No commands in the report**: show findings, not the grep that found them.

**No preamble**: start directly with the `## Auth Review` header.

**Collapse passed checks**: if all checks pass on more than 8 files, write `All N remaining checks passed.`

**Praise sparingly**: note one or two correct, non-obvious auth decisions if present (e.g., Argon2id with OWASP params, token family rotation, constant-time comparison). Omit if blocking findings exist.

**Empty diff**: emit `No auth concerns — non-code changes only.` and stop.

---

## Comment Style

- **Blocking**: explain the attack, not just the rule. "Any forged payload is accepted" beats "verify() required."
- **Non-blocking**: frame as risk and impact. "Session fixation possible" beats "regenerate() missing."
- **Discussion**: acknowledge the author may have reasons. "Worth considering lockout?" beats "you must implement lockout."
- **Never**: "you should have", "this is wrong", "why didn't you". The code is the subject, not the author.
