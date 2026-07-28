# Security Review — Checks

All checks run against added lines only (see SKILL.md Step 2 for extraction command).

Language tags: `[js]` = JS/TS only, `[py]` = Python only, no tag = language-agnostic.

---

## Tier 1 — Auto-Flag (Blocking)

Run against all changed source files.

### Hardcoded Secrets / Credentials

```bash
grep -nE "(password|passwd|pwd)\s*[=:]\s*['\"][^\$\{'\"][^'\"]{3,}['\"]|\
api[_-]?key\s*[=:]\s*['\"][^\$\{'\"][^'\"]{8,}['\"]|\
secret\s*[=:]\s*['\"][^\$\{'\"][^'\"]{8,}['\"]|\
token\s*[=:]\s*['\"][^\$\{'\"][^'\"]{8,}['\"]|\
sk_live_[a-zA-Z0-9]+|ghp_[a-zA-Z0-9]+|AKIA[A-Z0-9]{16}" <file> | head -5
```

Flag all matches. Applies to test files — secrets in tests leak to git history.

### SQL Injection via Template Literal [js]

```bash
grep -nE "(SELECT|INSERT|UPDATE|DELETE|WHERE).*\$\{|\
query\s*\(\s*[\x60'\"].*\$\{|\
db\.raw\s*\(\s*[\x60'\"].*\$\{" <file> | head -5
```

Flag any SQL string containing interpolation. Prisma tagged template literals (`prisma.\$queryRaw\`\``) are safe — check context.

### SQL Injection via f-string [py]

```bash
grep -nE "f['\"]SELECT.*\{|f['\"]INSERT.*\{|f['\"]UPDATE.*\{|\
['\"]SELECT.*['\"].*(\.format\(|\+\s*\w)" <file> | head -5
```

### Dynamic Code Execution [js]

```bash
grep -nE "\beval\s*\(|\bnew\s+Function\s*\(|\
setTimeout\s*\(\s*['\"]|setInterval\s*\(\s*['\"]" <file> | head -5
```

### Shell Command Injection [js]

```bash
grep -nE "exec\s*\(\s*[\x60'\"].*\$\{|execSync\s*\(\s*[\x60'\"].*\$\{|\
spawn\s*\([^,\)]*\$\{|child_process.*\$\{" <file> | head -5
```

### Shell Command Injection [py]

```bash
grep -nE "os\.system\s*\(|subprocess\.[a-z]+\s*\(\s*f['\"]|\
subprocess\.[a-z]+\s*\(\s*['\"].*\+\s*\w" <file> | head -5
```

### innerHTML / XSS Sinks [js]

```bash
grep -nE "\.innerHTML\s*=|\.outerHTML\s*=|document\.write\s*\(|\
v-html\s*=" <file> | head -5
```

For `dangerouslySetInnerHTML`, flag only if `DOMPurify.sanitize` is absent within ±3 lines:
```bash
grep -n "dangerouslySetInnerHTML" <file> | head -5
```

### HTTP (Non-HTTPS) External URL [js]

```bash
grep -nE "fetch\s*\(\s*['\"]http://(?!localhost|127\.0\.0\.1)|\
axios\.[a-z]+\s*\(\s*['\"]http://(?!localhost)" <file> | head -5
```

### Unvalidated Redirect [js]

```bash
grep -nE "res\.redirect\s*\(\s*req\.(query|params|body)|\
window\.location\s*=.*\$\{" <file> | head -5
```

### Path Traversal [js]

```bash
grep -nE "readFile(Sync)?\s*\(.*req\.(params|query|body)|\
path\.join\s*\([^)]*req\.(params|query|body)|\
res\.(sendFile|download)\s*\([^)]*req\." <file> | head -5
```

### JWT `none` Algorithm Acceptance [js]

```bash
grep -nE "algorithms\s*:\s*\[.*['\"]none['\"]|\
algorithm\s*:\s*['\"]none['\"]" <file> | head -5
```

### Missing Auth on Sensitive Routes [js]

```bash
grep -nE "app\.(get|post|put|patch|delete)\s*\(\s*['\"][^'\"]*/(admin|user|account|payment|order|invoice|delete|internal)[^'\"]*['\"]" <file> \
  | head -10
```

Check if each match has auth middleware visible in the route arguments. Routes with only the handler callback and no middleware function are suspicious.

---

## Tier 2 — Judgment Required

### Insecure Cookie (Missing httpOnly / Secure / SameSite) [js]

```bash
grep -n "res\.cookie\|setCookie\|Set-Cookie" <file> | head -5
```

Flag if the options object within ±5 lines lacks `httpOnly: true`. Also flag explicit `secure: false` or absent `sameSite`.

### Verbose Errors Leaking Stack Traces [js]

```bash
grep -nE "res\.(json|send)\s*\([^)]*\berr\.(stack|message)\b|\
res\.(json|send)\s*\([^)]*stack:" <file> | head -5
```

Flag unless `NODE_ENV === 'production'` guard is visible.

### Weak Hash for Passwords [js]

```bash
grep -nE "createHash\s*\(\s*['\"]md5['\"]|createHash\s*\(\s*['\"]sha1['\"]|\
createHash\s*\(\s*['\"]sha256['\"].*password" <file> | head -5
```

### Weak Hash for Passwords [py]

```bash
grep -nE "hashlib\.(md5|sha1)\s*\(.*password|hashlib\.sha256\s*\(.*password" <file> | head -5
```

### CORS Wildcard [js]

```bash
grep -nE "origin\s*:\s*['\"]?\*['\"]?|cors\s*\(\s*\)|\
Access-Control-Allow-Origin.*\*" <file> | head -5
```

Flag `origin: '*'` if `credentials: true` appears nearby. `cors()` with no args always flag.

### Mass Assignment [js]

```bash
grep -nE "\.\.\.(req\.body|request\.body)|\
data\s*:\s*req\.body(?!\[)|\
(create|update|save)\s*\(\s*req\.body\s*\)" <file> | head -5
```

### Timing-Unsafe Secret Comparison [js]

```bash
grep -nE "(password|token|secret|apiKey|hash)\s*===\s*[a-zA-Z_]|\
===\s*(password|token|secret|apiKey|hash)" <file> | head -5
```

### IDOR — Resource Fetched Without Ownership Check [js]

```bash
grep -nE "(findUnique|findFirst|findById|findOne)\s*\(\s*\{[^}]*id\s*:\s*(req\.params|req\.query)" <file> | head -5
```

Flag if `userId`, `ownerId`, or similar ownership field absent from same `where` clause.

---

## Tier 3 — Discussion Points

### Missing Rate Limiting on Auth Endpoints [js]

```bash
grep -nE "app\.(post|get)\s*\(\s*['\"][^'\"]*/(login|signin|auth|token|reset)['\"]" <file> \
  | grep -v "rateLimit\|throttle\|limiter" | head -5
```

### Logging Potentially Sensitive Fields [js]

```bash
grep -nE "console\.(log|info|debug|error)\s*\(.*\b(password|token|secret|apiKey)\b|\
logger\.\w+\s*\(.*req\.body" <file> | head -5
```

### Missing CSP Headers

```bash
grep -n "Content-Security-Policy\|contentSecurityPolicy\|helmet" <file> | head -5
```

Flag absence of CSP in HTTP header config files or middleware setup files only.
