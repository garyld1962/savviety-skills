# Auth Review — Checks

All checks run against added lines only (see SKILL.md Step 2 for extraction command).

---

## Tier 1 — Auto-Flag (Blocking)

### JWT Stored in localStorage

```bash
grep -nE "localStorage\.(setItem|getItem)\s*\([^,]*['\"].*token|\
localStorage\.(setItem|getItem)\s*\([^,]*['\"].*jwt|\
localStorage\.(setItem|getItem)\s*\([^,]*['\"].*access" <file> | head -5
```

XSS-accessible storage for auth tokens. Flag unconditionally.

### Token in URL Parameter

```bash
grep -nE "\?.*token=|\?.*access_token=|\?.*jwt=|\
searchParams\.(set|append)\s*\(['\"]token['\"]|\
params\.(set|append)\s*\(['\"]access_token['\"]" <file> | head -5
```

Tokens in URLs appear in server logs, CDN logs, proxy logs, and browser history.

### Plaintext Password Storage or Comparison

```bash
grep -nE "password\s*:\s*req\.body\.password|\
password\s*:\s*plaintext|\
user\.password\s*=\s*(password|req\.body\.)|\
\.password\s*===\s*" <file> | head -5
```

Flag if password appears to be stored or compared without hashing function in context.

### Weak Hash for Passwords (MD5, SHA1, SHA256)

```bash
grep -nE "(md5|sha1|sha256)\s*\([^)]*password|\
createHash\s*\(\s*['\"]md5['\"]|createHash\s*\(\s*['\"]sha1['\"]|\
hashlib\.(md5|sha1)\s*\(" <file> | head -5
```

These algorithms are designed to be fast — millions/sec on GPU. Use bcrypt or Argon2id.

### Missing JWT Signature Verification (decode instead of verify)

```bash
grep -nE "jwt\.decode\s*\(.*\.(userId|sub|role|admin|email)|\
decode\s*\(.*token.*\.(userId|sub|role)|\
\.decode\([^)]*\)\.(sub|userId|role|admin)" <file> | head -5
```

`decode()` does NOT verify the signature. Any payload can be forged.

### JWT Verification Without Explicit Algorithm

```bash
grep -nE "jwt\.verify\s*\(\s*\w+\s*,\s*\w+\s*\)(?!\s*[,{])|\
jwt\.verify\s*\(\s*[^)]+\)(?!.*algorithms)" <file> | head -5
```

Without `algorithms: ['HS256']` (or RS256), the `alg:none` attack is possible on some libraries.

### Hardcoded JWT Secret

```bash
grep -nE "jwt\.(sign|verify)\s*\([^,]+,\s*['\"][^'\"]{4,}['\"]|\
(JWT_SECRET|secret)\s*[=:]\s*['\"][a-zA-Z0-9_\-]{4,}['\"]" <file> | head -5
```

Flag if the secret appears to be a literal string, not `process.env.*`.

### OAuth State Parameter Missing

```bash
grep -nE "/authorize\?(?!.*state=)|authorizationUrl(?!.*state)|\
oauth.*callback(?![\s\S]{0,300}state)" <file> | head -5
```

Without state validation, OAuth CSRF (login CSRF) is possible.

### IDOR — User-Supplied ID Without Ownership Check

```bash
grep -nE "(findUnique|findFirst|findById|findOne|getById)\s*\(\s*\{?[^}]*id\s*:\s*(req\.params|req\.query)\." <file> \
  | grep -v "userId\|ownerId\|req\.user\.id" | head -5
```

Flag if query uses a URL/query param ID without scoping to the current user.

### Missing Authorization on Sensitive Operation

```bash
grep -nE "app\.(delete|put|patch)\s*\(\s*['\"][^'\"]*/:id['\"]" <file> \
  | head -5
```

Check if auth middleware is in the argument list. Route with `/:id` and no middleware is suspicious.

---

## Tier 2 — Judgment Required

### Session Cookie Missing Security Flags

```bash
grep -n "res\.cookie\|setCookie\|session(" <file> | head -10
```

Flag if session cookie set without `httpOnly: true`. Check ±5 lines. Also flag `secure: false` or missing `sameSite`.

### JWT Expiry Not Checked / Too Long

```bash
grep -nE "expiresIn\s*:\s*['\"][0-9]+d['\"]|\
expiresIn\s*:\s*['\"][2-9][0-9]*h['\"]|\
expiresIn\s*:\s*86400|maxAge\s*:\s*86400000" <file> | head -5
```

Access tokens beyond 1 hour are non-blocking but worth flagging. Refresh tokens can be longer.

### Refresh Token Not Rotated on Use

```bash
grep -n "refresh" <file> | grep -v "rotate\|revoke\|delete\|update\|invalidate\|family" | head -5
```

Flag if refresh token logic doesn't visibly invalidate the old token on each use.

### Session Not Regenerated After Login

```bash
grep -nE "session\.(userId|user)\s*=(?![\s\S]{0,80}regenerate)|\
req\.session\.[a-zA-Z]+\s*=.*user(?![\s\S]{0,100}regenerate)" <file> | head -5
```

Session fixation: attacker pre-sets a session ID, victim logs in, attacker hijacks the now-authenticated session.

### bcrypt Cost Factor Too Low

```bash
grep -nE "bcrypt\.(hash|genSalt)\s*\([^,]+,\s*[1-9]\s*\)|\
bcrypt\.(hash|genSalt)\s*\([^,]+,\s*1[01]\s*\)" <file> | head -5
```

Cost factor below 12 is non-blocking but meaningfully reduces brute-force resistance.

### Specific Auth Error Messages (User Enumeration)

```bash
grep -nEi "['\"]user.*not.*found['\"]|['\"]invalid.*password['\"]|\
['\"]wrong.*password['\"]|['\"]email.*not.*registered['\"]" <file> | head -5
```

Error specificity lets attackers enumerate valid email addresses. Use "Invalid credentials."

### Timing-Unsafe Comparison for Secrets

```bash
grep -nE "(password|token|secret|apiKey|hash)\s*===\s*[a-zA-Z_]" <file> | head -5
```

---

## Tier 3 — Discussion Points

### No MFA for Sensitive Operations

```bash
grep -nE "app\.(post|get)\s*\(\s*['\"][^'\"]*/(login|admin|payment|transfer|delete)['\"]" <file> \
  | grep -v "mfa\|totp\|2fa\|twoFactor\|otp" | head -5
```

Note if no MFA visible on high-risk operations. Discussion, not a blocker.

### Overly Broad OAuth Scopes

```bash
grep -nE "scope.*['\"][^'\"]*\*(all|:write|:admin)[^'\"]*['\"]|\
scope.*['\"][^'\"]*(admin|write:all)[^'\"]*['\"]" <file> | head -5
```

### No Account Lockout on Failed Attempts

```bash
grep -nE "app\.post\s*\(\s*['\"][^'\"]*/(login|signin)['\"]" <file> \
  | grep -v "lockout\|lock\|block\|rateLimit\|limiter" | head -5
```

Missing lockout allows brute force even with rate limiting at lower rates.
